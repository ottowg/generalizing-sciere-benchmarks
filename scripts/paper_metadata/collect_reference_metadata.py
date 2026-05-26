"""Collect OpenAlex metadata (title, year, citation count) for all referenced papers.

Reads every reference ID cited by any paper in all_papers.jsonl and fetches
metadata for unique OpenAlex IDs not yet in the local cache.  Saves results
incrementally so the script can be interrupted and resumed safely.

Output
------
data/metadata/references/reference_metadata.json
  {openalex_id: {"openalex_id", "title", "year", "cited_by_count"}}

Rate limiting
-------------
Uses the polite pool (OPENALEX_EMAIL env var) and batches up to 100 IDs per
request — ~80 requests for the full reference corpus, well under API limits.

Usage
-----
    uv run python scripts/paper_metadata/collect_reference_metadata.py
    uv run python scripts/paper_metadata/collect_reference_metadata.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = ROOT / "data" / "metadata" / "unified" / "all_papers.jsonl"
OUTPUT_PATH   = ROOT / "data" / "metadata" / "references" / "reference_metadata.json"

BATCH_SIZE = 100   # OpenAlex filter API supports up to 100 IDs per request


def collect_all_reference_ids() -> list[str]:
    """Return deduplicated sorted list of all OpenAlex reference IDs."""
    seen: set[str] = set()
    with open(METADATA_PATH) as f:
        for line in f:
            rec = json.loads(line)
            for ref_id in rec.get("references") or []:
                if ref_id:
                    seen.add(ref_id)
    return sorted(seen)


def main(dry_run: bool = False) -> None:
    from unifiedsciere.metadata.retriever.openalex import get_works_batch

    all_ids = collect_all_reference_ids()
    print(f"Unique reference IDs across corpus: {len(all_ids)}")

    # Load existing cache so the script is safely resumable
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cache: dict[str, dict] = {}
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH) as f:
            cache = json.load(f)
        print(f"Existing cache: {len(cache)} entries")

    to_fetch = [rid for rid in all_ids if rid not in cache]
    print(f"To fetch: {len(to_fetch)}")

    if dry_run:
        batches = (len(to_fetch) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"(dry-run) Would make ~{batches} batch requests — exiting.")
        return

    if not to_fetch:
        print("Nothing to fetch — cache is up to date.")
        return

    batches = [to_fetch[i : i + BATCH_SIZE] for i in range(0, len(to_fetch), BATCH_SIZE)]
    found_total = 0
    for i, batch in enumerate(batches, 1):
        print(f"  Batch {i}/{len(batches)} ({len(batch)} IDs)…", end=" ", flush=True)
        results = get_works_batch(batch)
        cache.update(results)
        found_total += len(results)
        print(f"{len(results)} found")
        # Write after every batch so partial runs are usable
        with open(OUTPUT_PATH, "w") as f:
            json.dump(cache, f, ensure_ascii=False)

    not_found = len(to_fetch) - found_total
    print(f"\nDone.  {found_total} fetched, {not_found} not found in OpenAlex.")
    print(f"Cache total: {len(cache)} entries → {OUTPUT_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show stats and exit without making API calls")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
