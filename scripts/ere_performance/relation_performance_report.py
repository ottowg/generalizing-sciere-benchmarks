"""Generate a vanilla RE Partial (relaxed) report for GSAP test on GSAP.

This script evaluates relation extraction performance on the GSAP test split
using gsap-hub's relaxed partial matching. No unification is applied.

Usage:
    python scripts/relation_performance_report.py
"""

from pathlib import Path

import pandas as pd

import gsaphub as gh

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import (
    filter_relations_with_valid_entities,
    mention_to_gsaphub,
    relation_to_gsaphub,
)
from unifiedsciere.unification.pipeline import apply_unification_pipeline


def evaluate_dataset(
    dataset: str,
    split: str = "test",
    trained_on: str | None = None,
    apply_unification: bool = True,
) -> dict[str, object] | None:
    """Evaluate relation extraction for a single dataset.

    Args:
        dataset: Dataset name (gsap, scier, scinlp)
        split: Data split (train, dev, test)
        trained_on: Model trained on (for predictions)
        apply_unification: Whether to run the unification pipeline

    Returns:
        Dict with RE Partial (relaxed partial match) metrics and filter stats,
        or None if missing predictions
    """
    mode_label = "Unified" if apply_unification else "Vanilla"
    print(f"\n=== Evaluating {dataset.upper()} {split} ({mode_label}) ===")

    # Load gold data
    print(f"Loading gold data: {dataset}/{split}")
    gold_corpus = load_corpus(dataset, split, data_type="gold")

    # Load predictions if available
    if trained_on:
        print(
            f"Loading predictions: trained_on={trained_on}, evaluated_on={dataset}/{split}"
        )
        try:
            pred_corpus = load_corpus(
                dataset, split, data_type="predictions", trained_on=trained_on
            )
        except (FileNotFoundError, ValueError) as e:
            print(f"  WARNING: Could not load predictions: {e}")
            return None
    else:
        print("  No predictions specified, skipping evaluation")
        return None

    if apply_unification:
        # Apply unification pipeline on-the-fly
        print("  Applying unification pipeline to gold annotations...")
        gold_corpus, gold_stats = apply_unification_pipeline(
            gold_corpus, dataset, apply_to_gold=True, apply_to_predicted=False
        )

        print("  Applying unification pipeline to predictions...")
        pred_corpus, pred_stats = apply_unification_pipeline(
            pred_corpus, dataset, apply_to_gold=False, apply_to_predicted=True
        )

    # Convert to gsap-hub format
    rels_gold = [
        relation_to_gsaphub(r, idx) for idx, r in enumerate(gold_corpus.relation)
    ]
    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]

    rels_pred = [
        relation_to_gsaphub(r, idx)
        for idx, r in enumerate(pred_corpus.relations_predicted)
    ]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]

    # Filter out relations that reference non-existent entities
    pred_ent_ids = {e["id"] for e in ents_pred}
    original_pred_count = len(rels_pred)
    rels_pred = filter_relations_with_valid_entities(rels_pred, pred_ent_ids)
    filtered_pred_count = original_pred_count - len(rels_pred)
    if filtered_pred_count > 0:
        print(
            f"  Filtered {filtered_pred_count} predicted relations with missing entities"
        )

    # Same for gold relations
    gold_ent_ids = {e["id"] for e in ents_gold}
    original_gold_count = len(rels_gold)
    rels_gold = [
        r
        for r in rels_gold
        if r["subject_id"] in gold_ent_ids and r["object_id"] in gold_ent_ids
    ]
    filtered_gold_count = original_gold_count - len(rels_gold)
    if filtered_gold_count > 0:
        print(f"  Filtered {filtered_gold_count} gold relations with missing entities")

    print(f"  Gold relations: {len(rels_gold)}")
    print(f"  Pred relations: {len(rels_pred)}")
    print(f"  Gold entities: {len(ents_gold)}")
    print(f"  Pred entities: {len(ents_pred)}")

    # Calculate metrics: RE Partial (relaxed partial match) only
    print("  Computing RE Partial (relaxed partial match)...")
    results = gh.evaluate.relations.precision_recall_f1(
        rels_gold,
        ents_gold,
        rels_pred,
        ents_pred,
        re_metrics=[
            gh.evaluate.relations.RelationExtractionMetric.RELAXED_PARTIAL_MATCH
        ],
        score_types=[
            gh.evaluate.relations.ScoreType.F1,
            gh.evaluate.relations.ScoreType.PRECISION,
            gh.evaluate.relations.ScoreType.RECALL,
        ],
        show_counts=True,
    )

    gold_rel_counts = {}
    for rel in rels_gold:
        gold_rel_counts[rel["relation_label"]] = (
            gold_rel_counts.get(rel["relation_label"], 0) + 1
        )
    pred_rel_counts = {}
    for rel in rels_pred:
        pred_rel_counts[rel["relation_label"]] = (
            pred_rel_counts.get(rel["relation_label"], 0) + 1
        )

    return {
        "metrics": results,
        "filtered_pred_relations": filtered_pred_count,
        "filtered_gold_relations": filtered_gold_count,
        "ambiguity_gold": getattr(gold_corpus, "ambiguity_stats_gold", {}),
        "ambiguity_pred": getattr(pred_corpus, "ambiguity_stats_pred", {}),
        "missing_relations_gold": getattr(gold_corpus, "missing_relations_gold", 0),
        "missing_relations_pred": getattr(pred_corpus, "missing_relations_pred", 0),
        "gold_rel_counts": gold_rel_counts,
        "pred_rel_counts": pred_rel_counts,
    }


def _ambiguity_table(stats: dict[tuple[str, str, str, str], int]) -> pd.DataFrame:
    if not stats:
        return pd.DataFrame(
            columns=[
                "selected_label",
                "not_selected_label",
                "relation_label",
                "role",
                "count",
            ]
        )
    rows = [
        {
            "selected_label": k[0],
            "not_selected_label": k[1],
            "relation_label": k[2],
            "role": k[3],
            "count": v,
        }
        for k, v in sorted(stats.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    return pd.DataFrame(rows)


def _get_f1_column(df: pd.DataFrame) -> str:
    def is_f1_col(col) -> bool:
        if isinstance(col, tuple):
            return any("f1" in str(part).lower() for part in col)
        return "f1" in str(col).lower()

    for col in df.columns:
        if is_f1_col(col):
            return col
    raise ValueError(f"F1 column not found in metrics DataFrame: {list(df.columns)}")


def _get_relation_cols(df: pd.DataFrame) -> tuple[object, object]:
    group_col = None
    label_col = None
    for col in df.columns:
        if isinstance(col, tuple):
            if col == ("relation", "group"):
                group_col = col
            if col == ("relation", "label"):
                label_col = col
        else:
            col_str = str(col).lower()
            if col_str == "relation_group":
                group_col = col
            if col_str == "relation_label":
                label_col = col
    if group_col is None or label_col is None:
        raise ValueError("Relation group/label columns not found in metrics DataFrame.")
    return group_col, label_col


def _build_f1_comparison(unified: pd.DataFrame, vanilla: pd.DataFrame) -> pd.DataFrame:
    unified_f1_col = _get_f1_column(unified)
    vanilla_f1_col = _get_f1_column(vanilla)
    unified_group_col, unified_label_col = _get_relation_cols(unified)
    vanilla_group_col, vanilla_label_col = _get_relation_cols(vanilla)

    unified_tbl = unified[[unified_group_col, unified_label_col, unified_f1_col]].copy()
    unified_tbl.columns = ["relation_group", "relation_label", "Unified F1"]

    vanilla_tbl = vanilla[[vanilla_group_col, vanilla_label_col, vanilla_f1_col]].copy()
    vanilla_tbl.columns = ["relation_group", "relation_label", "Vanilla F1"]

    compare = unified_tbl.merge(
        vanilla_tbl, on=["relation_group", "relation_label"], how="outer"
    )
    compare["Delta (Unified - Vanilla)"] = compare["Unified F1"] - compare["Vanilla F1"]
    return compare


def generate_markdown_report(all_results: dict, output_path: Path):
    """Generate a Markdown report from evaluation results."""
    md_parts = [
        "# Relation Extraction Performance Report",
        "",
        "_Unified and vanilla (comparison)_",
        "",
    ]

    for config_key, results in all_results.items():
        md_parts.append(f"## {config_key}")
        md_parts.append("")
        for mode in ("unified", "vanilla"):
            mode_label = "Unified" if mode == "unified" else "Vanilla"
            mode_results = results[mode]
            md_parts.append(f"### {mode_label}")
            md_parts.append("")
            md_parts.append(
                f"- Filtered gold relations (missing mentions): {mode_results['filtered_gold_relations']}"
            )
            md_parts.append(
                f"- Filtered predicted relations (missing mentions): {mode_results['filtered_pred_relations']}"
            )
            md_parts.append(
                f"- Missing gold relations (unmatched spans): {mode_results['missing_relations_gold']}"
            )
            md_parts.append(
                f"- Missing predicted relations (unmatched spans): {mode_results['missing_relations_pred']}"
            )
            md_parts.append("")
            md_parts.append("Metrics: F1, Precision, Recall")
            md_parts.append("")
            metrics_df = mode_results["metrics"].reset_index()
            metrics_df = metrics_df.drop(columns=["index"], errors="ignore")
            drop_cols = [c for c in metrics_df.columns if "count" in str(c).lower()]
            if drop_cols:
                metrics_df = metrics_df.drop(columns=drop_cols)
            renamed = []
            for col in metrics_df.columns:
                if isinstance(col, tuple):
                    renamed.append(col[-1])
                else:
                    renamed.append(str(col))
            metrics_df.columns = renamed
            if "label" in metrics_df.columns:
                metrics_df.insert(
                    metrics_df.columns.get_loc("label") + 1,
                    "gold_relations",
                    metrics_df["label"].map(mode_results["gold_rel_counts"]).fillna(""),
                )
                metrics_df.insert(
                    metrics_df.columns.get_loc("label") + 2,
                    "pred_relations",
                    metrics_df["label"].map(mode_results["pred_rel_counts"]).fillna(""),
                )
            md_parts.append(metrics_df.to_markdown(index=False, floatfmt=".4f"))
            md_parts.append("")

            gold_amb = _ambiguity_table(mode_results["ambiguity_gold"])
            pred_amb = _ambiguity_table(mode_results["ambiguity_pred"])

            md_parts.append(f"### Ambiguity Summary (Gold Relations, {mode_label})")
            md_parts.append("")
            md_parts.append(gold_amb.to_markdown(index=False))
            md_parts.append("")

            md_parts.append(
                f"### Ambiguity Summary (Predicted Relations, {mode_label})"
            )
            md_parts.append("")
            md_parts.append(pred_amb.to_markdown(index=False))
            md_parts.append("")

        md_parts.append("### F1 Comparison (Unified vs Vanilla)")
        md_parts.append("")
        md_parts.append(results["compare"].to_markdown(index=False, floatfmt=".4f"))
        md_parts.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(md_parts))

    print(f"\n✓ Markdown report written to: {output_path}")


def main():
    output_path = Path("reports/ere_performance/relation_performance.md")
    print("=== Relation Extraction Performance Report ===")
    print(f"Output: {output_path}")

    dataset = "gsap-ere"
    split = "test"
    trained_on = "gsap-ere"
    config_key = f"{trained_on.upper()}→{dataset.upper()} ({split})"

    unified = evaluate_dataset(dataset, split, trained_on, apply_unification=True)
    vanilla = evaluate_dataset(dataset, split, trained_on, apply_unification=False)
    if unified is None or vanilla is None:
        print("\nNo results to report. Check that prediction files exist.")
        return

    compare = _build_f1_comparison(unified["metrics"], vanilla["metrics"])
    all_results = {
        config_key: {"unified": unified, "vanilla": vanilla, "compare": compare}
    }

    # Generate Markdown report
    generate_markdown_report(all_results, output_path)

    print("\n=== Report Complete ===")


if __name__ == "__main__":
    main()
