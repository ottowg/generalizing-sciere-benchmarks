"""Analyze span differences between models on partial (non-exact) matches.

For each anchor model, finds predictions that partially overlap with other models'
predictions but have different span boundaries. Reports the most frequent text pairs
to identify systematic span extension/reduction patterns.
"""

import copy
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from gsaphub.match.entities import partial

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.types import Mention
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["scier", "scinlp", "gsap"]] = ["scier", "scinlp", "gsap"]
MODELS: list[Literal["scier", "scinlp", "gsap"]] = ["scier", "scinlp", "gsap"]
SPLIT: Literal["dev"] = "dev"
TOP_N = 30


def _mentions_to_gsaphub_format(
    mentions: list[Mention],
) -> list[dict]:
    """Convert Mention objects to gsaphub dict format with normalized doc_ids."""
    result = []
    for m in mentions:
        # Normalize doc_id: strip model prefix for cross-model matching
        # e.g. "gsap_scier_dev_0" -> "scier_dev_0"
        doc_id = m.document_id
        parts = doc_id.split("_", 1)
        if len(parts) > 1:
            doc_id = parts[1]

        result.append(
            {
                "id": m.id,
                "doc_id": doc_id,
                "begin": m.begin,
                "end": m.end,
                "label": m.label,
                "annotator": m.annotator,
            }
        )
    return result


def load_unified_predictions(
    dataset: Literal["scier", "scinlp", "gsap"],
    model: Literal["scier", "scinlp", "gsap"],
) -> list[Mention]:
    """Load predictions and apply unification pipeline."""
    corpus = load_corpus(dataset, SPLIT, data_type="predictions", trained_on=model)
    unified, _ = apply_unification_pipeline(
        corpus,
        dataset=model,
        apply_to_gold=False,
        apply_to_predicted=True,
    )
    return unified.mentions_predicted


def find_partial_only_matches(
    anchor_mentions: list[Mention],
    comp_mentions: list[Mention],
) -> list[tuple[Mention, Mention]]:
    """Find mention pairs that overlap but don't have exact spans.

    Returns list of (anchor_mention, comp_mention) tuples.
    """
    # Convert to gsaphub format (with normalized doc_ids)
    anchor_gs = _mentions_to_gsaphub_format(anchor_mentions)
    comp_gs = _mentions_to_gsaphub_format(comp_mentions)

    # Build lookups: gsaphub id -> original Mention
    anchor_by_id = {m.id: m for m in anchor_mentions}
    comp_by_id_gs = {m["id"]: m for m in comp_gs}
    comp_by_id = {m.id: m for m in comp_mentions}

    # Run partial matching (mutates anchor_gs in-place)
    partial(anchor_gs, comp_gs, target_key="matched_ent_ids", only_same_annotator=False)

    pairs = []
    for a_ent in anchor_gs:
        matched_ids = a_ent.get("matched_ent_ids", [])
        if not matched_ids:
            continue

        a_mention = anchor_by_id[a_ent["id"]]

        for c_id in matched_ids:
            c_gs = comp_by_id_gs[c_id]
            # Skip exact span matches
            if a_ent["begin"] == c_gs["begin"] and a_ent["end"] == c_gs["end"]:
                continue
            c_mention = comp_by_id[c_id]
            pairs.append((a_mention, c_mention))

    return pairs


def main():
    output_dir = Path("reports/ere_confusion_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Pre-load all unified predictions: cache[dataset][model] -> list[Mention]
    print("Loading and unifying all predictions...")
    cache: dict[str, dict[str, list[Mention]]] = defaultdict(dict)
    for dataset in DATASETS:
        for model in MODELS:
            print(f"  {model} -> {dataset}")
            cache[dataset][model] = load_unified_predictions(dataset, model)

    md = f"""# Span Difference Analysis (Partial Matches)

**Generated:** {timestamp}

**Split:** {SPLIT}

## Overview

For each anchor model, this report lists predictions that partially overlap with
other models' predictions but have **different span boundaries** (non-exact matches).

The most frequent text pairs are shown to reveal systematic span extension/reduction
patterns (e.g., "the X" vs "X", or "Y dataset" vs "Y").

All predictions are evaluated after applying the complete unification pipeline.

"""

    for anchor_model in MODELS:
        md += f"## {anchor_model.upper()} Model (anchor)\n\n"
        comp_models = [m for m in MODELS if m != anchor_model]

        # Collect all partial-only pairs across datasets and comparison models
        # Key: (anchor_label, anchor_text, comp_text, comp_model)
        all_pairs: list[tuple[str, str, str, str]] = []

        for dataset in DATASETS:
            anchor_preds = cache[dataset][anchor_model]
            for comp_model in comp_models:
                comp_preds = cache[dataset][comp_model]
                pairs = find_partial_only_matches(anchor_preds, comp_preds)
                for a_m, c_m in pairs:
                    all_pairs.append(
                        (a_m.label, a_m.text, c_m.text, comp_model.upper())
                    )

        if not all_pairs:
            md += "No partial-only matches found.\n\n---\n\n"
            continue

        # Group by entity type
        by_label: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        for label, a_text, c_text, c_model in all_pairs:
            by_label[label].append((a_text, c_text, c_model))

        for label in sorted(by_label.keys()):
            entries = by_label[label]
            md += f"### {label} ({len(entries)} partial matches)\n\n"

            # Count unique (anchor_text, comp_text) pairs, track which comp models
            pair_counter: Counter[tuple[str, str]] = Counter()
            pair_models: dict[tuple[str, str], set[str]] = defaultdict(set)
            for a_text, c_text, c_model in entries:
                pair_counter[(a_text, c_text)] += 1
                pair_models[(a_text, c_text)].add(c_model)

            md += f"| # | {anchor_model.upper()} Text | Other Model Text | Count | Models |\n"
            md += f"|---|{'-' * len(anchor_model + ' Text')}--|------------------|-------|--------|\n"

            for rank, ((a_text, c_text), count) in enumerate(
                pair_counter.most_common(TOP_N), 1
            ):
                models_str = ", ".join(sorted(pair_models[(a_text, c_text)]))
                a_esc = a_text.replace("|", "\\|")
                c_esc = c_text.replace("|", "\\|")
                md += f"| {rank} | {a_esc} | {c_esc} | {count} | {models_str} |\n"

            remaining = len(pair_counter) - TOP_N
            if remaining > 0:
                md += f"\n*... and {remaining} more unique pairs*\n"

            md += "\n"

        md += "---\n\n"

    md += """## Notes

- **Partial match**: Overlapping spans where begin/end offsets differ between models
- **Exact matches are excluded**: Only span differences are shown
- Pairs are aggregated across all three dev datasets (SCIER, SCINLP, GSAP)
- All predictions processed through the full unification pipeline

---
*Generated by UnifiedSciERE Span Difference Analysis*
"""

    out_path = output_dir / f"span_differences_{SPLIT}.md"
    out_path.write_text(md)
    print(f"\nReport saved to: {out_path}")


if __name__ == "__main__":
    main()
