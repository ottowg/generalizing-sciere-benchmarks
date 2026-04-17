"""Copy HGERE predictions into data/predictions_vN/.

Source layout:
  <src_root>/datasets/<test_dataset>/pred_<trained_on>/<split>.jsonl

Destination layout:
  data/predictions_v<N>/<test_dataset>_model_<trained_on>_<split>.jsonl

Usage:
  uv run scripts/copy_hgere_predictions.py --version 2
  uv run scripts/copy_hgere_predictions.py --version 2 --dry-run
"""

import argparse
import shutil
from pathlib import Path

from unifiedsciere.paths import project_root

SRC_ROOT = Path("/home/ottowg/projects/gsap/gsap-rel-related/HGERE/datasets")
SPLITS = {"train", "dev", "test"}
SPLITS_OOD = {"test_ood"}

# Normalize typos/aliases in pred_<trained_on> directory names to canonical trained_on identifiers.
TRAINED_ON_ALIASES = {
    "unfied-sciere": "unified-sciere",  # typo in gsap-ere/pred_unfied-sciere
}


def collect_files(src_root: Path) -> tuple[list[tuple[Path, str]], list[str]]:
    """Return (found, missing) where found is a list of (src_path, dest_name) pairs
    and missing is a list of human-readable descriptions of expected but absent files."""
    found = []
    missing = []
    for test_dataset_dir in sorted(src_root.iterdir()):
        if not test_dataset_dir.is_dir():
            continue
        test_dataset = test_dataset_dir.name
        for pred_dir in sorted(test_dataset_dir.iterdir()):
            if not pred_dir.is_dir() or not pred_dir.name.startswith("pred_"):
                continue
            raw_trained_on = pred_dir.name[len("pred_"):]
            trained_on = TRAINED_ON_ALIASES.get(raw_trained_on, raw_trained_on)
            splits = SPLITS | (SPLITS_OOD if test_dataset == "scier" else set())
            for split in sorted(splits):
                split_file = pred_dir / f"{split}.jsonl"
                dest_name = f"{test_dataset}_model_{trained_on}_{split}.jsonl"
                if split_file.exists():
                    found.append((split_file, dest_name))
                else:
                    missing.append(str(split_file))
    return found, missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy HGERE predictions to predictions_vN.")
    parser.add_argument("--version", "-v", type=int, required=True, help="Target version number N")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying")
    args = parser.parse_args()

    dest_dir = project_root() / "data" / f"predictions_v{args.version}"
    if not args.dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    files, missing = collect_files(SRC_ROOT)

    if missing:
        print(f"Missing ({len(missing)}):")
        for path in missing:
            print(f"  {path}")
        print()

    if not files:
        print("No matching files found.")
        return

    for src, dest_name in files:
        dest = dest_dir / dest_name
        if args.dry_run:
            print(f"  {src}\n    -> {dest}")
        else:
            shutil.copy2(src, dest)
            print(f"Copied {dest_name}")

    if not args.dry_run:
        print(f"\nDone: {len(files)} file(s) copied to {dest_dir}")


if __name__ == "__main__":
    main()
