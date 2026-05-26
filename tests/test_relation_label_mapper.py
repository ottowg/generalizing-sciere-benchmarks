"""Tests for unifiedsciere.unification.relation_label_mapper."""

from pathlib import Path

import pytest
import yaml
from conftest import make_corpus, make_mention, make_relation

from unifiedsciere.unification.relation_label_mapper import (
    drop_unmapped_relations,
    load_relation_mappings,
    map_relations_to_unified,
)

SIMPLE_REL_MAPPING = {
    "canonical_relations": [
        "appliedTo",
        "benchmarkFor",
        "trainedEvaluatedOn",
        "coreference",
        "isHyponymOf",
        "isComparedTo",
        "usedFor",
    ],
    "undirected_relations": ["coreference", "isComparedTo"],
    "mappings": {
        "testds": {
            "Used-For": "appliedTo",
            "evaluatedOn": {"canonical": "benchmarkFor", "inverted": True},
            "UsedFor": "appliedTo",
            "UsedFor_if_object_is_Method": "usedFor",
            "JunkRel": None,
        }
    },
}


@pytest.fixture
def mapping_file(tmp_path):
    p = tmp_path / "relation_mappings.yaml"
    p.write_text(yaml.dump(SIMPLE_REL_MAPPING))
    return p


def test_load_default_mappings():
    mappings = load_relation_mappings()
    assert "mappings" in mappings
    assert "gsap-ere" in mappings["mappings"]


def test_load_custom_mappings(mapping_file):
    mappings = load_relation_mappings(mapping_file)
    assert mappings["mappings"]["testds"]["Used-For"] == "appliedTo"
    assert mappings["mappings"]["testds"]["JunkRel"] is None


def test_drop_unmapped_relations(mapping_file):
    m1 = make_mention(id="m1", label="Method")
    m2 = make_mention(id="m2", label="Task")
    r1 = make_relation(m1, m2, label="Used-For")
    r2 = make_relation(m1, m2, label="JunkRel")
    corpus = make_corpus(mentions=[m1, m2], relations=[r1, r2])

    filtered, stats = drop_unmapped_relations(
        corpus,
        "testds",
        drop_gold=True,
        drop_predicted=False,
        mapping_file=mapping_file,
    )
    assert len(filtered.relation) == 1
    assert filtered.relation[0].label == "Used-For"
    assert stats["gold_relations_dropped"] == 1


def test_map_relations_to_unified(mapping_file):
    m_method = make_mention(id="m1", label="Method")
    m_task = make_mention(id="m2", label="Task")
    m_dataset = make_mention(id="m3", label="Dataset")

    r1 = make_relation(m_method, m_task, label="Used-For")
    r2 = make_relation(m_task, m_dataset, label="evaluatedOn")
    r3 = make_relation(m_method, m_method, label="UsedFor")
    r4 = make_relation(m_method, m_dataset, label="UsedFor")

    corpus = make_corpus(
        mentions=[m_method, m_task, m_dataset], relations=[r1, r2, r3, r4]
    )

    mapped, stats = map_relations_to_unified(
        corpus, "testds", map_gold=True, map_predicted=False, mapping_file=mapping_file
    )

    assert [r.label for r in mapped.relation] == [
        "appliedTo",
        "benchmarkFor",
        "usedFor",
        "appliedTo",
    ]
    # evaluatedOn is inverted: m_dataset -> m_task
    assert mapped.relation[1].subject == m_dataset
    assert mapped.relation[1].object == m_task
    assert stats["gold_relations_inverted"] == 1


def test_map_normalizes_undirected_relation(mapping_file):
    m_left = make_mention(id="m1", label="Method", begin=10, end=20)
    m_right = make_mention(id="m2", label="Method", begin=30, end=40)
    rel = make_relation(m_right, m_left, label="coreference")
    corpus = make_corpus(mentions=[m_left, m_right], relations=[rel])

    mapped, _ = map_relations_to_unified(
        corpus, "testds", map_gold=True, map_predicted=False, mapping_file=mapping_file
    )
    assert mapped.relation[0].subject == m_left
    assert mapped.relation[0].object == m_right
