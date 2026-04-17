"""Enrich paper metadata and outlets from a DOI mapping.

Given a mapping of arXiv IDs to DOIs, this script:

1. Looks up each DOI on Crossref to get the container/journal name, ISSN, and type.
2. Checks whether an outlet with that ISSN (or a sufficiently similar name) already
   exists in outlet_info.json.
3. If not found, searches OpenAlex for the source (by ISSN first, then by name).
4. Creates a new outlet entry if needed.
5. Updates each paper in all_papers.jsonl with the DOI and outlet_id.

What requires manual follow-up
-------------------------------
- ``outlet_topic``: the 13-category classification cannot be assigned automatically.
  New outlets are written with ``outlet_topic = ""``. Run the reclassification step
  manually after this script completes.
- DOI discovery: finding which arXiv papers have a published DOI still requires
  manual lookup or external data sources.
- OpenAlex source disambiguation: if multiple similar sources are returned and none
  has an ISSN match, the best match is chosen by name similarity (>= 0.70).  Review
  the "REVIEW" lines in the output to confirm these matches.

Usage
-----
    uv run scripts/outlet_metadata/enrich_from_doi_mapping.py --mapping '{"1910.07762": "10.3390/e25101367"}'
    uv run scripts/outlet_metadata/enrich_from_doi_mapping.py --mapping-file mappings.json
    uv run scripts/outlet_metadata/enrich_from_doi_mapping.py --dry-run --mapping '{"1910.07762": "10.3390/e25101367"}'
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

from unifiedsciere.metadata.retriever.openalex import find_best_source

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUTLET_INFO_PATH = DATA_DIR / "metadata" / "outlet_info.json"
PAPERS_PATH = DATA_DIR / "metadata" / "unified" / "all_papers.jsonl"

OPENALEX_FIELDS = [
    "openalex_id", "issn_l", "h_index", "i10_index", "works_count",
    "cited_by_count", "mean_citedness_2yr", "openalex_type", "openalex_topics",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_outlets() -> list[dict]:
    with open(OUTLET_INFO_PATH) as f:
        return json.load(f)


def _save_outlets(outlets: list[dict]) -> None:
    with open(OUTLET_INFO_PATH, "w") as f:
        json.dump(outlets, f, indent=4, ensure_ascii=False)


def _load_papers() -> list[dict]:
    with open(PAPERS_PATH) as f:
        return [json.loads(l) for l in f if l.strip()]


def _save_papers(papers: list[dict]) -> None:
    with open(PAPERS_PATH, "w") as f:
        for p in papers:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")


def _next_outlet_id(outlets: list[dict]) -> str:
    nums = [int(o["id"].split("_")[1]) for o in outlets if o["id"].startswith("outlet_")]
    return f"outlet_{max(nums) + 1:03d}"


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _crossref(doi: str) -> dict | None:
    """Fetch basic metadata from Crossref for a DOI."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}"
    req = urllib.request.Request(url, headers={"User-Agent": "UnifiedSciERE/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            msg = json.loads(resp.read())["message"]
        container = msg.get("container-title") or []
        return {
            "title": (msg.get("title") or [""])[0],
            "container": container[0] if container else "",
            "type": msg.get("type", ""),
            "issn": msg.get("ISSN") or [],
            "publisher": msg.get("publisher", ""),
            "event": msg.get("event", {}),
        }
    except Exception as exc:
        print(f"  [crossref] error for {doi}: {exc}")
        return None


def _openalex_source_by_issn(issn: str) -> dict | None:
    """Fetch OpenAlex source by ISSN."""
    resp = httpx.get(
        "https://api.openalex.org/sources",
        params={"filter": f"issn:{issn}", "per_page": "1"},
        timeout=20,
    )
    time.sleep(0.15)
    if resp.status_code != 200 or not resp.json().get("results"):
        return None
    r = resp.json()["results"][0]
    stats = r.get("summary_stats") or {}
    short_id = r.get("id", "").rsplit("/", 1)[-1]
    topics = [
        t.get("display_name", "") for t in (r.get("topics") or [])[:10]
        if t.get("display_name")
    ]
    return {
        "openalex_id": short_id,
        "issn_l": r.get("issn_l", ""),
        "h_index": stats.get("h_index"),
        "i10_index": stats.get("i10_index"),
        "works_count": r.get("works_count"),
        "cited_by_count": r.get("cited_by_count"),
        "mean_citedness_2yr": stats.get("2yr_mean_citedness"),
        "openalex_type": r.get("type", ""),
        "openalex_topics": topics,
        "_display_name": r.get("display_name", ""),
    }


def _find_existing_outlet(
    outlets: list[dict],
    issn: str | None,
    container: str,
    min_similarity: float = 0.70,
) -> dict | None:
    """Return an existing outlet matching by ISSN or name similarity."""
    if issn:
        for o in outlets:
            if o.get("issn_l") == issn or issn in (o.get("openalex_topics") or []):
                return o
            # Check issn_l match
            if o.get("issn_l") and o["issn_l"] == issn:
                return o
    if container:
        scored = [(o, _similarity(container, o["name"])) for o in outlets]
        scored.sort(key=lambda x: x[1], reverse=True)
        if scored and scored[0][1] >= min_similarity:
            return scored[0][0]
    return None


def _outlet_type_from_crossref(cr_type: str) -> str:
    if cr_type == "journal-article":
        return "journal"
    if cr_type == "proceedings-article":
        return "conference"
    if cr_type == "book-chapter":
        return "book"
    return "other"


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def process_mapping(
    mapping: dict[str, str],
    dry_run: bool = False,
) -> None:
    outlets = _load_outlets()
    papers = _load_papers()
    paper_by_arxiv: dict[str, list[dict]] = {}
    for p in papers:
        aid = p.get("arxiv_id", "")
        if aid:
            paper_by_arxiv.setdefault(aid, []).append(p)

    outlets_added = 0
    papers_updated = 0

    for arxiv_id, doi in mapping.items():
        print(f"\narXiv:{arxiv_id} → doi:{doi}")

        # 1. Crossref
        cr = _crossref(doi)
        if not cr:
            print("  SKIP: Crossref lookup failed")
            continue
        container = cr["container"]
        issn_list = cr["issn"]
        issn_l = issn_list[0] if issn_list else ""
        cr_type = cr["type"]
        print(f"  Crossref: container='{container}' issn={issn_list} type={cr_type}")

        # 2. Check existing outlets
        existing = _find_existing_outlet(outlets, issn_l, container)
        if existing:
            outlet_id = existing["id"]
            print(f"  Matched existing outlet: {outlet_id} ({existing['name']})")
        else:
            # 3. Fetch OpenAlex source
            oa_source = None
            if issn_l:
                oa_source = _openalex_source_by_issn(issn_l)
            if oa_source is None and container:
                oa_source = find_best_source(container)
                if oa_source:
                    print(f"  REVIEW: OpenAlex matched '{oa_source.get('_display_name')}' by name — verify correctness")

            # 4. Create new outlet
            outlet_id = _next_outlet_id(outlets)
            outlet_type = _outlet_type_from_crossref(cr_type)
            # Use event name for proceedings if container is empty
            if not container and cr.get("event"):
                container = cr["event"].get("name", "")

            new_outlet: dict = {
                "name": container or doi,
                "abbr": "",
                "outlet_type": outlet_type,
                "outlet_topic": "",  # requires manual classification
                "wikidata_id": "",
                "canonical_url": "",
                "dblp_outlet_id": "",
                "identification_pattern": "",
                "id": outlet_id,
            }
            if oa_source:
                for field in OPENALEX_FIELDS:
                    if field in oa_source:
                        new_outlet[field] = oa_source[field]

            print(f"  New outlet: {outlet_id} '{new_outlet['name']}' (outlet_topic=MANUAL REQUIRED)")
            if not dry_run:
                outlets.append(new_outlet)
                outlets_added += 1

        # 5. Update papers
        targets = paper_by_arxiv.get(arxiv_id, [])
        if not targets:
            print(f"  WARNING: no paper found with arxiv_id={arxiv_id}")
            continue
        for p in targets:
            old_doi = p.get("doi", "")
            old_outlet = p.get("outlet_id", "")
            print(f"  Paper {p['doc_id']}: doi {old_doi!r}->{doi!r}, outlet {old_outlet!r}->{outlet_id!r}")
            if not dry_run:
                p["doi"] = doi
                p["outlet_id"] = outlet_id
                papers_updated += 1

    if not dry_run:
        _save_outlets(outlets)
        _save_papers(papers)
        print(f"\nSaved: {outlets_added} new outlet(s), {papers_updated} paper(s) updated.")
    else:
        print("\n(dry-run: no changes written)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mapping", help='JSON dict of {"arxiv_id": "doi", ...}')
    parser.add_argument("--mapping-file", help="Path to a JSON file with the mapping dict")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    args = parser.parse_args()

    if args.mapping_file:
        with open(args.mapping_file) as f:
            mapping = json.load(f)
    elif args.mapping:
        mapping = json.loads(args.mapping)
    else:
        parser.error("Provide --mapping or --mapping-file")

    process_mapping(mapping, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
