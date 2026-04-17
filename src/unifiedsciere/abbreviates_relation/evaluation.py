"""Test set management and evaluation for the abbreviation detection AL loop.

Test set lifecycle
------------------
1. On the first rebuild, a stratified 15 % sample of weak-labeled candidates
   (positives + negatives) is drawn and saved to *test_set_path*.  These items
   are excluded from classifier training from that point on.

2. On every subsequent rebuild, the ordered annotation history is scanned.
   The N-th annotation (N = 10, 20, 30, …) is promoted into the test set:
   if the candidate is already in the test set its label is overridden with
   the human label and its source is updated to "manual"; otherwise a new
   test item is appended.

3. After training the classifiers are evaluated on the current test set and a
   record is appended to *history_path*.

Files
-----
data/abbreviation/test_set.json     — current test set (persisted across runs)
data/abbreviation/eval_history.json — list of evaluation snapshots
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

TEST_FRACTION = 0.15
EVERY_N = 2  # promote every N-th annotation to test set
RANDOM_SEED = 42


# ---------------------------------------------------------------------------
# Test set I/O
# ---------------------------------------------------------------------------


def load_test_set(path: Path | str) -> dict | None:
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_test_set(test_set: dict, path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(test_set, indent=2))


# ---------------------------------------------------------------------------
# Test set construction
# ---------------------------------------------------------------------------


def _stratified_sample(
    items: list, labels: list[int], fraction: float, seed: int
) -> list[tuple]:
    """Return a stratified (item, label) list of size ≈ fraction × total."""
    rng = random.Random(seed)
    pos = [(it, lb) for it, lb in zip(items, labels) if lb == 1]
    neg = [(it, lb) for it, lb in zip(items, labels) if lb == 0]
    n_pos = max(1, round(len(pos) * fraction))
    n_neg = max(1, round(len(neg) * fraction))
    selected = rng.sample(pos, min(n_pos, len(pos))) + rng.sample(
        neg, min(n_neg, len(neg))
    )
    rng.shuffle(selected)
    return selected


def build_initial_test_set(
    labeled_a: list[tuple[str, int]],  # [(cid, label), ...]
    labeled_b: list[tuple[str, int]],
    fraction: float = TEST_FRACTION,
    seed: int = RANDOM_SEED,
) -> dict:
    """Create initial test set from weakly-labeled (cid, label) pairs."""

    def sample(pairs):
        if not pairs:
            return []
        ids, labels = zip(*pairs)
        return [
            {"id": cid, "label": label, "source": "weak"}
            for cid, label in _stratified_sample(
                list(ids), list(labels), fraction, seed
            )
        ]

    return {
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "every_n": EVERY_N,
        "A": sample(labeled_a),
        "B": sample(labeled_b),
    }


# ---------------------------------------------------------------------------
# Test set update from annotation history
# ---------------------------------------------------------------------------


def update_test_set_from_annotations(
    test_set: dict,
    annotations_path: Path | str,
    every_n: int = EVERY_N,
) -> dict:
    """Promote every N-th annotation into the test set (overrides weak label).

    Uses the ordered history from the JSONL file (first-occurrence order when
    the same candidate is annotated more than once).
    """
    from .annotations import iter_annotations

    # Build ordered unique list by first occurrence
    seen: set = set()
    ordered: list = []
    for r in iter_annotations(annotations_path):
        if r["id"] not in seen:
            seen.add(r["id"])
            ordered.append(r)

    # Build mutable index: subtask → {cid: list_index}
    idx: dict[str, dict[str, int]] = {
        "A": {item["id"]: i for i, item in enumerate(test_set["A"])},
        "B": {item["id"]: i for i, item in enumerate(test_set["B"])},
    }

    for i, record in enumerate(ordered):
        if (i + 1) % every_n != 0:
            continue

        cid = record["id"]
        subtask = "A" if cid.startswith("A_") else "B"
        items = test_set[subtask]

        if cid in idx[subtask]:
            # Upgrade existing weak item to manual
            items[idx[subtask][cid]].update(
                {
                    "label": record["label"],
                    "source": "manual",
                    "annotator": record.get("annotator", ""),
                }
            )
        else:
            # Add entirely new manual test item
            items.append(
                {
                    "id": cid,
                    "label": record["label"],
                    "source": "manual",
                    "annotator": record.get("annotator", ""),
                }
            )
            idx[subtask][cid] = len(items) - 1

    test_set["updated"] = datetime.now(timezone.utc).isoformat()
    return test_set


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def evaluate_rule_based(
    test_items: list[dict],
    cand_by_id: dict,
) -> dict | None:
    """Evaluate the rule-based detector (all signals must fire) on *test_items*."""
    matched = [
        (item, cand_by_id[item["id"]])
        for item in test_items
        if item["id"] in cand_by_id
    ]
    if len(matched) < 2:
        return None
    items_matched, cands = zip(*matched)
    y_true_list = [item["label"] for item in items_matched]
    if len(set(y_true_list)) < 2:
        return None
    try:
        import numpy as np
        from sklearn.metrics import precision_recall_fscore_support

        y_true = np.array(y_true_list, dtype=int)
        y_pred = np.array([int(c.rule_based_positive) for c in cands], dtype=int)
        p, r, f, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        return {
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1": round(float(f), 4),
        }
    except Exception:
        return None


def evaluate_classifier(
    clf,  # AbbrevClassifier (must have .predict())
    test_items: list[dict],  # [{id, label, source}]
    cand_by_id: dict,  # {cid: candidate object}
) -> dict | None:
    """Evaluate *clf* on *test_items* that are present in *cand_by_id*.

    Returns a metrics dict, or None if there are too few examples.
    """
    if clf is None:
        return None

    matched = [
        (item, cand_by_id[item["id"]])
        for item in test_items
        if item["id"] in cand_by_id
    ]
    if len(matched) < 2:
        return None

    items_matched, cands = zip(*matched)
    y_true_list = [item["label"] for item in items_matched]

    # Need both classes present
    if len(set(y_true_list)) < 2:
        return None

    try:
        import numpy as np
        from sklearn.metrics import precision_recall_fscore_support

        y_true = np.array(y_true_list, dtype=int)
        y_pred = clf.predict(list(cands))
        p, r, f, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        n_manual = sum(1 for item in items_matched if item.get("source") == "manual")
        return {
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1": round(float(f), 4),
            "n_test": len(matched),
            "n_manual": n_manual,
            "pct_manual": round(n_manual / len(matched) * 100, 1),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Evaluation history
# ---------------------------------------------------------------------------


def load_eval_history(path: Path | str) -> list:
    path = Path(path)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, ValueError):
        return []


def append_eval_history(path: Path | str, record: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    history = load_eval_history(path)
    history.append(record)
    path.write_text(json.dumps(history, indent=2))
