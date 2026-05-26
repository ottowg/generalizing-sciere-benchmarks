"""Domain-shift auxiliary transfer results report.

Evaluates predictions for each run (A/B/C/D) of the SciER NLP domain-shift
experiment on both the dev (non-NLP) and test (NLP) splits.

Prediction layout (inside DATA_DATASETS_FOLDER):
  domain-shift-scier/
    dev.jsonl                          gold dev (non-NLP source domain)
    test.jsonl                         gold test (NLP target domain)
    pred_{run_id}/{seed}/dev.jsonl     per-run seeded predictions
    pred_{run_id}/{seed}/test.jsonl

Runs are auto-discovered by scanning for pred_* directories. A mapping table
provides human-readable display names; unknown runs fall back to the directory name.

Metrics (same as multi_sciere_results_report):
  NER  — exact and partial span match
  RE   — relaxed match
  RE+  — strict match

Output:
  data/webapp/domain_shift_results.json

Usage:
  uv run python scripts/ere_performance/domain_shift_results_report.py
"""

import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

import gsaphub as gh
from dotenv import load_dotenv
from gsaphub.evaluate.relations import RelationExtractionMetric, ScoreType

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.evaluate import (
    filter_relations_with_valid_entities,
    mention_to_gsaphub,
    relation_to_gsaphub,
)
from unifiedsciere.paths import project_root

load_dotenv(project_root() / ".env")

DATASET = "domain-shift-scier"
SPLITS = ["dev", "test"]

OUTPUT_PATH = project_root() / "data" / "webapp" / "domain_shift_results.json"

# Human-readable run labels. Unknown pred_* dirs get the dir name as display.
RUN_DISPLAY: dict[str, str] = {
    "A_baseline":          "A – SciER baseline",
    "B_non_nlp_auxiliary": "B – non-NLP auxiliary",
    "C_nlp_auxiliary":     "C – NLP auxiliary",
    "D_mixed_auxiliary":   "D – mixed auxiliary",
}

SYMMETRIC_RELATIONS = [
    "coreference", "Synonym-Of", "similarWith",
    "isComparedTo", "compareWith", "Compare-With",
]

F1_KEYS = [
    "ner_exact_f1",
    "ner_partial_f1",
    "re_relaxed_f1",
    "re_relaxed_partial_f1",
    "re_strict_f1",
    "re_strict_partial_f1",
]


# ── metric helpers (mirrored from multi_sciere_results_report) ────────────────

def _evaluate_ner(gold, pred, partial: bool = False):
    ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]
    ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]
    return gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=partial)


def _evaluate_relations(gold, pred):
    rels_gold = [relation_to_gsaphub(r, i, annotator="gold") for i, r in enumerate(gold.relation)]
    ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]
    rels_pred = [relation_to_gsaphub(r, i, annotator="pred") for i, r in enumerate(pred.relations_predicted)]
    ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]
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


def _ner_micro(df) -> dict:
    row = df[df["label"] == "micro"].iloc[0]
    p = next(c for c in df.columns if "precision" in str(c).lower())
    r = next(c for c in df.columns if "recall"    in str(c).lower())
    f = next(c for c in df.columns if "f1"        in str(c).lower())
    return {"precision": float(row[p]), "recall": float(row[r]), "f1": float(row[f])}


def _rel_micro(df, metric_name: str) -> dict:
    lc = ("relation", "label")
    row = df[df[lc] == "micro"].iloc[0]
    return {
        "precision": float(row[("precision",  metric_name)]),
        "recall":    float(row[("recall",     metric_name)]),
        "f1":        float(row[("f1_score",   metric_name)]),
    }


def _extract_metrics(ner_exact, ner_partial, rel) -> dict:
    ne  = _ner_micro(ner_exact)
    np_ = _ner_micro(ner_partial)
    re  = _rel_micro(rel, "RE")
    rep = _rel_micro(rel, "RE partial")
    res = _rel_micro(rel, "RE+")
    rsp = _rel_micro(rel, "RE+ partial")
    r = lambda v: round(v * 100, 1)
    return {
        "ner_exact_precision":          r(ne["precision"]),
        "ner_exact_recall":             r(ne["recall"]),
        "ner_exact_f1":                 r(ne["f1"]),
        "ner_partial_precision":        r(np_["precision"]),
        "ner_partial_recall":           r(np_["recall"]),
        "ner_partial_f1":               r(np_["f1"]),
        "re_relaxed_precision":         r(re["precision"]),
        "re_relaxed_recall":            r(re["recall"]),
        "re_relaxed_f1":                r(re["f1"]),
        "re_relaxed_partial_precision": r(rep["precision"]),
        "re_relaxed_partial_recall":    r(rep["recall"]),
        "re_relaxed_partial_f1":        r(rep["f1"]),
        "re_strict_precision":          r(res["precision"]),
        "re_strict_recall":             r(res["recall"]),
        "re_strict_f1":                 r(res["f1"]),
        "re_strict_partial_precision":  r(rsp["precision"]),
        "re_strict_partial_recall":     r(rsp["recall"]),
        "re_strict_partial_f1":         r(rsp["f1"]),
    }


def _mean_std(vals: list[float]) -> tuple[float, float]:
    mean = round(statistics.mean(vals), 2)
    std  = round(statistics.stdev(vals) if len(vals) > 1 else 0.0, 2)
    return mean, std


# ── discovery ────────────────────────────────────────────────────────────────

def _discover_runs(dataset_dir: Path) -> list[str]:
    """Return sorted list of trained_on keys (pred_* dir names minus 'pred_')."""
    runs = []
    for d in sorted(dataset_dir.iterdir()):
        if d.is_dir() and d.name.startswith("pred_"):
            runs.append(d.name[len("pred_"):])
    return runs


def _scier_base(pred_dir: Path) -> Path:
    """Multi-head layout uses pred_dir/scier/; single-head uses pred_dir directly."""
    sub = pred_dir / "scier"
    return sub if sub.is_dir() else pred_dir


def _discover_seeds(pred_dir: Path) -> list[int]:
    base = _scier_base(pred_dir)
    return sorted(int(d.name) for d in base.iterdir() if d.is_dir() and d.name.isdigit())


def _load_pred(pred_dir: Path, seed: int | None, split: str) -> "Corpus":
    """Load prediction corpus, handling both single-head and multi-head layouts."""
    from unifiedsciere.data_loader import _load_docs, _process_docs  # type: ignore[attr-defined]
    base = _scier_base(pred_dir)
    target = (base / str(seed) if seed is not None else base) / f"{split}.jsonl"
    if not target.exists():
        raise FileNotFoundError(target)
    docs = _load_docs(target.parent, [target.name])
    return _process_docs(docs, dataset=DATASET, annotator="pred", is_prediction=True)


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    datasets_folder = os.environ.get("DATA_DATASETS_FOLDER", "")
    if not datasets_folder:
        raise RuntimeError("DATA_DATASETS_FOLDER not set")
    dataset_dir = Path(datasets_folder) / DATASET

    trained_on_list = _discover_runs(dataset_dir)
    print(f"Discovered runs: {trained_on_list}")

    # Pre-load gold corpora (shared across all runs).
    gold: dict = {}
    for split in SPLITS:
        print(f"Loading gold {split} …")
        gold[split] = load_corpus(DATASET, split, data_type="gold")  # type: ignore[arg-type]

    runs_out: list[dict] = []

    for trained_on in trained_on_list:
        display = RUN_DISPLAY.get(trained_on, trained_on)
        print(f"\n=== {trained_on} ({display}) ===")

        pred_dir = dataset_dir / f"pred_{trained_on}"
        seeds = _discover_seeds(pred_dir)
        print(f"  Seeds: {seeds or 'none (unseeded)'}")

        split_results: dict[str, dict] = {}

        for split in SPLITS:
            seed_metrics: list[dict] = []
            seed_records: list[dict] = []

            if seeds:
                for seed in seeds:
                    print(f"  [{split}] seed {seed} …", end=" ", flush=True)
                    try:
                        pred = _load_pred(pred_dir, seed, split)
                        m = _extract_metrics(
                            _evaluate_ner(gold[split], pred, partial=False),
                            _evaluate_ner(gold[split], pred, partial=True),
                            _evaluate_relations(gold[split], pred),
                        )
                        seed_metrics.append(m)
                        seed_records.append({"seed": seed, **m})
                        print(f"NER={m['ner_exact_f1']}  RE={m['re_relaxed_f1']}  RE+={m['re_strict_f1']}")
                    except FileNotFoundError as exc:
                        print(f"not found ({exc})")
            else:
                # Unseeded (legacy single prediction)
                print(f"  [{split}] unseeded …", end=" ", flush=True)
                try:
                    pred = _load_pred(pred_dir, None, split)
                    m = _extract_metrics(
                        _evaluate_ner(gold[split], pred, partial=False),
                        _evaluate_ner(gold[split], pred, partial=True),
                        _evaluate_relations(gold[split], pred),
                    )
                    seed_metrics.append(m)
                    seed_records.append({"seed": None, **m})
                    print(f"NER={m['ner_exact_f1']}  RE={m['re_relaxed_f1']}  RE+={m['re_strict_f1']}")
                except FileNotFoundError as exc:
                    print(f"not found ({exc})")

            if not seed_metrics:
                split_results[split] = None
                continue

            agg: dict = {"n_seeds": len(seed_metrics), "seeds": seed_records}
            for key in F1_KEYS:
                vals = [m[key] for m in seed_metrics]
                agg[f"{key}_mean"], agg[f"{key}_std"] = _mean_std(vals)
            # Include full precision/recall means for all metrics
            for key in seed_metrics[0]:
                if key not in F1_KEYS and key + "_mean" not in agg:
                    vals = [m[key] for m in seed_metrics]
                    agg[f"{key}_mean"] = round(statistics.mean(vals), 2)
            split_results[split] = agg

        runs_out.append({
            "trained_on": trained_on,
            "display":    display,
            **{split: split_results[split] for split in SPLITS},
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": DATASET,
        "splits": SPLITS,
        "runs": runs_out,
    }, indent=2))
    print(f"\nWrote {OUTPUT_PATH.relative_to(project_root())}")


if __name__ == "__main__":
    main()
