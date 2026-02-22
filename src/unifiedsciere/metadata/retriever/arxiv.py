"""Retrieve paper metadata from the arXiv API."""

from __future__ import annotations

import re
import time

import arxiv


def extract_arxiv_id(doc_id: str) -> str:
    """Extract an arXiv ID from a GSAP-style doc_id.

    Example: "00015_1910_09700.txt" -> "1910.09700"
    """
    # Strip .txt suffix, then grab the last two underscore-separated parts
    stem = doc_id.removesuffix(".txt")
    parts = stem.split("_")
    if len(parts) < 3:
        raise ValueError(f"Cannot extract arXiv ID from doc_id: {doc_id!r}")
    return f"{parts[-2]}.{parts[-1]}"


def _result_to_dict(result: arxiv.Result) -> dict:
    """Convert an arxiv.Result to a plain dict matching our metadata schema."""
    return {
        "title": result.title,
        "authors": [{"name": a.name} for a in result.authors],
        "year": result.published.year if result.published else None,
        "venue": None,  # arXiv doesn't provide venue
        "abstract": result.summary,
        "url": result.entry_id,
        "externalIds": {
            "ArXiv": result.get_short_id(),
        },
        "categories": result.categories,
        "published": result.published.isoformat() if result.published else None,
        "updated": result.updated.isoformat() if result.updated else None,
        "doi": result.doi,
        "comment": result.comment,
        "journal_ref": result.journal_ref,
        "primary_category": result.primary_category,
        "pdf_url": result.pdf_url,
    }


def get_metadata(arxiv_id: str) -> dict | None:
    """Retrieve metadata for a single arXiv paper.

    Args:
        arxiv_id: arXiv paper ID (e.g. "1910.09700").

    Returns:
        Metadata dict or None if not found.
    """
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    try:
        result = next(client.results(search))
        return _result_to_dict(result)
    except StopIteration:
        return None


def get_metadata_batch(
    arxiv_ids: list[str],
    batch_size: int = 50,
    page_delay: float = 3.0,
) -> list[dict | None]:
    """Retrieve metadata for multiple arXiv papers in batches.

    The arXiv API supports fetching multiple papers at once via id_list.
    We batch requests to stay within API guidelines.

    Args:
        arxiv_ids: List of arXiv paper IDs.
        batch_size: Number of papers to fetch per API call.
        page_delay: Seconds to wait between batches.

    Returns:
        List of metadata dicts (None for papers that weren't found).
    """
    client = arxiv.Client(page_size=batch_size, delay_seconds=page_delay)

    # Process in batches
    results_map: dict[str, dict] = {}
    for start in range(0, len(arxiv_ids), batch_size):
        batch = arxiv_ids[start : start + batch_size]
        batch_num = start // batch_size + 1
        total_batches = (len(arxiv_ids) + batch_size - 1) // batch_size
        print(
            f"  [batch {batch_num}/{total_batches}] Fetching {len(batch)} papers from arXiv..."
        )

        search = arxiv.Search(id_list=batch)
        for result in client.results(search):
            # Map by the short ID (e.g. "1910.09700")
            short_id = result.get_short_id()
            # Remove version suffix (e.g. "1910.09700v2" -> "1910.09700")
            short_id = re.sub(r"v\d+$", "", short_id)
            results_map[short_id] = _result_to_dict(result)

        if start + batch_size < len(arxiv_ids):
            time.sleep(page_delay)

    # Return in the same order as the input
    return [results_map.get(aid) for aid in arxiv_ids]
