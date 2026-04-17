"""Enrich unified metadata with Semantic Scholar IDs and fields-of-study.

For each paper, the script:
1. Looks up the paper on Semantic Scholar using all available identifiers
   (s2_paper_id → s2_corpus_id → arxiv_id → doi → acl_id → title).
2. Fills in missing ``s2_paper_id`` and ``s2_corpus_id`` from the S2 response.
3. Stores the ``s2FieldsOfStudy`` classification as ``s2_fields_of_study``
   (list of {"category": str, "source": str} dicts, source is either
   "s2-fos-model" or "external").

Papers that already have both ``s2_paper_id`` and ``s2_fields_of_study``
are skipped unless ``--force`` is given.

Rate limiting: the default cap is 40 requests/minute, which is safe for the
unauthenticated tier.  Set S2_API_KEY in the environment to use a higher cap
(--max-per-minute 90 is appropriate for a personal API key).

Usage:
    uv run python scripts/paper_metadata/enrich_s2.py
    uv run python scripts/paper_metadata/enrich_s2.py --dry-run
    uv run python scripts/paper_metadata/enrich_s2.py --force
    uv run python scripts/paper_metadata/enrich_s2.py --dataset gsap
    uv run python scripts/paper_metadata/enrich_s2.py --max-per-minute 90
"""

import argparse
import json
import os
import shutil
from collections import Counter
from pathlib import Path

from unifiedsciere.metadata.read_metadata import load_papers
from unifiedsciere.metadata.retriever.semantic_scholar import enrich_papers_batch

ROOT = Path(__file__).resolve().parents[2]
ALL_PAPERS_PATH = ROOT / "data" / "metadata" / "unified" / "all_papers.jsonl"

# Default rate limit for the unauthenticated tier (~1 req/s with headroom)
DEFAULT_MAX_PER_MINUTE = 40


def _needs_enrichment(paper, force: bool) -> bool:
    if force:
        return True
    return not (paper.s2_paper_id and paper.s2_fields_of_study)


def main():
    parser = argparse.ArgumentParser(
        description="Enrich unified metadata with Semantic Scholar IDs and fields-of-study"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without saving")
    parser.add_argument("--force", action="store_true",
                        help="Re-enrich papers that already have S2 data")
    parser.add_argument("--dataset", default="",
                        help="Restrict to a single dataset (gsap, scier, scinlp, scier_ood)")
    parser.add_argument("--max-per-minute", type=int, default=DEFAULT_MAX_PER_MINUTE,
                        help=f"Max S2 requests per minute (default: {DEFAULT_MAX_PER_MINUTE})")
    args = parser.parse_args()

    api_key = os.environ.get("S2_API_KEY", "")
    if api_key:
        print(f"S2_API_KEY found — using authenticated requests")

    print("=== Loading papers ===")
    all_papers = load_papers()
    papers = all_papers if not args.dataset else [p for p in all_papers if p.dataset == args.dataset]
    print(f"Loaded {len(papers)} papers" + (f" (dataset={args.dataset})" if args.dataset else ""))

    to_enrich = [p for p in papers if _needs_enrichment(p, args.force)]
    print(f"Already complete (skip): {len(papers) - len(to_enrich)}")
    print(f"To enrich:               {len(to_enrich)}")

    if not to_enrich:
        print("Nothing to do.")
        return

    # ── Build input for batch enrichment ───────────────────────────────────
    batch_input = [
        dict(
            s2_paper_id=p.s2_paper_id,
            s2_corpus_id=p.s2_corpus_id,
            arxiv_id=p.arxiv_id,
            doi=p.doi or p.doi_preprint,
            acl_id=p.acl_id,
            title=p.title,
        )
        for p in to_enrich
    ]

    print(f"\n=== Querying Semantic Scholar ({args.max_per_minute} req/min) ===")
    results = enrich_papers_batch(batch_input, max_per_minute=args.max_per_minute)

    # ── Apply results ──────────────────────────────────────────────────────
    n_found = n_ids_filled = n_fos_filled = n_not_found = 0

    for paper, result in zip(to_enrich, results):
        if result is None:
            n_not_found += 1
            continue

        n_found += 1

        s2_pid = result.get("paperId") or ""
        s2_cid = str(result.get("corpusId") or "")
        if s2_pid and not paper.s2_paper_id:
            paper.s2_paper_id = s2_pid
            n_ids_filled += 1
        if s2_cid and not paper.s2_corpus_id:
            paper.s2_corpus_id = s2_cid

        fos = result.get("s2FieldsOfStudy") or []
        if fos:
            paper.s2_fields_of_study = fos
            n_fos_filled += 1

    # ── Summary ────────────────────────────────────────────────────────────
    print("\n=== Summary ===")
    print(f"  Found on S2:          {n_found}/{len(to_enrich)}")
    print(f"  Not found:            {n_not_found}")
    print(f"  New s2_paper_id:      {n_ids_filled}")
    print(f"  s2_fields_of_study:   {n_fos_filled}")

    # Merge subset back into full list if --dataset was used
    if args.dataset:
        enriched_by_id = {p.doc_id: p for p in papers}
        for p in all_papers:
            if p.doc_id in enriched_by_id:
                ep = enriched_by_id[p.doc_id]
                p.s2_paper_id = ep.s2_paper_id
                p.s2_corpus_id = ep.s2_corpus_id
                p.s2_fields_of_study = ep.s2_fields_of_study
    papers_to_write = all_papers

    fos_by_dataset = Counter(p.dataset for p in papers_to_write if p.s2_fields_of_study)
    total_by_dataset = Counter(p.dataset for p in papers_to_write)
    print("\n  Fields-of-study coverage by dataset:")
    for ds in sorted(total_by_dataset):
        have = fos_by_dataset[ds]
        total = total_by_dataset[ds]
        print(f"    {ds:12s}: {have:3d}/{total:3d} ({have / total * 100:.0f}%)")

    if args.dry_run:
        print("\n=== DRY RUN — not saving ===")
        return

    # ── Write back ─────────────────────────────────────────────────────────
    backup = ALL_PAPERS_PATH.with_suffix(".jsonl.backup")
    shutil.copy2(ALL_PAPERS_PATH, backup)
    print(f"\n=== Backup → {backup.name} ===")

    with open(ALL_PAPERS_PATH, "w") as f:
        for paper in papers_to_write:
            f.write(json.dumps(paper.to_dict(), ensure_ascii=False) + "\n")
    print(f"✓ Wrote {len(papers_to_write)} papers to {ALL_PAPERS_PATH.name}")
    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
