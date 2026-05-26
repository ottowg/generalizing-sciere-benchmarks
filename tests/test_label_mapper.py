"""Tests for unifiedsciere.unification.label_mapper."""

from pathlib import Path

import pytest
import yaml
from conftest import make_corpus, make_mention, make_relation

from unifiedsciere.unification.label_mapper import (
    drop_unmapped_mentions,
    load_label_mappings,
    map_labels_to_unified,
)

# ---------- Fixtures ----------

SIMPLE_MAPPING = {
    "unified_labels": ["Dataset", "Method", "Task"],
    "mappings": {
        "testds": {
            "Method": "Method",
            "Dataset": "Dataset",
            "Task": "Task",
            "Junk": None,  # unmapped
        }
    },
}


@pytest.fixture
def mapping_file(tmp_path):
    """Write a small label-mapping YAML and return its path."""
    p = tmp_path / "mappings.yaml"
    p.write_text(yaml.dump(SIMPLE_MAPPING))
    return p


@pytest.fixture
def corpus_with_junk():
    """Corpus where some mentions have the 'Junk' label (maps to null)."""
    m1 = make_mention(id="m1", label="Method", text="BERT")
    m2 = make_mention(id="m2", label="Junk", text="something")
    m3 = make_mention(id="m3", label="Dataset", text="GLUE")
    r1 = make_relation(m1, m3, label="Used-for")
    r2 = make_relation(m1, m2, label="Used-for")  # references junk mention

    p1 = make_mention(id="p1", label="Method", text="GPT", annotator="model")
    p2 = make_mention(id="p2", label="Junk", text="stuff", annotator="model")
    pr1 = make_relation(p1, p2, label="Used-for", annotator="model")

    return make_corpus(
        mentions=[m1, m2, m3],
        relations=[r1, r2],
        mentions_predicted=[p1, p2],
        relations_predicted=[pr1],
    )


# ---------- load_label_mappings ----------


def test_load_default_mappings():
    """Default label_mappings.yaml should load without error."""
    mappings = load_label_mappings()
    assert "mappings" in mappings
    assert "gsap-ere" in mappings["mappings"]


def test_load_custom_mappings(mapping_file):
    mappings = load_label_mappings(mapping_file)
    assert mappings["mappings"]["testds"]["Method"] == "Method"
    assert mappings["mappings"]["testds"]["Junk"] is None


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_label_mappings(Path("/nonexistent/file.yaml"))


# ---------- drop_unmapped_mentions ----------


def test_drop_unmapped_gold_and_predicted(corpus_with_junk, mapping_file):
    filtered, stats = drop_unmapped_mentions(
        corpus_with_junk,
        "testds",
        drop_gold=True,
        drop_predicted=True,
        mapping_file=mapping_file,
    )
    # m2 (Junk) should be dropped from gold
    assert len(filtered.mentions) == 2
    assert all(m.label != "Junk" for m in filtered.mentions)
    # r2 references m2 so should be dropped
    assert len(filtered.relation) == 1

    # p2 (Junk) should be dropped from predicted
    assert len(filtered.mentions_predicted) == 1
    # pr1 references p2 so should be dropped
    assert len(filtered.relations_predicted) == 0

    assert stats["gold_mentions_dropped"] == 1
    assert stats["predicted_mentions_dropped"] == 1
    assert stats["gold_relations_dropped"] == 1
    assert stats["predicted_relations_dropped"] == 1
    assert "Junk" in stats["dropped_labels"]


def test_drop_unmapped_skip_gold(corpus_with_junk, mapping_file):
    filtered, stats = drop_unmapped_mentions(
        corpus_with_junk,
        "testds",
        drop_gold=False,
        drop_predicted=True,
        mapping_file=mapping_file,
    )
    # Gold should be unchanged
    assert len(filtered.mentions) == 3
    assert len(filtered.relation) == 2
    # Predicted should be filtered
    assert len(filtered.mentions_predicted) == 1


def test_drop_unmapped_skip_predicted(corpus_with_junk, mapping_file):
    filtered, stats = drop_unmapped_mentions(
        corpus_with_junk,
        "testds",
        drop_gold=True,
        drop_predicted=False,
        mapping_file=mapping_file,
    )
    assert len(filtered.mentions) == 2
    # Predicted should be unchanged
    assert len(filtered.mentions_predicted) == 2
    assert len(filtered.relations_predicted) == 1

    # ---------- map_labels_to_unified ----------

    m1 = make_mention(id="m1", label="Method")
    m2 = make_mention(id="m2", label="Dataset")
    r1 = make_relation(m1, m2)
    corpus = make_corpus(mentions=[m1, m2], relations=[r1])

    mapped, stats = map_labels_to_unified(
        corpus, "testds", map_gold=True, map_predicted=False, mapping_file=mapping_file
    )
    # Labels should remain Method and Dataset (identity mapping in our fixture)
    labels = {m.label for m in mapped.mentions}
    assert labels == {"Method", "Dataset"}


def test_map_preserves_label_original(mapping_file):
    m1 = make_mention(id="m1", label="Method")
    corpus = make_corpus(mentions=[m1])

    mapped, _ = map_labels_to_unified(
        corpus, "testds", map_gold=True, map_predicted=False, mapping_file=mapping_file
    )
    # label_original should be set to the original label
    assert mapped.mentions[0].label_original == "Method"


def test_map_updates_relation_mentions(mapping_file):
    m1 = make_mention(id="m1", label="Method")
    m2 = make_mention(id="m2", label="Dataset")
    r1 = make_relation(m1, m2)
    corpus = make_corpus(mentions=[m1, m2], relations=[r1])

    mapped, _ = map_labels_to_unified(
        corpus, "testds", map_gold=True, map_predicted=False, mapping_file=mapping_file
    )
    # Relations should reference the new mention objects with label_original set
    assert mapped.relation[0].subject.label_original == "Method"


def test_map_skips_null_labels(mapping_file):
    """Mentions mapping to null should be silently skipped."""
    m1 = make_mention(id="m1", label="Junk")
    corpus = make_corpus(mentions=[m1])

    mapped, _ = map_labels_to_unified(
        corpus, "testds", map_gold=True, map_predicted=False, mapping_file=mapping_file
    )
    assert len(mapped.mentions) == 0


def test_map_predicted(mapping_file):
    p1 = make_mention(id="p1", label="Task", annotator="model")
    corpus = make_corpus(mentions_predicted=[p1])

    mapped, stats = map_labels_to_unified(
        corpus, "testds", map_gold=False, map_predicted=True, mapping_file=mapping_file
    )
    assert mapped.mentions_predicted[0].label == "Task"
    assert mapped.mentions_predicted[0].label_original == "Task"
