"""GSAP-specific analysis to identify unmatched MLModelGeneric predictions.

This module analyzes GSAP predictions that don't match SciER or SciNLP predictions,
focusing specifically on Method (unified label) and MLModelGeneric (original label)
mentions to identify systematic errors in GSAP predictions.
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from gsaphub.match.entities import partial

from ..data_loader import load_corpus
from .label_mapper import drop_unmapped_mentions, map_labels_to_unified
from .merge_stacked import merge_stacked_mentions


def analyze_gsap_unmatched_mlmodelgeneric(
    datasets: list[Literal["scier", "scinlp", "gsap"]],
    split: Literal["train", "dev", "test"],
    prefer_larger: bool = True,
    output_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Analyze GSAP MLModelGeneric predictions that don't match SciER or SciNLP.

    This function identifies GSAP predictions with unified label "Method" and
    original label "MLModelGeneric" that have no matching entity in either
    SciER or SciNLP predictions. This helps identify systematic overprediction
    or noise in GSAP's MLModelGeneric category.

    Args:
        datasets: List of datasets to analyze (typically ['scier', 'scinlp', 'gsap'])
        split: Data split to use
        prefer_larger: If True, prefer larger spans when merging
        output_dir: Output directory (default: reports/ere_confusion_analysis/unification/gsap_analysis/)

    Returns:
        Tuple of (json_path, report_path) for the generated files
    """
    if output_dir is None:
        output_dir = Path("reports/ere_confusion_analysis/unification/gsap_analysis")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load and process all datasets
    all_gsap_data = []
    all_scier_data = []
    all_scinlp_data = []

    for dataset in datasets:
        # Load GSAP predictions
        corpus_gsap = load_corpus(
            dataset, split, data_type="predictions", trained_on="gsap"
        )
        corpus_gsap = merge_stacked_mentions(
            corpus_gsap,
            prefer_larger=prefer_larger,
            merge_gold=False,
            merge_predicted=True,
        )[0]
        corpus_gsap = drop_unmapped_mentions(
            corpus_gsap, "gsap", drop_gold=False, drop_predicted=True
        )[0]
        corpus_gsap = map_labels_to_unified(
            corpus_gsap, "gsap", map_gold=False, map_predicted=True
        )[0]
        all_gsap_data.extend(corpus_gsap.mentions_predicted)

        # Load SciER predictions
        corpus_scier = load_corpus(
            dataset, split, data_type="predictions", trained_on="scier"
        )
        corpus_scier = merge_stacked_mentions(
            corpus_scier,
            prefer_larger=prefer_larger,
            merge_gold=False,
            merge_predicted=True,
        )[0]
        corpus_scier = drop_unmapped_mentions(
            corpus_scier, "scier", drop_gold=False, drop_predicted=True
        )[0]
        corpus_scier = map_labels_to_unified(
            corpus_scier, "scier", map_gold=False, map_predicted=True
        )[0]
        all_scier_data.extend(corpus_scier.mentions_predicted)

        # Load SciNLP predictions
        corpus_scinlp = load_corpus(
            dataset, split, data_type="predictions", trained_on="scinlp"
        )
        corpus_scinlp = merge_stacked_mentions(
            corpus_scinlp,
            prefer_larger=prefer_larger,
            merge_gold=False,
            merge_predicted=True,
        )[0]
        corpus_scinlp = drop_unmapped_mentions(
            corpus_scinlp, "scinlp", drop_gold=False, drop_predicted=True
        )[0]
        corpus_scinlp = map_labels_to_unified(
            corpus_scinlp, "scinlp", map_gold=False, map_predicted=True
        )[0]
        all_scinlp_data.extend(corpus_scinlp.mentions_predicted)

    # Filter GSAP mentions to only Method + MLModelGeneric
    gsap_mlmodelgeneric = [
        m
        for m in all_gsap_data
        if m.label == "Method" and m.label_original == "MLModelGeneric"
    ]

    # Convert to gsaphub format for matching
    def to_gsaphub(mentions):
        result = []
        for m in mentions:
            result.append(
                {
                    "id": m.id,
                    "doc_id": m.document_id,
                    "begin": m.begin,
                    "end": m.end,
                    "label": m.label,
                    "label_original": getattr(m, "label_original", ""),
                    "text": m.text,
                    "annotator": m.annotator,
                }
            )
        return result

    gsap_hub = to_gsaphub(gsap_mlmodelgeneric)
    scier_hub = to_gsaphub(all_scier_data)
    scinlp_hub = to_gsaphub(all_scinlp_data)

    # Match GSAP with SciER
    partial(
        gsap_hub, scier_hub, target_key="matched_scier_ids", only_same_annotator=False
    )

    # Match GSAP with SciNLP
    partial(
        gsap_hub, scinlp_hub, target_key="matched_scinlp_ids", only_same_annotator=False
    )

    # Find unmatched mentions (not matching either SciER or SciNLP)
    unmatched = []
    for g in gsap_hub:
        scier_match = g.get("matched_scier_ids", [])
        scinlp_match = g.get("matched_scinlp_ids", [])

        if not scier_match and not scinlp_match:
            unmatched.append(
                {
                    "text": g["text"],
                    "doc_id": g["doc_id"],
                    "begin": g["begin"],
                    "end": g["end"],
                    "gsap_label": g["label"],
                    "gsap_label_original": g["label_original"],
                }
            )

    # Group by text and count
    text_counts = defaultdict(list)
    for item in unmatched:
        text_counts[item["text"]].append(item)

    # Create summary statistics
    unmatched_by_text = {}
    for text, items in text_counts.items():
        unmatched_by_text[text] = {
            "count": len(items),
            "gsap_label": "Method",
            "gsap_label_original": "MLModelGeneric",
            "scier_label": "NIL",
            "scinlp_label": "NIL",
            "examples": items[:5],  # Keep up to 5 examples
        }

    # Sort by count
    sorted_unmatched = dict(
        sorted(unmatched_by_text.items(), key=lambda x: x[1]["count"], reverse=True)
    )

    # Save JSON resource
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"gsap_unmatched_mlmodelgeneric_{split}_{timestamp}.json"

    json_data = {
        "metadata": {
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "split": split,
            "datasets": datasets,
            "total_gsap_mlmodelgeneric": len(gsap_mlmodelgeneric),
            "total_unmatched": len(unmatched),
            "unique_unmatched_texts": len(sorted_unmatched),
        },
        "unmatched_by_text": sorted_unmatched,
    }

    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)

    # Generate markdown report
    report_path = output_dir / f"gsap_unmatched_mlmodelgeneric_{split}_{timestamp}.md"

    md_content = f"""# GSAP MLModelGeneric Unmatched Analysis

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Split:** {split}

**Datasets:** {", ".join([d.upper() for d in datasets])}

## Methodology

This analysis identifies GSAP predictions that are likely to be systematic errors or noise.
The methodology is as follows:

1. **Data Loading**: Load predictions from GSAP, SciER, and SciNLP models across all datasets
   ({", ".join([d.upper() for d in datasets])}) for the {split} split.

2. **Unification Pipeline**: Apply the complete unification pipeline to all predictions:
   - Merge stacked/overlapping mentions (prefer larger spans)
   - Drop unmapped labels (those mapping to null in unified schema)
   - Map labels to unified schema (Dataset, Method, Task)

3. **GSAP Filtering**: Select only GSAP predictions with:
   - **Unified label**: Method
   - **Original label**: MLModelGeneric

4. **Matching**: Use partial span matching (gsaphub) to find overlapping entities between:
   - GSAP vs SciER predictions
   - GSAP vs SciNLP predictions

5. **Unmatched Identification**: Identify GSAP predictions that have **no match** in either
   SciER or SciNLP. These represent potential systematic errors where GSAP predicts
   an entity that neither of the other two models recognize.

6. **Aggregation**: Group unmatched mentions by text and count occurrences.

## Summary Statistics

- **Total GSAP MLModelGeneric predictions**: {len(gsap_mlmodelgeneric):,}
- **Total unmatched predictions**: {len(unmatched):,} ({len(unmatched) / len(gsap_mlmodelgeneric) * 100:.1f}%)
- **Unique unmatched texts**: {len(sorted_unmatched):,}

## Top 50 Unmatched Mentions

The following table shows the most frequent GSAP MLModelGeneric predictions that have no
corresponding entity in either SciER or SciNLP predictions. These are likely candidates
for systematic error correction.

| Rank | Mention Text | GSAP Label | GSAP Original | SciER Label | SciNLP Label | Count |
|------|--------------|------------|---------------|-------------|--------------|-------|
"""

    # Add top 50
    for rank, (text, data) in enumerate(list(sorted_unmatched.items())[:50], 1):
        escaped_text = text.replace("|", "\\|")
        md_content += f"| {rank} | {escaped_text} | {data['gsap_label']} | {data['gsap_label_original']} | {data['scier_label']} | {data['scinlp_label']} | {data['count']} |\n"

    md_content += f"""

## Interpretation

The unmatched mentions often fall into these categories:

1. **Generic references**: Terms like "the model", "our model", "models" that are too
   generic or context-dependent to be useful entities.

2. **Procedural terms**: References to modeling processes rather than specific models
   (e.g., "fine-tuning", "training").

3. **False positives**: Text spans that GSAP incorrectly identifies as model mentions.

These unmatched mentions represent opportunities for improving GSAP's predictions through
systematic filtering or correction rules.

## Data Files

- **JSON Resource**: {json_path.name}
- **Report**: {report_path.name}

---
*Generated by UnifiedSciERE GSAP-Specific Analysis*
"""

    with open(report_path, "w") as f:
        f.write(md_content)

    return json_path, report_path


if __name__ == "__main__":
    # Example usage
    json_path, report_path = analyze_gsap_unmatched_mlmodelgeneric(
        datasets=["scier", "scinlp", "gsap"],
        split="dev",
        prefer_larger=True,
    )
    print(f"Generated JSON: {json_path}")
    print(f"Generated report: {report_path}")
