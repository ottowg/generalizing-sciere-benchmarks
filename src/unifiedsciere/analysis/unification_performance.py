"""Generate comprehensive unification report combining merging and mapping steps."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from ..data_loader import load_corpus
from ..unification.label_mapper import drop_unmapped_mentions, map_labels_to_unified
from ..unification.merge_stacked import merge_stacked_mentions
from ..unification.pipeline import apply_unification_pipeline


def generate_unification_report(
    datasets: list[Literal["scier", "scinlp", "gsap"]],
    split: Literal["train", "dev", "test"],
    models: list[Literal["scier", "scinlp", "gsap"]],
    prefer_larger: bool = True,
    output_dir: Path | None = None,
) -> Path:
    """Generate a comprehensive unification report.

    This report shows the complete unification pipeline:
    1. Merge stacked/overlapping mentions
    2. Drop unmapped mentions (labels that map to null)
    3. Map remaining labels to unified schema

    Args:
        datasets: List of datasets to process
        split: Data split to use
        models: List of models to process predictions from
        prefer_larger: If True, prefer larger spans when merging
        output_dir: Output directory (default: reports/ere_confusion_analysis/unification/)

    Returns:
        Path to generated markdown file
    """
    if output_dir is None:
        output_dir = Path("reports/ere_confusion_analysis/unification")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    span_preference = "larger" if prefer_larger else "smaller"

    md_content = f"""# Unification Report

**Generated:** {timestamp}

**Split:** {split}

**Span Preference:** Prefer {span_preference} spans when merging

## Overview

This report shows the complete unification pipeline applied to entity mentions:

1. **Merge Stacked Mentions**: Combine overlapping mentions within same sentence
2. **Drop Unmapped Labels**: Remove mentions that don't map to unified schema
3. **Map to Unified Labels**: Transform remaining labels to unified set (Dataset, Method, Task)

"""

    for dataset in datasets:
        md_content += f"\n## {dataset.upper()} Dataset\n\n"

        # Process gold annotations
        try:
            # Load gold from any prediction file
            gold_corpus = None
            for model in models:
                try:
                    temp_corpus = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )
                    from ..types import Corpus

                    gold_corpus = Corpus(
                        sentences=temp_corpus.sentences,
                        mentions=temp_corpus.mentions,
                        relation=temp_corpus.relation,
                        mentions_predicted=[],
                        relations_predicted=[],
                    )
                    break
                except Exception:
                    continue

            if gold_corpus is None:
                raise FileNotFoundError(
                    f"Could not load gold annotations for {dataset}"
                )

            md_content += "### Gold Annotations\n\n"

            # Step 1: Merge
            merged_corpus, merge_stats = merge_stacked_mentions(
                gold_corpus,
                prefer_larger=prefer_larger,
                merge_gold=True,
                merge_predicted=False,
            )

            md_content += f"""**Step 1: Merge Stacked Mentions**

- Original mentions: {merge_stats["gold_original_count"]}
- After merging: {merge_stats["gold_merged_count"]}
- Merged: {merge_stats["gold_original_count"] - merge_stats["gold_merged_count"]}
- Relations: {merge_stats["gold_relations_original"]} → {merge_stats["gold_relations_merged"]} (self-loops: {merge_stats["gold_relations_self_loops"]}, duplicates: {merge_stats["gold_relations_duplicates"]})

"""

            # Step 2: Drop unmapped
            dropped_corpus, drop_stats = drop_unmapped_mentions(
                merged_corpus, dataset, drop_gold=True, drop_predicted=False
            )

            md_content += f"""**Step 2: Drop Unmapped Mentions**

- Before dropping: {drop_stats["gold_mentions_original"]}
- Dropped: {drop_stats["gold_mentions_dropped"]}
- After dropping: {drop_stats["gold_mentions_kept"]}
- Relations: {drop_stats["gold_relations_original"]} → {drop_stats["gold_relations_kept"]} (dropped: {drop_stats["gold_relations_dropped"]})

"""

            if drop_stats["dropped_labels"]:
                md_content += (
                    f"**Dropped labels:** {', '.join(drop_stats['dropped_labels'])}\n\n"
                )

                # Count mentions by dropped label
                dropped_by_label = defaultdict(int)
                for m in merged_corpus.mentions:
                    if m.label in drop_stats["dropped_labels"]:
                        dropped_by_label[m.label] += 1

                if dropped_by_label:
                    md_content += "| Dropped Label | Count |\n"
                    md_content += "|---------------|-------|\n"
                    for label in sorted(dropped_by_label.keys()):
                        md_content += f"| {label} | {dropped_by_label[label]} |\n"
                    md_content += "\n"

            # Step 3: Map labels
            mapped_corpus, map_stats = map_labels_to_unified(
                dropped_corpus, dataset, map_gold=True, map_predicted=False
            )

            md_content += f"""**Step 3: Map to Unified Labels**

- Mentions with changed labels: {map_stats["gold_mentions_mapped"]}
- Final mention count: {len(mapped_corpus.mentions)}
- Final relation count: {len(mapped_corpus.relation)}

"""

            if map_stats["gold_label_changes"]:
                md_content += "**Label mappings applied:**\n\n"
                md_content += "| Original Label | Unified Label | Count |\n"
                md_content += "|----------------|---------------|-------|\n"
                for orig_label in sorted(map_stats["gold_label_changes"].keys()):
                    for unified_label, count in sorted(
                        map_stats["gold_label_changes"][orig_label].items()
                    ):
                        md_content += f"| {orig_label} | {unified_label} | {count} |\n"
                md_content += "\n"

            # Final statistics
            md_content += f"""**Summary:**

- Original → Final: {merge_stats["gold_original_count"]} → {len(mapped_corpus.mentions)} mentions ({merge_stats["gold_original_count"] - len(mapped_corpus.mentions)} removed)
- Original → Final: {merge_stats["gold_relations_original"]} → {len(mapped_corpus.relation)} relations ({merge_stats["gold_relations_original"] - len(mapped_corpus.relation)} removed)

---

"""

        except Exception as e:
            md_content += f"**Error processing gold annotations:** {str(e)}\n\n"

        # Process predictions from each model
        for model in models:
            try:
                pred_corpus = load_corpus(
                    dataset, split, data_type="predictions", trained_on=model
                )

                md_content += f"### {model.upper()} Predictions\n\n"

                # Step 1: Merge
                merged_corpus, merge_stats = merge_stacked_mentions(
                    pred_corpus,
                    prefer_larger=prefer_larger,
                    merge_gold=False,
                    merge_predicted=True,
                )

                md_content += f"""**Step 1: Merge Stacked Mentions**

- Original mentions: {merge_stats["predicted_original_count"]}
- After merging: {merge_stats["predicted_merged_count"]}
- Merged: {merge_stats["predicted_original_count"] - merge_stats["predicted_merged_count"]}
- Relations: {merge_stats["predicted_relations_original"]} → {merge_stats["predicted_relations_merged"]} (self-loops: {merge_stats["predicted_relations_self_loops"]}, duplicates: {merge_stats["predicted_relations_duplicates"]})

"""

                # Step 2: Drop unmapped
                dropped_corpus, drop_stats = drop_unmapped_mentions(
                    merged_corpus, dataset, drop_gold=False, drop_predicted=True
                )

                md_content += f"""**Step 2: Drop Unmapped Mentions**

- Before dropping: {drop_stats["predicted_mentions_original"]}
- Dropped: {drop_stats["predicted_mentions_dropped"]}
- After dropping: {drop_stats["predicted_mentions_kept"]}
- Relations: {drop_stats["predicted_relations_original"]} → {drop_stats["predicted_relations_kept"]} (dropped: {drop_stats["predicted_relations_dropped"]})

"""

                if drop_stats["dropped_labels"]:
                    md_content += f"**Dropped labels:** {', '.join(drop_stats['dropped_labels'])}\n\n"

                    # Count mentions by dropped label
                    dropped_by_label = defaultdict(int)
                    for m in merged_corpus.mentions_predicted:
                        if m.label in drop_stats["dropped_labels"]:
                            dropped_by_label[m.label] += 1

                    if dropped_by_label:
                        md_content += "| Dropped Label | Count |\n"
                        md_content += "|---------------|-------|\n"
                        for label in sorted(dropped_by_label.keys()):
                            md_content += f"| {label} | {dropped_by_label[label]} |\n"
                        md_content += "\n"

                # Step 3: Map labels
                mapped_corpus, map_stats = map_labels_to_unified(
                    dropped_corpus, dataset, map_gold=False, map_predicted=True
                )

                md_content += f"""**Step 3: Map to Unified Labels**

- Mentions with changed labels: {map_stats["predicted_mentions_mapped"]}
- Final mention count: {len(mapped_corpus.mentions_predicted)}
- Final relation count: {len(mapped_corpus.relations_predicted)}

"""

                if map_stats["predicted_label_changes"]:
                    md_content += "**Label mappings applied:**\n\n"
                    md_content += "| Original Label | Unified Label | Count |\n"
                    md_content += "|----------------|---------------|-------|\n"
                    for orig_label in sorted(
                        map_stats["predicted_label_changes"].keys()
                    ):
                        for unified_label, count in sorted(
                            map_stats["predicted_label_changes"][orig_label].items()
                        ):
                            md_content += (
                                f"| {orig_label} | {unified_label} | {count} |\n"
                            )
                    md_content += "\n"

                # Final statistics
                md_content += f"""**Summary:**

- Original → Final: {merge_stats["predicted_original_count"]} → {len(mapped_corpus.mentions_predicted)} mentions ({merge_stats["predicted_original_count"] - len(mapped_corpus.mentions_predicted)} removed)
- Original → Final: {merge_stats["predicted_relations_original"]} → {len(mapped_corpus.relations_predicted)} relations ({merge_stats["predicted_relations_original"] - len(mapped_corpus.relations_predicted)} removed)

---

"""

            except Exception as e:
                md_content += (
                    f"**Error processing {model.upper()} predictions:** {str(e)}\n\n"
                )

    md_content += """
## Notes

- **Merge step**: Combines overlapping mentions, preferring larger/smaller spans as specified
- **Drop step**: Removes mentions with labels that map to null in unified schema
- **Map step**: Transforms remaining labels to unified schema (Dataset, Method, Task)
- Relations are automatically updated and filtered at each step

---
*Generated by UnifiedSciERE Unification Pipeline*
"""

    # Save markdown file
    preference_suffix = "larger" if prefer_larger else "smaller"
    md_path = output_dir / f"unification_report_{split}_{preference_suffix}.md"
    md_path.write_text(md_content)

    return md_path


def _mentions_to_gsaphub_format(mentions):
    """Convert Mention objects to gsaphub dict format.

    Uses the actual doc_id from the JSON files (doc_key for SCINLP, doc_id for SCIER/GSAP).
    """
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


def evaluate_unified_performance(
    datasets: list[Literal["scier", "scinlp", "gsap"]],
    split: Literal["train", "dev", "test"],
    models: list[Literal["scier", "scinlp", "gsap"]],
    prefer_larger: bool = True,
    output_dir: Path | None = None,
) -> Path:
    """Evaluate model performance after applying unification pipeline.

    This generates performance metrics (precision, recall, F1) for entity recognition
    after applying the complete unification pipeline to both gold and predicted mentions.

    Args:
        datasets: List of datasets to evaluate
        split: Data split to use
        models: List of models to evaluate
        prefer_larger: If True, prefer larger spans when merging
        output_dir: Output directory (default: reports/ere_performance/)

    Returns:
        Path to generated markdown file
    """
    if output_dir is None:
        output_dir = Path("reports/ere_performance")

    output_dir.mkdir(parents=True, exist_ok=True)

    from gsaphub.evaluate.entities import precision_recall_f1 as evaluate_entities

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = f"""# Performance After Unification

**Generated:** {timestamp}

**Split:** {split}

## Overview

This report shows model performance metrics after applying the complete unification pipeline:

1. Merge stacked mentions (prefer larger spans)
2. Drop unmapped labels (null mappings)
3. Map to unified schema (Dataset, Method, Task)
4. Apply dataset-specific corrections (e.g., GSAP MLModelGeneric filtering)
5. Normalize spans (strip systematic prefixes/suffixes)

Performance is measured using strict and partial matching for entity recognition.

"""

    for dataset in datasets:
        md_content += f"\n## {dataset.upper()} Dataset\n\n"

        # Load gold annotations and apply unification
        try:
            gold_corpus = None
            for model in models:
                try:
                    temp_corpus = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )
                    gold_corpus = temp_corpus
                    break
                except Exception:
                    continue

            if gold_corpus is None:
                raise FileNotFoundError(
                    f"Could not load gold annotations for {dataset}"
                )

            # Apply unification to gold
            gold_unified, _ = apply_unification_pipeline(
                gold_corpus,
                dataset=dataset,
                apply_to_gold=True,
                apply_to_predicted=False,
            )

            # Evaluate each model
            for model in models:
                try:
                    # Load predictions
                    pred_corpus = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )

                    # Apply unification to predictions
                    # IMPORTANT: Use 'model' not 'dataset' because predictions have the model's label scheme
                    pred_unified, _ = apply_unification_pipeline(
                        pred_corpus,
                        dataset=model,
                        apply_to_gold=False,
                        apply_to_predicted=True,
                    )

                    # Convert to gsaphub format
                    gold_ments_dict = _mentions_to_gsaphub_format(gold_unified.mentions)
                    pred_ments_dict = _mentions_to_gsaphub_format(
                        pred_unified.mentions_predicted
                    )

                    # Evaluate with strict matching (partial=False)
                    strict_results = evaluate_entities(
                        gold_ments_dict, pred_ments_dict, partial=False
                    )

                    # Evaluate with partial matching (partial=True)
                    partial_results = evaluate_entities(
                        gold_ments_dict, pred_ments_dict, partial=True
                    )

                    md_content += f"""### {model.upper()} Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| """

                    # Sort labels, put micro last
                    labels = sorted(
                        [
                            lbl
                            for lbl in strict_results["label"].unique()
                            if lbl != "micro"
                        ]
                    )
                    labels.append("micro")

                    for label in labels:
                        row = strict_results[strict_results["label"] == label].iloc[0]
                        label_display = f"**{label}**" if label == "micro" else label
                        prec = (
                            f"**{row['precision']:.3f}**"
                            if label == "micro"
                            else f"{row['precision']:.3f}"
                        )
                        rec = (
                            f"**{row['recall']:.3f}**"
                            if label == "micro"
                            else f"{row['recall']:.3f}"
                        )
                        f1 = (
                            f"**{row['f1_score']:.3f}**"
                            if label == "micro"
                            else f"{row['f1_score']:.3f}"
                        )
                        support = (
                            f"**{int(row['support'])}**"
                            if label == "micro"
                            else f"{int(row['support'])}"
                        )
                        md_content += (
                            f"\n| {label_display} | {prec} | {rec} | {f1} | {support} |"
                        )

                    md_content += "\n\n**Partial Matching (Overlapping Spans):**\n\n"
                    md_content += "| Label | Precision | Recall | F1 | Support |\n"
                    md_content += "|-------|-----------|--------|----|---------| "

                    for label in labels:
                        row = partial_results[partial_results["label"] == label].iloc[0]
                        label_display = f"**{label}**" if label == "micro" else label
                        prec = (
                            f"**{row['precision']:.3f}**"
                            if label == "micro"
                            else f"{row['precision']:.3f}"
                        )
                        rec = (
                            f"**{row['recall']:.3f}**"
                            if label == "micro"
                            else f"{row['recall']:.3f}"
                        )
                        f1 = (
                            f"**{row['f1_score']:.3f}**"
                            if label == "micro"
                            else f"{row['f1_score']:.3f}"
                        )
                        support = (
                            f"**{int(row['support'])}**"
                            if label == "micro"
                            else f"{int(row['support'])}"
                        )
                        md_content += (
                            f"\n| {label_display} | {prec} | {rec} | {f1} | {support} |"
                        )

                    md_content += f"""\n\n**Entity Counts:**

- Gold mentions: {len(gold_unified.mentions)}
- Predicted mentions: {len(pred_unified.mentions_predicted)}

---

"""

                except Exception as e:
                    md_content += f"**Error evaluating {model.upper()}:** {str(e)}\n\n"

        except Exception as e:
            md_content += f"**Error processing dataset:** {str(e)}\n\n"

    # --- Comparison: with vs without span normalization ---
    from ..unification.pipeline import load_unification_config

    config_no_span = load_unification_config()
    config_no_span["span_normalization"] = {"enabled": False}

    # Collect micro F1 scores without span normalization
    baseline: dict[
        tuple[str, str], dict[str, float]
    ] = {}  # (dataset, model) -> metrics

    for dataset in datasets:
        try:
            gold_corpus_base = None
            for model in models:
                try:
                    gold_corpus_base = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )
                    break
                except Exception:
                    continue
            if gold_corpus_base is None:
                continue

            gold_unified_base, _ = apply_unification_pipeline(
                gold_corpus_base,
                dataset=dataset,
                config=config_no_span,
                apply_to_gold=True,
                apply_to_predicted=False,
            )

            for model in models:
                try:
                    pred_corpus_base = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )
                    pred_unified_base, _ = apply_unification_pipeline(
                        pred_corpus_base,
                        dataset=model,
                        config=config_no_span,
                        apply_to_gold=False,
                        apply_to_predicted=True,
                    )

                    gold_base_dict = _mentions_to_gsaphub_format(
                        gold_unified_base.mentions
                    )
                    pred_base_dict = _mentions_to_gsaphub_format(
                        pred_unified_base.mentions_predicted
                    )

                    strict_base = evaluate_entities(
                        gold_base_dict, pred_base_dict, partial=False
                    )
                    partial_base = evaluate_entities(
                        gold_base_dict, pred_base_dict, partial=True
                    )

                    micro_strict = strict_base[strict_base["label"] == "micro"].iloc[0]
                    micro_partial = partial_base[partial_base["label"] == "micro"].iloc[
                        0
                    ]

                    baseline[(dataset, model)] = {
                        "strict_p": float(micro_strict["precision"]),
                        "strict_r": float(micro_strict["recall"]),
                        "strict_f1": float(micro_strict["f1_score"]),
                        "partial_p": float(micro_partial["precision"]),
                        "partial_r": float(micro_partial["recall"]),
                        "partial_f1": float(micro_partial["f1_score"]),
                    }
                except Exception:
                    continue
        except Exception:
            continue

    # Now collect "after" metrics by re-running with full pipeline
    after: dict[tuple[str, str], dict[str, float]] = {}

    for dataset in datasets:
        try:
            gold_corpus_after = None
            for model in models:
                try:
                    gold_corpus_after = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )
                    break
                except Exception:
                    continue
            if gold_corpus_after is None:
                continue

            gold_unified_after, _ = apply_unification_pipeline(
                gold_corpus_after,
                dataset=dataset,
                apply_to_gold=True,
                apply_to_predicted=False,
            )

            for model in models:
                try:
                    pred_corpus_after = load_corpus(
                        dataset, split, data_type="predictions", trained_on=model
                    )
                    pred_unified_after, _ = apply_unification_pipeline(
                        pred_corpus_after,
                        dataset=model,
                        apply_to_gold=False,
                        apply_to_predicted=True,
                    )

                    gold_after_dict = _mentions_to_gsaphub_format(
                        gold_unified_after.mentions
                    )
                    pred_after_dict = _mentions_to_gsaphub_format(
                        pred_unified_after.mentions_predicted
                    )

                    strict_af = evaluate_entities(
                        gold_after_dict, pred_after_dict, partial=False
                    )
                    partial_af = evaluate_entities(
                        gold_after_dict, pred_after_dict, partial=True
                    )

                    micro_strict_af = strict_af[strict_af["label"] == "micro"].iloc[0]
                    micro_partial_af = partial_af[partial_af["label"] == "micro"].iloc[
                        0
                    ]

                    after[(dataset, model)] = {
                        "strict_p": float(micro_strict_af["precision"]),
                        "strict_r": float(micro_strict_af["recall"]),
                        "strict_f1": float(micro_strict_af["f1_score"]),
                        "partial_p": float(micro_partial_af["precision"]),
                        "partial_r": float(micro_partial_af["recall"]),
                        "partial_f1": float(micro_partial_af["f1_score"]),
                    }
                except Exception:
                    continue
        except Exception:
            continue

    # Generate comparison table
    md_content += """
## Impact of Span Normalization (Step 5)

Micro-averaged performance comparison: Steps 1--4 only vs. Steps 1--5 (with span normalization).

### Strict Matching (Exact Spans)

| Dataset | Model | P (before) | P (after) | P (diff) | R (before) | R (after) | R (diff) | F1 (before) | F1 (after) | F1 (diff) |
|---------|-------|------------|-----------|----------|------------|-----------|----------|-------------|------------|-----------|
"""

    for dataset in datasets:
        for model in models:
            key = (dataset, model)
            if key in baseline and key in after:
                b = baseline[key]
                a = after[key]
                dp = a["strict_p"] - b["strict_p"]
                dr = a["strict_r"] - b["strict_r"]
                df1 = a["strict_f1"] - b["strict_f1"]
                md_content += (
                    f"| {dataset.upper()} | {model.upper()} "
                    f"| {b['strict_p']:.3f} | {a['strict_p']:.3f} | {dp:+.3f} "
                    f"| {b['strict_r']:.3f} | {a['strict_r']:.3f} | {dr:+.3f} "
                    f"| {b['strict_f1']:.3f} | {a['strict_f1']:.3f} | {df1:+.3f} |\n"
                )

    md_content += """
### Partial Matching (Overlapping Spans)

| Dataset | Model | P (before) | P (after) | P (diff) | R (before) | R (after) | R (diff) | F1 (before) | F1 (after) | F1 (diff) |
|---------|-------|------------|-----------|----------|------------|-----------|----------|-------------|------------|-----------|
"""

    for dataset in datasets:
        for model in models:
            key = (dataset, model)
            if key in baseline and key in after:
                b = baseline[key]
                a = after[key]
                dp = a["partial_p"] - b["partial_p"]
                dr = a["partial_r"] - b["partial_r"]
                df1 = a["partial_f1"] - b["partial_f1"]
                md_content += (
                    f"| {dataset.upper()} | {model.upper()} "
                    f"| {b['partial_p']:.3f} | {a['partial_p']:.3f} | {dp:+.3f} "
                    f"| {b['partial_r']:.3f} | {a['partial_r']:.3f} | {dr:+.3f} "
                    f"| {b['partial_f1']:.3f} | {a['partial_f1']:.3f} | {df1:+.3f} |\n"
                )

    md_content += """
## Notes

- **Unified Labels**: Performance measured on Dataset, Method, Task labels only
- **Strict Matching**: Exact span and label match required
- **Partial Matching**: Overlapping span with correct label counts as match
- All metrics calculated after complete unification pipeline

---
*Generated by UnifiedSciERE Performance Analysis*
"""

    # Save markdown file
    md_path = output_dir / f"performance_unified_{split}.md"
    md_path.write_text(md_content)

    return md_path


if __name__ == "__main__":
    # Example: Generate unification report for all datasets
    report_path = generate_unification_report(
        datasets=["scier", "scinlp", "gsap"],
        split="dev",
        models=["scier", "scinlp", "gsap"],
        prefer_larger=True,
    )
    print(f"Generated unification report: {report_path}")
