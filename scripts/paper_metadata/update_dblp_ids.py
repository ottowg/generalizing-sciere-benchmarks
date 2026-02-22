"""Update DBLP IDs to separate preprint and published versions.

This script:
1. Loads papers from all_papers.jsonl
2. For papers with journals/corr DBLP IDs, tries to find published versions
3. Separates dblp_id (published) and dblp_preprint_id (arXiv)
4. Saves updated metadata

Usage:
    python scripts/update_dblp_ids.py
    python scripts/update_dblp_ids.py --dry-run
    python scripts/update_dblp_ids.py --force-all  # re-lookup all papers
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unifiedsciere.metadata.read_metadata import load_papers
from unifiedsciere.metadata.retriever.dblp import find_versions

DATA_DIR = Path(__file__).parent.parent / "data"
METADATA_DIR = DATA_DIR / "metadata"
UNIFIED_DIR = METADATA_DIR / "unified"
ALL_PAPERS_PATH = UNIFIED_DIR / "all_papers.jsonl"
ALL_PAPERS_BIB_PATH = UNIFIED_DIR / "all_papers.bib"


def main():
    parser = argparse.ArgumentParser(
        description="Update DBLP IDs to separate preprint and published versions"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without saving",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Re-lookup all papers, not just journals/corr",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of papers to process (for testing)",
    )
    args = parser.parse_args()

    print("=== Loading papers ===")
    papers = load_papers()
    print(f"Loaded {len(papers)} papers")

    # Identify papers to update
    if args.force_all:
        to_update = papers
        print("Force mode: will re-lookup all papers")
    else:
        # Only update papers with journals/corr or no dblp_id
        to_update = [
            p for p in papers if p.dblp_id.startswith("journals/corr/") or not p.dblp_id
        ]
        print(f"Papers with journals/corr or no DBLP ID: {len(to_update)}")

    if args.limit:
        to_update = to_update[: args.limit]
        print(f"Limited to first {args.limit} papers")

    if not to_update:
        print("No papers to update")
        return

    # Extract titles and years
    titles = [p.title for p in to_update]
    years = [p.year for p in to_update]

    print(f"\n=== Looking up {len(to_update)} papers on DBLP ===")
    import time
    import urllib.error

    # Use custom find_versions with higher year tolerance
    from unifiedsciere.metadata.retriever.dblp import find_versions

    results = []
    request_times = []
    window = 60.0
    max_per_minute = 5  # Conservative rate: 5 per minute
    max_retries = 3

    for i, (title, year) in enumerate(zip(titles, years)):
        # Rate limiting
        now = time.time()
        request_times = [t for t in request_times if now - t < window]
        if len(request_times) >= max_per_minute:
            wait = request_times[0] + window - now + 0.1
            print(f"  Rate limit: waiting {wait:.1f}s ({i}/{len(titles)} done)")
            time.sleep(wait)

        # Retry logic with exponential backoff for 429 errors
        result = (None, None)
        for attempt in range(max_retries):
            try:
                request_times.append(time.time())
                result = find_versions(
                    title,
                    year=year,
                    similarity_threshold=0.85,
                    year_tolerance=3,  # Allow up to 3 years difference
                )
                break  # Success
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    backoff = 2 ** (attempt + 1)
                    print(
                        f"  429 rate-limited on '{title[:40]}...', retry in {backoff}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(backoff)
                    continue
                else:
                    print(f"  WARNING: HTTP {e.code} for '{title[:50]}'")
                    result = (None, None)
                    break
            except Exception as e:
                print(f"  WARNING: Failed to lookup '{title[:50]}': {e}")
                result = (None, None)
                break

        results.append(result)

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(titles)} looked up")

    print(f"  Completed: {len(results)}/{len(titles)} papers")

    # Apply results
    stats = Counter()
    for paper, (published, preprint) in zip(to_update, results):
        old_id = paper.dblp_id

        # Update DBLP IDs
        if published:
            paper.dblp_id = published.get("dblp_key", "")
            stats["found_published"] += 1
        elif old_id.startswith("journals/corr/"):
            # Had preprint, but no published version found
            paper.dblp_id = ""  # Clear it
            stats["only_preprint"] += 1

        if preprint:
            paper.dblp_preprint_id = preprint.get("dblp_key", "")
            stats["found_preprint"] += 1

        # Track changes
        if old_id and old_id != paper.dblp_id:
            if paper.dblp_id:
                stats["upgraded"] += 1  # journals/corr → conf/xxx
            else:
                stats["cleared"] += 1  # journals/corr → (nothing found)
        elif not old_id and paper.dblp_id:
            stats["newly_found"] += 1

    # Print statistics
    print(f"\n=== Results ===")
    print(f"  Found published versions: {stats['found_published']}")
    print(f"  Found preprint versions: {stats['found_preprint']}")
    print(f"  Upgraded (preprint → published): {stats['upgraded']}")
    print(f"  Cleared (preprint, no published): {stats['cleared']}")
    print(f"  Newly found: {stats['newly_found']}")
    print(f"  Only preprint available: {stats['only_preprint']}")

    # Show examples
    print(f"\n=== Sample upgrades ===")
    upgrades = [
        (p.title, p.dblp_preprint_id, p.dblp_id)
        for p in to_update
        if p.dblp_id and p.dblp_preprint_id
    ]
    for title, preprint_id, published_id in upgrades[:5]:
        print(f"  {title[:50]:50s}")
        print(f"    Preprint:  {preprint_id}")
        print(f"    Published: {published_id}")

    if args.dry_run:
        print("\n=== DRY RUN - Not saving changes ===")
        return

    # Backup and save
    backup_path = ALL_PAPERS_PATH.with_suffix(".jsonl.backup")
    print(f"\n=== Backing up to {backup_path.name} ===")
    if ALL_PAPERS_PATH.exists():
        import shutil

        shutil.copy2(ALL_PAPERS_PATH, backup_path)
        print(f"✓ Backup created")

    # Save enriched JSONL
    print(f"\n=== Writing updated data to {ALL_PAPERS_PATH.name} ===")
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
    print("DBLP IDs updated!")


if __name__ == "__main__":
    main()
