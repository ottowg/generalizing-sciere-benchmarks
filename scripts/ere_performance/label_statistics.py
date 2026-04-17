"""Label statistics per dataset.

Computes per-paper annotation counts by label type for violin plot visualisation
in the webapp.  All splits (train/dev/test) are pooled.

Output: data/label_statistics.json

Usage:
    uv run python scripts/ere_performance/label_statistics.py
"""

import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from typing import Literal

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.metadata.read_metadata import load_papers
from unifiedsciere.paths import ensure_output

DATASETS: list[Literal["gsap-ere", "scier", "scinlp"]] = ["gsap-ere", "scier", "scinlp"]
SPLITS = ["train", "dev", "test"]


def _summary(counts: list[int]) -> dict:
    """Compute summary statistics for a list of per-paper counts."""
    if not counts:
        return {"mean": 0, "median": 0, "max": 0, "n": 0}
    return {
        "mean": round(statistics.mean(counts), 2),
        "median": round(statistics.median(counts), 2),
        "max": max(counts),
        "n": len(counts),
    }


def _entity_stats(dataset: str) -> dict:
    """Per-paper entity label counts for a dataset (all splits pooled)."""
    per_doc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for split in SPLITS:
        corpus = load_corpus(dataset, split, data_type="gold")
        for m in corpus.mentions:
            per_doc[m.document_id][m.label] += 1

    all_doc_ids = list(per_doc.keys())
    labels = sorted({lbl for counts in per_doc.values() for lbl in counts})
    n_docs = len(all_doc_ids)

    by_label: dict[str, dict] = {}
    for label in labels:
        per_paper_all = [per_doc[doc_id].get(label, 0) for doc_id in all_doc_ids]
        per_paper_present = [c for c in per_paper_all if c > 0]
        by_label[label] = {
            # Full distribution incl. zeros (for proportion-of-papers info)
            "per_paper": per_paper_all,
            # Distribution restricted to papers that have ≥1 annotation (for violin shape)
            "per_paper_present": per_paper_present,
            "n_papers_total": n_docs,
            "n_papers_present": len(per_paper_present),
            "pct_papers": round(100 * len(per_paper_present) / n_docs, 1) if n_docs else 0,
            "summary_all": _summary(per_paper_all),
            "summary_present": _summary(per_paper_present),
        }

    return {"labels": labels, "n_papers": n_docs, "by_label": by_label}


def _entities_by_year(dataset: str, doc_year: dict[str, int]) -> dict:
    """Mean entity count per paper per year, broken down by label.

    Returns: {year_str: {n_papers, total_mean, by_label: {label: mean}}}
    """
    # per_doc[doc_id][label] = count
    per_doc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for split in SPLITS:
        corpus = load_corpus(dataset, split, data_type="gold")
        for m in corpus.mentions:
            per_doc[m.document_id][m.label] += 1

    all_labels = sorted({lbl for counts in per_doc.values() for lbl in counts})

    # Group doc counts by year
    year_docs: dict[int, list[str]] = defaultdict(list)
    for doc_id in per_doc:
        year = doc_year.get(doc_id)
        if year is not None:
            year_docs[year].append(doc_id)

    result: dict[str, dict] = {}
    for year in sorted(year_docs):
        doc_ids = year_docs[year]
        n = len(doc_ids)
        totals = [sum(per_doc[d].values()) for d in doc_ids]
        by_label = {}
        for label in all_labels:
            means_label = [per_doc[d].get(label, 0) for d in doc_ids]
            by_label[label] = round(statistics.mean(means_label), 2)
        result[str(year)] = {
            "n_papers": n,
            "total_mean": round(statistics.mean(totals), 2),
            "by_label": by_label,
        }
    return result


def _relation_stats(dataset: str) -> dict:
    """Per-paper relation label counts for a dataset (all splits pooled)."""
    per_doc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for split in SPLITS:
        corpus = load_corpus(dataset, split, data_type="gold")
        for r in corpus.relation:
            per_doc[r.subject.document_id][r.label] += 1

    all_doc_ids = list(per_doc.keys())
    labels = sorted({lbl for counts in per_doc.values() for lbl in counts})
    n_docs = len(all_doc_ids)

    by_label: dict[str, dict] = {}
    for label in labels:
        per_paper_all = [per_doc[doc_id].get(label, 0) for doc_id in all_doc_ids]
        per_paper_present = [c for c in per_paper_all if c > 0]
        by_label[label] = {
            "per_paper": per_paper_all,
            "per_paper_present": per_paper_present,
            "n_papers_total": n_docs,
            "n_papers_present": len(per_paper_present),
            "pct_papers": round(100 * len(per_paper_present) / n_docs, 1) if n_docs else 0,
            "summary_all": _summary(per_paper_all),
            "summary_present": _summary(per_paper_present),
        }

    return {"labels": labels, "n_papers": n_docs, "by_label": by_label}


def main() -> None:
    print("Computing label statistics...")

    # Build doc_id → year lookup from metadata
    doc_year: dict[str, int] = {}
    for paper in load_papers():
        if paper.year is not None:
            doc_year[paper.doc_id] = paper.year

    result: dict = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "entities": {},
        "relations": {},
        "entities_by_year": {},
    }

    for dataset in DATASETS:
        print(f"  {dataset} — entities ...", end=" ", flush=True)
        result["entities"][dataset] = _entity_stats(dataset)
        print("done")

        print(f"  {dataset} — relations ...", end=" ", flush=True)
        result["relations"][dataset] = _relation_stats(dataset)
        print("done")

        print(f"  {dataset} — entities by year ...", end=" ", flush=True)
        result["entities_by_year"][dataset] = _entities_by_year(dataset, doc_year)
        print("done")

    out = ensure_output("data/label_statistics.json")
    out.write_text(json.dumps(result, indent=2))
    print(f"Written → {out}")


if __name__ == "__main__":
    main()
