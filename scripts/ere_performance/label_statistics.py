"""Label statistics per dataset.

Computes per-paper annotation counts by label type for histogram visualisation
in the webapp.  Produces both pooled ("all") and per-split breakdowns.

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

SPLITS_PER_DATASET: dict[str, list[str]] = {
    "gsap-ere": ["train", "dev", "test"],
    "scier":    ["train", "dev", "test", "test_ood"],
    "scinlp":   ["train", "dev", "test"],
}


def _summary(counts: list[int]) -> dict:
    if not counts:
        return {"mean": 0, "median": 0, "max": 0, "n": 0}
    return {
        "mean":   round(statistics.mean(counts), 2),
        "median": round(statistics.median(counts), 2),
        "max":    max(counts),
        "n":      len(counts),
    }


def _entity_stats(dataset: str, splits: list[str]) -> dict:
    """Per-paper entity label counts for the given dataset+splits pooled."""
    per_doc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for split in splits:
        try:
            corpus = load_corpus(dataset, split, data_type="gold")
        except FileNotFoundError:
            continue
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
            "per_paper":         per_paper_all,
            "per_paper_present": per_paper_present,
            "n_papers_total":    n_docs,
            "n_papers_present":  len(per_paper_present),
            "pct_papers":        round(100 * len(per_paper_present) / n_docs, 1) if n_docs else 0,
            "summary_all":       _summary(per_paper_all),
            "summary_present":   _summary(per_paper_present),
        }

    return {"labels": labels, "n_papers": n_docs, "by_label": by_label}


def _relation_stats(dataset: str, splits: list[str]) -> dict:
    """Per-paper relation label counts for the given dataset+splits pooled."""
    per_doc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    all_doc_ids_set: set[str] = set()

    for split in splits:
        try:
            corpus = load_corpus(dataset, split, data_type="gold")
        except FileNotFoundError:
            continue
        for s in corpus.sentences:
            all_doc_ids_set.add(s.doc_id)
        for r in corpus.relation:
            per_doc[r.subject.document_id][r.label] += 1

    all_doc_ids = sorted(all_doc_ids_set)
    labels = sorted({lbl for counts in per_doc.values() for lbl in counts})
    n_docs = len(all_doc_ids)

    by_label: dict[str, dict] = {}
    for label in labels:
        per_paper_all = [per_doc[doc_id].get(label, 0) for doc_id in all_doc_ids]
        per_paper_present = [c for c in per_paper_all if c > 0]
        by_label[label] = {
            "per_paper":         per_paper_all,
            "per_paper_present": per_paper_present,
            "n_papers_total":    n_docs,
            "n_papers_present":  len(per_paper_present),
            "pct_papers":        round(100 * len(per_paper_present) / n_docs, 1) if n_docs else 0,
            "summary_all":       _summary(per_paper_all),
            "summary_present":   _summary(per_paper_present),
        }

    return {"labels": labels, "n_papers": n_docs, "by_label": by_label}


def _entities_by_year(dataset: str, splits: list[str], doc_year: dict[str, int]) -> dict:
    """Mean entity count per paper per year for the given splits."""
    per_doc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for split in splits:
        try:
            corpus = load_corpus(dataset, split, data_type="gold")
        except FileNotFoundError:
            continue
        for m in corpus.mentions:
            per_doc[m.document_id][m.label] += 1

    all_labels = sorted({lbl for counts in per_doc.values() for lbl in counts})

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
        by_label = {
            label: round(statistics.mean([per_doc[d].get(label, 0) for d in doc_ids]), 2)
            for label in all_labels
        }
        result[str(year)] = {
            "n_papers":   n,
            "total_mean": round(statistics.mean(totals), 2),
            "by_label":   by_label,
        }
    return result


def _relations_by_year(dataset: str, splits: list[str], doc_year: dict[str, int]) -> dict:
    """Mean relation count per paper per year for the given splits."""
    per_doc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for split in splits:
        try:
            corpus = load_corpus(dataset, split, data_type="gold")
        except FileNotFoundError:
            continue
        for r in corpus.relation:
            per_doc[r.subject.document_id][r.label] += 1

    all_labels = sorted({lbl for counts in per_doc.values() for lbl in counts})

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
        by_label = {
            label: round(statistics.mean([per_doc[d].get(label, 0) for d in doc_ids]), 2)
            for label in all_labels
        }
        result[str(year)] = {
            "n_papers":   n,
            "total_mean": round(statistics.mean(totals), 2),
            "by_label":   by_label,
        }
    return result


def main() -> None:
    print("Computing label statistics...")

    doc_year: dict[str, int] = {}
    for paper in load_papers():
        if paper.year is not None:
            doc_year[paper.doc_id] = paper.year

    result: dict = {
        "generated":         datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "entities":          {},
        "relations":         {},
        "entities_by_year":  {},
        "relations_by_year": {},
    }

    for dataset in DATASETS:
        available = SPLITS_PER_DATASET[dataset]

        print(f"  {dataset} — entities ...", end=" ", flush=True)
        result["entities"][dataset] = {
            "splits": {
                "all": _entity_stats(dataset, available),
                **{sp: _entity_stats(dataset, [sp]) for sp in available},
            }
        }
        print("done")

        print(f"  {dataset} — relations ...", end=" ", flush=True)
        result["relations"][dataset] = {
            "splits": {
                "all": _relation_stats(dataset, available),
                **{sp: _relation_stats(dataset, [sp]) for sp in available},
            }
        }
        print("done")

        print(f"  {dataset} — entities by year ...", end=" ", flush=True)
        result["entities_by_year"][dataset] = {
            "splits": {
                "all": _entities_by_year(dataset, available, doc_year),
                **{sp: _entities_by_year(dataset, [sp], doc_year) for sp in available},
            }
        }
        print("done")

        print(f"  {dataset} — relations by year ...", end=" ", flush=True)
        result["relations_by_year"][dataset] = {
            "splits": {
                "all": _relations_by_year(dataset, available, doc_year),
                **{sp: _relations_by_year(dataset, [sp], doc_year) for sp in available},
            }
        }
        print("done")

    out = ensure_output("data/webapp/label_statistics.json")
    out.write_text(json.dumps(result, indent=2))
    print(f"Written → {out}")


if __name__ == "__main__":
    main()
