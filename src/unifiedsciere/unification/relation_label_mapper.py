"""Relation mapping functions for unifying relation labels across datasets.

This module provides functions to map relation labels from different annotation
schemes to a unified relation set, drop unmapped relations, and optionally
invert relations when required by the mapping.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml

from ..types import Corpus, Relation

_CONDITIONAL_RE = re.compile(
    r"^(?P<label>.+)_if_(?P<role>subject|object)_is_(?P<ent_label>.+)$"
)


def load_relation_mappings(mapping_file: Path | None = None) -> dict:
    """Load relation mappings from YAML file.

    Args:
        mapping_file: Path to YAML file with relation mappings.
            If None, uses default relation_mappings.yaml in this directory.

    Returns:
        Dictionary with relation mappings.
    """
    if mapping_file is None:
        mapping_file = Path(__file__).parent / "relation_mappings.yaml"

    with open(mapping_file, "r") as f:
        return yaml.safe_load(f)


def _normalize_undirected_relation(rel: Relation) -> Relation:
    subj = rel.subject
    obj = rel.object
    if (subj.begin, subj.end) <= (obj.begin, obj.end):
        return rel
    return Relation(
        subject=obj,
        label=rel.label,
        object=subj,
        score=rel.score,
        annotator=rel.annotator,
        dataset=rel.dataset,
    )


def _parse_mapping_value(value) -> tuple[str | None, bool]:
    if value is None:
        return None, False
    if isinstance(value, str):
        return value, False
    if isinstance(value, dict):
        canonical = value.get("canonical")
        inverted = bool(value.get("inverted", False))
        return canonical, inverted
    raise TypeError(f"Unsupported mapping value type: {type(value)}")


def _resolve_relation_mapping(
    label_map: dict,
    relation: Relation,
    canonical_relations: set[str] | None = None,
) -> tuple[str | None, bool, str | None]:
    """Resolve mapping for a relation label.

    Returns (canonical_label, inverted, matched_key).
    """
    subject_label = relation.subject.label
    object_label = relation.object.label

    for key in sorted(label_map.keys()):
        match = _CONDITIONAL_RE.match(key)
        if not match:
            continue
        if match.group("label") != relation.label:
            continue
        role = match.group("role")
        ent_label = match.group("ent_label")
        if role == "subject" and subject_label == ent_label:
            canonical, inverted = _parse_mapping_value(label_map[key])
            return canonical, inverted, key
        if role == "object" and object_label == ent_label:
            canonical, inverted = _parse_mapping_value(label_map[key])
            return canonical, inverted, key

    if relation.label in label_map:
        canonical, inverted = _parse_mapping_value(label_map[relation.label])
        return canonical, inverted, relation.label

    if canonical_relations and relation.label in canonical_relations:
        return relation.label, False, relation.label

    return None, False, None


def drop_unmapped_relations(
    corpus: Corpus,
    dataset: Literal["scier", "scinlp", "gsap"],
    drop_gold: bool = True,
    drop_predicted: bool = True,
    mapping_file: Path | None = None,
) -> tuple[Corpus, dict]:
    """Drop relations that map to null or are unmapped in the unified schema."""
    mappings = load_relation_mappings(mapping_file)
    label_map = mappings["mappings"][dataset]
    canonical_relations = set(mappings.get("canonical_relations", []))

    stats = {
        "gold_relations_original": len(corpus.relation),
        "gold_relations_dropped": 0,
        "gold_relations_kept": len(corpus.relation),
        "predicted_relations_original": len(corpus.relations_predicted),
        "predicted_relations_dropped": 0,
        "predicted_relations_kept": len(corpus.relations_predicted),
    }

    if drop_gold:
        kept_relations = []
        for rel in corpus.relation:
            canonical, _, _ = _resolve_relation_mapping(
                label_map, rel, canonical_relations
            )
            if canonical is None:
                continue
            kept_relations.append(rel)
        stats["gold_relations_dropped"] = len(corpus.relation) - len(kept_relations)
        stats["gold_relations_kept"] = len(kept_relations)
    else:
        kept_relations = corpus.relation

    if drop_predicted:
        kept_relations_pred = []
        for rel in corpus.relations_predicted:
            canonical, _, _ = _resolve_relation_mapping(
                label_map, rel, canonical_relations
            )
            if canonical is None:
                continue
            kept_relations_pred.append(rel)
        stats["predicted_relations_dropped"] = len(corpus.relations_predicted) - len(
            kept_relations_pred
        )
        stats["predicted_relations_kept"] = len(kept_relations_pred)
    else:
        kept_relations_pred = corpus.relations_predicted

    filtered_corpus = Corpus(
        sentences=corpus.sentences,
        mentions=corpus.mentions,
        relation=kept_relations,
        mentions_predicted=corpus.mentions_predicted,
        relations_predicted=kept_relations_pred,
    )
    return filtered_corpus, stats


def map_relations_to_unified(
    corpus: Corpus,
    dataset: Literal["scier", "scinlp", "gsap"],
    map_gold: bool = True,
    map_predicted: bool = True,
    mapping_file: Path | None = None,
) -> tuple[Corpus, dict]:
    """Map relation labels to the unified relation set, with optional inversion."""
    mappings = load_relation_mappings(mapping_file)
    label_map = mappings["mappings"][dataset]
    canonical_relations = set(mappings.get("canonical_relations", []))
    undirected = set(mappings.get("undirected_relations", []))

    from collections import defaultdict

    stats = {
        "gold_relation_changes": defaultdict(lambda: defaultdict(int)),
        "predicted_relation_changes": defaultdict(lambda: defaultdict(int)),
        "gold_relations_mapped": 0,
        "predicted_relations_mapped": 0,
        "gold_relations_inverted": 0,
        "predicted_relations_inverted": 0,
    }

    def _map_relation(rel: Relation) -> Relation | None:
        canonical, inverted, _ = _resolve_relation_mapping(
            label_map, rel, canonical_relations
        )
        if canonical is None:
            return None
        subject = rel.object if inverted else rel.subject
        object_ = rel.subject if inverted else rel.object
        mapped = Relation(
            subject=subject,
            label=canonical,
            object=object_,
            score=rel.score,
            annotator=rel.annotator,
            dataset=rel.dataset,
        )
        if mapped.label in undirected:
            mapped = _normalize_undirected_relation(mapped)
        return mapped

    if map_gold:
        mapped_relations = []
        for rel in corpus.relation:
            mapped = _map_relation(rel)
            if mapped is None:
                continue
            if rel.label != mapped.label:
                stats["gold_relation_changes"][rel.label][mapped.label] += 1
                stats["gold_relations_mapped"] += 1
            if mapped.subject != rel.subject:
                stats["gold_relations_inverted"] += 1
            mapped_relations.append(mapped)
    else:
        mapped_relations = corpus.relation

    if map_predicted:
        mapped_relations_pred = []
        for rel in corpus.relations_predicted:
            mapped = _map_relation(rel)
            if mapped is None:
                continue
            if rel.label != mapped.label:
                stats["predicted_relation_changes"][rel.label][mapped.label] += 1
                stats["predicted_relations_mapped"] += 1
            if mapped.subject != rel.subject:
                stats["predicted_relations_inverted"] += 1
            mapped_relations_pred.append(mapped)
    else:
        mapped_relations_pred = corpus.relations_predicted

    mapped_corpus = Corpus(
        sentences=corpus.sentences,
        mentions=corpus.mentions,
        relation=mapped_relations,
        mentions_predicted=corpus.mentions_predicted,
        relations_predicted=mapped_relations_pred,
    )

    stats["gold_relation_changes"] = dict(stats["gold_relation_changes"])
    stats["predicted_relation_changes"] = dict(stats["predicted_relation_changes"])
    return mapped_corpus, stats
