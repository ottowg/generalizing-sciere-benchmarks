"""Label confusion analysis for entity unification.

This module provides functions to analyze label confusion between different
annotation schemes using partial span matching from gsaphub.
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

import pandas as pd
from gsaphub.match.entities import partial

from ..data_loader import load_corpus
from ..types import Mention


def _mentions_to_gsaphub_format(
    mentions: list[Mention], normalize_doc_id: bool = True
) -> list[dict]:
    """Convert Mention objects to gsaphub dict format.

    Args:
        mentions: List of Mention objects
        normalize_doc_id: If True, removes model prefix from doc_id to enable cross-model matching
    """
    result = []
    for m in mentions:
        doc_id = m.document_id
        if normalize_doc_id:
            # Remove model prefix from doc_id (e.g., "scinlp_gsap_dev_0" -> "gsap_dev_0")
            # Format is: {model}_{dataset}_{split}_{doc_num}
            parts = doc_id.split("_", 1)
            if len(parts) > 1:
                doc_id = parts[1]  # Remove first part (model name)

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


def compute_confusion_matrix(
    dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"],
    model1: Literal["scier", "scinlp", "gsap"],
    model2: Literal["scier", "scinlp", "gsap"],
    return_details: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, dict]:
    """Compute confusion matrix between two models' entity labels.

    Uses partial matching from gsaphub to align entities with overlapping spans.
    Includes a "NIL" class for entities that don't have a match in the other model.

    Args:
        dataset: Target dataset to evaluate on
        split: Data split to use
        model1: First model (rows in confusion matrix)
        model2: Second model (columns in confusion matrix)

    Returns:
        DataFrame with confusion matrix (model1 labels as rows, model2 labels as columns)

    Example:
        >>> cm = compute_confusion_matrix("scinlp", "dev", "scinlp", "scier")
        >>> print(cm)
    """
    # Load predictions from both models
    model1_data = load_corpus(
        dataset, split, data_type="predictions", trained_on=model1
    )
    model2_data = load_corpus(
        dataset, split, data_type="predictions", trained_on=model2
    )

    # Use predicted mentions, not gold mentions
    model1_mentions = _mentions_to_gsaphub_format(model1_data.mentions_predicted)
    model2_mentions = _mentions_to_gsaphub_format(model2_data.mentions_predicted)

    # Use gsaphub partial matching to find overlapping entities
    # This adds 'matched_ent_ids' to each entity in model1_mentions
    partial(
        model1_mentions,
        model2_mentions,
        target_key="matched_ent_ids",
        only_same_annotator=False,
    )

    # Create a lookup for model2 mentions by ID
    model2_by_id = {m["id"]: m for m in model2_mentions}

    # Build confusion matrix and collect mapping details
    confusion = defaultdict(lambda: defaultdict(int))
    # Store mention texts for each label pair: {(m1_label, m2_label): [m2_texts]}
    mapping_details = defaultdict(list)

    for m1_ent in model1_mentions:
        m1_label = m1_ent["label"]
        matched_ids = m1_ent.get("matched_ent_ids", [])

        if not matched_ids:
            # No match in model2 -> NIL
            confusion[m1_label]["NIL"] += 1
        else:
            # Use the first match (best overlap)
            # TODO: Could use partial_ranked for better match selection
            m2_id = matched_ids[0]
            m2_ent = model2_by_id[m2_id]
            m2_label = m2_ent["label"]
            confusion[m1_label][m2_label] += 1

            # Store the model2 mention text and label for this mapping
            if return_details:
                # Find the original Mention object to get the text
                m2_mention = next(
                    (m for m in model2_data.mentions_predicted if m.id == m2_id), None
                )
                if m2_mention:
                    mapping_details[(m1_label, m2_label)].append(
                        {
                            "text": m2_mention.text,
                            "model2_label": m2_label,
                        }
                    )

    # Also find model2 entities that have no match in model1
    # (these would be NIL in model1's perspective)
    partial(
        model2_mentions,
        model1_mentions,
        target_key="matched_ent_ids",
        only_same_annotator=False,
    )

    for m2_ent in model2_mentions:
        m2_label = m2_ent["label"]
        matched_ids = m2_ent.get("matched_ent_ids", [])

        if not matched_ids:
            # No match in model1 -> this is a NIL from model1's perspective
            confusion["NIL"][m2_label] += 1

    # Convert to DataFrame
    df = pd.DataFrame(confusion).fillna(0).astype(int)

    # Sort rows and columns, but keep NIL at the end
    row_labels = sorted([r for r in df.index if r != "NIL"])
    col_labels = sorted([c for c in df.columns if c != "NIL"])

    if "NIL" in df.index:
        row_labels.append("NIL")
    if "NIL" in df.columns:
        col_labels.append("NIL")

    # Reindex to ensure consistent ordering
    df = df.reindex(index=row_labels, columns=col_labels, fill_value=0)

    if return_details:
        return df, dict(mapping_details)
    return df


def generate_confusion_report(
    datasets: list[Literal["scier", "scinlp", "gsap"]],
    split: Literal["train", "dev", "test"],
    model1: Literal["scier", "scinlp", "gsap"],
    model2: Literal["scier", "scinlp", "gsap"],
    output_dir: Path | None = None,
) -> Path:
    """Generate a markdown report with confusion matrices for multiple datasets.

    Args:
        datasets: List of datasets to analyze
        split: Data split to use
        model1: First model (rows in confusion matrix)
        model2: Second model (columns in confusion matrix)
        output_dir: Output directory (default: reports/confusion/)

    Returns:
        Path to generated markdown file

    Example:
        >>> path = generate_confusion_report(
        ...     ["scier", "scinlp", "gsap"],
        ...     "dev",
        ...     "scinlp",
        ...     "scier"
        ... )
    """
    if output_dir is None:
        output_dir = Path("reports/confusion")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = f"""# Entity Label Confusion Analysis

**Generated:** {timestamp}

**Split:** {split}

**Model 1 (Rows):** {model1.upper()}

**Model 2 (Columns):** {model2.upper()}

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.

"""

    for dataset in datasets:
        try:
            cm, mapping_details = compute_confusion_matrix(
                dataset, split, model1, model2, return_details=True
            )

            md_content += f"""
## {dataset.upper()} Dataset

### Confusion Matrix

Rows: {model1.upper()} labels | Columns: {model2.upper()} labels

"""

            # Convert confusion matrix to markdown table
            md_content += cm.to_markdown() + "\n"

            # Add summary statistics
            total_m1 = cm.sum(axis=1)
            total_m2 = cm.sum(axis=0)

            md_content += f"""
### Statistics

**{model1.upper()} Total Entities per Label:**

"""
            for label, count in total_m1.items():
                md_content += f"- {label}: {count}\n"

            md_content += f"""
**{model2.upper()} Total Entities per Label:**

"""
            for label, count in total_m2.items():
                md_content += f"- {label}: {count}\n"

            # Add detailed mapping lists for each label pair
            md_content += f"""
### Detailed Label Mappings

This section shows {model2.upper()} mention texts that were mapped to each {model1.upper()} label, grouped by {model2.upper()} label and sorted by frequency.

"""
            for m1_label in sorted(set(k[0] for k in mapping_details.keys())):
                # Get all mappings for this model1 label
                mappings_for_m1 = [
                    (k[1], v) for k, v in mapping_details.items() if k[0] == m1_label
                ]

                if not mappings_for_m1:
                    continue

                md_content += f"\n#### {model1.upper()} Label: **{m1_label}**\n\n"

                # Group by model2 label
                for m2_label in sorted(set(m[0] for m in mappings_for_m1)):
                    texts = [
                        item["text"]
                        for _, items in mappings_for_m1
                        if _ == m2_label
                        for item in items
                    ]

                    if not texts:
                        continue

                    # Count frequencies
                    from collections import Counter

                    text_counts = Counter(texts)

                    md_content += f"\n**→ {model2.upper()} label: {m2_label}** ({len(texts)} mentions)\n\n"
                    md_content += "| Mention Text | Count |\n"
                    md_content += "|--------------|-------|\n"

                    # Sort by frequency (descending) and take top 20
                    for text, count in text_counts.most_common(20):
                        # Escape pipe characters in text
                        escaped_text = text.replace("|", "\\|")
                        md_content += f"| {escaped_text} | {count} |\n"

                    if len(text_counts) > 20:
                        md_content += f"\n*... and {len(text_counts) - 20} more unique mentions*\n"

        except Exception as e:
            md_content += f"""
## {dataset.upper()} Dataset

**Error:** Could not generate confusion matrix: {str(e)}

"""

    md_content += """
## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Row label indicates the true/reference model label
- Column label indicates the predicted/comparison model label

---
*Generated by UnifiedSciERE Label Confusion Analysis*
"""

    # Save markdown file
    md_path = output_dir / f"confusion_{model1}_{model2}_{split}.md"
    md_path.write_text(md_content)

    return md_path


def generate_simplified_confusion_report(
    datasets: list[Literal["scier", "scinlp", "gsap"]],
    split: Literal["train", "dev", "test"],
    model1: Literal["scier", "scinlp", "gsap"],
    model2: Literal["scier", "scinlp", "gsap"],
    output_dir: Path | None = None,
    top_n: int = 15,
    combine_datasets: bool = False,
) -> Path:
    """Generate a simplified markdown report with single table per dataset.

    Args:
        datasets: List of datasets to analyze
        split: Data split to use
        model1: First model (rows in confusion matrix)
        model2: Second model (columns in confusion matrix)
        output_dir: Output directory (default: reports/confusion/)
        top_n: Number of top mentions to show per label pair
        combine_datasets: If True, combine predictions from all datasets into one report

    Returns:
        Path to generated markdown file

    Example:
        >>> path = generate_simplified_confusion_report(
        ...     ["gsap"],
        ...     "dev",
        ...     "gsap",
        ...     "scier"
        ... )
    """
    if output_dir is None:
        output_dir = Path("reports/confusion")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = f"""# Entity Label Confusion Analysis

**Generated:** {timestamp}

**Split:** {split}

**Model 1:** {model1.upper()}

**Model 2:** {model2.upper()}

"""

    if combine_datasets:
        md_content += f"""**Datasets Combined:** {", ".join([d.upper() for d in datasets])}

"""

    md_content += """## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.

"""

    if combine_datasets:
        # Load and combine all datasets
        all_model1_data = []
        all_model2_data = []

        for dataset in datasets:
            try:
                model1_data = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model1
                )
                model2_data = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model2
                )
                all_model1_data.extend(model1_data.mentions_predicted)
                all_model2_data.extend(model2_data.mentions_predicted)
            except Exception as e:
                print(f"Warning: Could not load {dataset}: {e}")
                continue

        if not all_model1_data or not all_model2_data:
            raise ValueError("No data loaded from any dataset")

        # Process combined data
        datasets = ["combined"]  # Process as a single combined dataset

    for dataset in datasets:
        try:
            if dataset == "combined":
                # Use the pre-loaded combined data
                # Build confusion matrix from combined mentions
                model1_mentions_gsap = _mentions_to_gsaphub_format(all_model1_data)
                model2_mentions_gsap = _mentions_to_gsaphub_format(all_model2_data)

                # Use gsaphub partial matching
                partial(
                    model1_mentions_gsap,
                    model2_mentions_gsap,
                    target_key="matched_ent_ids",
                    only_same_annotator=False,
                )

                model2_by_id = {m["id"]: m for m in model2_mentions_gsap}

                # Build confusion matrix and mapping details
                confusion = defaultdict(lambda: defaultdict(int))
                mapping_details = defaultdict(list)

                for m1_ent in model1_mentions_gsap:
                    m1_label = m1_ent["label"]
                    matched_ids = m1_ent.get("matched_ent_ids", [])

                    if not matched_ids:
                        confusion[m1_label]["NIL"] += 1
                    else:
                        m2_id = matched_ids[0]
                        m2_ent = model2_by_id[m2_id]
                        m2_label = m2_ent["label"]
                        confusion[m1_label][m2_label] += 1

                        m2_mention = next(
                            (m for m in all_model2_data if m.id == m2_id), None
                        )
                        if m2_mention:
                            mapping_details[(m1_label, m2_label)].append(
                                {
                                    "text": m2_mention.text,
                                    "model2_label": m2_label,
                                }
                            )

                # Find model2 entities with no match
                partial(
                    model2_mentions_gsap,
                    model1_mentions_gsap,
                    target_key="matched_ent_ids",
                    only_same_annotator=False,
                )

                for m2_ent in model2_mentions_gsap:
                    m2_label = m2_ent["label"]
                    matched_ids = m2_ent.get("matched_ent_ids", [])
                    if not matched_ids:
                        confusion["NIL"][m2_label] += 1

                # Convert to DataFrame
                cm = pd.DataFrame(confusion).fillna(0).astype(int)

                row_labels = sorted([r for r in cm.index if r != "NIL"])
                col_labels = sorted([c for c in cm.columns if c != "NIL"])
                if "NIL" in cm.index:
                    row_labels.append("NIL")
                if "NIL" in cm.columns:
                    col_labels.append("NIL")
                cm = cm.reindex(index=row_labels, columns=col_labels, fill_value=0)

                model1_data = all_model1_data
                model2_data = all_model2_data
            else:
                cm, mapping_details = compute_confusion_matrix(
                    dataset, split, model1, model2, return_details=True
                )
                model1_data = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model1
                )
                model2_data = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model2
                )

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

            # Convert confusion matrix to markdown table
            md_content += cm.to_markdown() + "\n"

            # Add summary statistics
            total_m1 = cm.sum(axis=1)
            total_m2 = cm.sum(axis=0)

            md_content += f"""
### Statistics

**{model1.upper()} Total Entities per Label:**

"""
            for label, count in total_m1.items():
                md_content += f"- {label}: {count}\n"

            md_content += f"""
**{model2.upper()} Total Entities per Label:**

"""
            for label, count in total_m2.items():
                md_content += f"- {label}: {count}\n"

            # Create simplified table with all label pairs
            md_content += f"""
### Label Mappings (Top {top_n} per Label Pair)

| {model1.upper()} Label | {model2.upper()} Label | Mention Text | Count |
|----------|----------|--------------|-------|
"""

            # Collect all mappings with counts
            from collections import Counter

            all_mappings = []

            # First, handle non-NIL mappings from mapping_details
            for (m1_label, m2_label), items in mapping_details.items():
                texts = [item["text"] for item in items]
                text_counts = Counter(texts)

                for text, count in text_counts.most_common(top_n):
                    all_mappings.append((m1_label, m2_label, text, count))

            # Now we need to handle NIL cases
            # For model1 labels with NIL (entities in model1 not in model2)
            # We need to get the actual mention texts from model1
            if dataset != "combined":
                model1_data_corpus = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model1
                )
                model2_data_corpus = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model2
                )
                model1_mentions_list = model1_data_corpus.mentions_predicted
                model2_mentions_list = model2_data_corpus.mentions_predicted
            else:
                model1_mentions_list = model1_data
                model2_mentions_list = model2_data

            model1_mentions = _mentions_to_gsaphub_format(model1_mentions_list)
            model2_mentions = _mentions_to_gsaphub_format(model2_mentions_list)

            # Run partial matching again to get matched_ent_ids
            partial(
                model1_mentions,
                model2_mentions,
                target_key="matched_ent_ids",
                only_same_annotator=False,
            )

            # Find model1 entities with no match (NIL in model2)
            nil_m1_texts = defaultdict(list)
            for m1_ent in model1_mentions:
                matched_ids = m1_ent.get("matched_ent_ids", [])
                if not matched_ids:
                    m1_label = m1_ent["label"]
                    # Find original mention to get text
                    m1_mention = next(
                        (m for m in model1_mentions_list if m.id == m1_ent["id"]),
                        None,
                    )
                    if m1_mention:
                        nil_m1_texts[m1_label].append(m1_mention.text)

            # Add top N for each model1 label -> NIL
            for m1_label, texts in nil_m1_texts.items():
                text_counts = Counter(texts)
                for text, count in text_counts.most_common(top_n):
                    all_mappings.append((m1_label, "NIL", text, count))

            # Find model2 entities with no match (NIL in model1)
            partial(
                model2_mentions,
                model1_mentions,
                target_key="matched_ent_ids",
                only_same_annotator=False,
            )

            nil_m2_texts = defaultdict(list)
            for m2_ent in model2_mentions:
                matched_ids = m2_ent.get("matched_ent_ids", [])
                if not matched_ids:
                    m2_label = m2_ent["label"]
                    # Find original mention to get text
                    m2_mention = next(
                        (m for m in model2_mentions_list if m.id == m2_ent["id"]),
                        None,
                    )
                    if m2_mention:
                        nil_m2_texts[m2_label].append(m2_mention.text)

            # Add top N for NIL -> each model2 label
            for m2_label, texts in nil_m2_texts.items():
                text_counts = Counter(texts)
                for text, count in text_counts.most_common(top_n):
                    all_mappings.append(("NIL", m2_label, text, count))

            # Sort mappings by (m1_label, m2_label, count desc)
            # Put NIL at the end for both dimensions
            def sort_key(item):
                m1_label, m2_label, text, count = item
                # Sort NIL to the end
                m1_sort = (1, m1_label) if m1_label == "NIL" else (0, m1_label)
                m2_sort = (1, m2_label) if m2_label == "NIL" else (0, m2_label)
                return (m1_sort, m2_sort, -count)

            all_mappings.sort(key=sort_key)

            # Write to table
            for m1_label, m2_label, text, count in all_mappings:
                # Escape pipe characters in text
                escaped_text = text.replace("|", "\\|")
                md_content += (
                    f"| {m1_label} | {m2_label} | {escaped_text} | {count} |\n"
                )

        except Exception as e:
            md_content += f"""
## {dataset.upper()} Dataset

**Error:** Could not generate confusion matrix: {str(e)}

"""

    md_content += """
## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
"""

    # Save markdown file
    suffix = "combined" if combine_datasets else "simplified"
    md_path = output_dir / f"confusion_{model1}_{model2}_{split}_{suffix}.md"
    md_path.write_text(md_content)

    return md_path


if __name__ == "__main__":
    # Example: Compare SCINLP and SCIER labels on all datasets (dev split)
    report_path = generate_confusion_report(
        datasets=["scier", "scinlp", "gsap"],
        split="dev",
        model1="scinlp",
        model2="scier",
    )
    print(f"Generated confusion report: {report_path}")
