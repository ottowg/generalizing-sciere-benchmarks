"""Tests for unifiedsciere.unification.merge_stacked."""

from conftest import make_mention, make_relation

from unifiedsciere.unification.merge_stacked import (
    _mentions_overlap,
    _merge_mentions,
    _remap_relations,
    merge_stacked_mentions,
)

# ---------- _mentions_overlap ----------


def test_overlap_same_doc_sent_overlapping():
    m1 = make_mention(id="a", document_id="d1", sent_idx="0", begin=0, end=10)
    m2 = make_mention(id="b", document_id="d1", sent_idx="0", begin=5, end=15)
    assert _mentions_overlap(m1, m2) is True


def test_overlap_same_doc_sent_contained():
    m1 = make_mention(id="a", document_id="d1", sent_idx="0", begin=0, end=20)
    m2 = make_mention(id="b", document_id="d1", sent_idx="0", begin=5, end=10)
    assert _mentions_overlap(m1, m2) is True


def test_overlap_non_overlapping():
    m1 = make_mention(id="a", document_id="d1", sent_idx="0", begin=0, end=5)
    m2 = make_mention(id="b", document_id="d1", sent_idx="0", begin=10, end=15)
    assert _mentions_overlap(m1, m2) is False


def test_overlap_adjacent_not_overlapping():
    """Adjacent spans (end of one == begin of other) should NOT overlap."""
    m1 = make_mention(id="a", document_id="d1", sent_idx="0", begin=0, end=5)
    m2 = make_mention(id="b", document_id="d1", sent_idx="0", begin=5, end=10)
    assert _mentions_overlap(m1, m2) is False


def test_overlap_different_document():
    m1 = make_mention(id="a", document_id="d1", sent_idx="0", begin=0, end=10)
    m2 = make_mention(id="b", document_id="d2", sent_idx="0", begin=0, end=10)
    assert _mentions_overlap(m1, m2) is False


def test_overlap_different_sentence():
    m1 = make_mention(id="a", document_id="d1", sent_idx="0", begin=0, end=10)
    m2 = make_mention(id="b", document_id="d1", sent_idx="1", begin=0, end=10)
    assert _mentions_overlap(m1, m2) is False


# ---------- _merge_mentions ----------


def test_merge_empty_list():
    merged, mapping, stats = _merge_mentions([])
    assert merged == []
    assert mapping == {}
    assert stats == []


def test_merge_no_overlaps():
    m1 = make_mention(id="a", begin=0, end=5)
    m2 = make_mention(id="b", begin=10, end=15)
    merged, mapping, stats = _merge_mentions([m1, m2])
    assert len(merged) == 2
    assert stats == []


def test_merge_two_overlapping_prefer_larger():
    small = make_mention(id="small", begin=4, end=8, text="BERT")
    large = make_mention(id="large", begin=0, end=14, text="the BERT model")
    merged, mapping, stats = _merge_mentions([small, large], prefer_larger=True)
    assert len(merged) == 1
    assert merged[0].id == "large"
    assert mapping["small"].id == "large"
    assert mapping["large"].id == "large"


def test_merge_two_overlapping_prefer_smaller():
    small = make_mention(id="small", begin=4, end=8, text="BERT")
    large = make_mention(id="large", begin=0, end=14, text="the BERT model")
    merged, mapping, stats = _merge_mentions([small, large], prefer_larger=False)
    assert len(merged) == 1
    assert merged[0].id == "small"
    assert mapping["large"].id == "small"


def test_merge_three_overlapping_chain():
    """Three mentions in a chain: A overlaps B, B overlaps C."""
    a = make_mention(id="a", begin=0, end=10)
    b = make_mention(id="b", begin=5, end=15)
    c = make_mention(id="c", begin=12, end=20)
    merged, mapping, stats = _merge_mentions([a, b, c], prefer_larger=True)
    # a overlaps b, b overlaps c; the largest span should be kept
    assert len(merged) < 3


def test_merge_id_mapping_complete():
    """All input mention IDs should appear in the mapping."""
    m1 = make_mention(id="a", begin=0, end=10)
    m2 = make_mention(id="b", begin=5, end=15)
    m3 = make_mention(id="c", begin=20, end=25)
    merged, mapping, stats = _merge_mentions([m1, m2, m3])
    assert "a" in mapping
    assert "b" in mapping
    assert "c" in mapping


# ---------- _remap_relations ----------


def test_remap_no_changes_needed():
    m1 = make_mention(id="a", begin=0, end=5)
    m2 = make_mention(id="b", begin=10, end=15)
    rel = make_relation(m1, m2)
    mapping = {"a": m1, "b": m2}
    remapped, self_loops, duplicates, labels = _remap_relations([rel], mapping)
    assert len(remapped) == 1
    assert self_loops == 0
    assert duplicates == 0


def test_remap_subject_remapped():
    m1 = make_mention(id="a", begin=0, end=5)
    m2 = make_mention(id="b", begin=10, end=15)
    m_merged = make_mention(id="merged", begin=0, end=10)
    rel = make_relation(m1, m2)
    mapping = {"a": m_merged, "b": m2}
    remapped, _, _, _ = _remap_relations([rel], mapping)
    assert remapped[0].subject.id == "merged"


def test_remap_self_loop_removed():
    """When subject and object merge to same mention, relation becomes a self-loop."""
    m1 = make_mention(id="a", begin=0, end=10)
    m2 = make_mention(id="b", begin=5, end=15)
    m_merged = make_mention(id="merged", begin=0, end=15)
    rel = make_relation(m1, m2, label="Used-for")
    mapping = {"a": m_merged, "b": m_merged}
    remapped, self_loops, _, self_loop_labels = _remap_relations([rel], mapping)
    assert len(remapped) == 0
    assert self_loops == 1
    assert self_loop_labels == ["Used-for"]


def test_remap_duplicate_removed():
    m1 = make_mention(id="a", begin=0, end=5)
    m2 = make_mention(id="b", begin=10, end=15)
    rel1 = make_relation(m1, m2, label="Used-for")
    rel2 = make_relation(m1, m2, label="Used-for")
    mapping = {"a": m1, "b": m2}
    remapped, _, duplicates, _ = _remap_relations([rel1, rel2], mapping)
    assert len(remapped) == 1
    assert duplicates == 1


# ---------- merge_stacked_mentions ----------


def test_merge_stacked_full(sample_corpus):
    merged_corpus, stats = merge_stacked_mentions(sample_corpus, prefer_larger=True)
    # Overlapping gold mentions g1 and g2 should merge (keep g1, the larger)
    assert stats["gold_merged_count"] < stats["gold_original_count"]
    # Overlapping predicted mentions p1 and p2 should merge
    assert stats["predicted_merged_count"] < stats["predicted_original_count"]


def test_merge_stacked_skip_gold(sample_corpus):
    merged_corpus, stats = merge_stacked_mentions(
        sample_corpus, merge_gold=False, merge_predicted=True
    )
    # Gold should be unchanged
    assert len(merged_corpus.mentions) == len(sample_corpus.mentions)
    # Predicted should have fewer mentions
    assert len(merged_corpus.mentions_predicted) < len(sample_corpus.mentions_predicted)


def test_merge_stacked_stats_keys(sample_corpus):
    _, stats = merge_stacked_mentions(sample_corpus)
    expected_keys = [
        "gold_merges",
        "predicted_merges",
        "gold_original_count",
        "gold_merged_count",
        "predicted_original_count",
        "predicted_merged_count",
        "gold_relations_original",
        "gold_relations_merged",
        "predicted_relations_original",
        "predicted_relations_merged",
    ]
    for key in expected_keys:
        assert key in stats, f"Missing stats key: {key}"
