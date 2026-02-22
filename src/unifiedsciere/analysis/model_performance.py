"""Model performance analysis for scientific entity and relation extraction."""

from datetime import datetime
from pathlib import Path
from typing import Literal

from great_tables import GT, loc, style
from gsaphub.evaluate.entities import precision_recall_f1 as evaluate_entities
from gsaphub.evaluate.relations import (
    RelationExtractionMetric,
)
from gsaphub.evaluate.relations import (
    precision_recall_f1 as evaluate_relations,
)

from ..data_loader import load_corpus


def _mentions_to_gsaphub_format(mentions):
    """Convert Mention objects to gsaphub dict format."""
    return [
        {
            "id": m.id,
            "doc_id": m.document_id,
            "begin": m.begin,
            "end": m.end,
            "label": m.label,
            "annotator": m.annotator,
        }
        for m in mentions
    ]


def _relations_to_gsaphub_format(relations):
    """Convert Relation objects to gsaphub dict format."""
    return [
        {
            "id": f"{r.subject.id}_{r.object.id}_{r.label}",
            "doc_id": r.document_id,
            "subject_id": r.subject.id,
            "object_id": r.object.id,
            "relation_label": r.label,  # gsaphub expects 'relation_label' not 'label'
        }
        for r in relations
    ]


def evaluate_model_performance(
    dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"],
    trained_on: Literal["scier", "scinlp", "gsap"],
) -> dict[str, float]:
    """Evaluate model performance by comparing predictions to gold standard.

    Args:
        dataset: Dataset to evaluate on
        split: Data split to evaluate
        trained_on: Dataset the model was trained on

    Returns:
        Dictionary containing performance metrics:
        - n_pred_sentences: Number of sentences in predictions
        - n_gold_sentences: Number of sentences in gold standard
        - n_pred_mentions: Number of predicted mentions
        - n_gold_mentions: Number of gold mentions
        - mention_precision: Precision for mentions
        - mention_recall: Recall for mentions
        - mention_f1: F1 score for mentions
        - n_pred_relations: Number of predicted relations
        - n_gold_relations: Number of gold relations
        - relation_precision: Precision for relations
        - relation_recall: Recall for relations
        - relation_f1: F1 score for relations

    Example:
        >>> metrics = evaluate_model_performance("scinlp", "test", "gsap")
        >>> print(f"Mention F1: {metrics['mention_f1']:.2%}")
        >>> print(f"Relation F1: {metrics['relation_f1']:.2%}")
    """
    # Load predictions (which includes both gold and predicted data)
    corpus = load_corpus(
        dataset=dataset, split=split, data_type="predictions", trained_on=trained_on
    )

    # Extract gold and predicted mentions/relations
    gold_mentions = corpus.mentions
    pred_mentions = corpus.mentions_predicted
    gold_relations = corpus.relation
    pred_relations = corpus.relations_predicted

    # Calculate mention metrics using gsaphub
    gold_ments_dict = _mentions_to_gsaphub_format(gold_mentions)
    pred_ments_dict = _mentions_to_gsaphub_format(pred_mentions)

    # Get both exact and partial matching metrics for entities
    mention_results_exact = evaluate_entities(
        gold_ments_dict, pred_ments_dict, partial=False
    )
    mention_results_partial = evaluate_entities(
        gold_ments_dict, pred_ments_dict, partial=True
    )

    # Extract micro-averaged metrics for exact matching
    micro_exact = mention_results_exact[mention_results_exact["label"] == "micro"]
    if not micro_exact.empty:
        mention_precision_exact = float(micro_exact["precision"].iloc[0])
        mention_recall_exact = float(micro_exact["recall"].iloc[0])
        mention_f1_exact = float(micro_exact["f1_score"].iloc[0])
    else:
        mention_precision_exact = 0.0
        mention_recall_exact = 0.0
        mention_f1_exact = 0.0

    # Extract micro-averaged metrics for partial matching
    micro_partial = mention_results_partial[mention_results_partial["label"] == "micro"]
    if not micro_partial.empty:
        mention_precision_partial = float(micro_partial["precision"].iloc[0])
        mention_recall_partial = float(micro_partial["recall"].iloc[0])
        mention_f1_partial = float(micro_partial["f1_score"].iloc[0])
    else:
        mention_precision_partial = 0.0
        mention_recall_partial = 0.0
        mention_f1_partial = 0.0

    # Calculate relation metrics using gsaphub with RE, RE+, and their partial versions
    gold_rels_dict = _relations_to_gsaphub_format(gold_relations)
    pred_rels_dict = _relations_to_gsaphub_format(pred_relations)

    # Evaluate with all metric types: RE (relaxed), RE+ (strict), and partial versions
    re_metrics = [
        RelationExtractionMetric.RELAXED_MATCH,  # RE (exact spans, any label)
        RelationExtractionMetric.STRICT_MATCH,  # RE+ (exact spans, correct label)
        RelationExtractionMetric.RELAXED_PARTIAL_MATCH,  # RE partial
        RelationExtractionMetric.STRICT_PARTIAL_MATCH,  # RE+ partial
    ]

    relation_results = evaluate_relations(
        gold_rels_dict,
        gold_ments_dict,
        pred_rels_dict,
        pred_ments_dict,
        re_metrics=re_metrics,
        show_counts=False,
    )

    # Extract micro-averaged metrics for each relation metric type
    micro_rel = relation_results[relation_results[("relation", "label")] == "micro"]

    if not micro_rel.empty:
        # RE (relaxed/exact spans)
        re_precision = float(micro_rel[("precision", "RE")].iloc[0])
        re_recall = float(micro_rel[("recall", "RE")].iloc[0])
        re_f1 = float(micro_rel[("f1_score", "RE")].iloc[0])

        # RE+ (strict/exact spans + correct labels)
        re_plus_precision = float(micro_rel[("precision", "RE+")].iloc[0])
        re_plus_recall = float(micro_rel[("recall", "RE+")].iloc[0])
        re_plus_f1 = float(micro_rel[("f1_score", "RE+")].iloc[0])

        # RE partial
        re_partial_precision = float(micro_rel[("precision", "RE partial")].iloc[0])
        re_partial_recall = float(micro_rel[("recall", "RE partial")].iloc[0])
        re_partial_f1 = float(micro_rel[("f1_score", "RE partial")].iloc[0])

        # RE+ partial
        re_plus_partial_precision = float(
            micro_rel[("precision", "RE+ partial")].iloc[0]
        )
        re_plus_partial_recall = float(micro_rel[("recall", "RE+ partial")].iloc[0])
        re_plus_partial_f1 = float(micro_rel[("f1_score", "RE+ partial")].iloc[0])
    else:
        re_precision = re_recall = re_f1 = 0.0
        re_plus_precision = re_plus_recall = re_plus_f1 = 0.0
        re_partial_precision = re_partial_recall = re_partial_f1 = 0.0
        re_plus_partial_precision = re_plus_partial_recall = re_plus_partial_f1 = 0.0

    # Calculate basic statistics and return all metrics
    metrics = {
        "n_pred_sentences": len(corpus.sentences),
        "n_gold_sentences": len(corpus.sentences),
        "n_pred_mentions": len(pred_mentions),
        "n_gold_mentions": len(gold_mentions),
        # Entity metrics - exact
        "mention_precision_exact": mention_precision_exact,
        "mention_recall_exact": mention_recall_exact,
        "mention_f1_exact": mention_f1_exact,
        # Entity metrics - partial
        "mention_precision_partial": mention_precision_partial,
        "mention_recall_partial": mention_recall_partial,
        "mention_f1_partial": mention_f1_partial,
        # Backward compatibility (partial as default)
        "mention_precision": mention_precision_partial,
        "mention_recall": mention_recall_partial,
        "mention_f1": mention_f1_partial,
        # Relation counts
        "n_pred_relations": len(pred_relations),
        "n_gold_relations": len(gold_relations),
        # RE (exact spans)
        "re_precision": re_precision,
        "re_recall": re_recall,
        "re_f1": re_f1,
        # RE+ (exact spans + correct entity labels)
        "re_plus_precision": re_plus_precision,
        "re_plus_recall": re_plus_recall,
        "re_plus_f1": re_plus_f1,
        # RE partial (overlapping spans)
        "re_partial_precision": re_partial_precision,
        "re_partial_recall": re_partial_recall,
        "re_partial_f1": re_partial_f1,
        # RE+ partial (overlapping spans + correct entity labels)
        "re_plus_partial_precision": re_plus_partial_precision,
        "re_plus_partial_recall": re_plus_partial_recall,
        "re_plus_partial_f1": re_plus_partial_f1,
        # Backward compatibility (RE+ as default relation)
        "relation_precision": re_plus_precision,
        "relation_recall": re_plus_recall,
        "relation_f1": re_plus_f1,
    }

    return metrics


def compare_models(
    dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"],
    models: list[Literal["scier", "scinlp", "gsap"]],
) -> dict[str, dict[str, float]]:
    """Compare performance of multiple models on the same dataset.

    Args:
        dataset: Dataset to evaluate on
        split: Data split to evaluate
        models: List of datasets that models were trained on

    Returns:
        Dictionary mapping model names to their performance metrics

    Example:
        >>> results = compare_models("scinlp", "test", ["gsap", "scier", "scinlp"])
        >>> for model, metrics in results.items():
        ...     print(f"{model}: F1={metrics['f1']:.2%}")
    """
    results = {}

    for trained_on in models:
        model_name = f"{trained_on}→{dataset}"
        metrics = evaluate_model_performance(dataset, split, trained_on)
        results[model_name] = metrics

    return results


def print_performance_summary(
    dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"],
    trained_on: Literal["scier", "scinlp", "gsap"],
) -> None:
    """Print a formatted summary of model performance.

    Args:
        dataset: Dataset to evaluate on
        split: Data split to evaluate
        trained_on: Dataset the model was trained on
    """
    metrics = evaluate_model_performance(dataset, split, trained_on)

    print(f"\n{'=' * 60}")
    print(f"Model Performance: {trained_on} → {dataset} ({split})")
    print(f"{'=' * 60}")
    print("\nDataset Statistics:")
    print(
        f"  Sentences (pred/gold): {metrics['n_pred_sentences']} / {metrics['n_gold_sentences']}"
    )
    print(
        f"  Mentions (pred/gold):  {metrics['n_pred_mentions']} / {metrics['n_gold_mentions']}"
    )
    print(
        f"  Relations (pred/gold): {metrics['n_pred_relations']} / {metrics['n_gold_relations']}"
    )
    print("\nMention Extraction:")
    print(f"  Precision: {metrics['mention_precision']:.2%}")
    print(f"  Recall:    {metrics['mention_recall']:.2%}")
    print(f"  F1 Score:  {metrics['mention_f1']:.2%}")
    print("\nRelation Extraction:")
    print(f"  Precision: {metrics['relation_precision']:.2%}")
    print(f"  Recall:    {metrics['relation_recall']:.2%}")
    print(f"  F1 Score:  {metrics['relation_f1']:.2%}")
    print(f"{'=' * 60}\n")


def analyze_cross_dataset_performance(
    target_dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"] = "test",
) -> None:
    """Analyze how models trained on different datasets perform on a target dataset.

    Args:
        target_dataset: The dataset to evaluate all models on
        split: Data split to use for evaluation

    Example:
        >>> # See how different models perform on SciNLP test set
        >>> analyze_cross_dataset_performance("scinlp", "test")
    """
    source_datasets: list[Literal["scier", "scinlp", "gsap"]] = [
        "scier",
        "scinlp",
        "gsap",
    ]

    print(f"\n{'=' * 60}")
    print("Cross-Dataset Performance Analysis")
    print(f"Target: {target_dataset} ({split})")
    print(f"{'=' * 60}\n")

    results = compare_models(target_dataset, split, source_datasets)

    for model_name, metrics in results.items():
        print(f"{model_name}:")
        print(
            f"  Mentions:  {metrics['n_pred_mentions']:4d} predicted / {metrics['n_gold_mentions']:4d} gold"
        )
        print(
            f"  Relations: {metrics['n_pred_relations']:4d} predicted / {metrics['n_gold_relations']:4d} gold"
        )
        print()


def create_performance_table(
    target_dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"] = "test",
) -> GT:
    """Create a formatted table of model performance using great_tables.

    Args:
        target_dataset: The dataset to evaluate all models on
        split: Data split to use for evaluation

    Returns:
        GT object containing the formatted table
    """
    source_datasets: list[Literal["scier", "scinlp", "gsap"]] = [
        "scier",
        "scinlp",
        "gsap",
    ]

    # Collect data for table
    table_data = []
    for trained_on in source_datasets:
        metrics = evaluate_model_performance(target_dataset, split, trained_on)
        table_data.append(
            {
                "Model": trained_on.upper(),
                "Mention P": metrics["mention_precision"],
                "Mention R": metrics["mention_recall"],
                "Mention F1": metrics["mention_f1"],
                "Relation P": metrics["relation_precision"],
                "Relation R": metrics["relation_recall"],
                "Relation F1": metrics["relation_f1"],
            }
        )

    # Convert to pandas DataFrame for GT
    import pandas as pd

    df = pd.DataFrame(table_data)

    # Create GT table
    gt_table = (
        GT(df)
        .tab_header(
            title=f"Model Performance on {target_dataset.upper()}",
            subtitle=f"Split: {split} | Date: {datetime.now().strftime('%Y-%m-%d')}",
        )
        .fmt_number(
            columns=[
                "Mention P",
                "Mention R",
                "Mention F1",
                "Relation P",
                "Relation R",
                "Relation F1",
            ],
            decimals=3,
        )
        .tab_spanner(
            label="Mention Extraction",
            columns=["Mention P", "Mention R", "Mention F1"],
        )
        .tab_spanner(
            label="Relation Extraction",
            columns=["Relation P", "Relation R", "Relation F1"],
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.column_labels(),
        )
        .tab_style(
            style=style.text(align="center"),
            locations=loc.body(
                columns=[
                    "Mention P",
                    "Mention R",
                    "Mention F1",
                    "Relation P",
                    "Relation R",
                    "Relation F1",
                ]
            ),
        )
    )

    return gt_table


def save_performance_table(
    target_dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"] = "test",
    output_dir: Path | None = None,
) -> dict[str, Path]:
    """Save performance table in multiple formats.

    Args:
        target_dataset: The dataset to evaluate all models on
        split: Data split to use for evaluation
        output_dir: Output directory (default: reports/ere_performance/)

    Returns:
        Dictionary with paths to generated files
    """
    if output_dir is None:
        output_dir = Path("reports/ere_performance")

    output_dir.mkdir(parents=True, exist_ok=True)
    latex_dir = output_dir / "tables" / "latex"
    latex_dir.mkdir(parents=True, exist_ok=True)

    # Create table
    gt_table = create_performance_table(target_dataset, split)

    # Generate filenames (no date in filename)
    base_name = f"{target_dataset}_{split}"

    # Save as LaTeX
    latex_path = latex_dir / f"{base_name}.tex"
    latex_output = gt_table.as_latex()
    latex_path.write_text(latex_output)

    # Save as HTML (using as_raw_html instead of save to avoid selenium dependency)
    html_path = output_dir / f"{base_name}.html"
    html_content = gt_table.as_raw_html()
    html_path.write_text(html_content)

    return {"latex": latex_path, "html": html_path}


def generate_markdown_report(
    target_dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"] = "test",
    output_dir: Path | None = None,
) -> Path:
    """Generate a comprehensive markdown report of model performance.

    Args:
        target_dataset: The dataset to evaluate all models on
        split: Data split to use for evaluation
        output_dir: Output directory (default: reports/ere_performance/)

    Returns:
        Path to the generated markdown file
    """
    if output_dir is None:
        output_dir = Path("reports/ere_performance")

    output_dir.mkdir(parents=True, exist_ok=True)

    source_datasets: list[Literal["scier", "scinlp", "gsap"]] = [
        "scier",
        "scinlp",
        "gsap",
    ]

    # Collect metrics
    results = compare_models(target_dataset, split, source_datasets)

    # Generate markdown content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_content = f"""# Model Performance Report

**Target Dataset:** {target_dataset.upper()}
**Split:** {split}
**Generated:** {timestamp}

## Overview

This report compares the performance of models trained on different datasets when evaluated on the {target_dataset.upper()} {split} set.

## Results Summary

### Mentions and Relations Performance

| Model | M-Pred | M-Gold | M-P | M-R | M-F1 | R-Pred | R-Gold | R-P | R-R | R-F1 |
|-------|--------|--------|-----|-----|------|--------|--------|-----|-----|------|
"""

    for model_name, metrics in results.items():
        trained_on = model_name.split("→")[0]
        md_content += (
            f"| {trained_on.upper()} "
            f"| {metrics['n_pred_mentions']} "
            f"| {metrics['n_gold_mentions']} "
            f"| {metrics['mention_precision']:.3f} "
            f"| {metrics['mention_recall']:.3f} "
            f"| {metrics['mention_f1']:.3f} "
            f"| {metrics['n_pred_relations']} "
            f"| {metrics['n_gold_relations']} "
            f"| {metrics['relation_precision']:.3f} "
            f"| {metrics['relation_recall']:.3f} "
            f"| {metrics['relation_f1']:.3f} |\n"
        )

    md_content += f"""
## Detailed Analysis

### Dataset Statistics

- **Total Sentences:** {results[list(results.keys())[0]]["n_gold_sentences"]}
- **Total Gold Mentions:** {results[list(results.keys())[0]]["n_gold_mentions"]}
- **Total Gold Relations:** {results[list(results.keys())[0]]["n_gold_relations"]}

### Mention Extraction Performance

"""

    for model_name, metrics in results.items():
        trained_on = model_name.split("→")[0]
        md_content += f"**{trained_on.upper()}:**\n"
        md_content += f"- Predicted: {metrics['n_pred_mentions']}\n"
        md_content += f"- Gold: {metrics['n_gold_mentions']}\n"
        md_content += f"- Precision: {metrics['mention_precision']:.2%}\n"
        md_content += f"- Recall: {metrics['mention_recall']:.2%}\n"
        md_content += f"- F1 Score: {metrics['mention_f1']:.2%}\n\n"

    md_content += "### Relation Extraction Performance\n\n"

    for model_name, metrics in results.items():
        trained_on = model_name.split("→")[0]
        md_content += f"**{trained_on.upper()}:**\n"
        md_content += f"- Predicted: {metrics['n_pred_relations']}\n"
        md_content += f"- Gold: {metrics['n_gold_relations']}\n"
        md_content += f"- Precision: {metrics['relation_precision']:.2%}\n"
        md_content += f"- Recall: {metrics['relation_recall']:.2%}\n"
        md_content += f"- F1 Score: {metrics['relation_f1']:.2%}\n\n"

    md_content += """
## Notes

- Precision (P): Proportion of predicted entities/relations that are correct
- Recall (R): Proportion of gold entities/relations that are predicted
- F1 Score: Harmonic mean of precision and recall
- Matching criteria: Exact span and label match for mentions; exact argument spans and label match for relations

---
*Generated by UnifiedSciERE Analysis Module*
"""

    # Save markdown file (no date in filename)
    md_path = output_dir / f"{target_dataset}_{split}.md"
    md_path.write_text(md_content)

    return md_path


def generate_comprehensive_report(
    output_dir: Path | None = None,
) -> Path:
    """Generate a comprehensive report across all datasets and splits.

    Args:
        output_dir: Output directory (default: reports/ere_performance/)

    Returns:
        Path to the generated markdown file
    """
    if output_dir is None:
        output_dir = Path("reports/ere_performance")

    output_dir.mkdir(parents=True, exist_ok=True)

    datasets: list[Literal["scier", "scinlp", "gsap"]] = ["scier", "scinlp", "gsap"]
    splits: list[Literal["train", "dev", "test"]] = ["train", "dev", "test"]
    source_datasets: list[Literal["scier", "scinlp", "gsap"]] = [
        "scier",
        "scinlp",
        "gsap",
    ]

    # Collect all metrics
    all_results = []
    for target_dataset in datasets:
        for split in splits:
            for trained_on in source_datasets:
                try:
                    metrics = evaluate_model_performance(
                        target_dataset, split, trained_on
                    )
                    all_results.append(
                        {
                            "dataset": target_dataset.upper(),
                            "split": split,
                            "model": trained_on.upper(),
                            **metrics,
                        }
                    )
                except Exception:
                    # Skip if data doesn't exist
                    continue

    # Sort by dataset name and then split
    all_results.sort(key=lambda x: (x["dataset"], x["split"]))

    # Generate markdown content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_content = f"""# Comprehensive Model Performance Report

**Generated:** {timestamp}

## Overview

This report evaluates all models across all datasets and splits.
"""

    # Generate tables for each split (Test first, then Dev, then Train)
    for split_name in ["test", "dev", "train"]:
        split_results = [r for r in all_results if r["split"] == split_name]
        if not split_results:
            continue

        md_content += f"""
## {split_name.capitalize()} Set Performance

### Entity (Mention) Extraction - {split_name.capitalize()}

#### Exact Match

| Dataset | Model | Precision | Recall | F1 | Pred | Gold |
|---------|-------|-----------|--------|-----|------|------|
"""

        for result in split_results:
            md_content += (
                f"| {result['dataset']} "
                f"| {result['model']} "
                f"| {result['mention_precision_exact']:.3f} "
                f"| {result['mention_recall_exact']:.3f} "
                f"| {result['mention_f1_exact']:.3f} "
                f"| {result['n_pred_mentions']} "
                f"| {result['n_gold_mentions']} |\n"
            )

        md_content += """
#### Partial Match

| Dataset | Model | Precision | Recall | F1 | Pred | Gold |
|---------|-------|-----------|--------|-----|------|------|
"""

        for result in split_results:
            md_content += (
                f"| {result['dataset']} "
                f"| {result['model']} "
                f"| {result['mention_precision_partial']:.3f} "
                f"| {result['mention_recall_partial']:.3f} "
                f"| {result['mention_f1_partial']:.3f} "
                f"| {result['n_pred_mentions']} "
                f"| {result['n_gold_mentions']} |\n"
            )

        md_content += f"""
### Relation Extraction - {split_name.capitalize()}

#### RE (Relaxed - Exact Spans)

| Dataset | Model | Precision | Recall | F1 | Pred | Gold |
|---------|-------|-----------|--------|-----|------|------|
"""

        for result in split_results:
            md_content += (
                f"| {result['dataset']} "
                f"| {result['model']} "
                f"| {result['re_precision']:.3f} "
                f"| {result['re_recall']:.3f} "
                f"| {result['re_f1']:.3f} "
                f"| {result['n_pred_relations']} "
                f"| {result['n_gold_relations']} |\n"
            )

        md_content += """
#### RE+ (Strict - Exact Spans + Correct Labels)

| Dataset | Model | Precision | Recall | F1 | Pred | Gold |
|---------|-------|-----------|--------|-----|------|------|
"""

        for result in split_results:
            md_content += (
                f"| {result['dataset']} "
                f"| {result['model']} "
                f"| {result['re_plus_precision']:.3f} "
                f"| {result['re_plus_recall']:.3f} "
                f"| {result['re_plus_f1']:.3f} "
                f"| {result['n_pred_relations']} "
                f"| {result['n_gold_relations']} |\n"
            )

        md_content += """
#### RE Partial (Relaxed - Overlapping Spans)

| Dataset | Model | Precision | Recall | F1 | Pred | Gold |
|---------|-------|-----------|--------|-----|------|------|
"""

        for result in split_results:
            md_content += (
                f"| {result['dataset']} "
                f"| {result['model']} "
                f"| {result['re_partial_precision']:.3f} "
                f"| {result['re_partial_recall']:.3f} "
                f"| {result['re_partial_f1']:.3f} "
                f"| {result['n_pred_relations']} "
                f"| {result['n_gold_relations']} |\n"
            )

        md_content += """
#### RE+ Partial (Strict - Overlapping Spans + Correct Labels)

| Dataset | Model | Precision | Recall | F1 | Pred | Gold |
|---------|-------|-----------|--------|-----|------|------|
"""

        for result in split_results:
            md_content += (
                f"| {result['dataset']} "
                f"| {result['model']} "
                f"| {result['re_plus_partial_precision']:.3f} "
                f"| {result['re_plus_partial_recall']:.3f} "
                f"| {result['re_plus_partial_f1']:.3f} "
                f"| {result['n_pred_relations']} "
                f"| {result['n_gold_relations']} |\n"
            )

    md_content += """
## Notes

### General
- **Dataset**: Target dataset (SCIER, SCINLP, or GSAP)
- **Model**: Source dataset the model was trained on
- **Precision**: Proportion of predictions that are correct
- **Recall**: Proportion of gold entities/relations that are predicted
- **F1**: Harmonic mean of precision and recall
- **Pred/Gold**: Number of predicted vs gold standard entities/relations

### Entity Extraction Metrics
- **Exact Match**: Requires exact span boundaries (character offsets must match exactly)
- **Partial Match**: Credits overlapping spans (uses gsaphub partial matching)

### Relation Extraction Metrics
- **RE (Relaxed)**: Requires exact spans for relation arguments, ignores entity labels
- **RE+ (Strict)**: Requires exact spans AND correct entity labels for relation arguments
- **RE Partial**: Allows overlapping spans for relation arguments, ignores entity labels
- **RE+ Partial**: Allows overlapping spans AND requires correct entity labels

---
*Generated by UnifiedSciERE Analysis Module*
"""

    # Save markdown file (no date in filename)
    md_path = output_dir / "comprehensive_report.md"
    md_path.write_text(md_content)

    return md_path


def generate_all_reports(
    target_dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"] = "test",
    output_dir: Path | None = None,
) -> dict[str, Path]:
    """Generate all report formats (LaTeX table, HTML table, and Markdown report).

    Args:
        target_dataset: The dataset to evaluate all models on
        split: Data split to use for evaluation
        output_dir: Output directory (default: reports/ere_performance/)

    Returns:
        Dictionary with paths to all generated files
    """
    table_paths = save_performance_table(target_dataset, split, output_dir)
    md_path = generate_markdown_report(target_dataset, split, output_dir)

    return {
        "latex": table_paths["latex"],
        "html": table_paths["html"],
        "markdown": md_path,
    }
