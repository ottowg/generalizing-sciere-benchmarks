"""Corpus-level abbreviation normalization.

Applies three transformations to a Corpus:
  1. Relabel  — replace the original relation label with 'Abbreviates'
  2. Canonicalize direction  — short form is always subject, long form object
  3. Split spans (Subtask B)  — split merged 'long (short)' mentions into two
                                separate mentions and insert an Abbreviates relation

The function returns a *new* Corpus; the input is not modified.
"""

from __future__ import annotations

import copy
import dataclasses
from dataclasses import dataclass

from unifiedsciere.types import Corpus, Mention, Relation

from .detect import DetectionResult, MentionPairCandidate, SingleSpanCandidate
from .signals import long_form, short_form, signal_parenthetical_pattern

CANONICAL_LABEL = "Abbreviates"


# ---------------------------------------------------------------------------
# Subtask A — relabel + canonicalize direction
# ---------------------------------------------------------------------------

def _normalize_pair(cand: MentionPairCandidate) -> Relation:
    """Return a new Relation with canonical label and direction."""
    rel = cand.relation
    subj = rel.subject
    obj = rel.object

    # Canonical: short form → subject, long form → object
    if len(subj.text) <= len(obj.text):
        new_subj, new_obj = subj, obj
    else:
        new_subj, new_obj = obj, subj

    return dataclasses.replace(rel, subject=new_subj, label=CANONICAL_LABEL, object=new_obj)


# ---------------------------------------------------------------------------
# Subtask B — split merged span into two mentions + one relation
# ---------------------------------------------------------------------------

def _split_span(cand: SingleSpanCandidate, id_suffix: str = "_abbr") -> tuple[Mention, Mention, Relation]:
    """Split a merged-span mention into (long_mention, short_mention, relation).

    The long mention retains the entity type and character offsets of the
    original mention.  The short mention gets the same entity type and a new
    id.  The Abbreviates relation points short → long.
    """
    m = signal_parenthetical_pattern(cand.mention.text)
    assert m is not None, "split_span called on non-matching candidate"

    orig = cand.mention
    long_t = m.group("long").strip()
    short_t = m.group("short").strip()

    # Character offsets within the original span
    long_start = orig.begin
    long_end = orig.begin + orig.text.index("(") - 1  # up to the space before '('
    paren_start = orig.text.index("(")
    short_start = orig.begin + paren_start + 1
    short_end = short_start + len(short_t)

    long_mention = dataclasses.replace(
        orig,
        id=orig.id + "_long",
        text=long_t,
        begin=long_start,
        end=long_end,
    )
    short_mention = dataclasses.replace(
        orig,
        id=orig.id + "_short",
        text=short_t,
        begin=short_start,
        end=short_end,
    )

    relation = Relation(
        subject=short_mention,
        label=CANONICAL_LABEL,
        object=long_mention,
        score=1.0,
        annotator=orig.annotator,
        dataset=orig.dataset,
    )
    return long_mention, short_mention, relation


# ---------------------------------------------------------------------------
# Main normalization entry point
# ---------------------------------------------------------------------------

def apply_normalization(corpus: Corpus, result: DetectionResult) -> Corpus:
    """Return a new Corpus with abbreviation normalization applied.

    Parameters
    ----------
    corpus:
        The original corpus (not modified).
    result:
        DetectionResult from detect.detect(corpus) — only rule_based_positive
        candidates are acted upon.
    """
    # Ids of relations that will be replaced (Subtask A)
    pair_positives: list[MentionPairCandidate] = result.positives_a()
    replaced_relation_ids: set[int] = {
        id(c.relation) for c in pair_positives
    }

    # Ids of mentions that will be split (Subtask B)
    span_positives: list[SingleSpanCandidate] = result.positives_b()
    replaced_mention_ids: set[int] = {
        id(c.mention) for c in span_positives
    }

    # Build updated relation list
    new_relations: list[Relation] = []
    pair_map = {id(c.relation): c for c in pair_positives}

    for rel in corpus.relation:
        if id(rel) in pair_map:
            new_relations.append(_normalize_pair(pair_map[id(rel)]))
        else:
            new_relations.append(rel)

    # Build updated mention list + additional split mentions and relations
    new_mentions: list[Mention] = []
    split_relations: list[Relation] = []

    for mention in corpus.mentions:
        if id(mention) not in replaced_mention_ids:
            new_mentions.append(mention)
        # replaced mentions are dropped; split parts are added below

    for cand in span_positives:
        long_m, short_m, rel = _split_span(cand)
        new_mentions.append(long_m)
        new_mentions.append(short_m)
        split_relations.append(rel)

    return dataclasses.replace(
        corpus,
        mentions=new_mentions,
        relation=new_relations + split_relations,
    )
