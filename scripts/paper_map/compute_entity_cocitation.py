"""Compute entity co-citation maps for Task, Dataset, and Method entities.

For each entity type:
  1. Load unified gold annotations across all datasets and splits.
  2. Build entity → {dataset: set_of_doc_ids} mapping.
  3. Select the top N entities by total publication count.
  4. Assign each entity a corpus label based on which datasets it appears in
     (7 combinations: GSAP, SciER, SciNLP, GSAP+SciER, GSAP+SciNLP,
      SciER+SciNLP, GSAP+SciER+SciNLP).
  5. Compute pairwise Jaccard similarity on shared papers (co-citation).
  6a. Reduce to 2-D with classical metric MDS (x, y).
  6b. Build a co-citation count graph and reduce to 2-D with spring layout
      (Fruchterman-Reingold), stored as x_spring, y_spring.
      Also store the sparse edge list (source, target, cocit_count).
  7. Write data/doc_embeddings/entity_cocitation.json.

Usage
-----
    uv run python scripts/paper_map/compute_entity_cocitation.py
    uv run python scripts/paper_map/compute_entity_cocitation.py --top-n 500
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
from sklearn.manifold import MDS

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.unification.pipeline import apply_unification_pipeline

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / "data" / "doc_embeddings"

DATASETS = ["gsap-ere", "scier", "scinlp"]
SPLITS = ["train", "dev", "test"]
ENTITY_TYPES = ["Task", "Dataset", "Method"]

CORPUS_LABEL_ORDER = [
    "GSAP",
    "SciER",
    "SciNLP",
    "GSAP+SciER",
    "GSAP+SciNLP",
    "SciER+SciNLP",
    "GSAP+SciER+SciNLP",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    return " ".join(text.lower().split())


# Abbreviation expansions applied after normalisation.
# Keys are lowercase; values are the canonical expanded form.
_METHOD_ABBREVS: dict[str, str] = {
    "cnn":  "convolutional neural network",
    "sgd":  "stochastic gradient descent",
    "gan":  "generative adversarial network",
    "svm":  "support vector machine",
    "lm":   "language model",
    "rnn":  "recurrent neural network",
    "mlp":  "multilayer perceptron",
    "vae":  "variational autoencoder",
    "fcn":  "fully convolutional network",
    "vcn":  "fully convolutional network",  # common alternative abbreviation
    "rpn":      "region proposal network",
    "plm":      "pretrained language model",
    "crf":      "conditional random field",
    "fpn":      "feature pyramid network",
    "vgg":      "visual geometry group",
    "vgg - 1 6": "vgg-16",
    "vgg 1 6":  "vgg-16",
    "pcfg":     "probabilistic context-free grammar",
    "ngram":    "n-gram",
    "mle":      "maximum likelihood estimation",
}

_TASK_ABBREVS: dict[str, str] = {
    "ner":                          "named entity recognition",
    "nli":                          "natural language inference",
    "nsp":                          "next sentence prediction",
    "nlp":                          "natural language processing",
    "qa":                           "question answering",
    "nlu":                          "natural language understanding",
    "sts":                          "semantic textual similarity",
    "mrpc":                         "microsoft research paraphrase corpus",
    "mlm":                          "masked language modeling",
    "rte":                          "recognizing textual entailment",
    "mt":                           "machine translation",
    "machine translation ( mt )":   "machine translation",
    "re":                           "relation extraction",
}

# Dataset normalizations: fix hyphenation artifacts, tokenization splits, and
# expand abbreviations. Keys are the lowercased/whitespace-normalised form
# (as produced by _normalise).
_DATASET_ABBREVS: dict[str, str] = {
    # ImageNet hyphenation artifacts (with and without spaces around hyphen)
    "ima genet":                            "imagenet",
    "im agenet":                            "imagenet",
    "ima - genet":                          "imagenet",
    "im - agenet":                          "imagenet",
    # STS-B
    "sts - b":                              "semantic textual similarity benchmark",
    # CIFAR tokenization artifacts
    "cifar - 1 0":                          "cifar-10",
    "cifar 1 0":                            "cifar-10",
    "cifar - 1 0 0":                        "cifar-100",
    # STS (benchmark)
    "sts":                                  "semantic textual similarity benchmark",
    # CNN/DailyMail
    "cnn / dailymail":                      "cnn / daily mail",
    # SQuAD versions
    "squad v 1 . 1":                        "squad v1.1",
    "squad 1. 1":                           "squad v1.1",
    "squad 2. 0":                           "squad v2.0",
    "stanford question answering dataset":  "squad",
    # GLUE
    "general language understanding evaluation": "glue",
    # WordNet plural
    "wordnets":                             "wordnet",
    # Abbreviations
    "snli":                                 "stanford natural language inference",
    "sst":                                  "stanford sentiment treebank",
    # Corpus name normalization
    "bookscorpus":                          "bookcorpus",
    # MS-COCO variants
    "mscoco":                               "ms-coco",
    "ms coco":                              "ms-coco",
}


def _canonicalize(norm: str, etype: str) -> str:
    """Apply entity-type-specific normalization to an already-lowercased term.

    For Method: strip a trailing 's' (plural), then expand known abbreviations.
    For Task:   expand known abbreviations.
    For Dataset: fix hyphenation artifacts and expand abbreviations.
    """
    if etype == "Method":
        if norm.endswith("s") and len(norm) > 1:
            norm = norm[:-1]
        norm = _METHOD_ABBREVS.get(norm, norm)
    elif etype == "Task":
        norm = _TASK_ABBREVS.get(norm, norm)
    elif etype == "Dataset":
        norm = _DATASET_ABBREVS.get(norm, norm)
    return norm


def _corpus_label(ds_set: frozenset) -> str:
    parts = []
    if "gsap-ere" in ds_set:
        parts.append("GSAP")
    if "scier" in ds_set:
        parts.append("SciER")
    if "scinlp" in ds_set:
        parts.append("SciNLP")
    return "+".join(parts) if parts else "Unknown"


def _jaccard(a: set, b: set) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _mds_coords(dissim: np.ndarray, random_state: int = 42) -> np.ndarray:
    mds = MDS(
        n_components=2,
        dissimilarity="precomputed",
        random_state=random_state,
        n_init=4,
        normalized_stress="auto",
    )
    return mds.fit_transform(dissim)


def _spring_coords(
    paper_sets: list[set],
    min_cocit: int = 1,
    random_state: int = 42,
) -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    """Build a co-citation graph and compute Fruchterman-Reingold spring layout.

    Edge weight = |papers(i) ∩ papers(j)| (raw co-citation count).
    Only edges with count >= min_cocit are included.

    Returns (coords array of shape (n, 2), edge list of (i, j, count)).
    """
    n = len(paper_sets)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    edges: list[tuple[int, int, int]] = []

    for i in range(n):
        for j in range(i + 1, n):
            cocit = len(paper_sets[i] & paper_sets[j])
            if cocit >= min_cocit:
                G.add_edge(i, j, weight=cocit)
                edges.append((i, j, cocit))

    pos = nx.spring_layout(G, weight="weight", seed=random_state, iterations=100)
    coords = np.array([pos[i] for i in range(n)])
    return coords, edges


# ---------------------------------------------------------------------------
# Step 1 — Build entity → papers mapping
# ---------------------------------------------------------------------------

def load_entity_paper_map() -> dict[str, dict[str, dict[str, set]]]:
    """Return entity_map[etype][normalised_text][dataset] = set(doc_ids)."""
    entity_map: dict[str, dict[str, dict[str, set]]] = {
        et: defaultdict(lambda: defaultdict(set)) for et in ENTITY_TYPES
    }

    for dataset in DATASETS:
        for split in SPLITS:
            print(f"  Loading {dataset}/{split} ...", end=" ", flush=True)
            try:
                corpus = load_corpus(dataset, split, data_type="gold")
            except FileNotFoundError:
                print("not found, skipping")
                continue

            corpus, _ = apply_unification_pipeline(
                corpus, dataset,
                apply_to_gold=True,
                apply_to_predicted=False,
            )

            for m in corpus.mentions:
                if m.label in ENTITY_TYPES:
                    norm = _canonicalize(_normalise(m.text), m.label)
                    entity_map[m.label][norm][dataset].add(m.document_id)

            print(f"{len(corpus.mentions)} mentions")

    return entity_map


# ---------------------------------------------------------------------------
# Step 2 — Select top-N, assign corpus label
# ---------------------------------------------------------------------------

def select_top_entities(
    entity_map: dict[str, dict[str, dict[str, set]]],
    top_n: int,
) -> dict[str, list[dict]]:
    """Return per-type list of entity dicts, sorted by total paper count desc."""
    result: dict[str, list[dict]] = {}

    for etype, term_map in entity_map.items():
        entries = []
        for term, ds_papers in term_map.items():
            all_papers: set[str] = set()
            for papers in ds_papers.values():
                all_papers |= papers
            n_total = len(all_papers)
            corpus_label = _corpus_label(frozenset(ds_papers.keys()))
            entries.append({
                "term": term,
                "etype": etype,
                "n_papers": n_total,
                "corpus": corpus_label,
                "papers": sorted(all_papers),
                "papers_by_ds": {ds: sorted(pps) for ds, pps in ds_papers.items()},
            })

        entries_multi = [e for e in entries if e["n_papers"] > 1]
        entries_multi.sort(key=lambda e: e["n_papers"], reverse=True)
        result[etype] = entries_multi[:top_n]
        print(
            f"  {etype}: {len(term_map)} unique terms → "
            f"{len(entries_multi)} with >1 paper → top {len(result[etype])} selected"
        )

    return result


# ---------------------------------------------------------------------------
# Step 3 — Co-citation layouts (MDS + Spring)
# ---------------------------------------------------------------------------

def compute_cocitation_layout(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """Compute MDS and spring layouts; return (entries, edges).

    Each entry gets x/y (MDS) and x_spring/y_spring (Fruchterman-Reingold).
    edges is a list of {source, target, cocit_count} dicts (index-based).
    """
    n = len(entries)
    paper_sets = [set(e["papers"]) for e in entries]

    # MDS on Jaccard dissimilarity
    dissim = np.ones((n, n))
    for i in range(n):
        dissim[i, i] = 0.0
        for j in range(i + 1, n):
            j_val = _jaccard(paper_sets[i], paper_sets[j])
            dissim[i, j] = dissim[j, i] = 1.0 - j_val

    mds_coords = _mds_coords(dissim)

    # Spring layout on raw co-citation counts
    spring_coords, raw_edges = _spring_coords(paper_sets, min_cocit=1)

    # Report
    nonzero = int((dissim < 1.0).sum() - n)
    print(f"    {nonzero}/{n*(n-1)} pairs share ≥1 paper ({100*nonzero/(n*(n-1)+1e-9):.1f}%)")
    print(f"    {len(raw_edges)} spring edges")

    # Serialise edges as index-based dicts
    edges_out = [
        {"i": i, "j": j, "cocit": cocit}
        for i, j, cocit in raw_edges
    ]

    for idx, entry in enumerate(entries):
        entry["x"]        = float(mds_coords[idx, 0])
        entry["y"]        = float(mds_coords[idx, 1])
        entry["x_spring"] = float(spring_coords[idx, 0])
        entry["y_spring"] = float(spring_coords[idx, 1])
        entry["papers_by_ds_counts"] = {
            ds: len(pps) for ds, pps in entry["papers_by_ds"].items()
        }
        del entry["papers"]
        del entry["papers_by_ds"]

    return entries, edges_out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(top_n: int = 300) -> None:
    print("=== Step 1: Load and unify gold annotations ===")
    entity_map = load_entity_paper_map()

    print("\n=== Step 2: Select top entities ===")
    top_entities = select_top_entities(entity_map, top_n=top_n)

    print("\n=== Step 3: Co-citation layout (MDS + Spring) ===")
    output: dict[str, list[dict]] = {}
    edges_output: dict[str, list[dict]] = {}
    for etype, entries in top_entities.items():
        print(f"  {etype} ({len(entries)} terms) ...")
        output[etype], edges_output[etype] = compute_cocitation_layout(entries)

    print("\n=== Step 4: Write output ===")
    out_path = ARTIFACTS_DIR / "entity_cocitation.json"
    with open(out_path, "w") as f:
        json.dump({"entities": output, "edges": edges_output}, f, ensure_ascii=False)
    print(f"  Written: {out_path}")

    # Summary
    for etype, entries in output.items():
        by_corpus = {}
        for e in entries:
            by_corpus[e["corpus"]] = by_corpus.get(e["corpus"], 0) + 1
        print(f"\n  {etype} corpus breakdown:")
        for label in CORPUS_LABEL_ORDER:
            if label in by_corpus:
                print(f"    {label:25s}: {by_corpus[label]}")

    print(f"\nDone. top_n={top_n}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--top-n", type=int, default=300,
                        help="Number of top entities per type to include (default: 300)")
    args = parser.parse_args()
    main(top_n=args.top_n)
