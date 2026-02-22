"""Enrich PaperMetadata instances with outlet information.

Loads the outlet catalogue from ``schemas/outlet_info.json``, compiles the
identification patterns, and matches each paper's *venue* (and *conference*)
string against them.  The first matching outlet is attached as
``paper.outlet``.

Usage (standalone)::

    python -m unifiedsciere.metadata.enrich_metadata

Or programmatically::

    from unifiedsciere.metadata.enrich_metadata import enrich_with_outlets

    enrich_with_outlets(papers)          # mutates in place
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from unifiedsciere.types import Outlet, PaperMetadata

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
OUTLET_INFO_PATH = DATA_DIR / "metadata" / "outlet_info.json"


# ---------------------------------------------------------------------------
# Catalogue loading
# ---------------------------------------------------------------------------

# Each entry is (compiled_regex, Outlet)
_CompiledEntry = tuple[re.Pattern[str], Outlet]


def load_outlet_catalogue(path: Path = OUTLET_INFO_PATH) -> list[_CompiledEntry]:
    """Load and compile the outlet catalogue from *path*.

    Returns a list of ``(compiled_pattern, Outlet)`` tuples sorted so that
    entries with longer *name* come first (longer names are more specific and
    should be tried before shorter ones, e.g. "2018 IEEE/CVF Conference on
    Computer Vision …" before "CVPR").
    """
    with open(path) as f:
        raw: list[dict] = json.loads(f.read())

    entries: list[_CompiledEntry] = []
    for item in raw:
        pattern_src = item.get("identification_pattern", "")
        if not pattern_src:
            continue
        try:
            compiled = re.compile(pattern_src)
        except re.error:
            continue

        outlet = Outlet(
            id=item.get("id", ""),
            name=item.get("name", ""),
            abbr=item.get("abbr", ""),
            outlet_type=item.get("outlet_type", ""),
            outlet_topic=item.get("outlet_topic") or "",
            wikidata_id=item.get("wikidata_id") or "",
            canonical_url=item.get("canonical_url") or "",
            dblp_outlet_id=item.get("dblp_outlet_id") or "",
            identification_pattern=pattern_src,
        )
        entries.append((compiled, outlet))

    # Sort longest name first → more specific matches win.
    entries.sort(key=lambda e: len(e[1].name), reverse=True)
    return entries


def load_outlet_index(path: Path = OUTLET_INFO_PATH) -> dict[str, Outlet]:
    """Load all outlets as a dict keyed by outlet id."""
    with open(path) as f:
        raw: list[dict] = json.loads(f.read())

    outlets: dict[str, Outlet] = {}
    for item in raw:
        outlet = Outlet(
            id=item.get("id", ""),
            name=item.get("name", ""),
            abbr=item.get("abbr", ""),
            outlet_type=item.get("outlet_type", ""),
            outlet_topic=item.get("outlet_topic") or "",
            wikidata_id=item.get("wikidata_id") or "",
            canonical_url=item.get("canonical_url") or "",
            dblp_outlet_id=item.get("dblp_outlet_id") or "",
            identification_pattern=item.get("identification_pattern") or "",
        )
        outlets[outlet.id] = outlet
    return outlets


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


def match_outlet_by_dblp(
    paper: PaperMetadata,
    catalogue: list[_CompiledEntry],
) -> Outlet | None:
    """Match outlet by DBLP ID prefix.

    If the paper has a dblp_id (e.g., "conf/cvpr/LiWCTT20"), extract the
    prefix (e.g., "conf/cvpr") and match against outlet dblp_outlet_id.

    Returns the matching Outlet or None.
    """
    if not paper.dblp_id:
        return None

    # Extract venue prefix from DBLP ID
    # Examples: "conf/cvpr/LiWCTT20" → "conf/cvpr"
    #           "journals/corr/abs-1910-09700" → "journals/corr"
    dblp_prefix = _dblp_prefix(paper.dblp_id)
    if not dblp_prefix:
        return None

    # Search for matching outlet
    for _, outlet in catalogue:
        if outlet.dblp_outlet_id and outlet.dblp_outlet_id == dblp_prefix:
            return outlet

    return None


def _dblp_prefix(dblp_id: str) -> str | None:
    parts = dblp_id.split("/")
    if len(parts) < 2:
        return None
    return "/".join(parts[:2])


def match_outlet(
    paper: PaperMetadata,
    catalogue: list[_CompiledEntry],
) -> Outlet | None:
    """Return the first matching Outlet for *paper*, or ``None``.

    Matching priority:
    1. DBLP ID prefix match (most reliable)
    2. Venue/conference string regex match
    """
    # Try DBLP match first
    outlet = match_outlet_by_dblp(paper, catalogue)
    if outlet:
        return outlet

    # Fall back to text matching
    candidates = [paper.venue, paper.conference]
    for text in candidates:
        if not text:
            continue
        for pattern, outlet in catalogue:
            if pattern.search(text):
                return outlet
    return None


# ---------------------------------------------------------------------------
# Public enrichment function
# ---------------------------------------------------------------------------


def enrich_with_outlets(
    papers: list[PaperMetadata],
    catalogue_path: Path = OUTLET_INFO_PATH,
) -> list[PaperMetadata]:
    """Enrich *papers* in-place with outlet_id information.

    Papers that already have an ``outlet_id`` set are skipped.

    Returns the same list for convenience.
    """
    catalogue = load_outlet_catalogue(catalogue_path)
    outlet_index = load_outlet_index(catalogue_path)

    to_match: list[PaperMetadata] = []
    for paper in papers:
        if not paper.outlet_id:
            to_match.append(paper)
            continue
        # Allow upgrading preprint outlets when a published DBLP ID is present.
        current = outlet_index.get(paper.outlet_id)
        if current and current.outlet_type == "preprint" and paper.dblp_id:
            to_match.append(paper)

    if not to_match:
        print("  All papers already have an outlet_id — nothing to match.")
        return papers

    matched = 0
    unmatched_prefixes: set[str] = set()
    for paper in to_match:
        outlet = match_outlet(paper, catalogue)
        if outlet is not None and paper.outlet_id != outlet.id:
            paper.outlet_id = outlet.id
            matched += 1
        elif outlet is None and paper.dblp_id:
            prefix = _dblp_prefix(paper.dblp_id)
            if prefix and prefix != "journals/corr":
                unmatched_prefixes.add(prefix)

    print(f"  Outlet enrichment: matched {matched}/{len(to_match)} papers.")
    if unmatched_prefixes:
        prefixes = ", ".join(sorted(unmatched_prefixes))
        print(
            "  Warning: no outlet_info match for DBLP prefixes "
            f"(excluding journals/corr): {prefixes}"
        )
    return papers
