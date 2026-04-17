"""Enrich outlet_info.json with OpenAlex source metadata.

For each outlet that does not yet have an ``openalex_id`` (or all outlets when
``--force`` is passed), the script:

1. Searches OpenAlex by outlet name (and abbreviation as fallback).
2. If a confident match is found, writes OpenAlex fields back into the outlet
   entry and saves the updated file.

Skipping logic
--------------
An outlet is considered *already enriched* when its ``openalex_id`` field is
non-empty.  Pass ``--force`` to re-fetch even those outlets.

Usage
-----
    uv run scripts/outlet_metadata/enrich_outlet.py            # enrich missing
    uv run scripts/outlet_metadata/enrich_outlet.py --force    # re-fetch all
    uv run scripts/outlet_metadata/enrich_outlet.py --dry-run  # show matches only
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Path setup — package is installed editable via uv
# ---------------------------------------------------------------------------
from unifiedsciere.metadata.retriever.openalex import find_best_source, get_source_by_id

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUTLET_INFO_PATH = DATA_DIR / "metadata" / "outlet_info.json"

# Fields written back from the OpenAlex result
OPENALEX_FIELDS = [
    "openalex_id",
    "issn_l",
    "h_index",
    "i10_index",
    "works_count",
    "cited_by_count",
    "mean_citedness_2yr",
    "openalex_type",
    "openalex_topics",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def _save(outlets: list[dict], path: Path) -> None:
    with open(path, "w") as f:
        json.dump(outlets, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(outlets)} outlets to {path}")


def _enrich_entry(entry: dict, email: str | None) -> dict | None:
    """Look up the outlet on OpenAlex and return the extracted fields (or None)."""
    name = entry.get("name", "")
    abbr = entry.get("abbr", "")

    # If we already have an openalex_id, fetch directly for a refresh
    existing_id = entry.get("openalex_id", "")
    if existing_id:
        result = get_source_by_id(existing_id, email=email)
        if result:
            return result

    return find_best_source(name, abbr=abbr, email=email)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch OpenAlex data even for outlets that already have an openalex_id.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print matches without writing anything to disk.",
    )
    parser.add_argument(
        "--outlet",
        metavar="ID_OR_ABBR",
        help="Enrich only the outlet with this id or abbreviation (e.g. 'outlet_002' or 'CVPR').",
    )
    args = parser.parse_args()

    email = os.getenv("OPENALEX_EMAIL")
    if not email:
        print(
            "Warning: OPENALEX_EMAIL is not set in .env — using anonymous rate limit (1 req/s).\n"
            "Add OPENALEX_EMAIL=your@email.com to .env to use the polite pool (10 req/s).",
            file=sys.stderr,
        )

    outlets = _load(OUTLET_INFO_PATH)

    enriched = 0
    skipped = 0
    failed = 0

    for entry in outlets:
        outlet_id = entry.get("id", "")
        abbr = entry.get("abbr", "")
        name = entry.get("name", "")

        # --outlet filter
        if args.outlet and args.outlet not in (outlet_id, abbr):
            continue

        already_done = bool(entry.get("openalex_id", ""))

        if already_done and not args.force:
            skipped += 1
            continue

        print(f"  Searching: [{outlet_id}] {abbr or name} …", end=" ", flush=True)
        result = _enrich_entry(entry, email=email)

        if result is None:
            print("NOT FOUND")
            failed += 1
            continue

        matched_name = result.get("_display_name", "?")
        print(f"matched '{matched_name}' (h={result.get('h_index')})")

        if not args.dry_run:
            for field in OPENALEX_FIELDS:
                if field in result:
                    entry[field] = result[field]
            enriched += 1

    if not args.dry_run:
        _save(outlets, OUTLET_INFO_PATH)

    print(
        f"\nDone — enriched: {enriched}, skipped (already done): {skipped}, not found: {failed}"
    )
    if args.dry_run:
        print("(dry-run: no changes written)")


if __name__ == "__main__":
    main()
