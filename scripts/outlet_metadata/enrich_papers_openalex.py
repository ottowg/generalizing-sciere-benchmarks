"""Enrich all_papers.jsonl with OpenAlex work metadata.

For each paper without an ``openalex_id`` (or all papers with ``--force``),
the script looks up the work in OpenAlex using:

1. DOI (if available).
2. arXiv ID (if available) — via its official DOI ``10.48550/arXiv.{id}``.
3. Title search (fallback) — for papers with neither DOI nor arXiv ID.

Enriched fields written back:
- ``openalex_id``       — short OpenAlex work ID (e.g. "W2741809807")
- ``cited_by_count``    — citation count
- ``references``        — list of OpenAlex work IDs of referenced works
- ``openalex_topics``   — list of {"name": str, "score": float} topic dicts

Use ``--topics-only`` to only refresh topics for papers that already have an
``openalex_id`` (fast batch re-fetch, skips ID lookup).

Usage
-----
    uv run scripts/outlet_metadata/enrich_papers_openalex.py                # enrich missing
    uv run scripts/outlet_metadata/enrich_papers_openalex.py --force        # re-fetch all
    uv run scripts/outlet_metadata/enrich_papers_openalex.py --topics-only  # refresh topics only
    uv run scripts/outlet_metadata/enrich_papers_openalex.py --dry-run      # show matches only
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from unifiedsciere.metadata.retriever.openalex import (
    get_work_by_doi,
    get_work_by_arxiv_id,
    get_work_by_title,
    WORKS_URL,
    _params,
    _get,
    _extract_work,
    _DEFAULT_DELAY,
)
import time

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PAPERS_PATH = DATA_DIR / "metadata" / "unified" / "all_papers.jsonl"

OPENALEX_FIELDS = ["openalex_id", "cited_by_count", "references", "openalex_topics"]


def _load(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _save(papers: list[dict], path: Path) -> None:
    with open(path, "w") as f:
        for paper in papers:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")
    print(f"Saved {len(papers)} papers to {path}")


def _fetch(paper: dict, email: str | None) -> dict | None:
    """Try DOI, then arXiv ID, then title search."""
    doi = paper.get("doi", "")
    arxiv_id = paper.get("arxiv_id", "")
    title = paper.get("title", "")
    year = paper.get("year")

    if doi:
        result = get_work_by_doi(doi, email=email)
        if result and result.get("openalex_id"):
            return result

    if arxiv_id:
        result = get_work_by_arxiv_id(arxiv_id, email=email)
        if result and result.get("openalex_id"):
            return result

    if title:
        result = get_work_by_title(title, year=year, email=email)
        if result and result.get("openalex_id"):
            return result

    return None


def _batch_fetch_topics(openalex_ids: list[str], email: str | None) -> dict[str, list[dict]]:
    """Fetch topics for a batch of OpenAlex work IDs (up to 200 per request).

    Returns a dict mapping short OpenAlex ID → list of topic dicts.
    """
    topics_by_id: dict[str, list[dict]] = {}
    batch_size = 50
    for i in range(0, len(openalex_ids), batch_size):
        batch = openalex_ids[i : i + batch_size]
        filter_val = "|".join(batch)
        resp = _get(
            WORKS_URL,
            _params({"filter": f"ids.openalex:{filter_val}", "select": "id,topics", "per_page": "50"}, email=email),
        )
        time.sleep(_DEFAULT_DELAY)
        if resp is None:
            continue
        for work in resp.json().get("results") or []:
            raw_id = work.get("id", "")
            short_id = raw_id.rsplit("/", 1)[-1] if raw_id else ""
            if not short_id:
                continue
            topics = [
                {"name": t["display_name"], "score": t.get("score")}
                for t in (work.get("topics") or [])
                if t.get("display_name")
            ]
            topics_by_id[short_id] = topics
    return topics_by_id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch even papers that already have an openalex_id.",
    )
    parser.add_argument(
        "--topics-only",
        action="store_true",
        help="Only refresh openalex_topics for papers that already have an openalex_id (batch fetch).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print matches without writing anything to disk.",
    )
    args = parser.parse_args()

    email = os.getenv("OPENALEX_EMAIL")
    if not email:
        print(
            "Warning: OPENALEX_EMAIL is not set — using anonymous rate limit (1 req/s).\n"
            "Add OPENALEX_EMAIL=your@email.com to .env for the polite pool (10 req/s).",
            file=sys.stderr,
        )

    papers = _load(PAPERS_PATH)

    # ── Topics-only mode: batch fetch topics for all papers with openalex_id ──
    if args.topics_only:
        ids_with_openalex = [p["openalex_id"] for p in papers if p.get("openalex_id")]
        print(f"Batch-fetching topics for {len(ids_with_openalex)} papers…")
        topics_map = _batch_fetch_topics(ids_with_openalex, email=email)
        updated = 0
        for paper in papers:
            oid = paper.get("openalex_id", "")
            if oid and oid in topics_map:
                if not args.dry_run:
                    paper["openalex_topics"] = topics_map[oid]
                updated += 1
        if not args.dry_run:
            _save(papers, PAPERS_PATH)
        print(f"Done — updated topics for {updated} / {len(ids_with_openalex)} papers.")
        if args.dry_run:
            print("(dry-run: no changes written)")
        return

    # ── Normal mode: look up openalex_id for papers that are missing it ──
    enriched = skipped = failed = 0

    for paper in papers:
        doc_id = paper.get("doc_id", "?")
        already_done = bool(paper.get("openalex_id", ""))

        if already_done and not args.force:
            skipped += 1
            continue

        doi = paper.get("doi", "")
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "")
        label = doi or (f"arxiv:{arxiv_id}" if arxiv_id else (title[:50] if title else doc_id))
        print(f"  Fetching: {doc_id} [{label}] …", end=" ", flush=True)

        result = _fetch(paper, email=email)

        if result is None:
            print("NOT FOUND")
            failed += 1
            continue

        matched_title = result.pop("_title", "")
        n_topics = len(result.get("openalex_topics") or [])
        print(
            f"found {result['openalex_id']} "
            f"(citations={result.get('cited_by_count')}, "
            f"refs={len(result.get('references', []))}, "
            f"topics={n_topics})"
            + (f"  [matched: {matched_title[:50]}]" if matched_title else "")
        )

        if not args.dry_run:
            for fld in OPENALEX_FIELDS:
                if fld in result:
                    paper[fld] = result[fld]
            enriched += 1

    if not args.dry_run:
        _save(papers, PAPERS_PATH)

    print(
        f"\nDone — enriched: {enriched}, skipped (already done): {skipped}, not found: {failed}"
    )
    if args.dry_run:
        print("(dry-run: no changes written)")


if __name__ == "__main__":
    main()
