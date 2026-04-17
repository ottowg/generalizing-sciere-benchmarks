"""Abbreviation-pair detection.

Subtask A — Mention-pair detection
    Scans existing binary relations whose label is in ABBREV_RELATION_LABELS
    and scores each pair against the six rule-based signals.

Subtask B — Single-span detection
    Scans entity mentions whose text matches the '<long> (<short>)' pattern
    and scores each against the three single-span signals.

Both subtasks return a list of dataclass instances that record which individual
signals fired.  This intermediate representation is consumed by:
  - the rule-based accept/reject decision  (all signals must fire)
  - features.py                            (signals_fired count + raw values)
  - the active learning queue              (borderline = partial signal match)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from unifiedsciere.types import Corpus, Mention, Relation

from .signals import (
    acronym_score,
    long_form,
    short_form,
    signal_acronym,
    signal_entity_type_match,
    signal_label_membership,
    signal_length_asymmetry,
    signal_paren_acronym,
    signal_paren_uppercase,
    signal_parenthetical_pattern,
    signal_short_uppercase,
    signal_span_proximity,
    uppercase_ratio,
)

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

WeakLabel = Literal["positive", "negative", "borderline"]


@dataclass
class MentionPairCandidate:
    """Result of Subtask A for one mention pair."""

    relation: Relation

    # Individual signal outcomes
    s_label_membership: bool = False  # A1
    s_entity_type_match: bool = False  # A2
    s_length_asymmetry: bool = False  # A3
    s_short_uppercase: bool = False  # A4
    s_span_proximity: bool = False  # A5
    s_acronym: bool = False  # A6

    # Derived quantities (used by features.py)
    char_distance: int = 0
    length_ratio: float = 0.0
    short_uppercase_ratio: float = 0.0
    acronym_score_value: float = 0.0

    @property
    def signals_fired(self) -> int:
        return sum(
            [
                self.s_label_membership,
                self.s_entity_type_match,
                self.s_length_asymmetry,
                self.s_short_uppercase,
                self.s_span_proximity,
                self.s_acronym,
            ]
        )

    @property
    def rule_based_positive(self) -> bool:
        """True when all six signals fire."""
        return self.signals_fired == 6

    @property
    def weak_label(self) -> WeakLabel:
        n = self.signals_fired
        if n == 6:
            return "positive"
        if n == 2:
            return "negative"
        return "borderline"

    @property
    def short_text(self) -> str:
        return short_form(self.relation.subject.text, self.relation.object.text)

    @property
    def long_text(self) -> str:
        return long_form(self.relation.subject.text, self.relation.object.text)


@dataclass
class SingleSpanCandidate:
    """Result of Subtask B for one single-span mention."""

    mention: Mention

    # Individual signal outcomes
    s_parenthetical_pattern: bool = False  # B1
    s_paren_uppercase: bool = False  # B2
    s_paren_acronym: bool = False  # B3

    # Derived quantities
    long_text: str = ""
    short_text: str = ""
    short_uppercase_ratio: float = 0.0
    acronym_score_value: float = 0.0

    @property
    def signals_fired(self) -> int:
        return sum(
            [
                self.s_parenthetical_pattern,
                self.s_paren_uppercase,
                self.s_paren_acronym,
            ]
        )

    @property
    def rule_based_positive(self) -> bool:
        return self.signals_fired == 3

    @property
    def weak_label(self) -> WeakLabel:
        n = self.signals_fired
        if n == 3:
            return "positive"
        if n == 0:
            return "negative"
        return "borderline"


# ---------------------------------------------------------------------------
# Subtask A — mention-pair detection
# ---------------------------------------------------------------------------


def detect_mention_pairs(corpus: Corpus) -> list[MentionPairCandidate]:
    """Score every relation in *corpus* that may encode an abbreviation pair.

    Only relations whose label is in ABBREV_RELATION_LABELS are considered;
    all others are skipped.  The function is read-only — it does not modify
    the corpus.
    """
    results: list[MentionPairCandidate] = []

    for rel in corpus.relation:
        if not signal_label_membership(rel.label):
            continue

        subj = rel.subject
        obj = rel.object
        ta, tb = subj.text, obj.text

        # Span ordering by character offset
        if subj.begin <= obj.begin:
            earlier_end, later_start = subj.end, obj.begin
        else:
            earlier_end, later_start = obj.end, subj.begin

        dist = max(0, later_start - earlier_end)
        la, lb = len(ta), len(tb)
        longer_t = ta if la >= lb else tb
        shorter_t = ta if la <= lb else tb
        ratio = (len(longer_t) / len(shorter_t)) if len(shorter_t) > 0 else 0.0
        up_ratio = uppercase_ratio(shorter_t)
        ac_score = acronym_score(longer_t, shorter_t)

        cand = MentionPairCandidate(
            relation=rel,
            s_label_membership=True,  # already filtered above
            s_entity_type_match=signal_entity_type_match(subj.label, obj.label),
            s_length_asymmetry=signal_length_asymmetry(ta, tb),
            s_short_uppercase=signal_short_uppercase(ta, tb),
            s_span_proximity=signal_span_proximity(earlier_end, later_start),
            s_acronym=signal_acronym(ta, tb),
            char_distance=dist,
            length_ratio=ratio,
            short_uppercase_ratio=up_ratio,
            acronym_score_value=ac_score,
        )
        results.append(cand)

    return results


# ---------------------------------------------------------------------------
# Subtask B — single-span detection
# ---------------------------------------------------------------------------


def detect_single_spans(corpus: Corpus) -> list[SingleSpanCandidate]:
    """Score every mention in *corpus* that may encode a merged abbreviation span.

    Only mentions whose text contains '(' are considered.  The function is
    read-only.
    """
    results: list[SingleSpanCandidate] = []

    for mention in corpus.mentions:
        if mention.label == "ReferenceLink":
            continue
        if "(" not in mention.text:
            continue

        m = signal_parenthetical_pattern(mention.text)
        if m is None:
            # '(' present but pattern doesn't match — still a candidate with
            # s_parenthetical_pattern=False so it ends up as negative/borderline
            results.append(
                SingleSpanCandidate(
                    mention=mention,
                    s_parenthetical_pattern=False,
                    s_paren_uppercase=False,
                    s_paren_acronym=False,
                )
            )
            continue

        long_t = m.group("long").strip()
        short_t = m.group("short").strip()
        up_ratio = uppercase_ratio(short_t)
        ac_score = acronym_score(long_t, short_t)

        results.append(
            SingleSpanCandidate(
                mention=mention,
                s_parenthetical_pattern=True,
                s_paren_uppercase=signal_paren_uppercase(mention.text),
                s_paren_acronym=signal_paren_acronym(mention.text),
                long_text=long_t,
                short_text=short_t,
                short_uppercase_ratio=up_ratio,
                acronym_score_value=ac_score,
            )
        )

    return results


# ---------------------------------------------------------------------------
# Convenience: run both subtasks at once
# ---------------------------------------------------------------------------


@dataclass
class DetectionResult:
    mention_pairs: list[MentionPairCandidate] = field(default_factory=list)
    single_spans: list[SingleSpanCandidate] = field(default_factory=list)

    def positives_a(self) -> list[MentionPairCandidate]:
        return [c for c in self.mention_pairs if c.rule_based_positive]

    def positives_b(self) -> list[SingleSpanCandidate]:
        return [c for c in self.single_spans if c.rule_based_positive]

    def borderline_a(self) -> list[MentionPairCandidate]:
        return [c for c in self.mention_pairs if c.weak_label == "borderline"]

    def borderline_b(self) -> list[SingleSpanCandidate]:
        return [c for c in self.single_spans if c.weak_label == "borderline"]


def detect(corpus: Corpus) -> DetectionResult:
    """Run both subtasks and return a combined DetectionResult."""
    return DetectionResult(
        mention_pairs=detect_mention_pairs(corpus),
        single_spans=detect_single_spans(corpus),
    )
