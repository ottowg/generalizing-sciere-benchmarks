"""MultiSciERE results report — in-distribution evaluation (no unification).

Each dataset is evaluated using the multi-sciere prediction variant whose label
space matches that dataset's native labels:
    gsap-ere  → multi-sciere-gsap
    scier     → multi-sciere-scier
    scinlp    → multi-sciere-scinlp

The first summary table (comparison with paper results) uses original labels only.
All other tables (micro-averaged P/R/F1, entities, relations) include both the
original and unified label sets.  Paper-reported baseline numbers are read from
data/reported_performance.json for direct comparison.

Metrics:
    NER  — exact and partial span match
    RE   — relaxed match (entity spans exact, relation label must match)
    RE+  — strict match (entity spans + labels exact, relation label must match)

Outputs:
    data/multi_sciere_results.json

Usage:
    uv run python scripts/ere_performance/multi_sciere_results_report.py
"""

import json
from datetime import datetime, timezone
from typing import Literal

import gsaphub as gh
import pandas as pd
from gsaphub.evaluate.relations import RelationExtractionMetric, ScoreType

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import (
    filter_relations_with_valid_entities,
    mention_to_gsaphub,
    relation_to_gsaphub,
)
from unifiedsciere.paths import project_root
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["gsap-ere", "scier", "scinlp"]] = ["gsap-ere", "scier", "scinlp"]
SPLIT = "test"
REPORTED_PERFORMANCE_PATH = project_root() / "data" / "reported_performance.json"
JSON_OUTPUT_PATH = project_root() / "data" / "multi_sciere_results.json"

PRED_LABEL_SETS = ["gsap", "scier", "scinlp"]

# For each test dataset, use the matching multi-sciere prediction label space.
DATASET_TO_PRED_LS: dict[str, str] = {
    "gsap-ere": "gsap",
    "scier": "scier",
    "scinlp": "scinlp",
}

# Map pred label space back to the dataset key expected by apply_unification_pipeline.
PRED_LS_TO_DATASET: dict[str, Literal["gsap-ere", "scier", "scinlp"]] = {
    "gsap": "gsap-ere",
    "scier": "scier",
    "scinlp": "scinlp",
}

SYMMETRIC_RELATIONS = [
    "coreference",
    "Synonym-Of",
    "similarWith",
    "isComparedTo",
    "compareWith",
    "Compare-With",
]


def evaluate_ner(gold_corpus, pred_corpus, partial: bool = False) -> pd.DataFrame:
    ents_gold = [mention_to_gsaphub(m) for m in gold_corpus.mentions]
    ents_pred = [mention_to_gsaphub(m) for m in pred_corpus.mentions_predicted]
    return gh.evaluate.entities.precision_recall_f1(
        ents_gold, ents_pred, partial=partial
    )


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

    rels_gold = filter_relations_with_valid_entities(
        rels_gold, {e["id"] for e in ents_gold}
    )
    rels_pred = filter_relations_with_valid_entities(
        rels_pred, {e["id"] for e in ents_pred}
    )

    gh.transform.relations.unify_undirected(rels_gold, ents_gold, SYMMETRIC_RELATIONS)
    gh.transform.relations.unify_undirected(rels_pred, ents_pred, SYMMETRIC_RELATIONS)

    return gh.evaluate.relations.precision_recall_f1(
        rels_gold,
        ents_gold,
        rels_pred,
        ents_pred,
        re_metrics=[
            RelationExtractionMetric.RELAXED_MATCH,
            RelationExtractionMetric.RELAXED_PARTIAL_MATCH,
            RelationExtractionMetric.STRICT_MATCH,
            RelationExtractionMetric.STRICT_PARTIAL_MATCH,
        ],
        score_types=[ScoreType.PRECISION, ScoreType.RECALL, ScoreType.F1],
        show_counts=False,
    )


def _extract_ner_micro(ner_results: pd.DataFrame) -> dict[str, float]:
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
    label_col = ("relation", "label")
    micro = rel_results[rel_results[label_col] == "micro"]
    row = micro.iloc[0]
    return {
        "precision": float(row[("precision", metric_name)]),
        "recall": float(row[("recall", metric_name)]),
        "f1": float(row[("f1_score", metric_name)]),
    }


AGGREGATE_LABELS = {"micro", "macro", "weighted"}


def _ner_label_rows(ner_results, dataset, label_set, match) -> list[dict]:
    p_col = next(c for c in ner_results.columns if "precision" in str(c).lower())
    r_col = next(c for c in ner_results.columns if "recall" in str(c).lower())
    f1_col = next(c for c in ner_results.columns if "f1" in str(c).lower())
    return [
        {
            "dataset": dataset,
            "label_set": label_set,
            "task": "ner",
            "match": match,
            "label": row["label"],
            "aggregate": row["label"] in AGGREGATE_LABELS,
            "precision": round(float(row[p_col]) * 100, 1),
            "recall": round(float(row[r_col]) * 100, 1),
            "f1": round(float(row[f1_col]) * 100, 1),
        }
        for _, row in ner_results.iterrows()
    ]


def _re_label_rows(rel_results, dataset, label_set, metric_name, match) -> list[dict]:
    label_col = ("relation", "label")
    return [
        {
            "dataset": dataset,
            "label_set": label_set,
            "task": "re",
            "match": match,
            "label": row[label_col],
            "aggregate": row[label_col] in AGGREGATE_LABELS,
            "precision": round(float(row[("precision", metric_name)]) * 100, 1),
            "recall": round(float(row[("recall", metric_name)]) * 100, 1),
            "f1": round(float(row[("f1_score", metric_name)]) * 100, 1),
        }
        for _, row in rel_results.iterrows()
    ]


def _run_eval(dataset: str, pred_label_set: str, label_set: str) -> tuple:
    trained_on = f"multi-sciere-{pred_label_set}"

    unify_pred_as = PRED_LS_TO_DATASET[pred_label_set]

    gold = load_corpus(dataset, SPLIT, data_type="gold")
    pred = load_corpus(dataset, SPLIT, data_type="predictions", trained_on=trained_on)

    if label_set == "unified":
        gold, _ = apply_unification_pipeline(
            gold, dataset, apply_to_gold=True, apply_to_predicted=False
        )
        pred, _ = apply_unification_pipeline(
            pred, unify_pred_as, apply_to_gold=False, apply_to_predicted=True
        )

    ner_exact = evaluate_ner(gold, pred, partial=False)
    ner_partial = evaluate_ner(gold, pred, partial=True)
    rel_results = evaluate_relations(gold, pred)
    return ner_exact, ner_partial, rel_results


def _append_results(
    json_summary: list,
    json_labels: list,
    ner_exact,
    ner_partial,
    rel_results,
    dataset: str,
    label_set: str,
    trained_on: str,
) -> None:
    ne = _extract_ner_micro(ner_exact)
    np_ = _extract_ner_micro(ner_partial)
    re = _extract_rel_micro(rel_results, "RE")
    rep_ = _extract_rel_micro(rel_results, "RE partial")
    res = _extract_rel_micro(rel_results, "RE+")
    reps = _extract_rel_micro(rel_results, "RE+ partial")

    print(f"  NER exact F1:   {ne['f1'] * 100:.1f}")
    print(f"  NER partial F1: {np_['f1'] * 100:.1f}")
    print(f"  RE  F1:         {re['f1'] * 100:.1f}")
    print(f"  RE≈ F1:         {rep_['f1'] * 100:.1f}")
    print(f"  RE+ F1:         {res['f1'] * 100:.1f}")
    print(f"  RE+≈ F1:        {reps['f1'] * 100:.1f}")

    json_summary.append(
        {
            "dataset": dataset,
            "label_set": label_set,
            "trained_on": trained_on,
            "ner_exact_precision": round(ne["precision"] * 100, 1),
            "ner_exact_recall": round(ne["recall"] * 100, 1),
            "ner_exact_f1": round(ne["f1"] * 100, 1),
            "ner_partial_precision": round(np_["precision"] * 100, 1),
            "ner_partial_recall": round(np_["recall"] * 100, 1),
            "ner_partial_f1": round(np_["f1"] * 100, 1),
            "re_relaxed_precision": round(re["precision"] * 100, 1),
            "re_relaxed_recall": round(re["recall"] * 100, 1),
            "re_relaxed_f1": round(re["f1"] * 100, 1),
            "re_relaxed_partial_precision": round(rep_["precision"] * 100, 1),
            "re_relaxed_partial_recall": round(rep_["recall"] * 100, 1),
            "re_relaxed_partial_f1": round(rep_["f1"] * 100, 1),
            "re_strict_precision": round(res["precision"] * 100, 1),
            "re_strict_recall": round(res["recall"] * 100, 1),
            "re_strict_f1": round(res["f1"] * 100, 1),
            "re_strict_partial_precision": round(reps["precision"] * 100, 1),
            "re_strict_partial_recall": round(reps["recall"] * 100, 1),
            "re_strict_partial_f1": round(reps["f1"] * 100, 1),
        }
    )
    json_labels.extend(_ner_label_rows(ner_exact, dataset, label_set, "exact"))
    json_labels.extend(_ner_label_rows(ner_partial, dataset, label_set, "partial"))
    json_labels.extend(_re_label_rows(rel_results, dataset, label_set, "RE", "relaxed"))
    json_labels.extend(
        _re_label_rows(rel_results, dataset, label_set, "RE partial", "relaxed_partial")
    )
    json_labels.extend(_re_label_rows(rel_results, dataset, label_set, "RE+", "strict"))
    json_labels.extend(
        _re_label_rows(rel_results, dataset, label_set, "RE+ partial", "strict_partial")
    )


def main() -> None:
    reported = json.loads(REPORTED_PERFORMANCE_PATH.read_text())

    json_summary: list[dict] = []
    json_labels: list[dict] = []

    # original: only the matching pred_label_set per dataset (no unification)
    print("\n=== original label set (matching pred) ===")
    for dataset in DATASETS:
        pred_label_set = DATASET_TO_PRED_LS[dataset]
        trained_on = f"multi-sciere-{pred_label_set}"
        print(f"\n--- {dataset.upper()} [original] ({trained_on}) ---")
        ner_exact, ner_partial, rel_results = _run_eval(
            dataset, pred_label_set, "original"
        )
        _append_results(
            json_summary,
            json_labels,
            ner_exact,
            ner_partial,
            rel_results,
            dataset,
            "original",
            trained_on,
        )

    # unified: all 9 combinations (test_dataset × pred_label_set)
    print("\n=== unified label set (all combinations) ===")
    for dataset in DATASETS:
        for pred_label_set in PRED_LABEL_SETS:
            trained_on = f"multi-sciere-{pred_label_set}"
            print(f"\n--- {dataset.upper()} [unified] ({trained_on}) ---")
            ner_exact, ner_partial, rel_results = _run_eval(
                dataset, pred_label_set, "unified"
            )
            _append_results(
                json_summary,
                json_labels,
                ner_exact,
                ner_partial,
                rel_results,
                dataset,
                "unified",
                trained_on,
            )

    JSON_OUTPUT_PATH.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": json_summary,
                "labels": json_labels,
                "reported": reported,
            },
            indent=2,
        )
    )
    print(f"\nWrote JSON to {JSON_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
