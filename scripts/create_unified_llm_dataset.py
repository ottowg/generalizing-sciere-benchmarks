"""Generate combined LLM datasets from all three sources.

Combines the per-dataset LLM annotation files into a single corpus for each
model variant.  Two variants are supported:

  gpt-5.4_v3  (default) — *_LLM_gpt-5.4_v3   → all_LLM_gpt-5.4_v3
  v3          (--v3)    — *_LLM_v3            → all_LLM_v3

Train, dev, and test splits are kept strictly separate and shuffled
independently with a fixed seed.

No unification pipeline is applied — all three LLM datasets already share
the same two-label space (concept / artifact).

Output files (in $DATA_DATASETS_FOLDER):
  all_LLM_gpt-5.4_v3/{train,dev,test}.jsonl
  all_LLM_v3/{train,dev,test}.jsonl

Each output record contains:
  doc_key           — original document key, unchanged
  original_dataset  — source dataset ("gsap-ere", "scier", "scinlp")
  split             — original split name
  sentences         — list of token lists
  ner               — list of [[begin_token, end_token, label], ...] per sentence
  relations         — list of [[s_begin, s_end, o_begin, o_end, label], ...] per sentence

Usage:
    uv run python scripts/create_unified_llm_dataset.py            # gpt-5.4_v3
    uv run python scripts/create_unified_llm_dataset.py --v3       # gpt-4.1-mini (v3)
    uv run python scripts/create_unified_llm_dataset.py --all      # both variants
    uv run python scripts/create_unified_llm_dataset.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

from dotenv import load_dotenv

from unifiedsciere.paths import project_root

load_dotenv()

DATASETS = ["gsap-ere", "scier", "scinlp"]
SPLITS = ["train", "dev", "test"]
SEED = 42

VARIANTS: dict[str, dict[str, str]] = {
    "gpt-5.4_v3": {
        "suffix": "_LLM_gpt-5.4_v3",
        "output": "all_LLM_gpt-5.4_v3",
    },
    "v3": {
        "suffix": "_LLM_v3",
        "output": "all_LLM_v3",
    },
}


def _datasets_root() -> Path:
    folder = os.getenv("DATA_DATASETS_FOLDER")
    if not folder:
        raise ValueError("DATA_DATASETS_FOLDER is not set in .env")
    root = Path(folder)
    if not root.is_absolute():
        root = project_root() / root
    return root


def _load_split(datasets_root: Path, dataset: str, split: str, suffix: str) -> list[dict]:
    path = datasets_root / f"{dataset}{suffix}" / f"{split}.jsonl"
    docs: list[dict] = []
    with open(path) as fh:
        for line in fh:
            doc = json.loads(line)
            out = {
                "doc_key": doc.get("doc_key") or doc.get("doc_id", ""),
                "original_dataset": dataset,
                "split": split,
                "sentences": doc["sentences"],
                "ner": doc.get("ner", []),
                "relations": doc.get("relations", []),
            }
            docs.append(out)
    return docs


def _run_variant(
    datasets_root: Path,
    variant_name: str,
    suffix: str,
    output_name: str,
    dry_run: bool,
) -> None:
    output_dir = datasets_root / output_name
    rng = random.Random(SEED)

    print(f"\n{'='*60}")
    print(f"Variant: {variant_name}  ({suffix}  →  {output_name})")

    for split in SPLITS:
        print(f"\n--- {split} ---")
        all_docs: list[dict] = []

        for dataset in DATASETS:
            docs = _load_split(datasets_root, dataset, split, suffix)
            print(f"  {dataset}: {len(docs)} docs")
            all_docs.extend(docs)

        rng.shuffle(all_docs)

        total_ner = sum(len(ent) for doc in all_docs for ent in doc["ner"])
        total_rel = sum(len(rel) for doc in all_docs for rel in doc["relations"])
        print(f"  Combined: {len(all_docs)} docs, {total_ner} mentions, {total_rel} relations")

        if dry_run:
            print("  (dry-run) Skipping write.")
            continue

        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"{split}.jsonl"
        with open(out_path, "w") as fh:
            for doc in all_docs:
                fh.write(json.dumps(doc, ensure_ascii=False) + "\n")
        print(f"  → {out_path}")


def main(variants: list[str], dry_run: bool = False) -> None:
    datasets_root = _datasets_root()

    for name in variants:
        v = VARIANTS[name]
        _run_variant(datasets_root, name, v["suffix"], v["output"], dry_run)

    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--v3", action="store_true",
                        help="Run the gpt-4.1-mini (LLM_v3) variant only")
    parser.add_argument("--all", dest="all_variants", action="store_true",
                        help="Run both variants (gpt-5.4_v3 and v3)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show stats without writing any files")
    args = parser.parse_args()

    if args.all_variants:
        selected = list(VARIANTS)
    elif args.v3:
        selected = ["v3"]
    else:
        selected = ["gpt-5.4_v3"]

    main(variants=selected, dry_run=args.dry_run)
