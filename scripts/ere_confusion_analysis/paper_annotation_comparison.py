"""Cross-dataset annotation comparison for shared papers (Sentence-BERT, FinBERT).

Compares gold annotations from GSAP and SciER for the two papers present in both
datasets. Produces an overview of entity/relation types (raw, unified, and on the
common sentence subset) plus a confusion matrix with random examples per cell.

Usage:
    uv run python scripts/ere_confusion_analysis/paper_annotation_comparison.py
"""

import random
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Literal

from gsaphub.match.entities import partial

from unifiedsciere.data_loader import load_corpus
from unifiedsciere.paths import ensure_output
from unifiedsciere.reporting import MarkdownReport
from unifiedsciere.types import Corpus, Mention, Relation, Sentence
from unifiedsciere.unification.pipeline import apply_unification_pipeline

# ── Paper manifest ────────────────────────────────────────────────────────────
PAPERS = [
    {
        "name": "Sentence-BERT",
        "gsap_doc_id": "00032_1908_10084.txt",
        "gsap_split": "train",
        "scier_doc_id": "201646309",
        "scier_split": "train",
    },
    {
        "name": "FinBERT",
        "gsap_doc_id": "00038_1908_10063.txt",
        "gsap_split": "train",
        "scier_doc_id": "201646244",
        "scier_split": "dev",
    },
]

RANDOM_SEED = 42
N_EXAMPLES = 5  # examples per confusion-matrix cell


# ── Corpus filtering ──────────────────────────────────────────────────────────

def filter_corpus_to_doc(corpus: Corpus, doc_id: str) -> Corpus:
    """Return a new Corpus containing only data for the given doc_id."""
    sents = [s for s in corpus.sentences if s.doc_id == doc_id]
    sent_idx_set = {(s.doc_id, s.idx) for s in sents}
    mentions = [
        m for m in corpus.mentions
        if (m.document_id, m.sent_idx) in sent_idx_set
    ]
    relations = [
        r for r in corpus.relation
        if (r.subject.document_id, r.subject.sent_idx) in sent_idx_set
    ]
    return Corpus(sents, mentions, relations)


# ── Sentence matching (text-based) ────────────────────────────────────────────

def _normalise(text: str) -> str:
    import re
    t = text.lower()
    t = " ".join(t.split())
    # Strip section-number suffixes that SciER appends to sentences
    # e.g. "... finbert . 3. 1 . 1 lstm ." → "... finbert ."
    t = re.sub(r"\.\s+\d+\.\s+\d+\s+\.\s+\d+\s+\w+\s+\.\s*$", ".", t)
    t = re.sub(r"\.\s+\d+\s*$", ".", t)
    # Strip trailing footnote references like "2 ." or "3 . 1 . 4 transformer ."
    t = re.sub(r"\s+\d+\s+\.\s*$", ".", t)
    # SciER splits digits with spaces (e.g. "2 0 1 8" -> "2018", "6 0 %" -> "60 %")
    t = re.sub(r"(?<!\w)(\d)(?: (\d))+(?!\w)", lambda m: m.group(0).replace(" ", ""), t)
    # Normalise hyphens: collapse all whitespace around hyphens and slashes
    t = re.sub(r"\s*-\s*", "-", t)
    t = re.sub(r"\s*/\s*", "/", t)
    # Collapse any new double-spaces introduced
    t = " ".join(t.split())
    return t


def _jaccard(a: str, b: str) -> float:
    ta, tb = set(a.split()), set(b.split())
    if not ta and not tb:
        return 1.0
    return len(ta & tb) / len(ta | tb)


FUZZY_THRESHOLD = 0.82  # minimum Jaccard similarity to accept a fuzzy match


def find_common_sentences(
    gsap_sents: list[Sentence],
    scier_sents: list[Sentence],
) -> tuple[list[tuple[Sentence, Sentence]], list[Sentence], list[Sentence]]:
    """Match sentences by normalised text, with Jaccard fuzzy fallback.

    Pass 1 — exact match after normalisation.
    Pass 2 — for remaining unmatched SciER sentences, find the best unmatched
              GSAP sentence by Jaccard token overlap; accept if >= FUZZY_THRESHOLD.

    Returns:
        common    – list of (gsap_sent, scier_sent) pairs
        gsap_only – sentences in GSAP without a SciER match
        scier_only – sentences in SciER without a match in either pass
    """
    gsap_norm = {_normalise(s.text): s for s in gsap_sents}
    scier_norm = {_normalise(s.text): s for s in scier_sents}

    # Pass 1: exact normalised match
    exact_keys = set(gsap_norm) & set(scier_norm)
    common: list[tuple[Sentence, Sentence]] = [
        (gsap_norm[k], scier_norm[k]) for k in sorted(exact_keys)
    ]
    matched_gsap_keys = set(exact_keys)
    matched_scier_keys = set(exact_keys)

    # Pass 2: fuzzy match for remaining SciER sentences
    unmatched_gsap = [(k, s) for k, s in gsap_norm.items() if k not in matched_gsap_keys]
    for sc_key, sc_sent in scier_norm.items():
        if sc_key in matched_scier_keys:
            continue
        best_j, best_gk, best_gs = 0.0, None, None
        for gk, gs in unmatched_gsap:
            j = _jaccard(sc_key, gk)
            if j > best_j:
                best_j, best_gk, best_gs = j, gk, gs
        if best_j >= FUZZY_THRESHOLD and best_gk is not None:
            common.append((best_gs, sc_sent))
            matched_gsap_keys.add(best_gk)
            matched_scier_keys.add(sc_key)
            # Remove from candidates so it can't be matched again
            unmatched_gsap = [(k, s) for k, s in unmatched_gsap if k != best_gk]

    gsap_only  = [s for k, s in gsap_norm.items()  if k not in matched_gsap_keys]
    scier_only = [s for k, s in scier_norm.items() if k not in matched_scier_keys]
    return common, gsap_only, scier_only


def filter_corpus_to_sentences(
    corpus: Corpus,
    keep_sent_ids: set[tuple[str, int]],  # {(doc_id, sent_idx)}
) -> Corpus:
    """Return a new Corpus restricted to the specified sentence ids."""
    sents = [s for s in corpus.sentences if (s.doc_id, s.idx) in keep_sent_ids]
    mentions = [
        m for m in corpus.mentions
        if (m.document_id, m.sent_idx) in keep_sent_ids
    ]
    relations = [
        r for r in corpus.relation
        if (r.subject.document_id, r.subject.sent_idx) in keep_sent_ids
    ]
    return Corpus(sents, mentions, relations)


# ── Label counting helpers ────────────────────────────────────────────────────

def count_entity_labels(corpus: Corpus) -> Counter:
    return Counter(m.label for m in corpus.mentions)


def count_relation_labels(corpus: Corpus) -> Counter:
    return Counter(r.label for r in corpus.relation)


def count_original_entity_labels(corpus: Corpus) -> Counter:
    return Counter(
        (m.label_original or m.label) for m in corpus.mentions
    )


def count_original_relation_labels(corpus: Corpus) -> Counter:
    return Counter(r.label for r in corpus.relation)


# ── Confusion matrix (gold GSAP vs gold SciER, partial span matching) ─────────

def build_confusion(
    gsap_mentions: list[Mention],
    scier_mentions: list[Mention],
    gsap_sentences: list[Sentence],
    scier_sentences: list[Sentence],
    common_pairs: list[tuple[Sentence, Sentence]],
    rng: random.Random,
    n_examples: int = N_EXAMPLES,
) -> tuple[dict, dict]:
    """Build a confusion dict and example dict.

    Rows = GSAP labels (+ NIL for unmatched SciER)
    Cols = SciER labels (+ NIL for unmatched GSAP)

    Matching is done per common-sentence pair so that character offsets are
    comparable (sentence-relative) across the two datasets.

    Returns:
        counts   – {gsap_label: {scier_label: int}}
        examples – {(gsap_label, scier_label): [(gsap_text, scier_text), ...]}
    """
    # We need a shared virtual doc_id for each matched sentence pair.
    # Build maps: (real_doc_id, sent_idx) -> virtual_doc_id
    gsap_virtual: dict[tuple[str, int], str] = {}
    scier_virtual: dict[tuple[str, int], str] = {}
    for i, (gs, sc) in enumerate(common_pairs):
        vid = f"common_sent_{i}"
        gsap_virtual[(gs.doc_id, gs.idx)] = vid
        scier_virtual[(sc.doc_id, sc.idx)] = vid

    # Build sentence-relative hub entries per virtual doc
    def _to_hub_virtual(
        mentions: list[Mention],
        sentences: list[Sentence],
        virtual_map: dict[tuple[str, int], str],
    ) -> list[dict]:
        sent_text_by_id = {(s.doc_id, s.idx): s.text for s in sentences}
        # Per-sentence offset within a virtual doc: since each virtual doc has
        # exactly one sentence, base offset is always 0.
        result = []
        for m in mentions:
            key = (m.document_id, m.sent_idx)
            vid = virtual_map.get(key)
            if vid is None:
                continue
            sent_text = sent_text_by_id.get(key, "")
            mention_text = m.text
            try:
                rel_begin = sent_text.index(mention_text)
                rel_end = rel_begin + len(mention_text)
            except ValueError:
                rel_begin = m.begin_token * 5
                rel_end = rel_begin + len(mention_text)
            result.append(
                {
                    "id": m.id,
                    "doc_id": vid,
                    "begin": rel_begin,
                    "end": rel_end,
                    "label": m.label,
                    "annotator": m.annotator,
                }
            )
        return result

    gsap_hub = _to_hub_virtual(gsap_mentions, gsap_sentences, gsap_virtual)
    scier_hub = _to_hub_virtual(scier_mentions, scier_sentences, scier_virtual)

    # Sentence text lookup for both datasets
    gsap_sent_text = {(s.doc_id, s.idx): s.text for s in gsap_sentences}
    scier_sent_text = {(s.doc_id, s.idx): s.text for s in scier_sentences}
    # Reverse map: virtual_doc_id -> sentence text (one sentence per virtual doc)
    vid_to_gsap_sent = {v: gsap_sent_text.get(k, "") for k, v in gsap_virtual.items()}
    vid_to_scier_sent = {v: scier_sent_text.get(k, "") for k, v in scier_virtual.items()}

    # Match GSAP → SciER
    partial(gsap_hub, scier_hub, target_key="matched_ids", only_same_annotator=False)
    scier_by_id = {m["id"]: m for m in scier_hub}
    scier_mentions_by_id = {m.id: m for m in scier_mentions}
    gsap_mentions_by_id = {m.id: m for m in gsap_mentions}

    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # Store all (gsap_mention_text, scier_mention_text, sentence_text) triples per cell
    # sentence_text is from the GSAP perspective (same text in both for matched sentences)
    cell_pairs: dict[tuple[str, str], list[tuple[str, str, str]]] = defaultdict(list)

    for gh in gsap_hub:
        g_label = gh["label"]
        matched = gh.get("matched_ids", [])
        gm = gsap_mentions_by_id.get(gh["id"])
        sent = vid_to_gsap_sent.get(gh["doc_id"], "")
        if not matched:
            counts[g_label]["NIL"] += 1
            cell_pairs[(g_label, "NIL")].append((gm.text if gm else "?", "—", sent))
        else:
            s_hub = scier_by_id[matched[0]]
            s_label = s_hub["label"]
            counts[g_label][s_label] += 1
            sm = scier_mentions_by_id.get(matched[0])
            cell_pairs[(g_label, s_label)].append(
                (gm.text if gm else "?", sm.text if sm else "?", sent)
            )

    # Match SciER → GSAP to find SciER-only (NIL in GSAP)
    partial(scier_hub, gsap_hub, target_key="matched_ids", only_same_annotator=False)
    for sh in scier_hub:
        if not sh.get("matched_ids"):
            s_label = sh["label"]
            counts["NIL"][s_label] += 1
            sm = scier_mentions_by_id.get(sh["id"])
            sent = vid_to_scier_sent.get(sh["doc_id"], "")
            cell_pairs[("NIL", s_label)].append(("—", sm.text if sm else "?", sent))

    return dict(counts), dict(cell_pairs)


# ── Markdown rendering helpers ────────────────────────────────────────────────

def _label_table(report: MarkdownReport, counter: Counter, header: str) -> None:
    import pandas as pd
    report.heading(header, level=4)
    if not counter:
        report.text("_(none)_")
        return
    df = pd.DataFrame(counter.most_common(), columns=["Label", "Count"])
    report.table(df)


def _comparison_table(
    report: MarkdownReport,
    gsap_counter: Counter,
    scier_counter: Counter,
    header: str,
) -> None:
    """Render a single side-by-side comparison table for GSAP vs SciER counts."""
    import pandas as pd
    report.heading(header, level=4)
    all_labels = sorted(set(gsap_counter) | set(scier_counter))
    if not all_labels:
        report.text("_(none)_")
        return
    rows = []
    for label in all_labels:
        rows.append({
            "Label": label,
            "GSAP": gsap_counter.get(label, 0),
            "SciER": scier_counter.get(label, 0),
        })
    df = pd.DataFrame(rows).set_index("Label")
    # Sort by combined total descending
    df["_total"] = df["GSAP"] + df["SciER"]
    df = df.sort_values("_total", ascending=False).drop(columns="_total")
    report.table(df.reset_index())


def _esc(text: str) -> str:
    return text.replace("|", "\\|")


def _confusion_md(
    counts: dict,
    cell_pairs: dict,
    gsap_labels: list[str],
    scier_labels: list[str],
    rng: random.Random,
    n_examples: int = N_EXAMPLES,
) -> str:
    """Render confusion matrix + per-cell example tables as a markdown string.

    Diagonal / matching cells: up to n_examples random rows (sampled).
    Off-diagonal and NIL cells: all rows listed.
    Each example row includes: GSAP mention | SciER mention | sentence.
    """
    import pandas as pd

    # Build matrix DataFrame
    rows = gsap_labels + (["NIL"] if "NIL" in counts else [])
    cols = scier_labels + (["NIL"] if any("NIL" in v for v in counts.values()) else [])
    if "NIL" in counts and "NIL" not in cols:
        cols.append("NIL")

    data = {col: [] for col in cols}
    for row in rows:
        for col in cols:
            data[col].append(counts.get(row, {}).get(col, 0))

    df = pd.DataFrame(data, index=rows)
    df.index.name = "GSAP \\ SciER"

    lines = [df.to_markdown(), ""]

    for row in rows:
        for col in cols:
            pairs = cell_pairs.get((row, col), [])
            if not pairs:
                continue
            total = counts.get(row, {}).get(col, 0)
            is_diagonal = (row == col)
            is_nil = (row == "NIL" or col == "NIL")

            if is_diagonal:
                # Sample up to n_examples for matching cells
                show = rng.sample(pairs, min(n_examples, len(pairs)))
                caption = f"up to {n_examples} random"
            else:
                # Show all for off-diagonal and NIL cells
                show = pairs
                caption = "all"

            lines.append(
                f"\n**{row} → {col}** ({total} total, {caption}):\n"
            )
            lines.append("| GSAP mention | SciER mention | Sentence |")
            lines.append("|---|---|---|")
            for g_text, s_text, sent in show:
                lines.append(
                    f"| `{_esc(g_text)}` | `{_esc(s_text)}` | {_esc(sent)} |"
                )

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    rng = random.Random(RANDOM_SEED)

    report = MarkdownReport(
        "Cross-Dataset Annotation Comparison: Sentence-BERT & FinBERT (GSAP vs SciER)"
    )
    report.text(
        "This report compares gold annotations for two papers that appear in both "
        "the **GSAP** and **SciER** datasets: *Sentence-BERT* and *FinBERT*. "
        "Because SciER annotates only a subset of sentences, the comparison is done "
        "at three levels:\n\n"
        "1. **Raw** — all annotations in each dataset's native label scheme\n"
        "2. **Unified** — after applying each dataset's unification mapping\n"
        "3. **Reduced** — unified annotations restricted to the common sentences "
        "(sentences whose text appears in both GSAP and SciER)\n\n"
        "The confusion matrix in Section 3 uses partial span matching "
        "(gsaphub `partial`) to align entities on the common sentences."
    )

    # Pre-load full gold corpora (we filter per doc below)
    gsap_train_full = load_corpus("gsap-ere", "train", data_type="gold")
    scier_train_full = load_corpus("scier", "train", data_type="gold")
    scier_dev_full   = load_corpus("scier", "dev",   data_type="gold")

    def _get_scier(split: Literal["train", "dev"]) -> Corpus:
        return scier_train_full if split == "train" else scier_dev_full

    for paper in PAPERS:
        name = paper["name"]
        gsap_doc_id  = paper["gsap_doc_id"]
        scier_doc_id = paper["scier_doc_id"]

        report.heading(name, level=2)

        # ── 1. Raw counts ─────────────────────────────────────────────────────
        gsap_raw  = filter_corpus_to_doc(gsap_train_full, gsap_doc_id)
        scier_raw = filter_corpus_to_doc(_get_scier(paper["scier_split"]), scier_doc_id)

        report.heading("1. Raw Annotations (native label scheme)", level=3)
        report.text(
            f"GSAP: **{len(gsap_raw.sentences)}** sentences, "
            f"**{len(gsap_raw.mentions)}** entities, "
            f"**{len(gsap_raw.relation)}** relations  \n"
            f"SciER: **{len(scier_raw.sentences)}** sentences, "
            f"**{len(scier_raw.mentions)}** entities, "
            f"**{len(scier_raw.relation)}** relations"
        )

        _label_table(report, count_entity_labels(gsap_raw),   "GSAP Entity Types (raw)")
        _label_table(report, count_relation_labels(gsap_raw), "GSAP Relation Types (raw)")
        _label_table(report, count_entity_labels(scier_raw),   "SciER Entity Types (raw)")
        _label_table(report, count_relation_labels(scier_raw), "SciER Relation Types (raw)")

        # ── 2. Unified counts ──────────────────────────────────────────────────
        # Unify gold using each dataset's own scheme
        gsap_unified, _  = apply_unification_pipeline(
            deepcopy(gsap_raw),  "gsap-ere",  apply_to_gold=True, apply_to_predicted=False
        )
        scier_unified, _ = apply_unification_pipeline(
            deepcopy(scier_raw), "scier", apply_to_gold=True, apply_to_predicted=False
        )

        report.heading("2. Unified Annotations", level=3)
        report.text(
            f"GSAP: **{len(gsap_unified.mentions)}** entities, "
            f"**{len(gsap_unified.relation)}** relations  \n"
            f"SciER: **{len(scier_unified.mentions)}** entities, "
            f"**{len(scier_unified.relation)}** relations"
        )

        _comparison_table(
            report,
            count_entity_labels(gsap_unified),
            count_entity_labels(scier_unified),
            "Entity Types (unified)",
        )
        _comparison_table(
            report,
            count_relation_labels(gsap_unified),
            count_relation_labels(scier_unified),
            "Relation Types (unified)",
        )

        # ── 3. Common sentences ───────────────────────────────────────────────
        common_pairs, gsap_only_sents, scier_only_sents = find_common_sentences(
            gsap_unified.sentences, scier_unified.sentences
        )

        report.heading("3. Common Sentences & Confusion Analysis", level=3)
        report.text(
            f"Sentence matching by normalised text content:  \n"
            f"- **{len(common_pairs)}** sentences in common  \n"
            f"- **{len(gsap_only_sents)}** sentences only in GSAP  \n"
            f"- **{len(scier_only_sents)}** sentences only in SciER"
        )

        if not common_pairs:
            report.text("_No common sentences found — skipping confusion analysis._")
            continue

        gsap_common_ids  = {(s.doc_id, s.idx) for s, _ in common_pairs}
        scier_common_ids = {(s.doc_id, s.idx) for _, s in common_pairs}

        gsap_reduced  = filter_corpus_to_sentences(gsap_unified,  gsap_common_ids)
        scier_reduced = filter_corpus_to_sentences(scier_unified, scier_common_ids)

        report.text(
            f"On common sentences —  \n"
            f"GSAP: **{len(gsap_reduced.mentions)}** entities, "
            f"**{len(gsap_reduced.relation)}** relations  \n"
            f"SciER: **{len(scier_reduced.mentions)}** entities, "
            f"**{len(scier_reduced.relation)}** relations"
        )

        # ── 4. Confusion matrix (unified labels, common sentences) ─────────────
        report.heading(
            "4. Entity Label Confusion Matrix (unified labels, common sentences)",
            level=3,
        )
        report.text(
            "Built on the **unified** label scheme (Dataset / Method / Task) "
            "restricted to the sentences shared between both datasets. "
            "Rows = GSAP labels, Columns = SciER labels. "
            "NIL = entity present in one dataset with no partially-overlapping "
            "span in the other."
        )

        counts, cell_pairs = build_confusion(
            gsap_reduced.mentions, scier_reduced.mentions,
            gsap_unified.sentences, scier_unified.sentences,
            common_pairs, rng,
        )

        # Collect all labels (excluding NIL for sorting)
        gsap_entity_labels = sorted(
            {lbl for lbl in counts if lbl != "NIL"}
        )
        scier_entity_labels = sorted(
            {lbl for row in counts.values() for lbl in row if lbl != "NIL"}
        )

        cm_text = _confusion_md(
            counts, cell_pairs, gsap_entity_labels, scier_entity_labels, rng
        )
        report.text(cm_text)

    report.write("reports/ere_confusion_analysis/paper_annotation_comparison.md")


if __name__ == "__main__":
    main()
