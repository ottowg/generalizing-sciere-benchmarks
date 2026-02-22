"""Retrieve paper metadata from the DBLP API.

Uses the DBLP publication search endpoint to look up papers by title.
Intelligently distinguishes between preprint and published versions.

https://dblp.org/faq/How+to+use+the+dblp+search+API.html
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

DBLP_SEARCH_URL = "https://dblp.org/search/publ/api"

# DBLP publication types
TYPE_CONFERENCE = "Conference and Workshop Papers"
TYPE_JOURNAL = "Journal Articles"
TYPE_INFORMAL = "Informal and Other Publications"


def _normalise(text: str) -> str:
    """Lower-case, strip punctuation for fuzzy title comparison."""
    return "".join(c for c in text.lower() if c.isalnum() or c == " ").strip()


def _title_similarity(a: str, b: str) -> float:
    """Return 0-1 similarity between two title strings."""
    return SequenceMatcher(None, _normalise(a), _normalise(b)).ratio()


def _parse_authors(authors_raw) -> list[str]:
    """Extract author name strings from DBLP's author field.

    DBLP returns a single dict for one author, a list for multiple.
    """
    if not authors_raw:
        return []
    author_field = authors_raw.get("author", [])
    if isinstance(author_field, dict):
        author_field = [author_field]
    return [a["text"] for a in author_field if "text" in a]


def _parse_hit(info: dict) -> dict:
    """Convert a DBLP search hit ``info`` dict to our metadata schema."""
    year_str = info.get("year", "")

    return {
        "title": info.get("title", "").rstrip("."),
        "authors": _parse_authors(info.get("authors", {})),
        "year": int(year_str) if year_str.isdigit() else None,
        "venue": info.get("venue", ""),
        "pages": info.get("pages", ""),
        "type": info.get("type", ""),
        "doi": info.get("doi", ""),
        "dblp_key": info.get("key", ""),
        "dblp_url": info.get("url", ""),
        "ee": info.get("ee", ""),  # electronic edition (often the PDF/publisher link)
        "access": info.get("access", ""),
        "volume": info.get("volume", ""),
    }


def _is_preprint(hit: dict) -> bool:
    """Check if a DBLP entry is a preprint (arXiv/CoRR)."""
    key = hit.get("dblp_key", "")
    return key.startswith("journals/corr/") or hit.get("type") == TYPE_INFORMAL


def _is_published(hit: dict) -> bool:
    """Check if a DBLP entry is a published version (conference/journal)."""
    return hit.get("type") in (TYPE_CONFERENCE, TYPE_JOURNAL)


def search_by_title(
    title: str,
    max_hits: int = 10,
) -> list[dict]:
    """Search DBLP for publications matching *title*.

    Args:
        title: The paper title to search for.
        max_hits: Maximum number of results to return.

    Returns:
        List of parsed DBLP result dicts, ordered by relevance.
    """
    params = urllib.parse.urlencode(
        {
            "q": title,
            "format": "json",
            "h": str(max_hits),
        }
    )
    url = f"{DBLP_SEARCH_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "UnifiedSciERE/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    hits_wrapper = data.get("result", {}).get("hits", {})
    raw_hits = hits_wrapper.get("hit", [])
    if isinstance(raw_hits, dict):
        raw_hits = [raw_hits]

    return [_parse_hit(h["info"]) for h in raw_hits if "info" in h]


def find_versions(
    title: str,
    year: int | None = None,
    similarity_threshold: float = 0.85,
    year_tolerance: int = 2,
) -> tuple[dict | None, dict | None]:
    """Find both preprint and published versions of a paper.

    Searches DBLP and returns both the preprint version (if any) and the
    published version (if any). This allows tracking papers from arXiv
    preprint to conference/journal publication.

    Args:
        title: Paper title.
        year: Expected publication year (optional, used for filtering).
        similarity_threshold: Minimum title similarity (0-1) to accept.
        year_tolerance: Accept papers within ±year_tolerance of expected year.

    Returns:
        Tuple of (published_version, preprint_version), either may be None.
        Published version is prioritized if both exist.
    """
    hits = search_by_title(title, max_hits=10)
    if not hits:
        return (None, None)

    # Filter by title similarity
    candidates = []
    for h in hits:
        sim = _title_similarity(title, h["title"])
        if sim >= similarity_threshold:
            # Filter by year if provided
            if year is not None and h.get("year") is not None:
                if abs(h["year"] - year) > year_tolerance:
                    continue
            candidates.append((sim, h))

    if not candidates:
        return (None, None)

    # Separate into published and preprint versions
    published = []
    preprints = []

    for sim, h in candidates:
        if _is_published(h):
            published.append((sim, h))
        elif _is_preprint(h):
            preprints.append((sim, h))

    # Pick best of each type (highest similarity)
    best_published = max(published, key=lambda x: x[0])[1] if published else None
    best_preprint = max(preprints, key=lambda x: x[0])[1] if preprints else None

    return (best_published, best_preprint)


def best_match(
    title: str,
    year: int | None = None,
    prefer_published: bool = True,
    similarity_threshold: float = 0.85,
) -> dict | None:
    """Find the single best DBLP match for a paper.

    This is the legacy interface, now implemented using find_versions().

    Args:
        title: Paper title.
        year: Expected publication year (optional).
        prefer_published: Prefer conference/journal over arXiv preprints.
        similarity_threshold: Minimum title similarity (0-1) to accept.

    Returns:
        Best matching DBLP result dict, or None if no good match found.
    """
    published, preprint = find_versions(title, year, similarity_threshold)

    if prefer_published and published:
        return published
    elif published:
        return published
    else:
        return preprint


def get_metadata_batch(
    titles: list[str],
    years: list[int | None] | None = None,
    max_per_minute: int = 30,
    prefer_published: bool = True,
    similarity_threshold: float = 0.85,
    max_retries: int = 3,
    return_both_versions: bool = False,
) -> list[dict | None] | list[tuple[dict | None, dict | None]]:
    """Look up DBLP metadata for multiple papers by title.

    Args:
        titles: List of paper titles.
        years: Optional list of expected years (same length as titles).
        max_per_minute: Maximum number of API requests per 60 seconds.
        prefer_published: Prefer conference/journal over preprints.
        similarity_threshold: Minimum title similarity to accept a match.
        max_retries: Number of retries on 429 errors before giving up.
        return_both_versions: If True, return (published, preprint) tuples.

    Returns:
        If return_both_versions=False:
            List of DBLP result dicts (None for papers not found).
        If return_both_versions=True:
            List of (published, preprint) tuples, either may be None.
    """
    if years is None:
        years = [None] * len(titles)

    # Sliding window: track timestamps of recent requests
    request_times: list[float] = []
    window = 60.0  # seconds

    results: list = []
    for i, (title, year) in enumerate(zip(titles, years)):
        # Rate limiting
        now = time.time()
        request_times = [t for t in request_times if now - t < window]
        if len(request_times) >= max_per_minute:
            wait = request_times[0] + window - now + 0.1
            print(f"  Rate limit: waiting {wait:.1f}s ({i}/{len(titles)} done)")
            time.sleep(wait)

        # Retry logic
        result = None
        for attempt in range(max_retries):
            try:
                request_times.append(time.time())
                if return_both_versions:
                    result = find_versions(
                        title,
                        year=year,
                        similarity_threshold=similarity_threshold,
                    )
                else:
                    result = best_match(
                        title,
                        year=year,
                        prefer_published=prefer_published,
                        similarity_threshold=similarity_threshold,
                    )
                break
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < max_retries - 1:
                    backoff = 2 ** (attempt + 1)
                    print(
                        f"  429 rate-limited, retrying in {backoff}s... ({title[:50]})"
                    )
                    time.sleep(backoff)
                    continue
                print(f"  WARNING: DBLP lookup failed for {title!r}: {exc}")
                break
            except Exception as exc:
                print(f"  WARNING: DBLP lookup failed for {title!r}: {exc}")
                break

        if return_both_versions and result is None:
            result = (None, None)

        results.append(result)

        if (i + 1) % 25 == 0:
            print(f"  Progress: {i + 1}/{len(titles)} looked up")

    return results
