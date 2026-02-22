"""Build unified PaperMetadata records from existing per-source metadata.

Reads the existing JSONL metadata (arXiv for GSAP, Semantic Scholar for SciER,
ACL Anthology for SciNLP), converts each record into a PaperMetadata object,
enriches with DBLP where possible, and exports a single unified JSONL and BibTeX
file containing all papers.

Usage:
    python scripts/build_unified_metadata.py               # all corpora
    python scripts/build_unified_metadata.py --skip-dblp    # without DBLP enrichment
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unifiedsciere.metadata.retriever import dblp as dblp_retriever
from unifiedsciere.types import PaperMetadata, RepositoryLink

DATA_DIR = Path(__file__).parent.parent / "data"
METADATA_DIR = DATA_DIR / "metadata"
JSONL_DIR = METADATA_DIR / "jsonl"
OUT_DIR = METADATA_DIR / "unified"


# ---------------------------------------------------------------------------
# Per-source converters  (existing JSONL -> PaperMetadata)
# ---------------------------------------------------------------------------


def _extract_authors(raw: list[dict]) -> list[str]:
    """Extract author name strings from various API formats."""
    names = []
    for a in raw:
        name = a.get("name", "")
        if not name:
            # Semantic Scholar sometimes has authorId only
            continue
        names.append(name)
    return names


def _strip_arxiv_version(arxiv_id: str) -> str:
    """Remove version suffix: '1910.09700v2' -> '1910.09700'."""
    return re.sub(r"v\d+$", "", arxiv_id)


def _gsap_selection(doc_id: str) -> str:
    if doc_id.startswith("0"):
        return "huggingface_selection"
    elif doc_id.startswith("1"):
        return "arxiv_random_selection"
    return ""


def convert_gsap(record: dict) -> PaperMetadata:
    """Convert a GSAP (arXiv) metadata record."""
    meta = record["metadata"]
    doc_id = record["doc_id"]
    ext = meta.get("externalIds", {})
    arxiv_raw = ext.get("ArXiv", "")
    arxiv_id = _strip_arxiv_version(arxiv_raw)

    repos = []
    if arxiv_id:
        repos.append(
            RepositoryLink(
                repository="arxiv",
                url_landing_page=f"https://arxiv.org/abs/{arxiv_id}",
                url_pdf=meta.get("pdf_url", "") or f"https://arxiv.org/pdf/{arxiv_id}",
            )
        )

    return PaperMetadata(
        doc_id=doc_id,
        dataset="gsap",
        split=record["split"],
        title=meta.get("title", ""),
        authors=_extract_authors(meta.get("authors", [])),
        year=meta.get("year"),
        venue=meta.get("venue", "") or "",
        abstract=meta.get("abstract", "") or "",
        article_type="preprint",
        arxiv_id=arxiv_id,
        doi=meta.get("doi", "") or "",
        selection=_gsap_selection(doc_id),
        repositories=repos,
    )


def convert_scier(record: dict) -> PaperMetadata:
    """Convert a SciER (Semantic Scholar) metadata record."""
    meta = record["metadata"]
    doc_id = str(record["doc_id"])
    ext = meta.get("externalIds", {})
    arxiv_id = _strip_arxiv_version(ext.get("ArXiv", "") or "")
    dblp_key = ext.get("DBLP", "") or ""

    repos = []
    # Semantic Scholar
    s2_url = meta.get("url", "")
    if s2_url:
        repos.append(
            RepositoryLink(
                repository="semantic_scholar",
                url_landing_page=s2_url,
            )
        )
    # arXiv (if available)
    if arxiv_id:
        repos.append(
            RepositoryLink(
                repository="arxiv",
                url_landing_page=f"https://arxiv.org/abs/{arxiv_id}",
                url_pdf=f"https://arxiv.org/pdf/{arxiv_id}",
            )
        )
    # Open access PDF from S2
    oa_pdf = (meta.get("openAccessPdf") or {}).get("url", "")
    if oa_pdf and repos:
        # Attach to the first repo if it doesn't have a pdf yet
        for r in repos:
            if not r.url_pdf:
                r.url_pdf = oa_pdf
                break

    # Determine article type from S2 publication types
    pub_types = meta.get("publicationTypes") or []
    s2_venue = meta.get("venue", "") or ""
    if any("Conference" in t for t in pub_types):
        article_type = "conference_proceeding"
    elif any("Journal" in t for t in pub_types):
        if s2_venue.lower() in ("arxiv.org", "arxiv"):
            article_type = "preprint"
        else:
            article_type = "journal"
    else:
        article_type = "preprint" if arxiv_id else ""

    return PaperMetadata(
        doc_id=doc_id,
        dataset="scier",
        split=record["split"],
        title=meta.get("title", ""),
        authors=_extract_authors(meta.get("authors", [])),
        year=meta.get("year"),
        venue=s2_venue,
        abstract=meta.get("abstract", "") or "",
        article_type=article_type,
        doi=ext.get("DOI", "") or "",
        arxiv_id=arxiv_id,
        s2_corpus_id=str(ext.get("CorpusId", "") or ""),
        s2_paper_id=meta.get("paperId", ""),
        dblp_id=dblp_key,
        repositories=repos,
    )


def convert_scier_ood(record: dict) -> PaperMetadata:
    """Convert a SciER-OOD record (same format as SciER but from bib)."""
    p = convert_scier(record)
    p.dataset = "scier_ood"
    return p


def convert_scinlp(record: dict) -> PaperMetadata:
    """Convert a SciNLP (ACL Anthology) metadata record."""
    meta = record["metadata"]
    doc_id = record["doc_id"]
    ext = meta.get("externalIds", {})
    acl_id = ext.get("ACL", "") or ""
    doi = ext.get("DOI", "") or ""
    year_raw = meta.get("year", "")
    year = int(year_raw) if str(year_raw).isdigit() else None

    repos = []
    acl_url = meta.get("url", "")
    pdf_name = meta.get("pdf", "")
    if acl_url:
        repos.append(
            RepositoryLink(
                repository="acl_anthology",
                url_landing_page=acl_url,
                url_pdf=f"https://aclanthology.org/{pdf_name}.pdf" if pdf_name else "",
            )
        )

    return PaperMetadata(
        doc_id=doc_id,
        dataset="scinlp",
        split=record["split"],
        title=meta.get("title", ""),
        authors=_extract_authors(meta.get("authors", [])),
        year=year,
        venue=meta.get("venue", "") or "",
        abstract=meta.get("abstract", "") or "",
        article_type="conference_proceeding",
        conference="ACL",
        conference_year=year,
        doi=doi,
        acl_id=acl_id,
        repositories=repos,
    )


# ---------------------------------------------------------------------------
# DBLP enrichment
# ---------------------------------------------------------------------------

# Map DBLP type strings to our article_type
_DBLP_TYPE_MAP = {
    dblp_retriever.TYPE_CONFERENCE: "conference_proceeding",
    dblp_retriever.TYPE_JOURNAL: "journal",
    dblp_retriever.TYPE_INFORMAL: "preprint",
}


def enrich_with_dblp(papers: list[PaperMetadata]) -> list[PaperMetadata]:
    """Enrich papers with DBLP metadata (venue, conference, type, DOI)."""
    # Only look up papers that don't already have a DBLP key
    to_lookup = [(i, p) for i, p in enumerate(papers) if not p.dblp_id and p.title]

    if not to_lookup:
        print("  All papers already have DBLP IDs — nothing to look up.")
        return papers

    titles = [p.title for _, p in to_lookup]
    years = [p.year for _, p in to_lookup]

    print(f"  Looking up {len(titles)} papers on DBLP...")
    results = dblp_retriever.get_metadata_batch(titles, years=years)

    found = 0
    for (idx, paper), dblp in zip(to_lookup, results):
        if dblp is None:
            continue
        found += 1
        _apply_dblp(paper, dblp)

    print(f"  DBLP: matched {found}/{len(to_lookup)} papers.")
    return papers


def _apply_dblp(paper: PaperMetadata, dblp: dict) -> None:
    """Merge DBLP data into an existing PaperMetadata object."""
    paper.dblp_id = dblp.get("dblp_key", "")

    # Add DBLP repository link
    dblp_url = dblp.get("dblp_url", "")
    ee = dblp.get("ee", "")
    if dblp_url:
        paper.repositories.append(
            RepositoryLink(
                repository="dblp",
                url_landing_page=dblp_url,
                url_pdf=ee if ee.endswith(".pdf") else "",
            )
        )

    # Fill in DOI if missing
    if not paper.doi and dblp.get("doi"):
        paper.doi = dblp["doi"]

    # Fill in article_type / conference from the published version
    dblp_type = dblp.get("type", "")
    mapped_type = _DBLP_TYPE_MAP.get(dblp_type, "")

    if mapped_type and mapped_type != "preprint":
        # DBLP found a published version — upgrade article_type
        paper.article_type = mapped_type
        dblp_venue = dblp.get("venue", "")
        if dblp_venue and dblp_venue != "CoRR":
            paper.conference = dblp_venue
            dblp_year = dblp.get("year")
            if dblp_year:
                paper.conference_year = dblp_year
            # Update venue if it was empty or just arXiv
            if not paper.venue or paper.venue.lower() in (
                "arxiv.org",
                "arxiv",
                "corr",
                "",
            ):
                paper.venue = dblp_venue
    elif mapped_type == "preprint" and not paper.article_type:
        paper.article_type = "preprint"


# ---------------------------------------------------------------------------
# Loading existing per-source JSONL
# ---------------------------------------------------------------------------


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if r.get("metadata") is not None:
                records.append(r)
    return records


def load_all_sources() -> list[PaperMetadata]:
    """Load all existing metadata and convert to PaperMetadata."""
    papers: list[PaperMetadata] = []

    # GSAP
    gsap_path = JSONL_DIR / "gsap_all.jsonl"
    if gsap_path.exists():
        print(f"Loading GSAP from {gsap_path}")
        for r in _load_jsonl(gsap_path):
            papers.append(convert_gsap(r))
        print(f"  {sum(1 for p in papers if p.dataset == 'gsap')} GSAP papers")

    # SciER (the combined scier.jsonl has dev entries; split files have all)
    for split_name, fname in [
        ("train", "scier_train.jsonl"),
        ("dev", "scier_dev.jsonl"),
        ("test", "scier_test.jsonl"),
    ]:
        path = JSONL_DIR / fname
        if path.exists():
            for r in _load_jsonl(path):
                papers.append(convert_scier(r))
    scier_count = sum(1 for p in papers if p.dataset == "scier")
    if scier_count:
        print(f"Loading SciER from split files")
        print(f"  {scier_count} SciER papers")

    # SciER-OOD — we don't have a separate JSONL, build from bib
    # Skip if no JSONL exists; the bib-based approach is handled separately

    # SciNLP
    scinlp_path = JSONL_DIR / "scinlp.jsonl"
    if scinlp_path.exists():
        print(f"Loading SciNLP from {scinlp_path}")
        for r in _load_jsonl(scinlp_path):
            papers.append(convert_scinlp(r))
        print(f"  {sum(1 for p in papers if p.dataset == 'scinlp')} SciNLP papers")

    # Deduplicate by (dataset, doc_id)
    seen: set[tuple[str, str]] = set()
    unique: list[PaperMetadata] = []
    for p in papers:
        key = (p.dataset, p.doc_id)
        if key not in seen:
            seen.add(key)
            unique.append(p)
    if len(unique) < len(papers):
        print(f"Deduplicated: {len(papers)} -> {len(unique)} papers")
    return unique


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def export_jsonl(papers: list[PaperMetadata], path: Path) -> None:
    """Write papers as one-JSON-per-line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for p in papers:
            f.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")
    print(f"Wrote {len(papers)} records to {path}")


def export_bib(papers: list[PaperMetadata], path: Path) -> None:
    """Write papers as a BibTeX file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = [p.to_bib() for p in papers]
    with open(path, "w") as f:
        f.write("\n\n".join(entries) + "\n")
    print(f"Wrote {len(entries)} BibTeX entries to {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Build unified metadata")
    parser.add_argument(
        "--skip-dblp",
        action="store_true",
        help="Skip DBLP enrichment (faster, offline)",
    )
    args = parser.parse_args()

    papers = load_all_sources()
    print(f"\nTotal: {len(papers)} papers")

    if not args.skip_dblp:
        print("\nEnriching with DBLP...")
        enrich_with_dblp(papers)

    # Summary
    print("\n--- Summary ---")
    from collections import Counter

    by_dataset = Counter(p.dataset for p in papers)
    for ds, n in sorted(by_dataset.items()):
        print(f"  {ds}: {n}")
    by_type = Counter(p.article_type for p in papers)
    print(f"  article_type: {dict(by_type)}")
    with_dblp = sum(1 for p in papers if p.dblp_id)
    print(f"  with DBLP ID: {with_dblp}/{len(papers)}")
    with_doi = sum(1 for p in papers if p.doi)
    print(f"  with DOI: {with_doi}/{len(papers)}")
    with_conference = sum(1 for p in papers if p.conference)
    print(f"  with conference: {with_conference}/{len(papers)}")

    # Export
    print()
    export_jsonl(papers, OUT_DIR / "all_papers.jsonl")
    export_bib(papers, OUT_DIR / "all_papers.bib")


if __name__ == "__main__":
    main()
