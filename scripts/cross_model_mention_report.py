"""Cross-model mention detection report.

Compares mentions detected by GSAP, SciER, and SciNLP across all three
datasets' dev sets (combined). Groups each mention into one of 7 categories
based on which subset of models detected it, using gsaphub partial span matching.

Predictions are unified via apply_unification_pipeline using the model's label
scheme (trained_on), since predictions carry the model's label vocabulary
regardless of which dataset they are evaluated on.
"""

import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gsaphub.match.entities import partial

from unifiedsciere.analysis.label_confusion import (
    _mentions_to_gsaphub_format,
)
from unifiedsciere.data_loader import load_corpus
from unifiedsciere.unification.pipeline import apply_unification_pipeline

MODELS = ["gsap", "scier", "scinlp"]
DATASETS = ["gsap", "scier", "scinlp"]
ENTITY_TYPES = ["Dataset", "Method", "Task"]

# Pipeline config: merge + drop + map + span normalization, no dataset-specific corrections
PIPELINE_CONFIG = {
    "merge_stacked": {"enabled": True, "prefer_larger": True},
    "drop_unmapped": {"enabled": True},
    "map_labels": {"enabled": True},
    "dataset_corrections": {
        "gsap": {"enabled": False},
        "scier": {"enabled": False},
        "scinlp": {"enabled": False},
    },
    "span_normalization": {"enabled": True},
}

# Human-readable group names, ordered: single models, pairs, all three
GROUP_ORDER = [
    frozenset(["gsap"]),
    frozenset(["scier"]),
    frozenset(["scinlp"]),
    frozenset(["gsap", "scier"]),
    frozenset(["gsap", "scinlp"]),
    frozenset(["scier", "scinlp"]),
    frozenset(["gsap", "scier", "scinlp"]),
]

GROUP_NAMES = {
    frozenset(["gsap"]): "GSAP only",
    frozenset(["scier"]): "SciER only",
    frozenset(["scinlp"]): "SciNLP only",
    frozenset(["gsap", "scier"]): "GSAP + SciER",
    frozenset(["gsap", "scinlp"]): "GSAP + SciNLP",
    frozenset(["scier", "scinlp"]): "SciER + SciNLP",
    frozenset(["gsap", "scier", "scinlp"]): "All three",
}

TOP_N = 30  # Number of top mentions to show per group


def load_and_unify(dataset: str, model: str):
    """Load predictions and apply unification pipeline.

    Uses the model name (trained_on) as the label scheme for unification,
    since predictions carry the model's label vocabulary regardless of
    which dataset they are evaluated on.
    """
    corpus = load_corpus(dataset, "dev", data_type="predictions", trained_on=model)
    # Use model (trained_on) as the dataset parameter for label mapping,
    # since predictions use the model's label scheme
    corpus, _ = apply_unification_pipeline(
        corpus,
        dataset=model,
        config=PIPELINE_CONFIG,
        apply_to_gold=False,
        apply_to_predicted=True,
    )
    return corpus


def run_matching_for_dataset(dataset: str):
    """Load all 3 models for a dataset, run pairwise matching, return canonical mentions.

    Returns a list of dicts: {text, label, detected_by: frozenset}
    """
    # Load and convert mentions per model
    model_ents = {}  # model -> list of gsaphub entity dicts

    for model in MODELS:
        corpus = load_and_unify(dataset, model)
        mentions = corpus.mentions_predicted
        # Convert to gsaphub format — doc_ids are already consistent across models
        # within a dataset, so no normalization needed
        ents = _mentions_to_gsaphub_format(mentions, normalize_doc_id=False)
        # Store original text on each entity dict for later use
        for ent, mention in zip(ents, mentions):
            ent["text"] = mention.text
        model_ents[model] = ents

    # Run pairwise partial matching: for each model, annotate with matches from other models
    for model_a in MODELS:
        for model_b in MODELS:
            if model_a == model_b:
                continue
            target_key = f"matched_by_{model_b}"
            partial(
                model_ents[model_a],
                model_ents[model_b],
                target_key=target_key,
                only_same_annotator=False,
            )

    # Build canonical mention list using deduplication:
    # Iterate models in fixed order. A mention from model X is canonical only if
    # it was NOT matched by any earlier model.
    canonical_mentions = []

    for i, model in enumerate(MODELS):
        earlier_models = MODELS[:i]
        for ent in model_ents[model]:
            # Check if this mention was already matched by an earlier model
            matched_by_earlier = False
            for earlier in earlier_models:
                key = f"matched_by_{earlier}"
                if ent.get(key):
                    matched_by_earlier = True
                    break

            if matched_by_earlier:
                continue  # Already counted via an earlier model's canonical mention

            # This is a canonical mention. Determine full detected_by set.
            detected_by = {model}
            for other_model in MODELS:
                if other_model == model:
                    continue
                key = f"matched_by_{other_model}"
                if ent.get(key):
                    detected_by.add(other_model)

            canonical_mentions.append(
                {
                    "text": ent["text"],
                    "label": ent["label"],
                    "detected_by": frozenset(detected_by),
                }
            )

    return canonical_mentions


def generate_report(all_mentions):
    """Generate the markdown report from all canonical mentions."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Aggregate: (label, group) -> list of texts
    group_data = defaultdict(list)
    for m in all_mentions:
        group_data[(m["label"], m["detected_by"])].append(m["text"])

    # --- Overview table ---
    md = f"""# Cross-Model Mention Detection Report

**Generated:** {timestamp}
**Split:** dev (all three datasets combined: GSAP, SciER, SciNLP)
**Matching:** gsaphub partial span matching
**Unification:** apply_unification_pipeline (merge stacked, drop unmapped, map labels, normalize spans)

## Overview

This report analyzes which mentions are detected by which subset of the three
models (GSAP, SciER, SciNLP). All predictions are unified via the standard
unification pipeline (using each model's label scheme) before comparison.
Mentions are matched across models using partial span overlap within each
dataset's dev set, then combined across all three datasets.

### Mention Counts by Group and Entity Type

"""

    # Build table header
    md += "| Group | "
    md += " | ".join(f"{et} (total / unique)" for et in ENTITY_TYPES)
    md += " | Total (total / unique) |\n"
    md += "| ----- | "
    md += " | ".join("---:" for _ in ENTITY_TYPES)
    md += " | ---: |\n"

    for group in GROUP_ORDER:
        name = GROUP_NAMES[group]
        row_total = 0
        row_unique = 0
        cells = []
        for et in ENTITY_TYPES:
            texts = group_data.get((et, group), [])
            total = len(texts)
            unique = len(set(texts))
            row_total += total
            row_unique += unique
            cells.append(f"{total:,} / {unique:,}")
        md += (
            f"| {name} | "
            + " | ".join(cells)
            + f" | {row_total:,} / {row_unique:,} |\n"
        )

    # Totals row
    md += "| **Total** | "
    grand_total = 0
    grand_unique_total = 0
    for et in ENTITY_TYPES:
        et_total = sum(len(group_data.get((et, g), [])) for g in GROUP_ORDER)
        et_unique = len(
            set(t for g in GROUP_ORDER for t in group_data.get((et, g), []))
        )
        grand_total += et_total
        grand_unique_total += et_unique
        md += f"**{et_total:,} / {et_unique:,}** | "
    md += f"**{grand_total:,} / {grand_unique_total:,}** |\n"

    # --- Detailed lists per entity type ---
    for et in ENTITY_TYPES:
        md += f"\n---\n\n## {et}\n"

        for group in GROUP_ORDER:
            name = GROUP_NAMES[group]
            texts = group_data.get((et, group), [])
            if not texts:
                md += f"\n### {name}\n\n*No mentions in this group.*\n"
                continue

            counter = Counter(texts)
            total = len(texts)
            unique = len(counter)
            top = counter.most_common(TOP_N)

            md += f"\n### {name}\n\n"
            md += f"**{total:,}** mentions, **{unique:,}** unique\n\n"
            md += "| Rank | Mention Text | Count |\n"
            md += "|-----:|:-------------|------:|\n"
            for rank, (text, count) in enumerate(top, 1):
                escaped = text.replace("|", "\\|")
                md += f"| {rank} | {escaped} | {count} |\n"

            remaining = unique - len(top)
            if remaining > 0:
                md += f"\n*... and {remaining:,} more unique mentions.*\n"

    md += """
---

## Notes

- **Matching method:** gsaphub `partial()` span matching — two mentions match if their
  character spans overlap within the same document and sentence.
- **Unification pipeline:** Predictions are processed through the standard pipeline
  (merge stacked mentions, drop unmapped labels, map to unified schema, normalize spans).
  Label mapping uses the **model's** label scheme (not the dataset's), since predictions
  carry the vocabulary of the model that produced them.
- **Deduplication:** Each physical mention span is counted once. When multiple models
  detect overlapping spans, the mention is attributed to all detecting models but counted
  only once in the group totals.
- **"Total"** counts mention occurrences; **"Unique"** counts distinct mention texts.

---
*Generated by UnifiedSciERE Cross-Model Mention Report*
"""

    return md


def main():
    print("Loading and matching mentions across all models and datasets...")

    all_mentions = []
    for dataset in DATASETS:
        print(f"  Processing dataset: {dataset}")
        mentions = run_matching_for_dataset(dataset)
        all_mentions.extend(mentions)
        print(f"    -> {len(mentions)} canonical mentions")

    print(f"\nTotal canonical mentions: {len(all_mentions)}")

    # Generate report
    report = generate_report(all_mentions)

    # Write report
    output_dir = Path("reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "cross_model_mention_report_dev.md"
    output_path.write_text(report)
    print(f"\nReport written to: {output_path}")


if __name__ == "__main__":
    main()
