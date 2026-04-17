"""Primitive signal functions for abbreviation-pair detection.

All functions are pure (no side effects) and operate on plain strings or
character offsets.  They are imported by both the rule-based detector
(detect.py) and the ML feature extractor (features.py) so that the two
approaches are always computed from the same primitives.
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Relation labels that may encode an abbreviation pair.
ABBREV_RELATION_LABELS: frozenset[str] = frozenset(
    {"coreference", "Synonym-Of", "similarWith"}
)

#: Maximum character distance between span end and next span start that is
#: still considered "proximate" (Signal A5).
MAX_CHAR_DISTANCE: int = 60

#: Minimum length ratio (longer / shorter) for the short form to be an abbr.
MIN_LENGTH_RATIO: float = 3.0

#: Minimum uppercase ratio for the short form (Signal A4 / B2).
MIN_UPPERCASE_RATIO: float = 0.5

#: Maximum character length of the short form.
MAX_SHORT_LEN: int = 10

#: Regex for Subtask B — two variants, tried in order:
#:   Normal:   "<long> (<short>)"  e.g. "unsupervised domain adaptation (UDA)"
#:   Inverted: "<short> (<long>)"  e.g. "MMR ( maximal marginal relevance )"
#: Space before "(" and closing ")" are both optional (annotation noise).
#: Named groups are always "long" and "short" so callers need no changes.
_PAREN_RE = re.compile(
    r"^(?P<long>[A-Za-z][^()]{3,})\s*\(\s*(?P<short>[^\)]{1,9})\s*\)?$"
)
_PAREN_RE_INV = re.compile(
    r"^(?P<short>[A-Za-z][A-Za-z0-9\-]{1,9})\s*\(\s*(?P<long>[A-Za-z][^()]{3,})\s*\)?$"
)

# ---------------------------------------------------------------------------
# String-level helpers
# ---------------------------------------------------------------------------


def uppercase_ratio(text: str) -> float:
    """Fraction of ASCII letters in *text* that are uppercase.

    Returns 0.0 if *text* contains no ASCII letters.
    """
    letters = [c for c in text if c.isascii() and c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)


def _is_camel_case(text: str) -> bool:
    last = None
    for c in text:
        if last is not None and last.islower() and c.isupper():
            return True
        last = c
    return False


def _content_word_initials(text: str) -> str:
    """Return the initial letters of content words (non-function words) in *text*.

    Function words (articles, prepositions, conjunctions) are skipped so that
    "Long Short-Term Memory" maps to "LSTM" rather than "LSTM".
    """
    STOPWORDS = frozenset(
        {
            "a",
            "an",
            "the",
            "of",
            "in",
            "on",
            "at",
            "to",
            "for",
            "and",
            "or",
            "but",
            "with",
            "by",
            "from",
            "as",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
        }
    )
    words = re.split(r"[\s\-]+", text)
    return "".join(w[0] for w in words if w and w.lower() not in STOPWORDS).upper()


def acronym_score(long_form: str, short_form: str) -> float:
    """Fraction of *short_form* characters matched by content-word initials of
    *long_form*, allowing at most one substitution (edit distance ≤ 1).

    Returns a value in [0, 1].  A score of 1.0 means perfect alignment.
    """
    initials = _content_word_initials(long_form)
    short = short_form.upper()

    if not initials or not short:
        return 0.0

    # Exact prefix match
    matches = sum(1 for a, b in zip(initials, short) if a == b)
    max_possible = max(len(initials), len(short))
    score = matches / max_possible

    # Allow one substitution: try dropping one character from either side
    if score < 1.0 and len(short) <= len(initials) + 1:
        for i in range(len(short)):
            trimmed = short[:i] + short[i + 1 :]
            m = sum(1 for a, b in zip(initials, trimmed) if a == b)
            alt = m / max_possible
            if alt > score:
                score = alt

    return score


# ---------------------------------------------------------------------------
# Span-pair signals (Subtask A)
# ---------------------------------------------------------------------------


def signal_label_membership(relation_label: str) -> bool:
    """A1 — Relation label is in the target set."""
    return relation_label in ABBREV_RELATION_LABELS


def signal_entity_type_match(type_a: str, type_b: str) -> bool:
    """A2 — Both mentions share the same entity type."""
    return type_a == type_b


def signal_length_asymmetry(text_a: str, text_b: str) -> bool:
    """A3 — One span is ≥3× longer than the other and the shorter has no space."""
    la, lb = len(text_a), len(text_b)
    if la == 0 or lb == 0:
        return False
    longer, shorter = (text_a, text_b) if la >= lb else (text_b, text_a)
    ratio = len(longer) / len(shorter)
    return ratio >= MIN_LENGTH_RATIO and " " not in shorter


def signal_short_uppercase(text_a: str, text_b: str) -> bool:
    """A4 — The shorter span has uppercase_ratio > MIN_UPPERCASE_RATIO."""
    shorter = text_a if len(text_a) <= len(text_b) else text_b
    return uppercase_ratio(shorter) > MIN_UPPERCASE_RATIO


def signal_span_proximity(end_earlier: int, start_later: int) -> bool:
    """A5 — Character distance between spans is within MAX_CHAR_DISTANCE."""
    return 0 <= (start_later - end_earlier) <= MAX_CHAR_DISTANCE


def signal_acronym(text_a: str, text_b: str, threshold: float = 0.75) -> bool:
    """A6 — Acronym check in either direction, score ≥ threshold."""
    longer, shorter = (
        (text_a, text_b) if len(text_a) >= len(text_b) else (text_b, text_a)
    )
    return acronym_score(longer, shorter) >= threshold


def short_form(text_a: str, text_b: str) -> str:
    """Return whichever of the two texts is shorter."""
    return text_a if len(text_a) <= len(text_b) else text_b


def long_form(text_a: str, text_b: str) -> str:
    """Return whichever of the two texts is longer."""
    return text_a if len(text_a) >= len(text_b) else text_b


# ---------------------------------------------------------------------------
# Single-span signals (Subtask B)
# ---------------------------------------------------------------------------


def signal_parenthetical_pattern(span_text: str) -> re.Match | None:
    """B1 — Span text matches '<long> (<short>)' pattern.

    Returns the regex match object (with groups 'long' and 'short') if the
    pattern fires, or None otherwise.
    """
    return _PAREN_RE.match(span_text.strip())


def signal_paren_uppercase(span_text: str) -> bool:
    """B2 — The parenthesised token in *span_text* has uppercase_ratio > threshold.

    Returns False if no parenthetical token is found.
    """
    m = signal_parenthetical_pattern(span_text)
    if m is None:
        return False
    return uppercase_ratio(m.group("short")) > MIN_UPPERCASE_RATIO


def signal_paren_acronym(span_text: str, threshold: float = 0.75) -> bool:
    """B3 — Acronym check between the long and short parts of a merged span."""
    m = signal_parenthetical_pattern(span_text)
    if m is None:
        return False
    return acronym_score(m.group("long"), m.group("short")) >= threshold
