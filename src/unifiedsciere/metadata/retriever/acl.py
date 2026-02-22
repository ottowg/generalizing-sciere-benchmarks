"""Retrieve paper metadata from the ACL Anthology."""

from __future__ import annotations

import re

from acl_anthology import Anthology

# Singleton so the (expensive) repo clone only happens once per process.
_anthology: Anthology | None = None


def _get_anthology() -> Anthology:
    global _anthology
    if _anthology is None:
        _anthology = Anthology.from_repo()
    return _anthology


def doc_key_to_acl_id(doc_key: str) -> str:
    """Convert a SciNLP doc_key to a clean ACL Anthology ID.

    Strips suffixes that are not part of the canonical ACL ID:
      - '.grobid'                          (processing artefact)
      - trailing version   'vN'            (e.g. P19-1028v2)
      - trailing page-range '-START-END'   (e.g. 2023.acl-long.362-1-10)

    Examples:
        >>> doc_key_to_acl_id('2020.acl-main.21.grobid')
        '2020.acl-main.21'
        >>> doc_key_to_acl_id('P19-1028v2.grobid')
        'P19-1028'
        >>> doc_key_to_acl_id('2023.acl-long.362-1-10.grobid')
        '2023.acl-long.362'
    """
    acl_id = doc_key.removesuffix(".grobid")
    # Remove version suffix (vN)
    acl_id = re.sub(r"v\d+$", "", acl_id)
    # Remove page-range suffix (-START-END) for new-style IDs
    # Only applies when there are at least two trailing dash-number groups
    # after the main paper number (e.g. .362-1-10 but not P19-1028)
    acl_id = re.sub(r"(-\d+){2}$", "", acl_id)
    return acl_id


def _paper_to_dict(paper, doc_key: str, acl_id: str) -> dict:
    """Convert an acl_anthology Paper object to our metadata dict schema."""
    authors = [{"name": f"{a.name.first} {a.name.last}"} for a in paper.authors]
    # title and abstract are MarkupText objects; convert to plain str
    title = str(paper.title) if paper.title else ""
    abstract = str(paper.abstract) if paper.abstract else ""
    venue = str(paper.parent.title) if paper.parent and paper.parent.title else ""

    return {
        "title": title,
        "authors": authors,
        "year": paper.year,
        "venue": venue,
        "abstract": abstract,
        "url": f"https://aclanthology.org/{acl_id}/",
        "externalIds": {
            "ACL": acl_id,
            "DOI": paper.doi or "",
        },
        "doc_key": doc_key,
        "bibkey": paper.bibkey,
        "pdf": str(paper.pdf.name) if paper.pdf else "",
    }


def get_metadata(doc_key: str) -> dict | None:
    """Retrieve metadata for a single SciNLP paper.

    Args:
        doc_key: SciNLP document key (e.g. '2020.acl-main.21.grobid').

    Returns:
        Metadata dict or None if the paper was not found.
    """
    anthology = _get_anthology()
    acl_id = doc_key_to_acl_id(doc_key)
    paper = anthology.get(acl_id)
    if paper is None:
        return None
    return _paper_to_dict(paper, doc_key, acl_id)


def get_metadata_batch(doc_keys: list[str]) -> list[dict | None]:
    """Retrieve metadata for multiple SciNLP papers.

    Args:
        doc_keys: List of SciNLP document keys.

    Returns:
        List of metadata dicts (None for papers not found), same order as input.
    """
    anthology = _get_anthology()
    results: list[dict | None] = []
    for doc_key in doc_keys:
        acl_id = doc_key_to_acl_id(doc_key)
        paper = anthology.get(acl_id)
        if paper is None:
            print(f"  WARNING: ACL paper not found: {acl_id} (from {doc_key})")
            results.append(None)
        else:
            results.append(_paper_to_dict(paper, doc_key, acl_id))
    return results
