"""Retrieve source (outlet) and work (paper) metadata from the OpenAlex API.

OpenAlex calls what we call "outlets" *sources* and individual papers *works*.
This module provides functions to look up sources by name or ID, and works by
DOI or arXiv ID, extracting the fields we care about.

Polite-pool usage
-----------------
Adding ``mailto=<email>`` to every request puts us in OpenAlex's "polite
pool" (10 req/s instead of 1 req/s).  Pass *email* to every function or set
the ``OPENALEX_EMAIL`` environment variable.  The module reads the variable
automatically on import.

Rate limiting
-------------
We insert a small delay between requests and honour ``Retry-After`` headers
so we never hammer the API.
"""

from __future__ import annotations

import os
import time
from difflib import SequenceMatcher

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openalex.org/sources"
WORKS_URL = "https://api.openalex.org/works"

# Fields to request for work lookups (keeps responses small)
_WORK_SELECT = "id,cited_by_count,referenced_works,topics"

# Default delay between requests (polite pool allows ~10 req/s; 0.15 s is safe)
_DEFAULT_DELAY = 0.15


def _email() -> str | None:
    return os.getenv("OPENALEX_EMAIL") or None


def _params(extra: dict | None = None, email: str | None = None) -> dict:
    """Build query-param dict, injecting the mailto polite-pool identifier."""
    mailto = email or _email()
    p: dict = {}
    if mailto:
        p["mailto"] = mailto
    if extra:
        p.update(extra)
    return p


def _get(url: str, params: dict, retries: int = 3) -> httpx.Response | None:
    """GET with retry on 429 / transient errors."""
    for attempt in range(retries):
        try:
            resp = httpx.get(url, params=params, timeout=20)
            if resp.status_code == 200:
                return resp
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", 5))
                print(f"  [openalex] rate-limited, waiting {retry_after}s…")
                time.sleep(retry_after)
                continue
            if resp.status_code == 404:
                return None
            print(f"  [openalex] HTTP {resp.status_code} for {url}")
            return None
        except httpx.RequestError as exc:
            wait = 2 ** attempt
            print(f"  [openalex] request error ({exc}), retry in {wait}s…")
            time.sleep(wait)
    return None


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def _extract_work(data: dict) -> dict:
    """Pull the fields we care about from a raw OpenAlex work object."""
    raw_id = data.get("id", "")
    short_id = raw_id.rsplit("/", 1)[-1] if raw_id else ""

    ref_urls = data.get("referenced_works") or []
    references = [url.rsplit("/", 1)[-1] for url in ref_urls if url]

    topics = [
        {"name": t["display_name"], "score": t.get("score")}
        for t in (data.get("topics") or [])
        if t.get("display_name")
    ]

    return {
        "openalex_id": short_id,
        "cited_by_count": data.get("cited_by_count"),
        "references": references,
        "openalex_topics": topics,
    }


def _extract_source(data: dict) -> dict:
    """Pull the fields we care about from a raw OpenAlex source object."""
    stats = data.get("summary_stats") or {}
    # OpenAlex returns the full URL as id, e.g. "https://openalex.org/S1234"
    raw_id = data.get("id", "")
    short_id = raw_id.rsplit("/", 1)[-1] if raw_id else ""

    topics: list[str] = []
    for t in data.get("topics") or []:
        display = t.get("display_name") or t.get("name") or ""
        if display and display not in topics:
            topics.append(display)

    # issn_l is present on the source object directly
    issn_l = data.get("issn_l") or ""

    return {
        "openalex_id": short_id,
        "issn_l": issn_l,
        "h_index": stats.get("h_index"),
        "i10_index": stats.get("i10_index"),
        "works_count": data.get("works_count"),
        "cited_by_count": data.get("cited_by_count"),
        "mean_citedness_2yr": stats.get("2yr_mean_citedness"),
        "openalex_type": data.get("type") or "",
        "openalex_topics": topics,
        # keep for reference / matching; not stored in Outlet
        "_display_name": data.get("display_name") or "",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_source_by_id(
    openalex_id: str,
    email: str | None = None,
    delay: float = _DEFAULT_DELAY,
) -> dict | None:
    """Fetch a single source by its OpenAlex ID (short form, e.g. 'S137773608').

    Args:
        openalex_id: Short OpenAlex source ID (with or without the 'S' prefix).
        email: Polite-pool e-mail address (falls back to OPENALEX_EMAIL env var).
        delay: Seconds to sleep after the request.

    Returns:
        Extracted source dict or None if not found.
    """
    sid = openalex_id if openalex_id.startswith("S") else f"S{openalex_id}"
    url = f"{BASE_URL}/{sid}"
    resp = _get(url, _params(email=email))
    time.sleep(delay)
    if resp is None:
        return None
    return _extract_source(resp.json())


def search_sources(
    query: str,
    email: str | None = None,
    delay: float = _DEFAULT_DELAY,
) -> list[dict]:
    """Search OpenAlex sources by display name.

    Args:
        query: Search string (outlet name or abbreviation).
        email: Polite-pool e-mail address.
        delay: Seconds to sleep after the request.

    Returns:
        List of extracted source dicts (may be empty).
    """
    resp = _get(
        BASE_URL,
        _params({"search": query, "per_page": "10"}, email=email),
    )
    time.sleep(delay)
    if resp is None:
        return []
    data = resp.json()
    results = data.get("results") or []
    return [_extract_source(r) for r in results]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_best_source(
    name: str,
    abbr: str = "",
    email: str | None = None,
    min_similarity: float = 0.60,
) -> dict | None:
    """Search OpenAlex and return the best-matching source for an outlet.

    Strategy:
    1. Search by full name; pick the result with the highest name similarity.
    2. If no good match, search by abbreviation (if provided).

    Args:
        name: Full outlet name.
        abbr: Outlet abbreviation (optional, used as fallback search term).
        email: Polite-pool e-mail address.
        min_similarity: Minimum SequenceMatcher ratio to accept a match.

    Returns:
        Best-matching source dict or None.
    """

    def _best(candidates: list[dict], reference: str) -> dict | None:
        scored = [
            (c, _similarity(reference, c["_display_name"])) for c in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        if scored and scored[0][1] >= min_similarity:
            return scored[0][0]
        return None

    # 1. Search by full name
    candidates = search_sources(name, email=email)
    match = _best(candidates, name)
    if match:
        return match

    # 2. Search by abbreviation
    if abbr:
        candidates = search_sources(abbr, email=email)
        # For abbreviation search, compare against the full name as well
        match = _best(candidates, name)
        if match is None and candidates:
            # Loosen: accept best abbreviation match if similarity >= 0.40
            scored = [
                (c, _similarity(abbr, c["_display_name"])) for c in candidates
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            if scored and scored[0][1] >= 0.40:
                match = scored[0][0]
        if match:
            return match

    return None


# ---------------------------------------------------------------------------
# Work (paper) lookup
# ---------------------------------------------------------------------------


def get_work_by_doi(
    doi: str,
    email: str | None = None,
    delay: float = _DEFAULT_DELAY,
) -> dict | None:
    """Fetch a work by DOI and return its OpenAlex ID, citation count, and references.

    Args:
        doi: DOI string (with or without the ``https://doi.org/`` prefix).
        email: Polite-pool e-mail address (falls back to OPENALEX_EMAIL env var).
        delay: Seconds to sleep after the request.

    Returns:
        Dict with ``openalex_id``, ``cited_by_count``, ``references``, or None.
    """
    clean = doi.removeprefix("https://doi.org/").removeprefix("http://doi.org/")
    url = f"{WORKS_URL}/https://doi.org/{clean}"
    resp = _get(url, _params({"select": _WORK_SELECT}, email=email))
    time.sleep(delay)
    if resp is None:
        return None
    return _extract_work(resp.json())


def get_work_by_title(
    title: str,
    year: int | None = None,
    email: str | None = None,
    delay: float = _DEFAULT_DELAY,
    min_similarity: float = 0.85,
) -> dict | None:
    """Search for a work by title and return the best match.

    Args:
        title: Paper title to search for.
        year: Publication year used to filter results (optional but recommended).
        email: Polite-pool e-mail address (falls back to OPENALEX_EMAIL env var).
        delay: Seconds to sleep after the request.
        min_similarity: Minimum SequenceMatcher title similarity to accept.

    Returns:
        Dict with ``openalex_id``, ``cited_by_count``, ``references``,
        ``openalex_topics``, and ``_title`` (matched title), or None.
    """
    extra: dict = {"search": title, "select": f"{_WORK_SELECT},title", "per_page": "5"}
    if year:
        extra["filter"] = f"publication_year:{year}"
    resp = _get(WORKS_URL, _params(extra, email=email))
    time.sleep(delay)
    if resp is None:
        return None
    results = (resp.json().get("results") or [])
    if not results:
        return None

    # Pick best title match
    best: dict | None = None
    best_score = 0.0
    for r in results:
        candidate_title = r.get("title") or r.get("display_name") or ""
        score = _similarity(title, candidate_title)
        if score > best_score:
            best_score = score
            best = r

    if best is None or best_score < min_similarity:
        return None

    extracted = _extract_work(best)
    extracted["_title"] = best.get("title") or best.get("display_name") or ""
    return extracted


def get_work_by_arxiv_id(
    arxiv_id: str,
    email: str | None = None,
    delay: float = _DEFAULT_DELAY,
) -> dict | None:
    """Fetch a work by arXiv ID via its official DOI (``10.48550/arXiv.{id}``).

    Args:
        arxiv_id: arXiv ID string (e.g. ``"1910.09700"``), without version suffix.
        email: Polite-pool e-mail address (falls back to OPENALEX_EMAIL env var).
        delay: Seconds to sleep after the request.

    Returns:
        Dict with ``openalex_id``, ``cited_by_count``, ``references``, or None.
    """
    # arXiv papers have official DOIs: 10.48550/arXiv.{id}
    return get_work_by_doi(f"10.48550/arXiv.{arxiv_id}", email=email, delay=delay)
