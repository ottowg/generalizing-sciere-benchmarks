"""Baseline results report for in-distribution test sets.

Replicates the baseline results from the original papers for GSAP, SciER, and SciNLP.
Each model is evaluated on the test split of the dataset it was trained on.
No label unification is applied. All metrics use exact (non-partial) span matching.

Metrics:
    NER  — exact span match
    RE   — relaxed match (entity spans exact, relation label must match)
    RE+  — strict match (entity spans + labels exact, relation label must match)

Usage:
    uv run python scripts/ere_performance/reproduce_results_report.py
"""

import json
from typing import Literal

import pandas as pd

import gsaphub as gh
from gsaphub.evaluate.relations import RelationExtractionMetric, ScoreType

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import (
    filter_relations_with_valid_entities,
    mention_to_gsaphub,
    relation_to_gsaphub,
)
from unifiedsciere.paths import project_root
from unifiedsciere.reporting import MarkdownReport

DATASETS: list[Literal["gsap", "scier", "scinlp"]] = ["gsap", "scier", "scinlp"]
SPLIT = "test"
REPORTED_PERFORMANCE_PATH = project_root() / "data" / "reported_performance.json"


def evaluate_ner(gold_corpus, pred_corpus) -> pd.DataFrame:
    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]
    return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=False)


def evaluate_relations(gold_corpus, pred_corpus) -> pd.DataFrame:
    rels_gold = [
        relation_to_gsaphub(r, idx) for idx, r in enumerate(gold_corpus.relation)
    ]
    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]

    rels_pred = [
        relation_to_gsaphub(r, idx)
        for idx, r in enumerate(pred_corpus.relations_predicted)
    ]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]

    rels_gold = filter_relations_with_valid_entities(
        rels_gold, {e["id"] for e in ents_gold}
    )
    rels_pred = filter_relations_with_valid_entities(
        rels_pred, {e["id"] for e in ents_pred}
    )

    return gh.evaluate.relations.precision_recall_f1(
        rels_gold,
        ents_gold,
        rels_pred,
        ents_pred,
        re_metrics=[
            RelationExtractionMetric.RELAXED_MATCH,
            RelationExtractionMetric.STRICT_MATCH,
        ],
        score_types=[ScoreType.PRECISION, ScoreType.RECALL, ScoreType.F1],
        show_counts=False,
    )


def _extract_ner_micro(ner_results: pd.DataFrame) -> dict[str, float]:
    """Extract micro-averaged P, R, F1 from NER results."""
    micro = ner_results[ner_results["label"] == "micro"]
    row = micro.iloc[0]
    p_col = next(c for c in ner_results.columns if "precision" in str(c).lower())
    r_col = next(c for c in ner_results.columns if "recall" in str(c).lower())
    f1_col = next(c for c in ner_results.columns if "f1" in str(c).lower())
    return {
        "precision": float(row[p_col]),
        "recall": float(row[r_col]),
        "f1": float(row[f1_col]),
    }


def _extract_rel_micro(rel_results: pd.DataFrame, metric_name: str) -> dict[str, float]:
    """Extract micro-averaged P, R, F1 for a given RE metric."""
    label_col = ("relation", "label")
    micro = rel_results[rel_results[label_col] == "micro"]
    row = micro.iloc[0]
    return {
        "precision": float(row[(metric_name, "precision")]),
        "recall": float(row[(metric_name, "recall")]),
        "f1": float(row[(metric_name, "f1_score")]),
    }


def _format_ner_per_label(ner_results: pd.DataFrame) -> pd.DataFrame:
    """Format NER per-label results as a clean table."""
    p_col = next(c for c in ner_results.columns if "precision" in str(c).lower())
    r_col = next(c for c in ner_results.columns if "recall" in str(c).lower())
    f1_col = next(c for c in ner_results.columns if "f1" in str(c).lower())
    rows = []
    for _, row in ner_results.iterrows():
        rows.append(
            {
                "Label": row["label"],
                "P": f"{float(row[p_col]) * 100:.1f}",
                "R": f"{float(row[r_col]) * 100:.1f}",
                "F1": f"{float(row[f1_col]) * 100:.1f}",
            }
        )
    return pd.DataFrame(rows)


def _format_rel_per_label(rel_results: pd.DataFrame, metric_name: str) -> pd.DataFrame:
    """Format RE per-label results as a clean table."""
    label_col = ("relation", "label")
    rows = []
    for _, row in rel_results.iterrows():
        rows.append(
            {
                "Label": row[label_col],
                "P": f"{float(row[(metric_name, 'precision')]) * 100:.1f}",
                "R": f"{float(row[(metric_name, 'recall')]) * 100:.1f}",
                "F1": f"{float(row[(metric_name, 'f1_score')]) * 100:.1f}",
            }
        )
    return pd.DataFrame(rows)


def _build_comparison_table(
    summary_rows: list[dict], reported: dict
) -> pd.DataFrame:
    """Compare reproduced micro F1 against paper-reported values."""
    rows = []
    for entry in summary_rows:
        ds = entry["Dataset"].lower()
        rep = reported.get(ds, {})
        for metric in ("NER", "RE", "RE+"):
            repro = float(entry[f"{metric} F1"])
            paper = rep.get(metric)
            delta = f"{repro - paper:+.2f}" if paper is not None else "N/A"
            paper_str = f"{paper:.2f}" if paper is not None else "N/A"
            rows.append(
                {
                    "Dataset": entry["Dataset"],
                    "Metric": metric,
                    "Reproduced F1": f"{repro:.1f}",
                    "Reported F1": paper_str,
                    "Δ (repro − paper)": delta,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    reported = json.loads(REPORTED_PERFORMANCE_PATH.read_text())

    # First pass: collect data
    summary_rows = []
    detail_data = []

    for dataset in DATASETS:
        print(f"\n--- {dataset.upper()} ---")
        gold_corpus = load_corpus(dataset, SPLIT, data_type="gold")
        pred_corpus = load_corpus(
            dataset, SPLIT, data_type="predictions", trained_on=dataset
        )

        ner_results = evaluate_ner(gold_corpus, pred_corpus)
        ner_micro = _extract_ner_micro(ner_results)

        rel_results = evaluate_relations(gold_corpus, pred_corpus)
        re_micro = _extract_rel_micro(rel_results, "RE")
        re_plus_micro = _extract_rel_micro(rel_results, "RE+")

        summary_rows.append(
            {
                "Dataset": dataset.upper(),
                "NER P": f"{ner_micro['precision'] * 100:.1f}",
                "NER R": f"{ner_micro['recall'] * 100:.1f}",
                "NER F1": f"{ner_micro['f1'] * 100:.1f}",
                "RE P": f"{re_micro['precision'] * 100:.1f}",
                "RE R": f"{re_micro['recall'] * 100:.1f}",
                "RE F1": f"{re_micro['f1'] * 100:.1f}",
                "RE+ P": f"{re_plus_micro['precision'] * 100:.1f}",
                "RE+ R": f"{re_plus_micro['recall'] * 100:.1f}",
                "RE+ F1": f"{re_plus_micro['f1'] * 100:.1f}",
            }
        )

        print(f"  NER F1: {ner_micro['f1'] * 100:.1f}")
        print(f"  RE  F1: {re_micro['f1'] * 100:.1f}")
        print(f"  RE+ F1: {re_plus_micro['f1'] * 100:.1f}")

        detail_data.append(
            (
                dataset,
                _format_ner_per_label(ner_results),
                _format_rel_per_label(rel_results, "RE"),
                _format_rel_per_label(rel_results, "RE+"),
            )
        )

    # Build report: summary first, then per-dataset details
    report = MarkdownReport("Baseline Results Report")
    report.text(
        "This report replicates the baseline results from the original papers for each "
        "of the three datasets: GSAP, SciER, and SciNLP. Each model is evaluated on the "
        "test split of the same dataset it was trained on (in-distribution evaluation), "
        "matching the experimental setup described in the respective publications.\n\n"
        "No label unification is applied. All metrics use exact span matching (no partial credit)."
    )

    report.heading("Summary (micro-averaged, exact span match)", level=2)
    report.text(
        f"_Micro-averaged precision, recall, and F1 for NER (exact span match), "
        f"RE (relaxed match), and RE+ (strict match) on the {SPLIT} split. "
        f"Each model is evaluated on the dataset it was trained on._"
    )
    report.table(pd.DataFrame(summary_rows))

    report.heading("Comparison with Paper-Reported Results", level=2)
    report.text(
        "_Difference between reproduced F1 scores and the micro-averaged F1 values "
        "reported in the original publications. Reported values are sourced from "
        f"`data/reported_performance.json`. "
        f"A positive Δ means the reproduction exceeds the paper result._"
    )
    comparison_table = _build_comparison_table(summary_rows, reported)
    report.table(comparison_table)

    for dataset, ner_table, re_table, re_plus_table in detail_data:
        report.heading(dataset.upper(), level=2)
        report.heading("NER (exact match)", level=3)
        report.text(
            f"_Per-label NER precision, recall, and F1 for the {dataset.upper()} model "
            f"on the {dataset.upper()} {SPLIT} split. Exact span matching._"
        )
        report.table(ner_table)
        report.heading("RE (relaxed match, exact entities)", level=3)
        report.text(
            f"_Per-label RE precision, recall, and F1 for the {dataset.upper()} model "
            f"on the {dataset.upper()} {SPLIT} split. "
            f"Relation counted as correct if entity spans match exactly and relation label matches "
            f"(entity label not required to match)._"
        )
        report.table(re_table)
        report.heading("RE+ (strict match, exact entities)", level=3)
        report.text(
            f"_Per-label RE+ precision, recall, and F1 for the {dataset.upper()} model "
            f"on the {dataset.upper()} {SPLIT} split. "
            f"Relation counted as correct if entity spans and entity labels match exactly and "
            f"relation label matches._"
        )
        report.table(re_plus_table)

    report.write("reports/ere_performance/reproduce_results/baseline_results.md")


if __name__ == "__main__":
    main()
