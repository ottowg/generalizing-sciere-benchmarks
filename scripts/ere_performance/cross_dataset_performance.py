"""Cross-dataset entity and relation performance overview.

Evaluates all train→test dataset pairs (unified label space) and emits
data/cross_dataset_performance.json for the webapp.

JSON structure:
  {
    "generated_at": "ISO8601",
    "summary": [
      { "train_ds", "test_ds", "split",
        "ner_exact_f1", "ner_partial_f1",
        "re_relaxed_f1", "re_relaxed_partial_f1",
        "re_strict_f1", "re_strict_partial_f1" }
    ],
    "entity_labels": [
      { "train_ds", "test_ds", "split", "match", "label",
        "precision", "recall", "f1", "aggregate" }
    ],
    "relation_labels": [
      { "train_ds", "test_ds", "split", "match", "label",
        "precision", "recall", "f1", "aggregate" }
    ]
  }

Usage:
    uv run python scripts/ere_performance/cross_dataset_performance.py
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
from unifiedsciere.paths import ensure_output, project_root
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["gsap-ere", "scier", "scinlp"]] = ["gsap-ere", "scier", "scinlp"]
TRAIN_DATASETS = [*DATASETS, "unified-sciere"]
SPLITS = ["dev", "test"]
AGGREGATE_LABELS = {"micro", "macro", "weighted"}

SYMMETRIC_RELATIONS = [
    "coreference", "Synonym-Of", "similarWith", "isComparedTo",
    "compareWith", "Compare-With",
]


# ── data loading ──────────────────────────────────────────────────────────────

def _load_unified_pair(train_ds: str, test_ds: str, split: str):
    gold = load_corpus(test_ds, split, data_type="gold")
    pred = load_corpus(test_ds, split, data_type="predictions", trained_on=train_ds)
    gold, _ = apply_unification_pipeline(gold, test_ds,  apply_to_gold=True,  apply_to_predicted=False)
    pred, _ = apply_unification_pipeline(pred, train_ds, apply_to_gold=False, apply_to_predicted=True)
    return gold, pred


# ── evaluation ────────────────────────────────────────────────────────────────

def _evaluate_ner(gold, pred, partial: bool) -> pd.DataFrame:
    ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]
    ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]
    return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=partial)


def _evaluate_re(gold, pred) -> pd.DataFrame:
    ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]
    ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]
    rels_gold = [relation_to_gsaphub(r, i, "gold") for i, r in enumerate(gold.relation)]
    rels_pred = [relation_to_gsaphub(r, i, "pred") for i, r in enumerate(pred.relations_predicted)]
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


def evaluate_pair(train_ds: str, test_ds: str, split: str):
    """Returns (ner_exact_df, ner_partial_df, re_df) — any may be None on failure."""
    try:
        gold, pred = _load_unified_pair(train_ds, test_ds, split)
    except Exception as e:
        print(f"  SKIP load {train_ds}→{test_ds} [{split}]: {e}")
        return None, None, None

    try:
        ner_exact   = _evaluate_ner(gold, pred, partial=False)
        ner_partial = _evaluate_ner(gold, pred, partial=True)
    except Exception as e:
        print(f"  SKIP NER {train_ds}→{test_ds} [{split}]: {e}")
        ner_exact = ner_partial = None

    try:
        re_results = _evaluate_re(gold, pred)
    except Exception as e:
        print(f"  SKIP RE {train_ds}→{test_ds} [{split}]: {e}")
        re_results = None

    return ner_exact, ner_partial, re_results


# ── row builders ──────────────────────────────────────────────────────────────

def _ner_micro_f1(df: pd.DataFrame) -> float | None:
    if df is None:
        return None
    f1_col = next(c for c in df.columns if "f1" in str(c).lower())
    micro  = df[df["label"] == "micro"]
    return round(float(micro.iloc[0][f1_col]) * 100, 1) if not micro.empty else None


def _re_micro_f1(df: pd.DataFrame, metric: str) -> float | None:
    if df is None:
        return None
    label_col = ("relation", "label")
    micro = df[df[label_col] == "micro"]
    # Column orientation: (score_type, metric) when len(re_metrics) > len(score_types)
    return round(float(micro.iloc[0][("f1_score", metric)]) * 100, 1) if not micro.empty else None


def _ner_label_rows(df: pd.DataFrame, train_ds, test_ds, split, match) -> list[dict]:
    p_col  = next(c for c in df.columns if "precision" in str(c).lower())
    r_col  = next(c for c in df.columns if "recall"    in str(c).lower())
    f1_col = next(c for c in df.columns if "f1"        in str(c).lower())
    return [
        {
            "train_ds": train_ds, "test_ds": test_ds, "split": split, "match": match,
            "label":     row["label"],
            "precision": round(float(row[p_col])  * 100, 1),
            "recall":    round(float(row[r_col])  * 100, 1),
            "f1":        round(float(row[f1_col]) * 100, 1),
            "aggregate": row["label"] in AGGREGATE_LABELS,
        }
        for _, row in df.iterrows()
    ]


def _re_label_rows(df: pd.DataFrame, train_ds, test_ds, split, match, metric) -> list[dict]:
    label_col = ("relation", "label")
    # Column orientation: (score_type, metric) when len(re_metrics) > len(score_types)
    return [
        {
            "train_ds": train_ds, "test_ds": test_ds, "split": split, "match": match,
            "label":     row[label_col],
            "precision": round(float(row[("precision", metric)]) * 100, 1),
            "recall":    round(float(row[("recall",    metric)]) * 100, 1),
            "f1":        round(float(row[("f1_score",  metric)]) * 100, 1),
            "aggregate": row[label_col] in AGGREGATE_LABELS,
        }
        for _, row in df.iterrows()
    ]


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== Cross-Dataset Performance ===")

    summary_rows   = []
    entity_rows    = []
    relation_rows  = []

    for split in SPLITS:
        for train_ds in TRAIN_DATASETS:
            for test_ds in DATASETS:
                print(f"  {train_ds} → {test_ds}  [{split}]")
                ner_exact, ner_partial, re_results = evaluate_pair(train_ds, test_ds, split)

                summary_rows.append({
                    "train_ds":               train_ds,
                    "test_ds":                test_ds,
                    "split":                  split,
                    "ner_exact_f1":           _ner_micro_f1(ner_exact),
                    "ner_partial_f1":         _ner_micro_f1(ner_partial),
                    "re_relaxed_f1":          _re_micro_f1(re_results, "RE"),
                    "re_relaxed_partial_f1":  _re_micro_f1(re_results, "RE partial"),
                    "re_strict_f1":           _re_micro_f1(re_results, "RE+"),
                    "re_strict_partial_f1":   _re_micro_f1(re_results, "RE+ partial"),
                })

                if ner_exact is not None:
                    entity_rows.extend(_ner_label_rows(ner_exact,   train_ds, test_ds, split, "exact"))
                if ner_partial is not None:
                    entity_rows.extend(_ner_label_rows(ner_partial, train_ds, test_ds, split, "partial"))
                if re_results is not None:
                    relation_rows.extend(_re_label_rows(re_results, train_ds, test_ds, split, "relaxed",         "RE"))
                    relation_rows.extend(_re_label_rows(re_results, train_ds, test_ds, split, "relaxed_partial",  "RE partial"))
                    relation_rows.extend(_re_label_rows(re_results, train_ds, test_ds, split, "strict",           "RE+"))
                    relation_rows.extend(_re_label_rows(re_results, train_ds, test_ds, split, "strict_partial",   "RE+ partial"))

    output = {
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "summary":         summary_rows,
        "entity_labels":   entity_rows,
        "relation_labels": relation_rows,
    }

    out_path = ensure_output("data/cross_dataset_performance.json")
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\n✓ Written to {out_path}")


if __name__ == "__main__":
    main()
