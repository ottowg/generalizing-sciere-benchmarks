"""Enrich the unified metadata with outlet information.

This script:
1. Loads papers from all_papers.jsonl
2. Enriches them with outlet_id using the outlet catalogue
3. Saves back to all_papers.jsonl (backing up the original)
4. Regenerates the BibTeX file

Usage:
    python scripts/enrich_unified_metadata.py
    python scripts/enrich_unified_metadata.py --dry-run  # preview without saving
"""

import argparse
import json
from collections import Counter
from pathlib import Path

# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from unifiedsciere.metadata.enrich_metadata import enrich_with_outlets
from unifiedsciere.metadata.read_metadata import load_papers

DATA_DIR = Path(__file__).parent.parent / "data"
METADATA_DIR = DATA_DIR / "metadata"
UNIFIED_DIR = METADATA_DIR / "unified"
ALL_PAPERS_PATH = UNIFIED_DIR / "all_papers.jsonl"
ALL_PAPERS_BIB_PATH = UNIFIED_DIR / "all_papers.bib"


def main():
    parser = argparse.ArgumentParser(
        description="Enrich unified metadata with outlet information"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without saving",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-enrichment even for papers that already have outlet_id",
    )
    args = parser.parse_args()

    print("=== Loading papers ===")
    papers = load_papers()
    print(f"Loaded {len(papers)} papers")

    # Count current outlet assignments
    before_count = sum(1 for p in papers if p.outlet_id)
    print(f"Papers with outlet_id before: {before_count}")

    # Clear outlet_ids if forcing re-enrichment
    if args.force:
        print("\n=== Forcing re-enrichment (clearing existing outlet_ids) ===")
        for paper in papers:
            paper.outlet_id = ""
        print(f"Cleared {before_count} outlet_ids")

    print("\n=== Enriching with outlet information ===")
    enrich_with_outlets(papers)

    # Count after enrichment
    after_count = sum(1 for p in papers if p.outlet_id)
    print(f"Papers with outlet_id after: {after_count}")
    print(f"Newly matched: {after_count - before_count}")

    # Show statistics
    print("\n=== Enrichment Statistics ===")
    by_dataset = Counter()
    matched_by_dataset = Counter()
    for p in papers:
        by_dataset[p.dataset] += 1
        if p.outlet_id:
            matched_by_dataset[p.dataset] += 1

    for dataset in sorted(by_dataset.keys()):
        total = by_dataset[dataset]
        matched = matched_by_dataset[dataset]
        pct = matched / total * 100 if total > 0 else 0
        print(f"  {dataset:10s}: {matched:3d}/{total:3d} ({pct:5.1f}%)")

    if args.dry_run:
        print("\n=== DRY RUN - Not saving changes ===")
        print("Run without --dry-run to save the enriched metadata.")
        return

    # Backup original file
    backup_path = ALL_PAPERS_PATH.with_suffix(".jsonl.backup")
    print(f"\n=== Backing up original to {backup_path.name} ===")
    if ALL_PAPERS_PATH.exists():
        import shutil

        shutil.copy2(ALL_PAPERS_PATH, backup_path)
        print(f"✓ Backup created")

    # Save enriched JSONL
    print(f"\n=== Writing enriched data to {ALL_PAPERS_PATH.name} ===")
    with open(ALL_PAPERS_PATH, "w") as f:
        for paper in papers:
            f.write(json.dumps(paper.to_dict(), ensure_ascii=False) + "\n")
    print(f"✓ Wrote {len(papers)} papers")

    # Regenerate BibTeX
    print(f"\n=== Regenerating {ALL_PAPERS_BIB_PATH.name} ===")
    with open(ALL_PAPERS_BIB_PATH, "w") as f:
        entries = [p.to_bib() for p in papers]
        f.write("\n\n".join(entries) + "\n")
    print(f"✓ Wrote {len(entries)} BibTeX entries")

    print("\n=== SUCCESS ===")
    print("Metadata enrichment complete!")
    print(f"To restore the original: cp {backup_path} {ALL_PAPERS_PATH}")


if __name__ == "__main__":
    main()
