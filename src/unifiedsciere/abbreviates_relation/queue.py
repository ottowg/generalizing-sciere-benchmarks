"""Build and serialise the active-learning annotation queue.

Public API
----------
    build_queue(corpora, human_labels) -> QueueResult
    load_queue(path)  -> dict          (raw JSON, for the webapp)
    save_queue(result, path)
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from unifiedsciere.types import Corpus

from .annotations import candidate_id_a, candidate_id_b
from .classify import AbbrevClassifier, weak_labels
from .detect import MentionPairCandidate, SingleSpanCandidate, detect

# Minimum examples per class needed to attempt ML training.
MIN_PER_CLASS = 3

# Gaussian queue sampling parameters.
QUEUE_SIZE = 20  # items per subtask (user-configurable via --queue-size)
GAUSSIAN_SIGMA = 0.15  # spread around p=0.5; smaller = more focused on uncertainty


# ---------------------------------------------------------------------------
# Input type
# ---------------------------------------------------------------------------


@dataclass
class CorpusEntry:
    """One corpus with its origin metadata."""

    corpus: Corpus
    dataset: str
    split: str


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------


@dataclass
class QueueItem:
    """One serialisable borderline candidate ready for human review."""

    id: str
    subtask: str  # "A" | "B"
    dataset: str
    split: str
    sentence: str
    tokens: list = field(default_factory=list)  # gold tokenization
    long_text: str = ""
    short_text: str = ""
    # Subtask A only
    type_a: str = ""
    type_b: str = ""
    relation_label: str = ""
    subject_text: str = ""
    object_text: str = ""
    subject_begin_token: int = -1
    subject_end_token: int = -1
    object_begin_token: int = -1
    object_end_token: int = -1
    # Subtask B only
    span_text: str = ""
    entity_type: str = ""
    begin_token: int = -1
    end_token: int = -1
    # Queue reason — which region of the probability distribution this item comes from
    queue_reason: str = (
        "uncertain"  # "uncertain" | "verify_positive" | "verify_negative"
    )
    # Signal details
    signals_fired: int = 0
    signals: dict = field(default_factory=dict)
    # Classifier output
    weak_label: str = "borderline"
    uncertainty: float = 0.5
    proba: float = 0.5

    def to_dict(self) -> dict:
        always = {"uncertainty", "proba", "signals_fired", "tokens", "queue_reason"}
        return {
            k: v
            for k, v in self.__dict__.items()
            if (v != "" and v != -1 and v != []) or k in always
        }


@dataclass
class SubtaskSummary:
    n_weak_pos: int = 0
    n_weak_neg: int = 0
    n_human_pos: int = 0
    n_human_neg: int = 0
    n_borderline_unannotated: int = 0
    ml_trained: bool = False

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class QueueResult:
    items: list[QueueItem]
    summary_a: SubtaskSummary
    summary_b: SubtaskSummary
    annotations_loaded: int = 0
    eval_a: dict | None = None
    eval_b: dict | None = None

    def to_dict(self) -> dict:
        d = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "annotations_loaded": self.annotations_loaded,
            "summary": {
                "A": self.summary_a.to_dict(),
                "B": self.summary_b.to_dict(),
            },
            "queue": [item.to_dict() for item in self.items],
        }
        if self.eval_a:
            d["eval_a"] = self.eval_a
        if self.eval_b:
            d["eval_b"] = self.eval_b
        return d


# ---------------------------------------------------------------------------
# Sentence lookup
# ---------------------------------------------------------------------------


def _sentence_index(corpus: Corpus) -> dict[tuple[str, str], str]:
    return {(s.doc_id, str(s.idx)): s.text for s in corpus.sentences}


def _sentence_tokens_index(corpus: Corpus) -> dict[tuple[str, str], list[str]]:
    return {
        (s.doc_id, str(s.idx)): (s.tokens if s.tokens else s.text.split())
        for s in corpus.sentences
    }


def _sent_token_start_index(corpus: Corpus) -> dict[tuple[str, str], int]:
    """Return the document-level token index of the first token of each sentence.

    Sentence token offsets are needed to convert Mention.begin_token /
    end_token (document-level) into sentence-relative indices, as expected
    by SentenceView.
    """
    from collections import defaultdict

    by_doc: dict = defaultdict(list)
    for s in corpus.sentences:
        by_doc[s.doc_id].append(s)
    result: dict = {}
    for doc_id, sents in by_doc.items():
        cumulative = 0
        for s in sorted(sents, key=lambda x: int(x.idx)):
            result[(doc_id, str(s.idx))] = cumulative
            cumulative += s.n_tokens
    return result


def _lookup(index: dict, doc_id: str, sent_idx) -> str:
    return index.get((doc_id, str(sent_idx)), "")


def _lookup_int(index: dict, doc_id: str, sent_idx) -> int:
    return index.get((doc_id, str(sent_idx)), 0)


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------


def _item_a(
    cid: str,
    cand: MentionPairCandidate,
    dataset: str,
    split: str,
    sentence: str,
    tokens: list,
    sent_start: int,
    uncertainty: float,
    proba: float,
) -> QueueItem:
    s, o = cand.relation.subject, cand.relation.object
    # Orient so that short form is subject (abbreviates → long form is object)
    short_m, long_m = (s, o) if len(s.text) <= len(o.text) else (o, s)
    return QueueItem(
        id=cid,
        subtask="A",
        dataset=dataset,
        split=split,
        sentence=sentence,
        tokens=tokens,
        long_text=cand.long_text,
        short_text=cand.short_text,
        type_a=short_m.label,
        type_b=long_m.label,
        relation_label=cand.relation.label,
        subject_text=short_m.text,
        object_text=long_m.text,
        subject_begin_token=short_m.begin_token - sent_start,
        subject_end_token=short_m.end_token - sent_start,
        object_begin_token=long_m.begin_token - sent_start,
        object_end_token=long_m.end_token - sent_start,
        signals_fired=cand.signals_fired,
        signals={
            "s_label_membership": cand.s_label_membership,
            "s_entity_type_match": cand.s_entity_type_match,
            "s_length_asymmetry": cand.s_length_asymmetry,
            "s_short_uppercase": cand.s_short_uppercase,
            "s_span_proximity": cand.s_span_proximity,
            "s_acronym": cand.s_acronym,
        },
        weak_label=cand.weak_label,
        uncertainty=round(uncertainty, 4),
        proba=round(proba, 4),
    )


def _item_b(
    cid: str,
    cand: SingleSpanCandidate,
    dataset: str,
    split: str,
    sentence: str,
    tokens: list,
    sent_start: int,
    uncertainty: float,
    proba: float,
) -> QueueItem:
    m = cand.mention
    return QueueItem(
        id=cid,
        subtask="B",
        dataset=dataset,
        split=split,
        sentence=sentence,
        tokens=tokens,
        long_text=cand.long_text,
        short_text=cand.short_text,
        span_text=m.text,
        entity_type=m.label,
        begin_token=m.begin_token - sent_start,
        end_token=m.end_token - sent_start,
        signals_fired=cand.signals_fired,
        signals={
            "s_parenthetical_pattern": cand.s_parenthetical_pattern,
            "s_paren_uppercase": cand.s_paren_uppercase,
            "s_paren_acronym": cand.s_paren_acronym,
        },
        weak_label=cand.weak_label,
        uncertainty=round(uncertainty, 4),
        proba=round(proba, 4),
    )


# ---------------------------------------------------------------------------
# Per-subtask ranking
# ---------------------------------------------------------------------------


def _gaussian_weight(p: float, sigma: float = GAUSSIAN_SIGMA) -> float:
    """Weight proportional to a Gaussian centered at p=0.5 (maximally uncertain)."""
    return math.exp(-0.5 * ((p - 0.5) / sigma) ** 2)


def _queue_reason(p: float) -> str:
    if p >= 0.75:
        return "verify_positive"
    if p <= 0.25:
        return "verify_negative"
    return "uncertain"


def _oof_predict_proba(
    fixed_cands: list,
    fixed_labels: list[int],
    pool_entries: list[dict],
    seed: int = 42,
    n_folds: int = 3,
    log=None,
    subtask: str = "",
) -> list[float]:
    """Return out-of-fold P(positive) for every entry in *pool_entries*.

    *fixed_cands* (manual annotations + cross-subtask data) are included in the
    training set of every fold.  *pool_entries* are randomly split into
    *n_folds* partitions; each partition is scored by a model trained on the
    fixed set plus the remaining (n_folds-1) partitions.

    Pseudo-labels for pool items:
        weak_label == "positive"  → 1
        anything else (negative / borderline) → 0
    """
    n = len(pool_entries)
    if n == 0:
        return []

    pseudo_labels = [
        1 if e["cand"].weak_label == "positive" else 0 for e in pool_entries
    ]

    # Shuffle pool indices for random fold assignment; seed varies with annotation count
    indices = list(range(n))
    random.Random(seed).shuffle(indices)
    # Split into n_folds using round-robin assignment so sizes are as equal as possible
    folds = [indices[i::n_folds] for i in range(n_folds)]

    oof_probas = [0.5] * n

    for fold_idx in range(n_folds):
        val_indices = folds[fold_idx]
        train_indices = [i for j in range(n_folds) if j != fold_idx for i in folds[j]]

        if not val_indices:
            continue

        tag = f"[{subtask}] " if subtask else ""
        if log:
            log(
                f"{tag}OOF fold {fold_idx + 1}/{n_folds} "
                f"(train {len(train_indices) + len(fixed_cands)}, val {len(val_indices)}) …"
            )

        fold_cands = fixed_cands  # + [pool_entries[i]["cand"] for i in train_indices]
        fold_labels = list(fixed_labels)  # + [pseudo_labels[i] for i in train_indices]

        if len(set(fold_labels)) < 2:
            # Both classes required; leave default 0.5 for this fold's val items
            if log:
                log(
                    f"{tag}  skipped fold {fold_idx + 1} — only one class in training set"
                )
            continue

        try:
            fold_clf = AbbrevClassifier(model="rf", subtask="unified")
            fold_clf.train(fold_cands, fold_labels)
            val_cands = [pool_entries[i]["cand"] for i in val_indices]
            val_probas = fold_clf.predict_proba(val_cands).tolist()
            for idx, p in zip(val_indices, val_probas):
                oof_probas[idx] = p
        except Exception as exc:
            if log:
                log(f"{tag}  fold {fold_idx + 1} failed ({exc}), using p=0.5")

    return oof_probas


def _rank_subtask(
    entries: list[dict],
    subtask: str,
    human_labels: dict[str, int],
    test_ids: set[str] | None = None,
    extra_entries: list[dict] | None = None,
    queue_size: int = QUEUE_SIZE,
    sigma: float = GAUSSIAN_SIGMA,
    log=None,
) -> tuple[list[QueueItem], SubtaskSummary, "AbbrevClassifier | None"]:
    """Train a unified model and Gaussian-sample the annotation queue.

    Training label scheme
    ---------------------
    - Manual annotation (human_labels)    → human label (0 / 1)
    - Weak positive (all signals fired)   → 1
    - Weak negative or borderline         → 0

    Manual items from *this* subtask go into every fold's training set (fixed
    set).  All other pool entries are split 3-way; each partition gets OOF
    scores from a model trained on fixed + the other two partitions.  A
    separate full model (trained on everything) is used for evaluation.

    extra_entries from the other subtask are treated as a fixed training
    supplement — no OOF needed since they are not in this subtask's pool.
    """
    pool_entries, pool_probas, summary, clf = get_pool_entries(
        entries, subtask, human_labels, test_ids, extra_entries, log=log
    )
    # Gaussian-weighted sample; seed varies so each rebuild explores new items
    weights = [_gaussian_weight(p, sigma) for p in pool_probas]
    rng = random.Random(len(human_labels))
    k = min(queue_size, len(pool_entries))
    sampled = rng.choices(range(len(pool_entries)), weights=weights, k=k * 3)
    seen: set[int] = set()
    unique: list[int] = []
    for i in sampled:
        if i not in seen:
            seen.add(i)
            unique.append(i)
        if len(unique) == k:
            break

    if log:
        log(
            f"[{subtask}] Gaussian sampling {k} items from {len(pool_entries)} candidates (σ={sigma}) …"
        )

    make_item = _item_a if subtask == "A" else _item_b
    items: list[QueueItem] = []
    for i in unique:
        e = pool_entries[i]
        prob = pool_probas[i]
        unc = float(0.5 - abs(prob - 0.5))  # prefer hard cases (~0.5)
        # unc = float(abs(prob - 0.5))  # prefer easy cases (~0.0 or ~1.0)
        item = make_item(
            e["cid"],
            e["cand"],
            e["dataset"],
            e["split"],
            e["sentence"],
            e["tokens"],
            e["sent_start"],
            unc,
            float(prob),
        )
        item.queue_reason = _queue_reason(prob)
        items.append(item)

    items.sort(key=lambda x: -x.uncertainty)
    return items, summary, clf


def get_pool_entries(
    entries: list[dict],
    subtask: str,
    human_labels: dict[str, int],
    test_ids: set[str] | None = None,
    extra_entries: list[dict] | None = None,
    log=None,
):
    test_ids = test_ids or set()

    # Partition this subtask's entries
    manual_entries = [
        e for e in entries if e["cid"] in human_labels and e["cid"] not in test_ids
    ]
    pool_entries = [
        e for e in entries if e["cid"] not in human_labels and e["cid"] not in test_ids
    ]

    manual_cands = [e["cand"] for e in manual_entries]
    manual_labels_list = [human_labels[e["cid"]] for e in manual_entries]

    n_human_pos = sum(1 for lb in manual_labels_list if lb == 1)
    n_human_neg = sum(1 for lb in manual_labels_list if lb == 0)
    n_weak_pos = sum(1 for e in pool_entries if e["cand"].weak_label == "positive")
    n_weak_neg = sum(1 for e in pool_entries if e["cand"].weak_label == "negative")

    summary = SubtaskSummary(
        n_weak_pos=n_weak_pos,
        n_weak_neg=n_weak_neg,
        n_human_pos=n_human_pos,
        n_human_neg=n_human_neg,
        n_borderline_unannotated=sum(
            1 for e in pool_entries if e["cand"].weak_label == "borderline"
        ),
    )

    # Extra-subtask data — always in training, no OOF (different pool)
    extra_cands: list = []
    extra_labels: list[int] = []
    if extra_entries:
        for e in extra_entries:
            cid = e["cid"]
            if cid in human_labels:
                extra_cands.append(e["cand"])
                extra_labels.append(human_labels[cid])
            elif e["cand"].weak_label == "positive":
                extra_cands.append(e["cand"])
                extra_labels.append(1)
            elif e["cand"].weak_label in ("negative", "borderline"):
                extra_cands.append(e["cand"])
                extra_labels.append(0)

    # Fixed set: manual (this subtask) + all extra (other subtask)
    fixed_cands = manual_cands + extra_cands
    fixed_labels = manual_labels_list + extra_labels

    # Pool pseudo-labels for trainability check and full-model training
    pool_pseudo = [1 if e["cand"].weak_label == "positive" else 0 for e in pool_entries]
    combined_labels = fixed_labels + pool_pseudo
    can_train = (
        combined_labels.count(0) >= MIN_PER_CLASS
        and combined_labels.count(1) >= MIN_PER_CLASS
    )

    clf: "AbbrevClassifier | None" = None

    if can_train:
        # Full model on all data — used for evaluation only, not for queue scoring
        if log:
            log(
                f"[{subtask}] Training full model "
                f"({len(fixed_cands) + len(pool_entries)} candidates, "
                f"{combined_labels.count(1)} pos / {combined_labels.count(0)} neg) …"
            )
        clf = AbbrevClassifier(model="rf", subtask="unified")
        clf.train(
            fixed_cands + [e["cand"] for e in pool_entries],
            fixed_labels + pool_pseudo,
        )
        summary.ml_trained = True
    elif log:
        log(
            f"[{subtask}] Skipping training — not enough labeled examples "
            f"({combined_labels.count(1)} pos, {combined_labels.count(0)} neg, "
            f"need ≥{MIN_PER_CLASS} each)"
        )

    if not pool_entries:
        return [], [], summary, clf

    # OOF probabilities for Gaussian sampling
    if can_train:
        if log:
            log(
                f"[{subtask}] Computing OOF scores for {len(pool_entries)} pool candidates …"
            )
        pool_probas = _oof_predict_proba(
            fixed_cands,
            fixed_labels,
            pool_entries,
            seed=len(human_labels),
            n_folds=3,
            log=log,
            subtask=subtask,
        )
    else:
        pool_probas = [0.5] * len(pool_entries)

    return pool_entries, pool_probas, summary, clf


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def build_queue(
    corpora: list[CorpusEntry],
    human_labels: dict[str, int],
    annotations_path: "Path | str | None" = None,
    test_set_path: "Path | str | None" = None,
    history_path: "Path | str | None" = None,
    queue_size: int = QUEUE_SIZE,
    sigma: float = GAUSSIAN_SIGMA,
    log=None,
) -> QueueResult:
    """Detect candidates, train classifiers, evaluate, return ranked queue."""
    from .evaluation import (
        append_eval_history,
        build_initial_test_set,
        evaluate_classifier,
        evaluate_rule_based,
        load_test_set,
        save_test_set,
        update_test_set_from_annotations,
    )

    entries_a, entries_b = get_entries(corpora, log)
    # ── Test set ──────────────────────────────────────────────────────────────
    test_ids_a: set[str] = set()
    test_ids_b: set[str] = set()
    test_set: dict | None = None

    if test_set_path:
        test_set_path = Path(test_set_path)
        test_set = load_test_set(test_set_path)

        if test_set is None:
            if log:
                log("Building initial test set …")
            # First run — build initial test set from weak-labeled candidates
            # Subtask A: positives = all-6-signal pairs; borderlines = negatives
            # (consistent with bootstrap training: borderline → label 0).
            labeled_a = [
                (e["cid"], 1 if e["cand"].weak_label == "positive" else 0)
                for e in entries_a
                if e["cand"].weak_label in ("positive", "negative", "borderline")
            ]
            labeled_b = [
                (e["cid"], 1 if e["cand"].weak_label == "positive" else 0)
                for e in entries_b
                if e["cand"].weak_label in ("positive", "negative")
            ]
            test_set = build_initial_test_set(labeled_a, labeled_b)

        if annotations_path:
            test_set = update_test_set_from_annotations(test_set, annotations_path)

        save_test_set(test_set, test_set_path)
        test_ids_a = {item["id"] for item in test_set["A"]}
        test_ids_b = {item["id"] for item in test_set["B"]}

    # ── Train unified model on combined A+B labeled data, then rank per subtask ─
    if log:
        log("— Subtask A —")
    items_a, summary_a, clf_a = _rank_subtask(
        entries_a,
        "A",
        human_labels,
        test_ids_a,
        extra_entries=entries_b,
        queue_size=queue_size,
        sigma=sigma,
        log=log,
    )
    if log:
        log("— Subtask B —")
    items_b, summary_b, clf_b = _rank_subtask(
        entries_b,
        "B",
        human_labels,
        test_ids_b,
        extra_entries=entries_a,
        queue_size=queue_size,
        sigma=sigma,
        log=log,
    )

    # ── Evaluate ─────────────────────────────────────────────────────────────
    if log:
        log("Evaluating on test set …")
    eval_a = eval_b = None
    if test_set:
        cand_by_id = {e["cid"]: e["cand"] for e in entries_a + entries_b}
        eval_a = evaluate_classifier(clf_a, test_set["A"], cand_by_id)
        eval_b = evaluate_classifier(clf_b, test_set["B"], cand_by_id)
        rule_a = evaluate_rule_based(test_set["A"], cand_by_id)
        rule_b = evaluate_rule_based(test_set["B"], cand_by_id)

        if eval_a and rule_a:
            eval_a["rule_based"] = rule_a
            eval_a["f1_gain"] = round(eval_a["f1"] - rule_a["f1"], 4)
        if eval_b and rule_b:
            eval_b["rule_based"] = rule_b
            eval_b["f1_gain"] = round(eval_b["f1"] - rule_b["f1"], 4)

        if history_path and (eval_a or eval_b):
            append_eval_history(
                history_path,
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "n_annotated": len(human_labels),
                    "A": eval_a,
                    "B": eval_b,
                },
            )

    combined = sorted(items_a + items_b, key=lambda x: -x.uncertainty)
    return QueueResult(
        items=combined,
        summary_a=summary_a,
        summary_b=summary_b,
        annotations_loaded=len(human_labels),
        eval_a=eval_a,
        eval_b=eval_b,
    )


def get_entries(corpora: list[CorpusEntry], log=None) -> tuple[list[dict], list[dict]]:
    entries_a: list[dict] = []
    entries_b: list[dict] = []

    n_corpora = len(corpora)
    for ci, ce in enumerate(corpora):
        if log:
            log(
                f"Detecting candidates in {ce.dataset}/{ce.split} ({ci + 1}/{n_corpora}) …"
            )
        sent_text = _sentence_index(ce.corpus)
        sent_tokens = _sentence_tokens_index(ce.corpus)
        sent_start = _sent_token_start_index(ce.corpus)
        result = detect(ce.corpus)

        n_a_before = len(entries_a)
        n_b_before = len(entries_b)

        for cand in result.mention_pairs:
            rel = cand.relation
            entries_a.append(
                {
                    "cid": candidate_id_a(ce.dataset, ce.split, rel),
                    "cand": cand,
                    "dataset": ce.dataset,
                    "split": ce.split,
                    "sentence": _lookup(sent_text, rel.document_id, rel.sent_idx),
                    "tokens": _lookup(sent_tokens, rel.document_id, rel.sent_idx),
                    "sent_start": _lookup_int(
                        sent_start, rel.document_id, rel.sent_idx
                    ),
                }
            )

        for cand in result.single_spans:
            m = cand.mention
            entries_b.append(
                {
                    "cid": candidate_id_b(ce.dataset, ce.split, m),
                    "cand": cand,
                    "dataset": ce.dataset,
                    "split": ce.split,
                    "sentence": _lookup(sent_text, m.document_id, m.sent_idx),
                    "tokens": _lookup(sent_tokens, m.document_id, m.sent_idx),
                    "sent_start": _lookup_int(sent_start, m.document_id, m.sent_idx),
                }
            )

        if log:
            log(
                f"  → {len(entries_a) - n_a_before} subtask-A, "
                f"{len(entries_b) - n_b_before} subtask-B candidates"
            )

    if log:
        log(
            f"Total: {len(entries_a)} subtask-A candidates, {len(entries_b)} subtask-B candidates"
        )
    return entries_a, entries_b


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def save_queue(result: QueueResult, path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2))


def load_queue(path: Path | str) -> dict:
    return json.loads(Path(path).read_text())
