#!/usr/bin/env python3
"""Build the active-learning annotation queue for abbreviation detection.

Usage
-----
    uv run scripts/abbreviation/build_al_queue.py [--datasets ...] [--splits ...] [--force]
"""

from __future__ import annotations

import argparse

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import project_root
from unifiedsciere.abbreviates_relation.annotations import load_annotations
from unifiedsciere.abbreviates_relation.queue import (
    CorpusEntry,
    build_queue,
    save_queue,
)

ALL_DATASETS = ["gsap-ere", "scier", "scinlp"]
ALL_SPLITS   = ["train", "dev", "test"]

ANNOTATIONS_PATH = project_root() / "data" / "abbreviation" / "annotations.jsonl"
QUEUE_PATH       = project_root() / "data" / "abbreviation" / "al_queue.json"
TEST_SET_PATH    = project_root() / "data" / "abbreviation" / "test_set.json"
HISTORY_PATH     = project_root() / "data" / "abbreviation" / "eval_history.json"


def _needs_rebuild() -> bool:
    """Return True if the queue needs rebuilding for any reason."""
    if not QUEUE_PATH.exists():
        return True
    # Test set missing — evaluation won't work without it
    if not TEST_SET_PATH.exists():
        return True
    # New annotations since last build
    if ANNOTATIONS_PATH.exists() and ANNOTATIONS_PATH.stat().st_mtime > QUEUE_PATH.stat().st_mtime:
        return True
    # Queue exists but a classifier wasn't trained (e.g. first run, changed features)
    try:
        import json
        summary = json.loads(QUEUE_PATH.read_text()).get("summary", {})
        if not all(summary.get(sub, {}).get("ml_trained") for sub in ("A", "B")):
            return True
    except Exception:
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets",   nargs="+", default=ALL_DATASETS, metavar="DS")
    parser.add_argument("--splits",     nargs="+", default=ALL_SPLITS,   metavar="SPLIT")
    parser.add_argument("--force",      action="store_true", help="Rebuild even without new annotations")
    parser.add_argument("--queue-size", type=int,   default=20,   metavar="N",
                        help="Number of items per subtask in the queue (default: 20)")
    parser.add_argument("--sigma",      type=float, default=0.15, metavar="S",
                        help="Gaussian σ for sampling (default: 0.15)")
    args = parser.parse_args()

    if not args.force and not _needs_rebuild():
        print("Queue is up to date — no new annotations since last build. Use --force to rebuild anyway.")
        return

    human_labels = load_annotations(ANNOTATIONS_PATH)
    print(f"Loaded {len(human_labels)} human annotations")

    corpora: list[CorpusEntry] = []
    for dataset in args.datasets:
        for split in args.splits:
            print(f"  Loading {dataset}/{split} … ", end="", flush=True)
            try:
                corpus = load_corpus(dataset, split, data_type="gold")
                corpora.append(CorpusEntry(corpus=corpus, dataset=dataset, split=split))
                print("ok")
            except Exception as e:
                print(f"skip ({e})")

    print(f"Building queue (queue_size={args.queue_size}, sigma={args.sigma}) …", flush=True)
    result = build_queue(
        corpora, human_labels,
        annotations_path=ANNOTATIONS_PATH,
        test_set_path=TEST_SET_PATH,
        history_path=HISTORY_PATH,
        queue_size=args.queue_size,
        sigma=args.sigma,
        log=lambda msg: print(msg, flush=True),
    )
    save_queue(result, QUEUE_PATH)

    sa, sb = result.summary_a, result.summary_b
    print(
        f"Wrote {len(result.items)} borderline candidates → {QUEUE_PATH}\n"
        f"  Subtask A: {sa.n_weak_pos} weak-pos, {sa.n_weak_neg} weak-neg, "
        f"{sa.n_borderline_unannotated} borderline, ML={sa.ml_trained}\n"
        f"  Subtask B: {sb.n_weak_pos} weak-pos, {sb.n_weak_neg} weak-neg, "
        f"{sb.n_borderline_unannotated} borderline, ML={sb.ml_trained}"
    )
    if result.eval_a:
        ea = result.eval_a
        print(f"  Eval A: P={ea['precision']:.3f} R={ea['recall']:.3f} F1={ea['f1']:.3f} "
              f"(n={ea['n_test']}, {ea['pct_manual']:.0f}% manual)")
    if result.eval_b:
        eb = result.eval_b
        print(f"  Eval B: P={eb['precision']:.3f} R={eb['recall']:.3f} F1={eb['f1']:.3f} "
              f"(n={eb['n_test']}, {eb['pct_manual']:.0f}% manual)")


if __name__ == "__main__":
    main()
