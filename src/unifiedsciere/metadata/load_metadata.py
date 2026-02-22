"""Load paper metadata from Semantic Scholar / arXiv and export as BibTeX + raw JSON."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from unifiedsciere.metadata.retriever.acl import (
    get_metadata_batch as acl_get_metadata_batch,
)
from unifiedsciere.metadata.retriever.arxiv import (
    extract_arxiv_id,
)
from unifiedsciere.metadata.retriever.arxiv import (
    get_metadata_batch as arxiv_get_metadata_batch,
)
from unifiedsciere.metadata.retriever.semantic_scholar import (
    get_metadata_batch,
    get_metadata_by_corpus_id,
)

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
GOLD_DIR = DATA_DIR / "gold"
METADATA_DIR = DATA_DIR / "metadata"


# ---------------------------------------------------------------------------
# BibTeX conversion
# ---------------------------------------------------------------------------


def _make_bib_key(meta: dict) -> str:
    """Generate a citekey like 'Wei2019' from metadata."""
    first_author = meta.get("authors", [{}])[0].get("name", "Unknown")
    surname = first_author.split()[-1]
    year = meta.get("year", "")
    # Remove non-alphanumeric characters
    surname = re.sub(r"[^a-zA-Z]", "", surname)
    return f"{surname}{year}"


def _escape_bibtex(text: str) -> str:
    """Escape special BibTeX characters."""
    if not text:
        return ""
    # Protect braces that are already there, escape & and %
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("_", r"\_")
    return text


def metadata_to_bib_entry(
    meta: dict,
    doc_id: str,
    group: str,
) -> str:
    """Convert a Semantic Scholar metadata dict to a BibTeX entry string.

    Args:
        meta: Metadata dict from Semantic Scholar API.
        doc_id: The original doc_id from the dataset.
        group: The split name (e.g. 'train', 'dev', 'test').

    Returns:
        A BibTeX @article{...} string.
    """
    key = _make_bib_key(meta)
    authors = " and ".join(a["name"] for a in meta.get("authors", []))
    title = meta.get("title", "")
    year = meta.get("year", "")
    venue = meta.get("venue", "")
    abstract = meta.get("abstract", "") or ""
    url = meta.get("url", "")

    ext = meta.get("externalIds", {})
    doi = ext.get("DOI", "")
    arxiv = ext.get("ArXiv", "")

    lines = [
        f"@article{{{key},",
        f"  doc_id = {{{doc_id}}},",
        f"  group = {{{group}}},",
        f"  title = {{{{{_escape_bibtex(title)}}}}},",
        f"  author = {{{_escape_bibtex(authors)}}},",
        f"  year = {{{year}}},",
        f"  venue = {{{_escape_bibtex(venue)}}},",
        f"  abstract = {{{_escape_bibtex(abstract)}}},",
    ]
    if doi:
        lines.append(f"  doi = {{{doi}}},")
    if arxiv:
        lines.append(f"  arxiv = {{{arxiv}}},")
    if url:
        lines.append(f"  url = {{{url}}},")
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Loading doc_ids from data splits
# ---------------------------------------------------------------------------

SPLIT_FILES = {
    "dev": "scier_dev.jsonl",
    "test": "scier_test.jsonl",
    "train": "scier_train.jsonl",
}

GSAP_SPLIT_FILES = {
    "dev": "gsap_dev.jsonl",
    "test": "gsap_test.jsonl",
    "train": "gsap_train.jsonl",
}

SCINLP_SPLIT_FILES = {
    "dev": "scinlp_dev.jsonl",
    "test": "scinlp_test.jsonl",
    "train": "scinlp_train.jsonl",
}


def load_doc_ids(splits: list[str] | None = None) -> list[tuple[str, str]]:
    """Load (doc_id, split) pairs from the gold data files.

    Args:
        splits: Which splits to load. None means all splits.

    Returns:
        List of (doc_id, split_name) tuples.
    """
    if splits is None:
        splits = list(SPLIT_FILES.keys())

    pairs = []
    for split in splits:
        fname = SPLIT_FILES[split]
        path = GOLD_DIR / fname
        with open(path) as f:
            for line in f:
                doc = json.loads(line)
                pairs.append((doc["doc_id"], split))
    return pairs


# ---------------------------------------------------------------------------
# Raw JSON persistence
# ---------------------------------------------------------------------------


def _save_raw_json(
    pairs: list[tuple[str, str]],
    results: list[dict | None],
    json_path: Path,
) -> None:
    """Save raw API responses as a JSONL file (one object per line).

    Each line contains {"doc_id": ..., "split": ..., "metadata": ...}.
    """
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        for (doc_id, split), meta in zip(pairs, results):
            record = {
                "doc_id": doc_id,
                "split": split,
                "metadata": meta,  # None when fetch failed
            }
            f.write(json.dumps(record) + "\n")
    print(f"Wrote {len(results)} raw JSON records to {json_path}")


# ---------------------------------------------------------------------------
# Full pipeline: fetch metadata, write .jsonl + .bib
# ---------------------------------------------------------------------------


def _split_suffix(splits: list[str] | None) -> str:
    """Return a file-name suffix like '_dev' or '_all' based on selected splits."""
    if splits is None or set(splits) == set(SPLIT_FILES.keys()):
        return "_all"
    return "_" + "_".join(sorted(splits))


def build_scier_bib(
    splits: list[str] | None = None,
    limit: int | None = None,
    api_key: str | None = None,
) -> None:
    """Fetch metadata for SciERC doc_ids and write per-split .jsonl + .bib.

    Args:
        splits: Which splits to fetch (e.g. ["dev"]). None = all.
        limit: If set, only fetch the first N documents (for testing).
        api_key: Optional Semantic Scholar API key.
    """
    pairs = load_doc_ids(splits=splits)
    if limit is not None:
        pairs = pairs[:limit]

    doc_ids = [p[0] for p in pairs]
    suffix = _split_suffix(splits)

    print(f"Fetching metadata for {len(doc_ids)} papers...")
    results = get_metadata_batch(doc_ids, api_key=api_key)

    # --- save raw JSON ---
    json_path = METADATA_DIR / "jsonl" / f"scier{suffix}.jsonl"
    _save_raw_json(pairs, results, json_path)

    # --- save BibTeX ---
    bib_path = METADATA_DIR / "bib" / f"scier{suffix}.bib"
    entries = []
    failed = []
    for (doc_id, split), meta in zip(pairs, results):
        if meta is None:
            failed.append(doc_id)
            continue
        entry = metadata_to_bib_entry(meta, doc_id=doc_id, group=split)
        entries.append(entry)

    bib_path.parent.mkdir(parents=True, exist_ok=True)
    with open(bib_path, "w") as f:
        f.write("\n\n".join(entries) + "\n")

    print(f"Wrote {len(entries)} BibTeX entries to {bib_path}")
    if failed:
        print(f"Failed to fetch {len(failed)} papers: {failed}")


def load_gsap_doc_ids(splits: list[str] | None = None) -> list[tuple[str, str]]:
    """Load (doc_id, split) pairs from the GSAP gold data files.

    Args:
        splits: Which splits to load. None means all splits.

    Returns:
        List of (doc_id, split_name) tuples.
    """
    if splits is None:
        splits = list(GSAP_SPLIT_FILES.keys())

    pairs = []
    for split in splits:
        fname = GSAP_SPLIT_FILES[split]
        path = GOLD_DIR / fname
        with open(path) as f:
            for line in f:
                doc = json.loads(line)
                pairs.append((doc["doc_id"], split))
    return pairs


def _gsap_split_suffix(splits: list[str] | None) -> str:
    """Return a file-name suffix for GSAP based on selected splits."""
    if splits is None or set(splits) == set(GSAP_SPLIT_FILES.keys()):
        return "_all"
    return "_" + "_".join(sorted(splits))


def build_gsap_bib(
    splits: list[str] | None = None,
    limit: int | None = None,
) -> None:
    """Fetch metadata for GSAP doc_ids from arXiv and write .jsonl + .bib.

    Args:
        splits: Which splits to fetch (e.g. ["dev"]). None = all.
        limit: If set, only fetch the first N documents (for testing).
    """
    pairs = load_gsap_doc_ids(splits=splits)
    if limit is not None:
        pairs = pairs[:limit]

    doc_ids = [p[0] for p in pairs]
    arxiv_ids = [extract_arxiv_id(d) for d in doc_ids]
    suffix = _gsap_split_suffix(splits)

    print(f"Fetching arXiv metadata for {len(arxiv_ids)} papers...")
    results = arxiv_get_metadata_batch(arxiv_ids)

    # --- save raw JSON ---
    json_path = METADATA_DIR / "jsonl" / f"gsap{suffix}.jsonl"
    _save_raw_json(pairs, results, json_path)

    # --- save BibTeX ---
    bib_path = METADATA_DIR / "bib" / f"gsap{suffix}.bib"
    entries = []
    failed = []
    for (doc_id, split), meta in zip(pairs, results):
        if meta is None:
            failed.append(doc_id)
            continue
        entry = metadata_to_bib_entry(meta, doc_id=doc_id, group=split)
        entries.append(entry)

    bib_path.parent.mkdir(parents=True, exist_ok=True)
    with open(bib_path, "w") as f:
        f.write("\n\n".join(entries) + "\n")

    print(f"Wrote {len(entries)} BibTeX entries to {bib_path}")
    if failed:
        print(f"Failed to fetch {len(failed)} papers: {failed}")


def load_scinlp_doc_keys(splits: list[str] | None = None) -> list[tuple[str, str]]:
    """Load unique (doc_key, split) pairs from the SciNLP gold data files.

    SciNLP uses ``doc_key`` (ACL Anthology IDs) instead of ``doc_id``.

    Args:
        splits: Which splits to load. None means all splits.

    Returns:
        List of (doc_key, split_name) tuples, deduplicated by doc_key.
    """
    if splits is None:
        splits = list(SCINLP_SPLIT_FILES.keys())

    seen: set[str] = set()
    pairs: list[tuple[str, str]] = []
    for split in splits:
        fname = SCINLP_SPLIT_FILES[split]
        path = GOLD_DIR / fname
        with open(path) as f:
            for line in f:
                doc = json.loads(line)
                key = doc["doc_key"]
                if key not in seen:
                    seen.add(key)
                    pairs.append((key, split))
    return pairs


def _scinlp_split_suffix(splits: list[str] | None) -> str:
    """Return a file-name suffix for SciNLP based on selected splits."""
    if splits is None or set(splits) == set(SCINLP_SPLIT_FILES.keys()):
        return ""
    return "_" + "_".join(sorted(splits))


def build_scinlp_bib(
    splits: list[str] | None = None,
    limit: int | None = None,
) -> None:
    """Fetch metadata for SciNLP doc_keys from ACL Anthology and write .jsonl + .bib.

    Args:
        splits: Which splits to fetch (e.g. ["dev"]). None = all.
        limit: If set, only fetch the first N documents (for testing).
    """
    pairs = load_scinlp_doc_keys(splits=splits)
    if limit is not None:
        pairs = pairs[:limit]

    doc_keys = [p[0] for p in pairs]
    suffix = _scinlp_split_suffix(splits)

    print(f"Fetching ACL Anthology metadata for {len(doc_keys)} papers...")
    results = acl_get_metadata_batch(doc_keys)

    # --- save raw JSON ---
    json_path = METADATA_DIR / "jsonl" / f"scinlp{suffix}.jsonl"
    _save_raw_json(pairs, results, json_path)

    # --- save BibTeX ---
    bib_path = METADATA_DIR / "bib" / f"scinlp{suffix}.bib"
    entries = []
    failed = []
    for (doc_key, split), meta in zip(pairs, results):
        if meta is None:
            failed.append(doc_key)
            continue
        entry = metadata_to_bib_entry(meta, doc_id=doc_key, group=split)
        entries.append(entry)

    bib_path.parent.mkdir(parents=True, exist_ok=True)
    with open(bib_path, "w") as f:
        f.write("\n\n".join(entries) + "\n")

    print(f"Wrote {len(entries)} BibTeX entries to {bib_path}")
    if failed:
        print(f"Failed to fetch {len(failed)} papers: {failed}")


if __name__ == "__main__":
    # Usage:
    #   python -m unifiedsciere.metadata.load_metadata scier              # all scier splits
    #   python -m unifiedsciere.metadata.load_metadata scier dev          # single split
    #   python -m unifiedsciere.metadata.load_metadata scier dev 5        # first 5 from dev
    #   python -m unifiedsciere.metadata.load_metadata gsap               # all gsap splits
    #   python -m unifiedsciere.metadata.load_metadata gsap dev 3         # first 3 from gsap dev
    #   python -m unifiedsciere.metadata.load_metadata scinlp             # all scinlp splits
    #   python -m unifiedsciere.metadata.load_metadata scinlp dev 3       # first 3 from scinlp dev
    dataset = "scier"
    splits = None
    limit = None
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
    if len(sys.argv) > 2:
        splits = [sys.argv[2]]
    if len(sys.argv) > 3:
        limit = int(sys.argv[3])

    if dataset == "gsap":
        build_gsap_bib(splits=splits, limit=limit)
    elif dataset == "scinlp":
        build_scinlp_bib(splits=splits, limit=limit)
    else:
        build_scier_bib(splits=splits, limit=limit)
