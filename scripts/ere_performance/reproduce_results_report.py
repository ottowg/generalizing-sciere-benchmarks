"""Baseline results report for in-distribution test sets.

Replicates the baseline results from the original papers for GSAP, SciER, and SciNLP.
Each model is evaluated on the test split of the dataset it was trained on.
Evaluations are run for both raw and unified label sets, with exact and partial NER matching.

If seeded prediction files exist (integer-named subdirectories inside the prediction
directory), mean and standard deviation are computed across seeds.

Metrics:
    NER  — exact and partial span match
    RE   — relaxed match (entity spans exact, relation label must match)
    RE+  — strict match (entity spans + labels exact, relation label must match)

Outputs:
    data/reproduce_results.json                    — structured data for the webapp
    reports/reproduce_results/baseline_results.md  — markdown report (raw, exact only)

Usage:
    uv run python scripts/ere_performance/reproduce_results_report.py
"""

import json
import statistics
from datetime import datetime, timezone
from typing import Literal

import gsaphub as gh
import pandas as pd
from gsaphub.evaluate.relations import RelationExtractionMetric, ScoreType

from unifiedsciere.data_loader import discover_seeds, load_corpus
from unifiedsciere.evaluate import (
    filter_relations_with_valid_entities,
    mention_to_gsaphub,
    relation_to_gsaphub,
)
from unifiedsciere.paths import project_root
from unifiedsciere.reporting import MarkdownReport
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["gsap-ere", "scier", "scinlp"]] = ["gsap-ere", "scier", "scinlp"]
SPLIT = "test"
REPORTED_PERFORMANCE_PATH = project_root() / "data" / "webapp" / "static" / "reported_performance.json"
JSON_OUTPUT_PATH = project_root() / "data" / "webapp" / "reproduce_results.json"

F1_KEYS = [
    "ner_exact_f1", "ner_partial_f1",
    "re_relaxed_f1", "re_relaxed_partial_f1",
    "re_strict_f1", "re_strict_partial_f1",
]

SYMMETRIC_RELATIONS = [
    "coreference", "Synonym-Of", "similarWith", "isComparedTo",
    "compareWith", "Compare-With",
]


def evaluate_ner(gold_corpus, pred_corpus, partial: bool = False) -> pd.DataFrame:
    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]
    return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=partial)


def evaluate_relations(gold_corpus, pred_corpus) -> pd.DataFrame:
    rels_gold = [
        relation_to_gsaphub(r, idx, annotator="gold")
        for idx, r in enumerate(gold_corpus.relation)
    ]
    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]
    rels_pred = [
        relation_to_gsaphub(r, idx, annotator="pred")
        for idx, r in enumerate(pred_corpus.relations_predicted)
    ]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]

    rels_gold = filter_relations_with_valid_entities(rels_gold, {e["id"] for e in ents_gold})
    rels_pred = filter_relations_with_valid_entities(rels_pred, {e["id"] for e in ents_pred})

    gh.transform.relations.unify_undirected(rels_gold, ents_gold, SYMMETRIC_RELATIONS)
    gh.transform.relations.unify_undirected(rels_pred, ents_pred, SYMMETRIC_RELATIONS)

    return gh.evaluate.relations.precision_recall_f1(
        rels_gold, ents_gold, rels_pred, ents_pred,
        re_metrics=[
            RelationExtractionMetric.RELAXED_MATCH,
            RelationExtractionMetric.RELAXED_PARTIAL_MATCH,
            RelationExtractionMetric.STRICT_MATCH,
            RelationExtractionMetric.STRICT_PARTIAL_MATCH,
        ],
        score_types=[ScoreType.PRECISION, ScoreType.RECALL, ScoreType.F1],
        show_counts=False,
    )


def _run_eval(dataset: str, label_set: str, seed=None):
    gold = load_corpus(dataset, SPLIT, data_type="gold")
    pred = load_corpus(dataset, SPLIT, data_type="predictions", trained_on=dataset, seed=seed)
    if label_set == "unified":
        gold, _ = apply_unification_pipeline(gold, dataset, apply_to_gold=True,  apply_to_predicted=False)
        pred, _ = apply_unification_pipeline(pred, dataset, apply_to_gold=False, apply_to_predicted=True)
    return evaluate_ner(gold, pred, False), evaluate_ner(gold, pred, True), evaluate_relations(gold, pred)


# ── extraction helpers ────────────────────────────────────────────────────────

def _extract_ner_micro(ner_results: pd.DataFrame) -> dict[str, float]:
    micro = ner_results[ner_results["label"] == "micro"]
    row   = micro.iloc[0]
    p_col  = next(c for c in ner_results.columns if "precision" in str(c).lower())
    r_col  = next(c for c in ner_results.columns if "recall"    in str(c).lower())
    f1_col = next(c for c in ner_results.columns if "f1"        in str(c).lower())
    return {"precision": float(row[p_col]), "recall": float(row[r_col]), "f1": float(row[f1_col])}


def _extract_rel_micro(rel_results: pd.DataFrame, metric_name: str) -> dict[str, float]:
    label_col = ("relation", "label")
    micro = rel_results[rel_results[label_col] == "micro"]
    row   = micro.iloc[0]
    return {
        "precision": float(row[("precision", metric_name)]),
        "recall":    float(row[("recall",    metric_name)]),
        "f1":        float(row[("f1_score",  metric_name)]),
    }


def _extract_all_metrics(ner_exact, ner_partial, rel_results) -> dict[str, float]:
    """All micro-averaged metrics, values ×100 rounded to 1 dp."""
    ne   = _extract_ner_micro(ner_exact)
    np_  = _extract_ner_micro(ner_partial)
    re   = _extract_rel_micro(rel_results, "RE")
    rep_ = _extract_rel_micro(rel_results, "RE partial")
    res  = _extract_rel_micro(rel_results, "RE+")
    reps = _extract_rel_micro(rel_results, "RE+ partial")
    return {
        "ner_exact_precision":          round(ne["precision"]   * 100, 1),
        "ner_exact_recall":             round(ne["recall"]      * 100, 1),
        "ner_exact_f1":                 round(ne["f1"]          * 100, 1),
        "ner_partial_precision":        round(np_["precision"]  * 100, 1),
        "ner_partial_recall":           round(np_["recall"]     * 100, 1),
        "ner_partial_f1":               round(np_["f1"]         * 100, 1),
        "re_relaxed_precision":         round(re["precision"]   * 100, 1),
        "re_relaxed_recall":            round(re["recall"]      * 100, 1),
        "re_relaxed_f1":                round(re["f1"]          * 100, 1),
        "re_relaxed_partial_precision": round(rep_["precision"] * 100, 1),
        "re_relaxed_partial_recall":    round(rep_["recall"]    * 100, 1),
        "re_relaxed_partial_f1":        round(rep_["f1"]        * 100, 1),
        "re_strict_precision":          round(res["precision"]  * 100, 1),
        "re_strict_recall":             round(res["recall"]     * 100, 1),
        "re_strict_f1":                 round(res["f1"]         * 100, 1),
        "re_strict_partial_precision":  round(reps["precision"] * 100, 1),
        "re_strict_partial_recall":     round(reps["recall"]    * 100, 1),
        "re_strict_partial_f1":         round(reps["f1"]        * 100, 1),
    }


def _format_ner_per_label(ner_results: pd.DataFrame) -> pd.DataFrame:
    p_col  = next(c for c in ner_results.columns if "precision" in str(c).lower())
    r_col  = next(c for c in ner_results.columns if "recall"    in str(c).lower())
    f1_col = next(c for c in ner_results.columns if "f1"        in str(c).lower())
    return pd.DataFrame([
        {"Label": row["label"],
         "P":  f"{float(row[p_col])  * 100:.1f}",
         "R":  f"{float(row[r_col])  * 100:.1f}",
         "F1": f"{float(row[f1_col]) * 100:.1f}"}
        for _, row in ner_results.iterrows()
    ])


def _format_rel_per_label(rel_results: pd.DataFrame, metric_name: str) -> pd.DataFrame:
    label_col = ("relation", "label")
    return pd.DataFrame([
        {"Label": row[label_col],
         "P":  f"{float(row[('precision', metric_name)]) * 100:.1f}",
         "R":  f"{float(row[('recall',    metric_name)]) * 100:.1f}",
         "F1": f"{float(row[('f1_score',  metric_name)]) * 100:.1f}"}
        for _, row in rel_results.iterrows()
    ])


def _build_comparison_table(summary_rows: list[dict], reported: dict) -> pd.DataFrame:
    rows = []
    for entry in summary_rows:
        ds  = entry["Dataset"].lower()
        rep = reported.get(ds, {})
        for metric in ("NER", "RE", "RE+"):
            repro = float(entry[f"{metric} F1"])
            paper = rep.get(metric)
            rows.append({
                "Dataset":           entry["Dataset"],
                "Metric":            metric,
                "Reproduced F1":     f"{repro:.1f}",
                "Reported F1":       f"{paper:.2f}" if paper is not None else "N/A",
                "Δ (repro − paper)": f"{repro - paper:+.2f}" if paper is not None else "N/A",
            })
    return pd.DataFrame(rows)


# ── JSON helpers ──────────────────────────────────────────────────────────────

AGGREGATE_LABELS = {"micro", "macro", "weighted"}


def _ner_label_rows(ner_results, dataset, label_set, match) -> list[dict]:
    p_col  = next(c for c in ner_results.columns if "precision" in str(c).lower())
    r_col  = next(c for c in ner_results.columns if "recall"    in str(c).lower())
    f1_col = next(c for c in ner_results.columns if "f1"        in str(c).lower())
    return [
        {"dataset": dataset, "label_set": label_set, "task": "ner", "match": match,
         "label": row["label"],
         "aggregate": row["label"] in AGGREGATE_LABELS,
         "precision": round(float(row[p_col])  * 100, 1),
         "recall":    round(float(row[r_col])  * 100, 1),
         "f1":        round(float(row[f1_col]) * 100, 1)}
        for _, row in ner_results.iterrows()
    ]


def _re_label_rows(rel_results, dataset, label_set, metric_name, match) -> list[dict]:
    label_col = ("relation", "label")
    return [
        {"dataset": dataset, "label_set": label_set, "task": "re", "match": match,
         "label": row[label_col],
         "aggregate": row[label_col] in AGGREGATE_LABELS,
         "precision": round(float(row[("precision", metric_name)]) * 100, 1),
         "recall":    round(float(row[("recall",    metric_name)]) * 100, 1),
         "f1":        round(float(row[("f1_score",  metric_name)]) * 100, 1)}
        for _, row in rel_results.iterrows()
    ]


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    reported = json.loads(REPORTED_PERFORMANCE_PATH.read_text())

    md_summary_rows = []
    md_detail_data  = []
    json_summary    = []
    json_labels     = []

    for label_set in ("original", "unified"):
        for dataset in DATASETS:
            print(f"\n--- {dataset.upper()} [{label_set}] ---")
            seeds = discover_seeds(dataset, dataset)

            if seeds:
                print(f"  seeds: {seeds}")
                seed_results = []
                for seed in seeds:
                    print(f"  seed {seed} ...", end=" ", flush=True)
                    try:
                        ner_e, ner_p, rel = _run_eval(dataset, label_set, seed=seed)
                        m = _extract_all_metrics(ner_e, ner_p, rel)
                        seed_results.append((ner_e, ner_p, rel, m))
                        print(f"NER={m['ner_exact_f1']}  RE={m['re_relaxed_f1']}  RE+={m['re_strict_f1']}")
                    except FileNotFoundError as exc:
                        print(f"not found ({exc})")

                if seed_results:
                    all_keys = list(seed_results[0][3].keys())
                    metrics = {k: round(statistics.mean(sr[3][k] for sr in seed_results), 1)
                               for k in all_keys}
                    if len(seed_results) > 1:
                        for fk in F1_KEYS:
                            vals = [sr[3][fk] for sr in seed_results]
                            metrics[f"{fk}_std"] = round(statistics.stdev(vals), 2)
                    ner_exact, ner_partial, rel_results = seed_results[-1][:3]
                    print(f"  mean NER exact F1:  {metrics['ner_exact_f1']}  (n={len(seed_results)} seeds)")
                    print(f"  mean RE  F1:        {metrics['re_relaxed_f1']}")
                    print(f"  mean RE+ F1:        {metrics['re_strict_f1']}")
                else:
                    seeds = []  # all seeds failed — fall through to single run

            if not seeds:
                ner_exact, ner_partial, rel_results = _run_eval(dataset, label_set)
                metrics = _extract_all_metrics(ner_exact, ner_partial, rel_results)
                print(f"  NER exact F1:   {metrics['ner_exact_f1']}")
                print(f"  NER partial F1: {metrics['ner_partial_f1']}")
                print(f"  RE  F1:         {metrics['re_relaxed_f1']}")
                print(f"  RE+ F1:         {metrics['re_strict_f1']}")

            json_summary.append({"dataset": dataset, "label_set": label_set, **metrics})
            json_labels.extend(_ner_label_rows(ner_exact,   dataset, label_set, "exact"))
            json_labels.extend(_ner_label_rows(ner_partial, dataset, label_set, "partial"))
            json_labels.extend(_re_label_rows(rel_results,  dataset, label_set, "RE",          "relaxed"))
            json_labels.extend(_re_label_rows(rel_results,  dataset, label_set, "RE partial",  "relaxed_partial"))
            json_labels.extend(_re_label_rows(rel_results,  dataset, label_set, "RE+",         "strict"))
            json_labels.extend(_re_label_rows(rel_results,  dataset, label_set, "RE+ partial", "strict_partial"))

            if label_set == "original":
                md_summary_rows.append({
                    "Dataset": dataset.upper(),
                    "NER P":  f"{metrics['ner_exact_precision']:.1f}",
                    "NER R":  f"{metrics['ner_exact_recall']:.1f}",
                    "NER F1": f"{metrics['ner_exact_f1']:.1f}",
                    "RE P":   f"{metrics['re_relaxed_precision']:.1f}",
                    "RE R":   f"{metrics['re_relaxed_recall']:.1f}",
                    "RE F1":  f"{metrics['re_relaxed_f1']:.1f}",
                    "RE+ P":  f"{metrics['re_strict_precision']:.1f}",
                    "RE+ R":  f"{metrics['re_strict_recall']:.1f}",
                    "RE+ F1": f"{metrics['re_strict_f1']:.1f}",
                })
                md_detail_data.append((
                    dataset,
                    _format_ner_per_label(ner_exact),
                    _format_rel_per_label(rel_results, "RE"),
                    _format_rel_per_label(rel_results, "RE+"),
                ))

    # ── write JSON ──────────────────────────────────────────────────────────
    JSON_OUTPUT_PATH.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary":      json_summary,
        "labels":       json_labels,
        "reported":     reported,
    }, indent=2))
    print(f"\nWrote JSON to {JSON_OUTPUT_PATH}")

    # ── write markdown (raw + exact only) ───────────────────────────────────
    report = MarkdownReport("Baseline Results Report")
    report.text(
        "Replicates baseline results from the original papers. Each model is evaluated on "
        "the test split of the dataset it was trained on (in-distribution). "
        "No label unification applied. All metrics use exact span matching."
    )
    report.heading("Summary", level=2)
    report.table(pd.DataFrame(md_summary_rows))
    report.heading("Comparison with Paper-Reported Results", level=2)
    report.table(_build_comparison_table(md_summary_rows, reported))
    for dataset, ner_table, re_table, re_plus_table in md_detail_data:
        report.heading(dataset.upper(), level=2)
        report.heading("NER (exact match)", level=3)
        report.table(ner_table)
        report.heading("RE (relaxed match)", level=3)
        report.table(re_table)
        report.heading("RE+ (strict match)", level=3)
        report.table(re_plus_table)
    report.write("reports/reproduce_results/baseline_results.md")


if __name__ == "__main__":
    main()
