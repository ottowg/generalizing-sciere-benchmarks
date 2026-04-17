"""Compute abbreviation-pattern coverage statistics across all datasets and splits.

Produces data/abbreviation/coverage_stats.json consumed by the webapp
Quality > Abbreviation Relations view.

Statistics generated
--------------------
parenthesized_gold    : % of gold mentions with '(' per dataset × split
parenthesized_pred    : % of predicted mentions with '(' per dataset × model × split
subtask_a             : Subtask A (mention-pair) candidate / positive / borderline counts
subtask_b             : Subtask B (single-span)  candidate / positive / borderline counts

Usage
-----
    uv run python scripts/abbreviation/coverage_stats.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from unifiedsciere.abbreviates_relation.detect import detect
from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import project_root
from unifiedsciere.unification.pipeline import apply_unification_pipeline

DATASETS: list[str] = ["gsap-ere", "scier", "scinlp"]
MODELS:   list[str] = ["gsap-ere", "scier", "scinlp"]
SPLITS:   list[str] = ["train", "dev", "test"]

PAREN_RE = re.compile(r"\(.*?\)")

OUTPUT_PATH = project_root() / "data" / "abbreviation" / "coverage_stats.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paren_stats(mentions: list) -> dict:
    total = len(mentions)
    count = sum(1 for m in mentions if PAREN_RE.search(m.text))
    return {
        "count": count,
        "total": total,
        "pct":   round(count / total * 100, 1) if total else 0.0,
    }


def _detection_stats(corpus) -> dict:
    result = detect(corpus)
    return {
        "subtask_a": {
            "candidates":  len(result.mention_pairs),
            "positives":   len(result.positives_a()),
            "borderline":  len(result.borderline_a()),
            "negatives":   sum(1 for c in result.mention_pairs if c.weak_label == "negative"),
        },
        "subtask_b": {
            "candidates":  len(result.single_spans),
            "positives":   len(result.positives_b()),
            "borderline":  len(result.borderline_b()),
            "negatives":   sum(1 for c in result.single_spans if c.weak_label == "negative"),
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print("Computing abbreviation coverage statistics...")

    parenthesized_gold: list[dict] = []
    parenthesized_pred: list[dict] = []
    detection_rows:     list[dict] = []
    errors:             list[str]  = []

    for split in SPLITS:
        print(f"  split: {split}")
        for dataset in DATASETS:
            # Gold stats + detection
            try:
                corpus = load_corpus(dataset, split, data_type="gold")
                unified, _ = apply_unification_pipeline(
                    corpus, dataset=dataset,
                    apply_to_gold=True, apply_to_predicted=False,
                )
                pstat = _paren_stats(unified.mentions)
                parenthesized_gold.append({
                    "dataset": dataset, "split": split, **pstat
                })
                det = _detection_stats(unified)
                detection_rows.append({
                    "dataset": dataset, "split": split, "annotator": "gold", **det
                })
            except Exception as e:
                errors.append(f"gold {dataset}/{split}: {e}")
                print(f"    SKIP gold {dataset}/{split}: {e}")

            # Prediction stats
            for model in MODELS:
                try:
                    corpus = load_corpus(dataset, split, data_type="predictions", trained_on=model)
                    unified, _ = apply_unification_pipeline(
                        corpus, dataset=model,
                        apply_to_gold=False, apply_to_predicted=True,
                    )
                    pstat = _paren_stats(unified.mentions_predicted)
                    parenthesized_pred.append({
                        "dataset": dataset, "model": model, "split": split, **pstat
                    })
                except Exception as e:
                    errors.append(f"pred {model}→{dataset}/{split}: {e}")

    report = {
        "generated":          datetime.now(timezone.utc).isoformat(),
        "parenthesized_gold": parenthesized_gold,
        "parenthesized_pred": parenthesized_pred,
        "detection":          detection_rows,
        "errors":             errors,
    }

    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nSaved: {OUTPUT_PATH}")

    # Quick summary
    print("\n=== Parenthesized gold mentions % ===")
    for row in parenthesized_gold:
        print(f"  {row['dataset']:10} {row['split']:5}  {row['pct']:5.1f}%  ({row['count']}/{row['total']})")

    print("\n=== Detection (gold, all splits) ===")
    for row in detection_rows:
        a, b = row["subtask_a"], row["subtask_b"]
        print(
            f"  {row['dataset']:10} {row['split']:5}  "
            f"A: {a['positives']:3}+ {a['borderline']:3}? {a['negatives']:4}-  "
            f"B: {b['positives']:3}+ {b['borderline']:3}? {b['negatives']:4}-"
        )

    if errors:
        print(f"\n{len(errors)} errors (likely missing splits).")


if __name__ == "__main__":
    main()
