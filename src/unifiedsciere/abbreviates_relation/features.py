"""Feature extraction for supervised abbreviation classification.

Each candidate (MentionPairCandidate or SingleSpanCandidate) is converted to
a flat dict of named features.  The same primitive values computed during
detection are reused directly — nothing is recomputed from scratch.

Usage
-----
    from unifiedsciere.abbreviates_relation.features import (
        features_from_pair, features_from_span, PAIR_FEATURE_NAMES, SPAN_FEATURE_NAMES
    )

    feat_dict = features_from_pair(cand)
    # or build a numpy / pandas row:
    feat_vec  = [feat_dict[k] for k in PAIR_FEATURE_NAMES]
"""

from __future__ import annotations

from typing import Any

from .detect import MentionPairCandidate, SingleSpanCandidate
from .signals import ABBREV_RELATION_LABELS

CandidateType = MentionPairCandidate | SingleSpanCandidate


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _is_subsequence(short: str, long: str) -> bool:
    """Return True if every character of *short* appears in *long* in order.

    Comparison is case-insensitive.  This is a necessary (but not sufficient)
    condition for genuine acronym abbreviations (e.g. 'cnn' ⊆ 'convolutional
    neural network').
    """
    it = iter(long.lower())
    short = short.replace(" - ", "")
    short = short.replace("-", "")
    return all(c in it for c in short.lower())


def _is_camel_case(text: str) -> bool:
    last = None
    for c in text:
        if last is not None and last.islower() and c.isupper():
            return True
        last = c
    return False


_SORTED_DATASETS = ["gsap-ere", "scier", "scinlp"]


def _dataset_onehot(dataset: str) -> dict[str, int]:
    return {
        f"dataset_{ds.lower().replace('-', '_')}": int(ds == dataset)
        for ds in _SORTED_DATASETS
    }


# ---------------------------------------------------------------------------
# One-hot encoding for relation labels
# ---------------------------------------------------------------------------

_SORTED_LABELS = sorted(ABBREV_RELATION_LABELS)


def _label_onehot(label: str) -> dict[str, int]:
    return {
        f"rel_{lbl.lower().replace('-', '_')}": int(label == lbl)
        for lbl in _SORTED_LABELS
    }


# ---------------------------------------------------------------------------
# Subtask A — mention-pair features
# ---------------------------------------------------------------------------

#: Ordered list of feature names for Subtask A vectors.
PAIR_FEATURE_NAMES: list[str] = [
    "char_distance",
    "length_ratio",
    "length_asymmetric",
    "short_uppercase_ratio",
    "short_has_whitespace",
    "bracket_adjacent",
    "entity_type_match",
    "acronym_score",
    "char_subsequence",
    "is_identical",
    "is_camel_case",
    "short_len",
    "long_len",
    "signals_fired",
    # one-hot relation label
    *[f"rel_{lbl.lower().replace('-', '_')}" for lbl in _SORTED_LABELS]
    + [f"rel_{ds.replace('-', '_')}" for ds in _SORTED_DATASETS],
]


def features_from_pair(cand: MentionPairCandidate) -> dict[str, Any]:
    """Extract a feature dict from a MentionPairCandidate."""
    subj = cand.relation.subject
    obj = cand.relation.object
    ta, tb = subj.text, obj.text
    shorter = ta if len(ta) <= len(tb) else tb
    longer = ta if len(ta) > len(tb) else tb

    # 'bracket_adjacent': the shorter span is preceded by '(' in the sentence
    # We approximate this by checking whether the shorter mention is surrounded
    # by parentheses in the relation's document context.  Since we don't have
    # raw sentence text here we use a proxy: char_distance == 0 and the longer
    # span ends with ')' or the shorter text itself starts with '(' is not the
    # case, so we conservatively set it based on distance and the relation's
    # span ordering.
    bracket_adjacent = int(cand.char_distance <= 2 and "(" not in longer)

    feat: dict[str, Any] = {
        "char_distance": cand.char_distance,
        "length_ratio": cand.length_ratio,
        "length_asymmetric": int(len(shorter) < len(longer)),
        "short_uppercase_ratio": cand.short_uppercase_ratio,
        "short_has_whitespace": int(" " in shorter),
        "bracket_adjacent": bracket_adjacent,
        "entity_type_match": int(cand.s_entity_type_match),
        "acronym_score": cand.acronym_score_value,
        "char_subsequence": int(_is_subsequence(shorter, longer)),
        "is_identical": int(shorter.lower() == longer.lower()),
        "is_camel_case": int(_is_camel_case(shorter)),
        "short_len": len(shorter),
        "long_len": len(longer),
        "signals_fired": cand.signals_fired,
    }
    feat.update(_label_onehot(cand.relation.label))
    feat.update(_dataset_onehot(cand.relation.dataset))
    return feat


# ---------------------------------------------------------------------------
# Subtask B — single-span features
# ---------------------------------------------------------------------------

#: Ordered list of feature names for Subtask B vectors.
SPAN_FEATURE_NAMES: list[str] = [
    "length_ratio",
    "length_asymmetric",
    "short_uppercase_ratio",
    "short_has_whitespace",
    "bracket_present",
    "acronym_score",
    "char_subsequence",
    "is_identical",
    "is_camel_case",
    "short_len",
    "long_len",
    "signals_fired",
    *[f"rel_{ds.replace('-', '_')}" for ds in _SORTED_DATASETS],
]


def features_from_span(cand: SingleSpanCandidate) -> dict[str, Any]:
    """Extract a feature dict from a SingleSpanCandidate."""
    short_t = cand.short_text
    long_t = cand.long_text

    length_ratio = (len(long_t) / len(short_t)) if short_t else 0.0

    feat = {
        "length_ratio": length_ratio,
        "length_asymmetric": int(len(short_t) < len(long_t)),
        "short_uppercase_ratio": cand.short_uppercase_ratio,
        "short_has_whitespace": int(" " in short_t),
        "bracket_present": int(cand.s_parenthetical_pattern),
        "acronym_score": cand.acronym_score_value,
        "char_subsequence": int(_is_subsequence(short_t, long_t)),
        "is_identical": int(_normalize(short_t) == _normalize(long_t)),
        "is_camel_case": int(_is_camel_case(short_t)),
        "short_len": len(short_t),
        "long_len": len(long_t),
        "signals_fired": cand.signals_fired,
    }
    feat.update(_dataset_onehot(cand.mention.dataset))

    return feat


# ---------------------------------------------------------------------------
# Unified feature space (A + B combined training)
# ---------------------------------------------------------------------------

#: Feature names shared by both subtasks in the unified model.
UNIFIED_FEATURE_NAMES: list[str] = [
    "length_ratio",
    "length_asymmetric",
    "short_uppercase_ratio",
    "short_has_whitespace",
    "bracket_present",  # bracket_adjacent for A, parenthetical pattern for B
    "entity_type_match",  # actual for A; always 1 for B (same span)
    "char_distance",  # actual for A; 0 for B (forms are adjacent)
    "acronym_score",
    "char_subsequence",
    "is_identical",
    "is_camel_case",
    "short_len",
    "long_len",
    "signals_fired_ratio",  # signals_fired / max_signals (normalised 0–1)
    "is_pair",  # 1 for Subtask A candidates, 0 for Subtask B
    *[f"rel_{lbl.lower().replace('-', '_')}" for lbl in _SORTED_LABELS]
    + [f"rel_{ds.replace('-', '_')}" for ds in _SORTED_DATASETS],
]


def _normalize(text: str) -> str:
    return text.lower().replace("-", "").replace(" ", "")


def features_unified(cand: CandidateType) -> dict[str, Any]:
    """Extract a unified feature dict usable for both Subtask A and B candidates."""
    if isinstance(cand, MentionPairCandidate):
        subj = cand.relation.subject
        obj = cand.relation.object
        ta, tb = subj.text, obj.text
        shorter = ta if len(ta) <= len(tb) else tb
        longer = ta if len(ta) >= len(tb) else tb
        bracket_adjacent = int(cand.char_distance <= 2 and "(" not in longer)
        feat = {
            "length_ratio": cand.length_ratio,
            "length_asymmetric": int(len(shorter) < len(longer)),
            "short_uppercase_ratio": cand.short_uppercase_ratio,
            "short_has_whitespace": int(" " in shorter),
            "bracket_present": bracket_adjacent,
            "entity_type_match": int(cand.s_entity_type_match),
            "char_distance": cand.char_distance,
            "acronym_score": cand.acronym_score_value,
            "char_subsequence": int(_is_subsequence(shorter, longer)),
            "is_identical": int(_normalize(shorter) == _normalize(longer)),
            "is_camel_case": int(_is_camel_case(shorter)),
            "short_len": len(shorter),
            "long_len": len(longer),
            "signals_fired_ratio": cand.signals_fired / 6,
            "is_pair": 1,
        }
        feat.update(_dataset_onehot(cand.relation.dataset))
        return feat

    elif isinstance(cand, SingleSpanCandidate):
        short_t = cand.short_text
        long_t = cand.long_text
        length_ratio = (len(long_t) / len(short_t)) if short_t else 0.0
        feat = {
            "length_ratio": length_ratio,
            "length_asymmetric": int(len(short_t) < len(long_t)),
            "short_uppercase_ratio": cand.short_uppercase_ratio,
            "short_has_whitespace": int(" " in short_t),
            "bracket_present": int(cand.s_parenthetical_pattern),
            "entity_type_match": 1,  # same span → same entity type
            "char_distance": 0,  # forms are adjacent within the span
            "acronym_score": cand.acronym_score_value,
            "char_subsequence": int(_is_subsequence(short_t, long_t)),
            "is_identical": int(_normalize(short_t) == _normalize(long_t)),
            "is_camel_case": int(_is_camel_case(short_t)),
            "short_len": len(short_t),
            "long_len": len(long_t),
            "signals_fired_ratio": cand.signals_fired / 3,
            "is_pair": 0,
        }
        feat.update(_dataset_onehot(cand.mention.dataset))
        return feat
    else:
        raise ValueError(f"Unknown candidate type: {type(cand)}")
