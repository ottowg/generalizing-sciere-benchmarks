import random
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from json import loads as json_loads

import requests

FIELDS = ",".join(
    [
        "title",
        "year",
        "authors",
        "venue",
        "externalIds",  # ArXiv, MAG, ACL, PubMed, Medline, PubMedCentral, DBLP, DOI, …
        "url",
        "abstract",
        "citationCount",
        "paperId",
        "corpusId",
        "publicationVenue",
        "journal",
        # "influentialCitationCount",
        "isOpenAccess",
        "openAccessPdf",
        # "fieldsOfStudy",
        "s2FieldsOfStudy",
        "publicationTypes",
        "publicationDate",
        # "embedding.specter_v2 (and embedding.specter_v1 / embedding.specter_v2)
        "tldr",
        # "citations (supports nested paper fields)
        # "references",
    ]
)

# Lighter field set for enrichment lookups (IDs, links, and S2 topic classification)
ENRICH_FIELDS = ",".join(
    [
        "paperId",
        "corpusId",
        "title",
        "year",
        "venue",
        "authors",
        "url",
        "abstract",
        "externalIds",
        "citationCount",
        "openAccessPdf",
        "publicationTypes",
        "s2FieldsOfStudy",
    ]
)

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper"


def get_metadata_by_corpus_id(corpus_id: str, api_key: str | None = None) -> dict:
    """Retrieve paper metadata from Semantic Scholar by corpus ID.

    Args:
        corpus_id: The Semantic Scholar corpus ID (numeric string).
        api_key: Optional API key for higher rate limits.

    Returns:
        dict with paper metadata.
    """
    url = f"{BASE_URL}/CorpusId:{corpus_id}"
    params = {"fields": FIELDS}
    headers = {"x-api-key": api_key} if api_key else {}
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()


def get_metadata_batch(
    corpus_ids: list[str],
    api_key: str | None = None,
    max_retries: int = 5,
) -> list[dict]:
    """Retrieve metadata for multiple corpus IDs with dynamic rate-limit handling.

    On success, the next request fires immediately (no delay).
    On HTTP 429, waits a random 35-60 seconds before retrying.

    Args:
        corpus_ids: List of Semantic Scholar corpus IDs.
        api_key: Optional API key.
        max_retries: Max retries on 429 rate-limit errors per document.

    Returns:
        List of metadata dicts (None entries for failed lookups).
    """
    results = []
    for i, cid in enumerate(corpus_ids):
        print(f"  [{i + 1}/{len(corpus_ids)}] Fetching CorpusId:{cid}")
        meta = None
        for attempt in range(max_retries + 1):
            try:
                meta = get_metadata_by_corpus_id(cid, api_key=api_key)
                break
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    wait = random.uniform(35, 60)
                    print(
                        f"    Rate limited (429), waiting {wait:.1f}s "
                        f"(attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait)
                else:
                    print(f"    ERROR for {cid}: {e}")
                    break
        results.append(meta)
    return results


# ---------------------------------------------------------------------------
# Enrichment helpers — lightweight lookups via urllib (no `requests` needed)
# ---------------------------------------------------------------------------


def _normalise(text: str) -> str:
    """Lower-case, strip punctuation for fuzzy title comparison."""
    return "".join(c for c in text.lower() if c.isalnum() or c == " ").strip()


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalise(a), _normalise(b)).ratio()


def _s2_get(url: str, timeout: int = 15) -> dict | None:
    """GET a Semantic Scholar API URL, return parsed JSON or None on error."""
    req = urllib.request.Request(url, headers={"User-Agent": "UnifiedSciERE/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json_loads(resp.read())
    except urllib.error.HTTPError:
        raise  # let caller handle 404 / 429
    except Exception:
        return None


def lookup_by_id(
    identifier: str,
    fields: str | None = None,
) -> dict | None:
    """Look up a single paper by a qualified S2 identifier.

    Supported identifier prefixes (see S2 docs):
        ``ArXiv:<id>``, ``DOI:<doi>``, ``ACL:<id>``,
        ``CorpusId:<id>``, ``<s2_paper_id>``

    Returns:
        Parsed paper dict, or None if not found.
    """
    if fields is None:
        fields = ENRICH_FIELDS
    encoded_id = urllib.parse.quote(identifier, safe=":/")
    url = f"{BASE_URL}/{encoded_id}?fields={fields}"
    try:
        return _s2_get(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def search_by_title_match(
    title: str,
    fields: str | None = None,
) -> dict | None:
    """Use the ``/search/match`` endpoint for a single best-match lookup.

    Returns the top result if it exists, otherwise None.
    """
    if fields is None:
        fields = ENRICH_FIELDS
    params = urllib.parse.urlencode({"query": title, "fields": fields})
    url = f"{BASE_URL}/search/match?{params}"
    try:
        data = _s2_get(url)
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 400):
            return None
        raise
    if data and data.get("data"):
        return data["data"][0]
    return None


def search_by_title(
    title: str,
    limit: int = 5,
    fields: str | None = None,
) -> list[dict]:
    """Use the ``/search`` endpoint and return up to *limit* hits."""
    if fields is None:
        fields = ENRICH_FIELDS
    params = urllib.parse.urlencode(
        {
            "query": title,
            "limit": str(limit),
            "fields": fields,
        }
    )
    url = f"{BASE_URL}/search?{params}"
    try:
        data = _s2_get(url)
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 400):
            return []
        raise
    return data.get("data", []) if data else []


def enrich_paper(
    *,
    arxiv_id: str = "",
    doi: str = "",
    acl_id: str = "",
    s2_corpus_id: str = "",
    s2_paper_id: str = "",
    title: str = "",
    similarity_threshold: float = 0.85,
) -> dict | None:
    """Try to find a paper on Semantic Scholar using all available identifiers.

    Lookup order (fastest / most reliable first):
    1. S2 paper ID
    2. S2 corpus ID
    3. arXiv ID
    4. DOI
    5. ACL ID
    6. Title match (``/search/match``)
    7. Title search (``/search``) with similarity filter

    Returns:
        S2 paper dict, or None if nothing matched.
    """
    # --- direct ID lookups (most reliable) ---
    for prefix, value in [
        ("", s2_paper_id),
        ("CorpusId:", s2_corpus_id),
        ("ArXiv:", arxiv_id),
        ("DOI:", doi),
        ("ACL:", acl_id),
    ]:
        if not value:
            continue
        result = lookup_by_id(f"{prefix}{value}")
        if result:
            return result

    # --- title-based fallbacks ---
    if not title:
        return None

    # Try exact match endpoint first
    result = search_by_title_match(title)
    if result:
        sim = _title_similarity(title, result.get("title", ""))
        if sim >= similarity_threshold:
            return result

    # Fall back to ranked search
    hits = search_by_title(title, limit=5)
    for hit in hits:
        sim = _title_similarity(title, hit.get("title", ""))
        if sim >= similarity_threshold:
            return hit

    return None


def enrich_papers_batch(
    papers: list[dict],
    max_per_minute: int = 80,
    max_retries: int = 5,
) -> list[dict | None]:
    """Enrich a batch of papers with Semantic Scholar metadata.

    Each element of *papers* should be a dict with any of:
        ``arxiv_id``, ``doi``, ``acl_id``, ``s2_corpus_id``,
        ``s2_paper_id``, ``title``.

    Uses a sliding-window rate limiter and retry logic for 429 errors.
    On a 429 the request is retried after a random 35–60 s pause (matching
    the behaviour of ``get_metadata_batch``); the failed attempt does NOT
    consume a slot in the rate-limit window.

    Returns:
        List of S2 paper dicts (None when not found), same order.
    """
    request_times: list[float] = []
    window = 60.0
    results: list[dict | None] = []

    for i, p in enumerate(papers):
        # Rate limiting: wait until there is a free slot in the window
        now = time.time()
        request_times = [t for t in request_times if now - t < window]
        if len(request_times) >= max_per_minute:
            wait = request_times[0] + window - now + 0.1
            print(f"  S2 rate limit: waiting {wait:.1f}s ({i}/{len(papers)} done)")
            time.sleep(wait)

        result = None
        for attempt in range(max_retries):
            try:
                request_times.append(time.time())
                result = enrich_paper(**p)
                break
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    if attempt < max_retries - 1:
                        # Remove the failed request from the window counter and
                        # wait a long time before retrying (S2 needs 35-60 s).
                        if request_times:
                            request_times.pop()
                        wait = random.uniform(35, 60)
                        print(
                            f"  S2 429 — waiting {wait:.0f}s then retrying "
                            f"(attempt {attempt + 1}/{max_retries}): "
                            f"{p.get('title', '')[:50]}"
                        )
                        time.sleep(wait)
                        continue
                    else:
                        print(f"  WARNING: S2 429 after {max_retries} attempts, giving up.")
                else:
                    print(f"  WARNING: S2 lookup failed: {exc}")
                break
            except Exception as exc:
                print(f"  WARNING: S2 lookup failed: {exc}")
                break

        results.append(result)

        if (i + 1) % 25 == 0:
            print(f"  S2 progress: {i + 1}/{len(papers)} looked up")

    return results
