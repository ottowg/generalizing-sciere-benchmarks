"""Tests for analysis conversion helper functions."""

from conftest import make_mention, make_relation

from unifiedsciere.analysis.label_confusion import (
    _mentions_to_gsaphub_format as lc_mentions_format,
)
from unifiedsciere.analysis.model_performance import (
    _mentions_to_gsaphub_format as mp_mentions_format,
)
from unifiedsciere.analysis.model_performance import (
    _relations_to_gsaphub_format as mp_relations_format,
)


# ---------- model_performance._mentions_to_gsaphub_format ----------


def test_mp_mentions_format_keys():
    m = make_mention(
        id="m1", document_id="doc1", begin=0, end=4, label="Method", annotator="gsap-ere"
    )
    result = mp_mentions_format([m])
    assert len(result) == 1
    d = result[0]
    assert d["id"] == "m1"
    assert d["doc_id"] == "doc1"
    assert d["begin"] == 0
    assert d["end"] == 4
    assert d["label"] == "Method"
    assert d["annotator"] == "gsap-ere"


def test_mp_mentions_format_empty():
    assert mp_mentions_format([]) == []


def test_mp_mentions_format_multiple():
    m1 = make_mention(id="a")
    m2 = make_mention(id="b")
    result = mp_mentions_format([m1, m2])
    assert len(result) == 2


# ---------- model_performance._relations_to_gsaphub_format ----------


def test_mp_relations_format_keys():
    subj = make_mention(id="s1", document_id="doc1")
    obj = make_mention(id="o1", document_id="doc1")
    rel = make_relation(subj, obj, label="Used-for")
    result = mp_relations_format([rel])
    assert len(result) == 1
    d = result[0]
    assert d["doc_id"] == "doc1"
    assert d["subject_id"] == "s1"
    assert d["object_id"] == "o1"
    assert d["relation_label"] == "Used-for"
    assert "id" in d


def test_mp_relations_format_empty():
    assert mp_relations_format([]) == []


# ---------- label_confusion._mentions_to_gsaphub_format ----------


def test_lc_mentions_format_normalize_doc_id():
    """With normalize_doc_id=True, the first part of doc_id (model prefix) is stripped."""
    m = make_mention(id="m1", document_id="scinlp_gsap_dev_0")
    result = lc_mentions_format([m], normalize_doc_id=True)
    assert result[0]["doc_id"] == "gsap_dev_0"


def test_lc_mentions_format_no_normalize():
    m = make_mention(id="m1", document_id="scinlp_gsap_dev_0")
    result = lc_mentions_format([m], normalize_doc_id=False)
    assert result[0]["doc_id"] == "scinlp_gsap_dev_0"


def test_lc_mentions_format_no_underscore():
    """If doc_id has no underscore, it stays unchanged even with normalize=True."""
    m = make_mention(id="m1", document_id="simpledoc")
    result = lc_mentions_format([m], normalize_doc_id=True)
    assert result[0]["doc_id"] == "simpledoc"


def test_lc_mentions_format_keys():
    m = make_mention(
        id="m1",
        document_id="model_doc1",
        begin=5,
        end=10,
        label="Task",
        annotator="gold",
    )
    result = lc_mentions_format([m], normalize_doc_id=True)
    d = result[0]
    assert d["id"] == "m1"
    assert d["doc_id"] == "doc1"
    assert d["begin"] == 5
    assert d["end"] == 10
    assert d["label"] == "Task"
    assert d["annotator"] == "gold"
