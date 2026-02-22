"""Retrieve paper metadata from the CrossRef API."""

from __future__ import annotations

import re
import time

import requests

BASE_URL = "https://api.crossref.org/works"

# Polite pool: CrossRef asks users to provide a mailto for faster service
# https://api.crossref.org/swagger-ui/index.html
_DEFAULT_HEADERS = {
    "User-Agent": "UnifiedSciERE/0.1 (mailto:unifiedsciere@example.com)",
}


def _parse_date_parts(date_obj: dict | None) -> tuple[int | None, str | None]:
    """Extract year (int) and ISO date string from a CrossRef date object.

    CrossRef dates look like {"date-parts": [[2024, 3, 24]]}.
    """
    if not date_obj:
        return None, None
    parts = date_obj.get("date-parts", [[]])[0]
    if not parts:
        return None, None
    year = parts[0]
    iso = "-".join(str(p).zfill(2) for p in parts)
    return year, iso


def _strip_jats(text: str) -> str:
    """Remove JATS XML tags from CrossRef abstracts."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def _format_author(author: dict) -> str:
    """Format a CrossRef author dict as 'Given Family'."""
    given = author.get("given", "")
    family = author.get("family", "")
    return f"{given} {family}".strip()


def _message_to_dict(msg: dict) -> dict:
    """Convert a CrossRef works message to our standard metadata dict."""
    # Title
    titles = msg.get("title", [])
    title = titles[0] if titles else ""

    # Authors
    authors = [{"name": _format_author(a)} for a in msg.get("author", [])]

    # Year — prefer published-print, fall back to published-online, then issued
    year = None
    pub_date = None
    for date_key in ("published-print", "published-online", "issued", "created"):
        y, d = _parse_date_parts(msg.get(date_key))
        if y is not None:
            year = y
            pub_date = d
            break

    # Venue
    containers = msg.get("container-title", [])
    venue = containers[0] if containers else ""

    # Abstract (strip JATS tags)
    abstract = _strip_jats(msg.get("abstract", ""))

    # External IDs
    external_ids = {"DOI": msg.get("DOI", "")}

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "abstract": abstract,
        "url": msg.get("URL", ""),
        "externalIds": external_ids,
        "publisher": msg.get("publisher", ""),
        "type": msg.get("type", ""),
        "volume": msg.get("volume"),
        "issue": msg.get("issue"),
        "page": msg.get("page"),
        "ISSN": msg.get("ISSN"),
        "subject": msg.get("subject"),
        "published": pub_date,
        "is-referenced-by-count": msg.get("is-referenced-by-count"),
    }


def get_metadata(doi: str) -> dict | None:
    """Retrieve metadata for a single DOI from CrossRef.

    Args:
        doi: A DOI string (e.g. "10.1609/aaai.v38i12.29248").

    Returns:
        Metadata dict or None if not found.
    """
    url = f"{BASE_URL}/{doi}"
    r = requests.get(url, headers=_DEFAULT_HEADERS)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return _message_to_dict(r.json()["message"])


def get_metadata_batch(
    dois: list[str],
    delay: float = 0.5,
    max_retries: int = 3,
) -> list[dict | None]:
    """Retrieve metadata for multiple DOIs from CrossRef.

    CrossRef doesn't have a batch endpoint, so we query one at a time
    with a polite delay between requests.

    Args:
        dois: List of DOI strings.
        delay: Seconds to wait between requests.
        max_retries: Max retries on rate-limit (429) errors per DOI.

    Returns:
        List of metadata dicts (None for DOIs that weren't found).
    """
    results: list[dict | None] = []
    for i, doi in enumerate(dois):
        print(f"  [{i + 1}/{len(dois)}] Fetching DOI: {doi}")
        meta = None
        for attempt in range(max_retries + 1):
            try:
                meta = get_metadata(doi)
                break
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    wait = delay * (2**attempt)
                    print(
                        f"    Rate limited (429), waiting {wait:.1f}s "
                        f"(attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait)
                else:
                    print(f"    ERROR for {doi}: {e}")
                    break
        results.append(meta)
        if i < len(dois) - 1:
            time.sleep(delay)
    return results
