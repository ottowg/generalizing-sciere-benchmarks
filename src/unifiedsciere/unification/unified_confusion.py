"""Generate confusion reports using unified entity labels.

This module generates confusion matrices comparing predictions across models
after applying the complete unification pipeline (merge + drop + map).
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from gsaphub.match.entities import partial

from ..data_loader import load_corpus
from .label_mapper import drop_unmapped_mentions, map_labels_to_unified
from .merge_stacked import merge_stacked_mentions


def generate_unified_confusion_report(
    datasets: list[Literal["scier", "scinlp", "gsap-ere"]],
    split: Literal["train", "dev", "test"],
    model1: Literal["scier", "scinlp", "gsap-ere"],
    model2: Literal["scier", "scinlp", "gsap-ere"],
    prefer_larger: bool = True,
    top_n: int = 15,
    combine_datasets: bool = False,
    output_dir: Path | None = None,
) -> Path:
    """Generate confusion report using unified predictions.

    This applies the complete unification pipeline to both models' predictions,
    then generates a confusion matrix showing how unified labels align.

    Args:
        datasets: List of datasets to analyze
        split: Data split to use
        model1: First model (rows in confusion matrix)
        model2: Second model (columns in confusion matrix)
        prefer_larger: If True, prefer larger spans when merging
        top_n: Number of top mentions to show per label pair
        combine_datasets: If True, combine predictions from all datasets
        output_dir: Output directory (default: reports/ere_confusion_analysis/unification/)

    Returns:
        Path to generated markdown file
    """
    if output_dir is None:
        output_dir = Path("reports/ere_confusion_analysis/unification")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = f"""# Unified Label Confusion Analysis

**Generated:** {timestamp}

**Split:** {split}

**Model 1 (Rows):** {model1.upper()}

**Model 2 (Columns):** {model2.upper()}

"""

    if combine_datasets:
        md_content += f"""**Datasets Combined:** {", ".join([d.upper() for d in datasets])}

"""

    md_content += """## Overview

This report shows confusion matrices comparing entity labels between two models
after applying the complete unification pipeline:

1. Merge stacked mentions (prefer larger spans)
2. Drop unmapped labels (null mappings)
3. Map to unified schema (Dataset, Method, Task)

The confusion matrix uses partial span matching to align entities with overlapping spans.

"""

    if combine_datasets:
        # Load and combine all datasets
        all_model1_data = []
        all_model2_data = []
        all_gold_data = []

        for dataset in datasets:
            try:
                # Load gold data (from any corpus, they should all have the same gold)
                corpus_gold = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model1
                )
                # Apply unification pipeline to gold using dataset's label scheme
                corpus_gold = merge_stacked_mentions(
                    corpus_gold,
                    prefer_larger=prefer_larger,
                    merge_gold=True,
                    merge_predicted=False,
                )[0]
                corpus_gold = drop_unmapped_mentions(
                    corpus_gold, dataset, drop_gold=True, drop_predicted=False
                )[0]
                corpus_gold = map_labels_to_unified(
                    corpus_gold, dataset, map_gold=True, map_predicted=False
                )[0]
                all_gold_data.extend(corpus_gold.mentions)

                # Load model1 predictions
                corpus1 = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model1
                )
                # Apply unification pipeline using MODEL's label scheme
                corpus1 = merge_stacked_mentions(
                    corpus1,
                    prefer_larger=prefer_larger,
                    merge_gold=False,
                    merge_predicted=True,
                )[0]
                corpus1 = drop_unmapped_mentions(
                    corpus1, model1, drop_gold=False, drop_predicted=True
                )[0]
                corpus1 = map_labels_to_unified(
                    corpus1, model1, map_gold=False, map_predicted=True
                )[0]
                all_model1_data.extend(corpus1.mentions_predicted)

                # Load model2 predictions
                corpus2 = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model2
                )
                # Apply unification pipeline using MODEL's label scheme
                corpus2 = merge_stacked_mentions(
                    corpus2,
                    prefer_larger=prefer_larger,
                    merge_gold=False,
                    merge_predicted=True,
                )[0]
                corpus2 = drop_unmapped_mentions(
                    corpus2, model2, drop_gold=False, drop_predicted=True
                )[0]
                corpus2 = map_labels_to_unified(
                    corpus2, model2, map_gold=False, map_predicted=True
                )[0]
                all_model2_data.extend(corpus2.mentions_predicted)

            except Exception as e:
                print(f"Warning: Could not load {dataset}: {e}")
                continue

        if not all_model1_data or not all_model2_data:
            raise ValueError("No data loaded from any dataset")

        datasets = ["combined"]

    for dataset in datasets:
        try:
            if dataset == "combined":
                model1_mentions = all_model1_data
                model2_mentions = all_model2_data
                gold_mentions = all_gold_data
            else:
                # Load gold data
                corpus_gold = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model1
                )
                corpus_gold = merge_stacked_mentions(
                    corpus_gold,
                    prefer_larger=prefer_larger,
                    merge_gold=True,
                    merge_predicted=False,
                )[0]
                corpus_gold = drop_unmapped_mentions(
                    corpus_gold, dataset, drop_gold=True, drop_predicted=False
                )[0]
                corpus_gold = map_labels_to_unified(
                    corpus_gold, dataset, map_gold=True, map_predicted=False
                )[0]
                gold_mentions = corpus_gold.mentions

                # Load and process model1 predictions
                corpus1 = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model1
                )
                corpus1 = merge_stacked_mentions(
                    corpus1,
                    prefer_larger=prefer_larger,
                    merge_gold=False,
                    merge_predicted=True,
                )[0]
                corpus1 = drop_unmapped_mentions(
                    corpus1, model1, drop_gold=False, drop_predicted=True
                )[0]
                corpus1 = map_labels_to_unified(
                    corpus1, model1, map_gold=False, map_predicted=True
                )[0]
                model1_mentions = corpus1.mentions_predicted

                # Load and process model2 predictions
                corpus2 = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model2
                )
                corpus2 = merge_stacked_mentions(
                    corpus2,
                    prefer_larger=prefer_larger,
                    merge_gold=False,
                    merge_predicted=True,
                )[0]
                corpus2 = drop_unmapped_mentions(
                    corpus2, model2, drop_gold=False, drop_predicted=True
                )[0]
                corpus2 = map_labels_to_unified(
                    corpus2, model2, map_gold=False, map_predicted=True
                )[0]
                model2_mentions = corpus2.mentions_predicted

            # Convert to gsaphub format
            def to_gsaphub(mentions):
                result = []
                for m in mentions:
                    # Use actual doc_id from JSON files (already set by data_loader)
                    result.append(
                        {
                            "id": m.id,
                            "doc_id": m.document_id,
                            "begin": m.begin,
                            "end": m.end,
                            "label": m.label,
                            "annotator": m.annotator,
                        }
                    )
                return result

            model1_gsaphub = to_gsaphub(model1_mentions)
            model2_gsaphub = to_gsaphub(model2_mentions)

            # Use gsaphub partial matching
            partial(
                model1_gsaphub,
                model2_gsaphub,
                target_key="matched_ent_ids",
                only_same_annotator=False,
            )

            # Build confusion matrix and mapping details
            confusion = defaultdict(lambda: defaultdict(int))
            mapping_details = defaultdict(list)
            model2_by_id = {m["id"]: m for m in model2_gsaphub}

            for m1_ent in model1_gsaphub:
                m1_label = m1_ent["label"]
                matched_ids = m1_ent.get("matched_ent_ids", [])

                if not matched_ids:
                    confusion[m1_label]["NIL"] += 1
                else:
                    m2_id = matched_ids[0]
                    m2_ent = model2_by_id[m2_id]
                    m2_label = m2_ent["label"]
                    confusion[m1_label][m2_label] += 1

                    # Find original mention text and labels
                    m1_mention = next(
                        (m for m in model1_mentions if m.id == m1_ent["id"]), None
                    )
                    m2_mention = next(
                        (m for m in model2_mentions if m.id == m2_id), None
                    )
                    if m2_mention:
                        mapping_details[(m1_label, m2_label)].append(
                            {
                                "text": m2_mention.text,
                                "model1_original": m1_mention.label_original
                                if m1_mention
                                else "",
                                "model2_original": m2_mention.label_original,
                            }
                        )

            # Find model2 entities with no match
            partial(
                model2_gsaphub,
                model1_gsaphub,
                target_key="matched_ent_ids",
                only_same_annotator=False,
            )

            for m2_ent in model2_gsaphub:
                m2_label = m2_ent["label"]
                matched_ids = m2_ent.get("matched_ent_ids", [])
                if not matched_ids:
                    confusion["NIL"][m2_label] += 1

            # Convert to DataFrame
            import pandas as pd

            df = pd.DataFrame(confusion).fillna(0).astype(int)

            # Sort rows and columns
            row_labels = sorted([r for r in df.index if r != "NIL"])
            col_labels = sorted([c for c in df.columns if c != "NIL"])
            if "NIL" in df.index:
                row_labels.append("NIL")
            if "NIL" in df.columns:
                col_labels.append("NIL")
            df = df.reindex(index=row_labels, columns=col_labels, fill_value=0)

            dataset_title = (
                "Combined Datasets"
                if dataset == "combined"
                else f"{dataset.upper()} Dataset"
            )

            md_content += f"""
## {dataset_title}

### Confusion Matrix

Rows: {model1.upper()} labels | Columns: {model2.upper()} labels

"""

            md_content += df.to_markdown() + "\n"

            # Calculate statistics
            total_m1 = df.sum(axis=1)
            total_m2 = df.sum(axis=0)

            # Count gold entities by label
            from collections import Counter

            gold_counts = Counter([m.label for m in gold_mentions])

            # Get all unique labels
            all_labels = sorted(
                set(total_m1.index) | set(total_m2.index) | set(gold_counts.keys())
            )
            if "NIL" in all_labels:
                all_labels.remove("NIL")
                all_labels.append("NIL")

            # Create statistics table
            md_content += f"""
### Entity Counts per Label

| Label | Gold | {model1.upper()} | {model2.upper()} |
|-------|------|{"-" * len(model1.upper())}|{"-" * len(model2.upper())}|
"""
            for label in all_labels:
                gold_count = gold_counts.get(label, 0)
                m1_count = total_m1.get(label, 0)
                m2_count = total_m2.get(label, 0)
                md_content += f"| {label} | {gold_count} | {m1_count} | {m2_count} |\n"

            # Create simplified table with all label pairs
            md_content += f"""
### Label Mappings (Top {top_n} per Label Pair)

| {model1.upper()} Label | {model1.upper()} Original | {model2.upper()} Label | {model2.upper()} Original | Mention Text | Count |
|----------|----------|----------|----------|--------------|-------|
"""

            from collections import Counter

            all_mappings = []

            # Non-NIL mappings
            for (m1_label, m2_label), items in mapping_details.items():
                # Group by text and collect original labels
                text_data = defaultdict(
                    lambda: {"count": 0, "m1_originals": set(), "m2_originals": set()}
                )
                for item in items:
                    text = item["text"]
                    text_data[text]["count"] += 1
                    if item.get("model1_original"):
                        text_data[text]["m1_originals"].add(item["model1_original"])
                    if item.get("model2_original"):
                        text_data[text]["m2_originals"].add(item["model2_original"])

                # Sort by count and take top N
                sorted_texts = sorted(
                    text_data.items(), key=lambda x: x[1]["count"], reverse=True
                )[:top_n]
                for text, data in sorted_texts:
                    m1_orig = (
                        ", ".join(sorted(data["m1_originals"]))
                        if data["m1_originals"]
                        else m1_label
                    )
                    m2_orig = (
                        ", ".join(sorted(data["m2_originals"]))
                        if data["m2_originals"]
                        else m2_label
                    )
                    all_mappings.append(
                        (m1_label, m1_orig, m2_label, m2_orig, text, data["count"])
                    )

            # NIL mappings
            # Model1 -> NIL
            nil_m1_data = defaultdict(
                lambda: defaultdict(lambda: {"count": 0, "m1_originals": set()})
            )
            for m1_ent in model1_gsaphub:
                matched_ids = m1_ent.get("matched_ent_ids", [])
                if not matched_ids:
                    m1_label = m1_ent["label"]
                    m1_mention = next(
                        (m for m in model1_mentions if m.id == m1_ent["id"]), None
                    )
                    if m1_mention:
                        text = m1_mention.text
                        nil_m1_data[m1_label][text]["count"] += 1
                        if m1_mention.label_original:
                            nil_m1_data[m1_label][text]["m1_originals"].add(
                                m1_mention.label_original
                            )

            for m1_label, text_data in nil_m1_data.items():
                sorted_texts = sorted(
                    text_data.items(), key=lambda x: x[1]["count"], reverse=True
                )[:top_n]
                for text, data in sorted_texts:
                    m1_orig = (
                        ", ".join(sorted(data["m1_originals"]))
                        if data["m1_originals"]
                        else m1_label
                    )
                    all_mappings.append(
                        (m1_label, m1_orig, "NIL", "", text, data["count"])
                    )

            # NIL -> Model2
            nil_m2_data = defaultdict(
                lambda: defaultdict(lambda: {"count": 0, "m2_originals": set()})
            )
            for m2_ent in model2_gsaphub:
                matched_ids = m2_ent.get("matched_ent_ids", [])
                if not matched_ids:
                    m2_label = m2_ent["label"]
                    m2_mention = next(
                        (m for m in model2_mentions if m.id == m2_ent["id"]), None
                    )
                    if m2_mention:
                        text = m2_mention.text
                        nil_m2_data[m2_label][text]["count"] += 1
                        if m2_mention.label_original:
                            nil_m2_data[m2_label][text]["m2_originals"].add(
                                m2_mention.label_original
                            )

            for m2_label, text_data in nil_m2_data.items():
                sorted_texts = sorted(
                    text_data.items(), key=lambda x: x[1]["count"], reverse=True
                )[:top_n]
                for text, data in sorted_texts:
                    m2_orig = (
                        ", ".join(sorted(data["m2_originals"]))
                        if data["m2_originals"]
                        else m2_label
                    )
                    all_mappings.append(
                        ("NIL", "", m2_label, m2_orig, text, data["count"])
                    )

            # Sort mappings
            def sort_key(item):
                m1_label, m1_orig, m2_label, m2_orig, text, count = item
                m1_sort = (1, m1_label) if m1_label == "NIL" else (0, m1_label)
                m2_sort = (1, m2_label) if m2_label == "NIL" else (0, m2_label)
                return (m1_sort, m2_sort, -count)

            all_mappings.sort(key=sort_key)

            # Write to table
            for m1_label, m1_orig, m2_label, m2_orig, text, count in all_mappings:
                escaped_text = text.replace("|", "\\|")
                md_content += f"| {m1_label} | {m1_orig} | {m2_label} | {m2_orig} | {escaped_text} | {count} |\n"

        except Exception as e:
            md_content += f"""
## {dataset.upper()} Dataset

**Error:** Could not generate confusion matrix: {str(e)}

"""

    md_content += """
## Notes

- **Unified Labels**: All predictions mapped to unified schema (Dataset, Method, Task)
- **Partial Matching**: Uses gsaphub's partial span matching to align entities
- **NIL Class**: Represents entities annotated by one model but not the other
- **Pipeline Applied**: Merge → Drop → Map for both models before comparison

---
*Generated by UnifiedSciERE Unified Confusion Analysis*
"""

    # Save markdown file
    suffix = "combined" if combine_datasets else "unified"
    md_path = output_dir / f"confusion_unified_{model1}_{model2}_{split}_{suffix}.md"
    md_path.write_text(md_content)

    return md_path


if __name__ == "__main__":
    # Example: Generate unified confusion report
    report_path = generate_unified_confusion_report(
        datasets=["scier", "scinlp", "gsap-ere"],
        split="dev",
        model1="gsap-ere",
        model2="scier",
        prefer_larger=True,
        combine_datasets=True,
    )
    print(f"Generated unified confusion report: {report_path}")
