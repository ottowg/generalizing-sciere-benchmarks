"""Generate all data files required by the webapp into data/webapp/.

Runs each generation script in dependency order.  All output lands in
data/webapp/ so the directory can be inspected, zipped, or deployed to
HuggingFace Spaces as a self-contained bundle.

Scripts NOT included (require external API calls / manual input):
  - scripts/paper_metadata/build_webapp_metadata.py  (Semantic Scholar API)

Usage:
    uv run scripts/build_webapp_data.py
    uv run scripts/build_webapp_data.py --skip annotation_lookup confusion_matrices
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from unifiedsciere.paths import project_root

ROOT = project_root()

STEPS = [
    # (key, script_path)
    ("cross_dataset",      "scripts/ere_performance/cross_dataset_performance.py"),
    ("reproduce",          "scripts/ere_performance/reproduce_results_report.py"),
    ("label_statistics",   "scripts/ere_performance/label_statistics.py"),
    ("multi_sciere",       "scripts/ere_performance/multi_sciere_results_report.py"),
    ("signatures",         "scripts/ere_quality/relation_signatures.py"),
    ("allowed_signatures", "scripts/ere_quality/allowed_signatures.py"),
    ("example_papers",     "scripts/ere_quality/build_example_papers.py"),
    ("annotation_lookup",  "scripts/ere_performance/build_annotation_lookup.py"),
    ("confusion_matrices", "scripts/ere_confusion_analysis/build_confusion_matrices.py"),
]


def run_step(key: str, script: str) -> bool:
    script_path = ROOT / script
    print(f"\n{'─' * 60}")
    print(f"  {key}  ({script})")
    print(f"{'─' * 60}")
    t0 = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT,
    )
    elapsed = time.monotonic() - t0
    if result.returncode == 0:
        print(f"  OK  ({elapsed:.1f}s)")
        return True
    else:
        print(f"  FAILED (exit {result.returncode}, {elapsed:.1f}s)")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Build all webapp data into data/webapp/.")
    parser.add_argument(
        "--skip", nargs="*", metavar="KEY", default=[],
        help="Step keys to skip (e.g. --skip annotation_lookup confusion_matrices)",
    )
    args = parser.parse_args()

    skip = set(args.skip or [])
    valid_keys = {key for key, _ in STEPS}
    unknown = skip - valid_keys
    if unknown:
        print(f"Unknown step keys: {', '.join(sorted(unknown))}")
        print(f"Valid keys: {', '.join(k for k, _ in STEPS)}")
        sys.exit(1)

    steps = [(key, script) for key, script in STEPS if key not in skip]
    if skip:
        print(f"Skipping: {', '.join(sorted(skip))}")

    print(f"\nBuilding webapp data ({len(steps)} steps) → data/webapp/")

    failures = []
    for key, script in steps:
        ok = run_step(key, script)
        if not ok:
            failures.append(key)

    print(f"\n{'═' * 60}")
    if failures:
        print(f"FAILED steps: {', '.join(failures)}")
        sys.exit(1)
    else:
        print(f"All {len(steps)} steps completed successfully.")
        print(f"Output: {ROOT / 'data' / 'webapp'}")


if __name__ == "__main__":
    main()
