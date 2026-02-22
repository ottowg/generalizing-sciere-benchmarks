"""GSAP-specific corrections to filter out systematic errors.

This module provides functions to filter out GSAP predictions identified as
systematic errors through the gsap_specific_analysis module.
"""

import json
from pathlib import Path

from ..types import Corpus


def filter_gsap_mentions(
    corpus: Corpus,
    json_analysis_file: Path,
    min_count: int = 2,
    filter_predicted: bool = True,
    filter_gold: bool = False,
) -> tuple[Corpus, dict]:
    """Filter GSAP mentions based on unmatched analysis.

    This function removes mentions whose text appears in the unmatched analysis
    with a count >= min_count. This helps remove systematic errors like generic
    references ("the model", "models") that GSAP overpredicts.

    Args:
        corpus: Input corpus with GSAP predictions
        json_analysis_file: Path to JSON file from gsap_specific_analysis
        min_count: Minimum count threshold for filtering (default: 2)
        filter_predicted: If True, filter predicted mentions (default: True)
        filter_gold: If True, filter gold mentions (default: False)

    Returns:
        Tuple of:
        - New Corpus with filtered mentions
        - Dictionary with statistics about filtered mentions
    """
    # Load analysis data
    with open(json_analysis_file, "r") as f:
        analysis_data = json.load(f)

    # Get texts to filter (those with count >= min_count)
    texts_to_filter = set()
    for text, data in analysis_data["unmatched_by_text"].items():
        if data["count"] >= min_count:
            texts_to_filter.add(text)

    stats = {
        "total_texts_to_filter": len(texts_to_filter),
        "min_count_threshold": min_count,
        "gold_mentions_original": len(corpus.mentions),
        "gold_mentions_filtered": 0,
        "gold_mentions_kept": len(corpus.mentions),
        "gold_relations_original": len(corpus.relation),
        "gold_relations_filtered": 0,
        "gold_relations_kept": len(corpus.relation),
        "predicted_mentions_original": len(corpus.mentions_predicted),
        "predicted_mentions_filtered": 0,
        "predicted_mentions_kept": len(corpus.mentions_predicted),
        "predicted_relations_original": len(corpus.relations_predicted),
        "predicted_relations_filtered": 0,
        "predicted_relations_kept": len(corpus.relations_predicted),
        "filtered_texts": sorted(list(texts_to_filter)),
    }

    # Filter gold mentions
    if filter_gold:
        kept_mentions = [m for m in corpus.mentions if m.text not in texts_to_filter]
        kept_mention_ids = {m.id for m in kept_mentions}

        # Filter relations that reference filtered mentions
        kept_relations = [
            r
            for r in corpus.relation
            if r.subject.id in kept_mention_ids and r.object.id in kept_mention_ids
        ]

        stats["gold_mentions_filtered"] = len(corpus.mentions) - len(kept_mentions)
        stats["gold_mentions_kept"] = len(kept_mentions)
        stats["gold_relations_filtered"] = len(corpus.relation) - len(kept_relations)
        stats["gold_relations_kept"] = len(kept_relations)
    else:
        kept_mentions = corpus.mentions
        kept_relations = corpus.relation

    # Filter predicted mentions
    if filter_predicted:
        kept_mentions_pred = [
            m for m in corpus.mentions_predicted if m.text not in texts_to_filter
        ]
        kept_mention_ids_pred = {m.id for m in kept_mentions_pred}

        # Filter relations that reference filtered mentions
        kept_relations_pred = [
            r
            for r in corpus.relations_predicted
            if r.subject.id in kept_mention_ids_pred
            and r.object.id in kept_mention_ids_pred
        ]

        stats["predicted_mentions_filtered"] = len(corpus.mentions_predicted) - len(
            kept_mentions_pred
        )
        stats["predicted_mentions_kept"] = len(kept_mentions_pred)
        stats["predicted_relations_filtered"] = len(corpus.relations_predicted) - len(
            kept_relations_pred
        )
        stats["predicted_relations_kept"] = len(kept_relations_pred)
    else:
        kept_mentions_pred = corpus.mentions_predicted
        kept_relations_pred = corpus.relations_predicted

    # Create new corpus with filtered mentions
    filtered_corpus = Corpus(
        sentences=corpus.sentences,
        mentions=kept_mentions,
        relation=kept_relations,
        mentions_predicted=kept_mentions_pred,
        relations_predicted=kept_relations_pred,
    )

    return filtered_corpus, stats


def generate_correction_report(
    original_corpus: Corpus,
    filtered_corpus: Corpus,
    stats: dict,
    output_path: Path,
) -> None:
    """Generate a report about the corrections applied.

    Args:
        original_corpus: Original corpus before filtering
        filtered_corpus: Corpus after filtering
        stats: Statistics dictionary from filter_gsap_mentions
        output_path: Path to save the markdown report
    """
    from collections import Counter
    from datetime import datetime

    # Count labels in original vs filtered
    original_labels = Counter([m.label for m in original_corpus.mentions_predicted])
    filtered_labels = Counter([m.label for m in filtered_corpus.mentions_predicted])

    md_content = f"""# GSAP Correction Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

This report shows the impact of filtering GSAP predictions based on unmatched
analysis. Mentions with text appearing >= {stats["min_count_threshold"]} times
in the unmatched analysis were removed.

## Statistics

### Mentions

- **Original predicted mentions**: {stats["predicted_mentions_original"]:,}
- **Filtered mentions**: {stats["predicted_mentions_filtered"]:,}
- **Kept mentions**: {stats["predicted_mentions_kept"]:,}
- **Filtered percentage**: {stats["predicted_mentions_filtered"] / stats["predicted_mentions_original"] * 100:.1f}%

### Relations

- **Original predicted relations**: {stats["predicted_relations_original"]:,}
- **Filtered relations**: {stats["predicted_relations_filtered"]:,}
- **Kept relations**: {stats["predicted_relations_kept"]:,}
- **Filtered percentage**: {stats["predicted_relations_filtered"] / stats["predicted_relations_original"] * 100:.1f}%

## Label Distribution Changes

| Label | Original Count | Filtered Count | Change |
|-------|----------------|----------------|--------|
"""

    all_labels = sorted(set(original_labels.keys()) | set(filtered_labels.keys()))
    for label in all_labels:
        orig = original_labels.get(label, 0)
        filt = filtered_labels.get(label, 0)
        change = filt - orig
        change_pct = (change / orig * 100) if orig > 0 else 0
        md_content += f"| {label} | {orig} | {filt} | {change} ({change_pct:+.1f}%) |\n"

    md_content += f"""

## Filtered Texts

The following {stats["total_texts_to_filter"]} texts were filtered (appearing >= {stats["min_count_threshold"]} times):

"""

    for i, text in enumerate(stats["filtered_texts"][:100], 1):
        escaped_text = text.replace("|", "\\|")
        md_content += f"{i}. {escaped_text}\n"

    if len(stats["filtered_texts"]) > 100:
        md_content += f"\n... and {len(stats['filtered_texts']) - 100} more.\n"

    md_content += """

## Interpretation

The filtering removes systematic GSAP errors, particularly:

1. **Generic references**: "the model", "models", "our model", etc.
2. **Procedural terms**: "fine-tuning", "training", etc.
3. **Context-dependent terms**: References that lack specificity

This correction improves GSAP prediction quality by removing noise while
preserving legitimate entity mentions.

---
*Generated by UnifiedSciERE GSAP-Specific Corrections*
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(md_content)


if __name__ == "__main__":
    # Example usage
    from ..data_loader import load_corpus

    # Load GSAP predictions
    corpus = load_corpus("gsap", "dev", data_type="predictions", trained_on="gsap")

    # Filter using analysis results
    json_file = Path(
        "reports/ere_confusion_analysis/unification/gsap_analysis/gsap_unmatched_mlmodelgeneric_dev_latest.json"
    )
    if json_file.exists():
        filtered_corpus, stats = filter_gsap_mentions(
            corpus,
            json_file,
            min_count=2,
            filter_predicted=True,
            filter_gold=False,
        )

        # Generate report
        report_path = Path(
            "reports/ere_confusion_analysis/unification/gsap_analysis/gsap_correction_report_dev.md"
        )
        generate_correction_report(corpus, filtered_corpus, stats, report_path)

        print(f"Filtered {stats['predicted_mentions_filtered']} mentions")
        print(f"Report saved to {report_path}")
    else:
        print(f"Analysis file not found: {json_file}")
        print("Run gsap_specific_analysis.py first")
