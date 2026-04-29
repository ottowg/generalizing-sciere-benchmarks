"""Precompute all confusion matrices and save to data/confusion_matrices/.

Covers all dataset × split × annotation-pair × labelset combinations.
Run this before launching the webapp, or via the webapp's Build button.
"""
import itertools
import json
from pathlib import Path

from compute_confusion import VALID_ANNOTATIONS, VALID_DATASETS, VALID_LABELSETS, compute

SPLITS = ["dev"]  # extend to ["train", "dev", "test"] if needed

# 4 same-annotation + 6 unordered cross-pairs = 10 combinations.
# Reversed cross-pairs are derived by transposing in the API — no need to build both.
ANNOT_PAIRS = [(a, a) for a in VALID_ANNOTATIONS] + list(itertools.combinations(VALID_ANNOTATIONS, 2))

OUT_DIR = Path("data/confusion_matrices")


def cache_path(dataset, split, annot1, annot2, labelset) -> Path:
    key = f"{dataset}_{split}_{annot1}_{annot2}_{labelset}".replace("-", "_")
    return OUT_DIR / f"{key}.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(VALID_DATASETS) * len(SPLITS) * len(ANNOT_PAIRS) * len(VALID_LABELSETS)  # 3×1×10×2 = 60
    done = 0

    for dataset in VALID_DATASETS:
        for split in SPLITS:
            for annot1, annot2 in ANNOT_PAIRS:
                for labelset in VALID_LABELSETS:
                    done += 1
                    out = cache_path(dataset, split, annot1, annot2, labelset)
                    print(f"[{done}/{total}] {dataset} {split} {annot1} vs {annot2} ({labelset})", flush=True)
                    try:
                        result = compute(dataset, split, annot1, annot2, labelset)
                        out.write_text(json.dumps(result))
                    except Exception as e:
                        print(f"  ERROR: {e}", flush=True)

    print(f"\nDone. Files in {OUT_DIR}/", flush=True)


if __name__ == "__main__":
    main()
