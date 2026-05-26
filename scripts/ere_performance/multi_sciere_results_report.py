"""MultiSciERE results report — in-distribution evaluation (no unification).

Each dataset is evaluated using the multi-sciere prediction variant whose label
space matches that dataset's native labels:
    gsap-ere  → multi-sciere-gsap
    scier     → multi-sciere-scier
    scinlp    → multi-sciere-scinlp

For seeded models (e.g. multi-sciere-scinlp-gsap-ere), all seeds are evaluated and
mean/std are computed. Seed 1 results are also included in the main summary table.

Metrics:
    NER  — exact and partial span match
    RE   — relaxed match (entity spans exact, relation label must match)
    RE+  — strict match (entity spans + labels exact, relation label must match)

Outputs:
    data/webapp/multi_sciere_results.json

Usage:
    uv run python scripts/ere_performance/multi_sciere_results_report.py
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
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[Literal["gsap-ere", "scier", "scinlp"]] = ["gsap-ere", "scier", "scinlp"]
SPLIT = "test"
REPORTED_PERFORMANCE_PATH = (
    project_root() / "data" / "webapp" / "static" / "reported_performance.json"
)
JSON_OUTPUT_PATH = project_root() / "data" / "webapp" / "multi_sciere_results.json"

PRED_LABEL_SETS = ["gsap", "scier", "scinlp"]

# For each test dataset, the matching multi-sciere prediction label space.
DATASET_TO_PRED_LS: dict[str, str] = {
    "gsap-ere": "gsap",
    "scier": "scier",
    "scinlp": "scinlp",
}

# Map pred label space back to the dataset key for apply_unification_pipeline.
PRED_LS_TO_DATASET: dict[str, Literal["gsap-ere", "scier", "scinlp"]] = {
    "gsap": "gsap-ere",
    "scier": "scier",
    "scinlp": "scinlp",
}

# Seeded model configurations.
#
# Fields:
#   model_id           — identifier used in seeded_comparison["model_id"] and for display
#   trained_on_key     — optional override for the trained_on value passed to load_corpus.
#                        When absent, trained_on is computed as
#                        "multi-sciere-{model_id}-{pred_label_set}".
#                        When present, the value is used as-is (for single-dataset models).
#   display            — human-readable label for the model
#   Seeds are discovered automatically by scanning for integer-named subdirectories
#   inside the resolved prediction directory (no hard-coding needed).
#   dataset_label_sets — maps test dataset → pred label set (used for unified eval only).
#                        Use only datasets the model was trained on to keep labels consistent.
#   eval_label_set     — "original" or "unified".  "original" requires pred_label_set ==
#                        DATASET_TO_PRED_LS[dataset] (assertion, skipped when trained_on_key
#                        is set since label sets don't apply to single-dataset models).
SCIER_OOD_MODELS: list[dict] = [
    {
        "model_id": "scier",
        "trained_on_key": "scier",
        "display": "scier",
        "dataset_label_sets": {"scier": "scier"},
        "eval_label_set": "original",
    },
    {
        "model_id": "scinlp-scier",
        "display": "scinlp + scier",
        "dataset_label_sets": {"scier": "scier"},
        "eval_label_set": "original",
    },
    {
        "model_id": "gsap-ere-scier",
        "display": "gsap-ere + scier",
        "dataset_label_sets": {"scier": "scier"},
        "eval_label_set": "original",
    },
    {
        "model_id": "gsap-ere-scier-scinlp",
        "display": "gsap-ere + scier + scinlp",
        "dataset_label_sets": {"scier": "scier"},
        "eval_label_set": "original",
    },
]

SEEDED_MODELS: list[dict] = [
    # ── Baselines: single-dataset models ────────────────────────────────────
    {
        "model_id": "gsap-ere",
        "trained_on_key": "gsap-ere",
        "display": "gsap-ere",
        "dataset_label_sets": {"gsap-ere": "gsap"},
        "eval_label_set": "original",
    },
    {
        "model_id": "scier",
        "trained_on_key": "scier",
        "display": "scier",
        "dataset_label_sets": {"scier": "scier"},
        "eval_label_set": "original",
    },
    {
        "model_id": "scinlp",
        "trained_on_key": "scinlp",
        "display": "scinlp",
        "dataset_label_sets": {"scinlp": "scinlp"},
        "eval_label_set": "original",
    },
    # ── Multi-dataset seeded models ──────────────────────────────────────────
    {
        "model_id": "scinlp-gsap-ere",  # suffix only; stored as "multi-sciere-{model_id}"
        "display": "scinlp + gsap-ere",
        "dataset_label_sets": {
            "gsap-ere": "gsap",
            "scinlp": "scinlp",
        },
        "eval_label_set": "original",
    },
    {
        "model_id": "scinlp-scier",  # suffix only; stored as "multi-sciere-{model_id}"
        "display": "scinlp + scier",
        "dataset_label_sets": {
            "scinlp": "scinlp",
            "scier": "scier",
        },
        "eval_label_set": "original",
    },
    {
        "model_id": "gsap-ere-scier",  # suffix only; stored as "multi-sciere-{model_id}"
        "display": "gsap-ere + scier",
        "dataset_label_sets": {
            "gsap-ere": "gsap",
            "scier": "scier",
        },
        "eval_label_set": "original",
    },
    {
        "model_id": "gsap-ere-scier-scinlp",  # suffix only; stored as "multi-sciere-{model_id}"
        "display": "gsap-ere + scier + scinlp",
        "dataset_label_sets": {
            "gsap-ere": "gsap",
            "scier": "scier",
            "scinlp": "scinlp",
        },
        "eval_label_set": "original",
    },
]

SYMMETRIC_RELATIONS = [
    "coreference",
    "Synonym-Of",
    "similarWith",
    "isComparedTo",
    "compareWith",
    "Compare-With",
]


# ── evaluation helpers ────────────────────────────────────────────────────────


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


def _extract_summary_metrics(ner_exact, ner_partial, rel_results) -> dict:
    """Extract all micro-averaged metrics into a flat dict (values already ×100, rounded)."""
    ne = _extract_ner_micro(ner_exact)
    np_ = _extract_ner_micro(ner_partial)
    re = _extract_rel_micro(rel_results, "RE")
    rep_ = _extract_rel_micro(rel_results, "RE partial")
    res = _extract_rel_micro(rel_results, "RE+")
    reps = _extract_rel_micro(rel_results, "RE+ partial")
    return {
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


AGGREGATE_LABELS = {"micro", "macro", "weighted"}


def _ner_label_rows(ner_results, dataset, label_set, match, trained_on) -> list[dict]:
    p_col = next(c for c in ner_results.columns if "precision" in str(c).lower())
    r_col = next(c for c in ner_results.columns if "recall" in str(c).lower())
    f1_col = next(c for c in ner_results.columns if "f1" in str(c).lower())
    return [
        {
            "dataset": dataset,
            "label_set": label_set,
            "trained_on": trained_on,
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


def _re_label_rows(
    rel_results, dataset, label_set, metric_name, match, trained_on
) -> list[dict]:
    label_col = ("relation", "label")
    return [
        {
            "dataset": dataset,
            "label_set": label_set,
            "trained_on": trained_on,
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
    metrics = _extract_summary_metrics(ner_exact, ner_partial, rel_results)
    print(f"  NER exact F1:   {metrics['ner_exact_f1']}")
    print(f"  NER partial F1: {metrics['ner_partial_f1']}")
    print(f"  RE  F1:         {metrics['re_relaxed_f1']}")
    print(f"  RE+ F1:         {metrics['re_strict_f1']}")

    json_summary.append(
        {
            "dataset": dataset,
            "label_set": label_set,
            "trained_on": trained_on,
            **metrics,
        }
    )
    json_labels.extend(
        _ner_label_rows(ner_exact, dataset, label_set, "exact", trained_on)
    )
    json_labels.extend(
        _ner_label_rows(ner_partial, dataset, label_set, "partial", trained_on)
    )
    json_labels.extend(
        _re_label_rows(rel_results, dataset, label_set, "RE", "relaxed", trained_on)
    )
    json_labels.extend(
        _re_label_rows(
            rel_results, dataset, label_set, "RE partial", "relaxed_partial", trained_on
        )
    )
    json_labels.extend(
        _re_label_rows(rel_results, dataset, label_set, "RE+", "strict", trained_on)
    )
    json_labels.extend(
        _re_label_rows(
            rel_results, dataset, label_set, "RE+ partial", "strict_partial", trained_on
        )
    )


# ── run-eval helpers ──────────────────────────────────────────────────────────


def _run_eval(
    dataset: str, pred_label_set: str, label_set: str, trained_on: str, seed=None,
    split: str = SPLIT,
) -> tuple:
    gold = load_corpus(dataset, split, data_type="gold")
    pred = load_corpus(
        dataset, split, data_type="predictions", trained_on=trained_on, seed=seed
    )

    if label_set == "unified":
        unify_pred_as = PRED_LS_TO_DATASET[pred_label_set]
        gold, _ = apply_unification_pipeline(
            gold, dataset, apply_to_gold=True, apply_to_predicted=False
        )
        pred, _ = apply_unification_pipeline(
            pred, unify_pred_as, apply_to_gold=False, apply_to_predicted=True
        )

    return (
        evaluate_ner(gold, pred, partial=False),
        evaluate_ner(gold, pred, partial=True),
        evaluate_relations(gold, pred),
    )


def _mean_std(values: list[float]) -> tuple[float, float]:
    mean = round(statistics.mean(values), 2)
    std = round(statistics.stdev(values) if len(values) > 1 else 0.0, 2)
    return mean, std


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    reported = json.loads(REPORTED_PERFORMANCE_PATH.read_text())

    json_summary: list[dict] = []
    json_labels: list[dict] = []

    # ── Original label set (matching pred per dataset) ────────────────────────
    print("\n=== original label set (matching pred) ===")
    for dataset in DATASETS:
        pred_label_set = DATASET_TO_PRED_LS[dataset]
        trained_on = f"multi-sciere-{pred_label_set}"
        print(f"\n--- {dataset.upper()} [original] ({trained_on}) ---")
        ner_exact, ner_partial, rel_results = _run_eval(
            dataset, pred_label_set, "original", trained_on
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

    # ── Unified label set (all 9 combinations) ────────────────────────────────
    print("\n=== unified label set (all combinations) ===")
    for dataset in DATASETS:
        for pred_label_set in PRED_LABEL_SETS:
            trained_on = f"multi-sciere-{pred_label_set}"
            print(f"\n--- {dataset.upper()} [unified] ({trained_on}) ---")
            ner_exact, ner_partial, rel_results = _run_eval(
                dataset, pred_label_set, "unified", trained_on
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

    # ── Seeded models ─────────────────────────────────────────────────────────
    seeded_comparison: list[dict] = []

    for cfg in SEEDED_MODELS:
        model_id = cfg["model_id"]
        display = cfg["display"]
        ds_label_sets = cfg.get("dataset_label_sets", DATASET_TO_PRED_LS)
        eval_label_set = cfg.get("eval_label_set", "original")
        trained_on_override = cfg.get("trained_on_key")  # set for single-dataset models
        print(f"\n=== seeded model: {model_id} (eval={eval_label_set}) ===")

        # When evaluating in the original label space, each dataset must be paired
        # with its own native label set to avoid silent label mismatches.
        # Skip this check for single-dataset models (trained_on_key set explicitly).
        if eval_label_set == "original" and trained_on_override is None:
            for dataset, pred_label_set in ds_label_sets.items():
                expected = DATASET_TO_PRED_LS.get(dataset)
                assert pred_label_set == expected, (
                    f"SEEDED_MODELS config error for model '{model_id}': "
                    f"dataset '{dataset}' requires pred_label_set='{expected}' "
                    f"for original-space eval, got '{pred_label_set}'."
                )

        for dataset, pred_label_set in ds_label_sets.items():
            trained_on_key = (
                trained_on_override or f"multi-sciere-{model_id}-{pred_label_set}"
            )
            seeds = discover_seeds(dataset, trained_on_key)
            print(
                f"\n--- {dataset.upper()} ({trained_on_key}, {eval_label_set}) seeds={seeds} ---"
            )

            seed_metrics: list[dict] = []

            for seed in seeds:
                print(f"  seed {seed} …", end=" ", flush=True)
                try:
                    ner_e, ner_p, rel = _run_eval(
                        dataset,
                        pred_label_set,
                        eval_label_set,
                        trained_on_key,
                        seed=seed,
                    )
                    m = _extract_summary_metrics(ner_e, ner_p, rel)
                    seed_metrics.append(m)
                    print(
                        f"NER={m['ner_exact_f1']}  RE={m['re_relaxed_f1']}  RE+={m['re_strict_f1']}"
                    )
                except FileNotFoundError as exc:
                    print(f"not found ({exc})")

            if not seed_metrics:
                # Fallback: try a non-seeded (old-style) single prediction if it exists.
                print(
                    f"  No seeds found — trying old-style single prediction …",
                    end=" ",
                    flush=True,
                )
                try:
                    ner_e, ner_p, rel = _run_eval(
                        dataset,
                        pred_label_set,
                        eval_label_set,
                        trained_on_key,
                        seed=None,
                    )
                    m = _extract_summary_metrics(ner_e, ner_p, rel)
                    print(
                        f"NER={m['ner_exact_f1']}  RE={m['re_relaxed_f1']}  RE+={m['re_strict_f1']}"
                    )
                    _append_results(
                        json_summary,
                        json_labels,
                        ner_e,
                        ner_p,
                        rel,
                        dataset,
                        eval_label_set,
                        trained_on_key,
                    )
                except FileNotFoundError:
                    print("not found, skipping.")
                continue

            # Seeds available — add mean/std to seeded_comparison only.
            # Do NOT also add a single-seed entry to json_summary (prefer seeds).

            # Compute mean ± std across all seeds (Task 1)
            f1_keys = [
                "ner_exact_f1",
                "ner_partial_f1",
                "re_relaxed_f1",
                "re_relaxed_partial_f1",
                "re_strict_f1",
                "re_strict_partial_f1",
            ]
            full_model_id = (
                model_id if trained_on_override else f"multi-sciere-{model_id}"
            )
            row: dict = {
                "model_id": full_model_id,
                "display": display,
                "test_dataset": dataset,
                "split": "test",
                "pred_label_set": pred_label_set,
                "eval_label_set": eval_label_set,
                "n_seeds": len(seed_metrics),
            }
            for key in f1_keys:
                vals = [m[key] for m in seed_metrics]
                mean, std = _mean_std(vals)
                row[f"{key}_mean"] = mean
                row[f"{key}_std"] = std
            seeded_comparison.append(row)

    # ── SciER OOD evaluation (test_ood split) ─────────────────────────────────
    print("\n=== SciER OOD (test_ood) ===")
    for cfg in SCIER_OOD_MODELS:
        model_id = cfg["model_id"]
        display = cfg["display"]
        ds_label_sets = cfg["dataset_label_sets"]
        eval_label_set = cfg["eval_label_set"]
        trained_on_override = cfg.get("trained_on_key")
        print(f"\n--- scier OOD / {model_id} ---")

        for dataset, pred_label_set in ds_label_sets.items():
            trained_on_key = (
                trained_on_override or f"multi-sciere-{model_id}-{pred_label_set}"
            )
            seeds = discover_seeds(dataset, trained_on_key)
            print(f"  ({trained_on_key}, seeds={seeds})")

            seed_metrics: list[dict] = []
            for seed in seeds:
                print(f"  seed {seed} …", end=" ", flush=True)
                try:
                    ner_e, ner_p, rel = _run_eval(
                        dataset, pred_label_set, eval_label_set, trained_on_key,
                        seed=seed, split="test_ood",
                    )
                    m = _extract_summary_metrics(ner_e, ner_p, rel)
                    seed_metrics.append(m)
                    print(f"NER={m['ner_exact_f1']}  RE={m['re_relaxed_f1']}  RE+={m['re_strict_f1']}")
                except FileNotFoundError as exc:
                    print(f"not found ({exc})")

            if not seed_metrics:
                print("  No seeds — trying non-seeded …", end=" ", flush=True)
                try:
                    ner_e, ner_p, rel = _run_eval(
                        dataset, pred_label_set, eval_label_set, trained_on_key,
                        seed=None, split="test_ood",
                    )
                    m = _extract_summary_metrics(ner_e, ner_p, rel)
                    print(f"NER={m['ner_exact_f1']}  RE={m['re_relaxed_f1']}  RE+={m['re_strict_f1']}")
                    seed_metrics = [m]
                except FileNotFoundError:
                    print("not found, skipping.")
                    continue

            full_model_id = model_id if trained_on_override else f"multi-sciere-{model_id}"
            f1_keys = [
                "ner_exact_f1", "ner_partial_f1",
                "re_relaxed_f1", "re_relaxed_partial_f1",
                "re_strict_f1", "re_strict_partial_f1",
            ]
            row: dict = {
                "model_id": full_model_id,
                "display": display,
                "test_dataset": dataset,
                "split": "test_ood",
                "pred_label_set": pred_label_set,
                "eval_label_set": eval_label_set,
                "n_seeds": len(seed_metrics),
            }
            for key in f1_keys:
                vals = [m[key] for m in seed_metrics]
                mean, std = _mean_std(vals)
                row[f"{key}_mean"] = mean
                row[f"{key}_std"] = std
            seeded_comparison.append(row)

    JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT_PATH.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": json_summary,
                "labels": json_labels,
                "reported": reported,
                "seeded_comparison": seeded_comparison,
            },
            indent=2,
        )
    )
    print(f"\nWrote JSON to {JSON_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
