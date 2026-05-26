"""Read unified metadata from JSONL and optionally convert to pandas DataFrame.

This module provides functions to:
- Load PaperMetadata records from the unified JSONL file
- Load the outlet catalogue
- Join outlet information back into papers
- Convert to a pandas DataFrame for analysis

Usage (loading metadata)::

    from unifiedsciere.metadata.read_metadata import load_papers, load_outlets

    papers = load_papers()              # list of PaperMetadata
    outlets = load_outlets()            # dict: outlet_id -> Outlet

Usage (as DataFrame)::

    from unifiedsciere.metadata.read_metadata import read_as_dataframe

    df = read_as_dataframe()            # pandas DataFrame with joined outlet info
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from unifiedsciere.types import Outlet, PaperMetadata, RepositoryLink

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
METADATA_DIR = DATA_DIR / "metadata"
UNIFIED_DIR = METADATA_DIR / "unified"
OUTLET_INFO_PATH = METADATA_DIR / "outlet_info.json"
ALL_PAPERS_PATH = UNIFIED_DIR / "all_papers.jsonl"


# ---------------------------------------------------------------------------
# Load outlets
# ---------------------------------------------------------------------------


def load_outlets(path: Path = OUTLET_INFO_PATH) -> dict[str, Outlet]:
    """Load the outlet catalogue as a dictionary: outlet_id -> Outlet.

    Args:
        path: Path to outlet_info.json

    Returns:
        Dictionary mapping outlet IDs to Outlet objects.
    """
    with open(path) as f:
        raw: list[dict] = json.load(f)

    outlets = {}
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
            identification_pattern=item.get("identification_pattern", ""),
            openalex_id=item.get("openalex_id") or "",
            issn_l=item.get("issn_l") or "",
            h_index=item.get("h_index"),
            i10_index=item.get("i10_index"),
            works_count=item.get("works_count"),
            cited_by_count=item.get("cited_by_count"),
            mean_citedness_2yr=item.get("mean_citedness_2yr"),
            openalex_type=item.get("openalex_type") or "",
            openalex_topics=item.get("openalex_topics") or [],
        )
        outlets[outlet.id] = outlet

    return outlets


# ---------------------------------------------------------------------------
# Load papers
# ---------------------------------------------------------------------------


def _parse_paper_dict(d: dict[str, Any]) -> PaperMetadata:
    """Parse a single paper dict (from JSONL) into a PaperMetadata object."""
    # Reconstruct RepositoryLink objects
    repos = []
    for r in d.get("repositories", []):
        repos.append(
            RepositoryLink(
                repository=r.get("repository", ""),
                url_landing_page=r.get("url_landing_page", ""),
                url_pdf=r.get("url_pdf", ""),
                url_repository=r.get("url_repository", ""),
            )
        )

    return PaperMetadata(
        doc_id=d.get("doc_id", ""),
        dataset=d.get("dataset", ""),
        split=d.get("split", ""),
        title=d.get("title", ""),
        authors=d.get("authors", []),
        year=d.get("year"),
        venue=d.get("venue", ""),
        abstract=d.get("abstract", ""),
        article_type=d.get("article_type", ""),
        conference=d.get("conference", ""),
        conference_year=d.get("conference_year"),
        doi=d.get("doi", ""),
        doi_preprint=d.get("doi_preprint", ""),
        arxiv_id=d.get("arxiv_id", ""),
        acl_id=d.get("acl_id", ""),
        s2_corpus_id=d.get("s2_corpus_id", ""),
        s2_paper_id=d.get("s2_paper_id", ""),
        dblp_id=d.get("dblp_id", ""),
        dblp_preprint_id=d.get("dblp_preprint_id", ""),
        repositories=repos,
        outlet_id=d.get("outlet_id", ""),
        selection=d.get("selection", ""),
        openalex_id=d.get("openalex_id", ""),
        cited_by_count=d.get("cited_by_count"),
        references=d.get("references", []),
        openalex_topics=d.get("openalex_topics", []),
        s2_fields_of_study=d.get("s2_fields_of_study", []),
    )


def load_papers(path: Path = ALL_PAPERS_PATH) -> list[PaperMetadata]:
    """Load all papers from the unified JSONL file.

    Args:
        path: Path to all_papers.jsonl

    Returns:
        List of PaperMetadata objects.
    """
    papers = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            papers.append(_parse_paper_dict(d))
    return papers


# ---------------------------------------------------------------------------
# Convert to DataFrame
# ---------------------------------------------------------------------------


def read_as_dataframe(
    papers_path: Path = ALL_PAPERS_PATH,
    outlets_path: Path = OUTLET_INFO_PATH,
) -> "pd.DataFrame":
    """Load papers and outlets, then convert to a pandas DataFrame.

    The DataFrame includes:
    - All PaperMetadata fields (scalar fields only)
    - Outlet fields (prefixed with 'outlet_') joined by outlet_id

    Complex fields (authors, repositories) are included as-is (list columns).

    Args:
        papers_path: Path to all_papers.jsonl
        outlets_path: Path to outlet_info.json

    Returns:
        A pandas DataFrame with one row per paper.
    """

    # Load data
    papers = load_papers(papers_path)
    outlets = load_outlets(outlets_path)

    # Convert papers to records
    records = []
    for paper in papers:
        # Start with the paper dict
        rec = paper.to_dict()

        # Join outlet information if available
        if paper.outlet_id and paper.outlet_id in outlets:
            outlet = outlets[paper.outlet_id]
            rec["outlet_name"] = outlet.name
            rec["outlet_abbr"] = outlet.abbr
            rec["outlet_type"] = outlet.outlet_type
            rec["outlet_topic"] = outlet.outlet_topic
            rec["outlet_wikidata_id"] = outlet.wikidata_id
            rec["outlet_canonical_url"] = outlet.canonical_url
        else:
            # No outlet matched
            rec["outlet_name"] = None
            rec["outlet_abbr"] = None
            rec["outlet_type"] = None
            rec["outlet_topic"] = None
            rec["outlet_wikidata_id"] = None
            rec["outlet_canonical_url"] = None

        records.append(rec)

    df = pd.DataFrame(records)
    return df


# ---------------------------------------------------------------------------
# CLI for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--df" in sys.argv or "--dataframe" in sys.argv:
        df = read_as_dataframe()
        print(f"Loaded {len(df)} papers into DataFrame")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nDataset distribution:")
        print(df["dataset"].value_counts())
        print(f"\nOutlet type distribution:")
        print(df["outlet_type"].value_counts(dropna=False))
        print(f"\nFirst paper:")
        print(df.iloc[0].to_dict())
    else:
        papers = load_papers()
        outlets = load_outlets()
        print(f"Loaded {len(papers)} papers")
        print(f"Loaded {len(outlets)} outlets")
        print(f"\nDataset distribution:")
        from collections import Counter

        print(dict(Counter(p.dataset for p in papers)))
        print(f"\nPapers with outlet_id: {sum(1 for p in papers if p.outlet_id)}")
        print(f"\nFirst paper:")
        print(papers[0])
