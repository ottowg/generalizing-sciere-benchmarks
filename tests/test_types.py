"""Tests for dataclass types in unifiedsciere.types."""

from conftest import make_mention, make_relation

from unifiedsciere.types import Corpus, Sentence


def test_sentence_id_property():
    s = Sentence(text="Hello world.", doc_id="doc1", idx=3, split="dev")
    assert s.id == "doc1 3"


def test_sentence_default_n_mentions():
    s = Sentence(text="Hello.", doc_id="doc1", idx=0, split="dev")
    assert s.n_mentions == 0


def test_relation_signature():
    subj = make_mention(id="s1", label="Method")
    obj = make_mention(id="o1", label="Dataset")
    rel = make_relation(subj, obj, label="Used-for")
    assert rel.signature == ("Method", "Used-for", "Dataset")


def test_relation_split():
    subj = make_mention(id="s1", split="test")
    obj = make_mention(id="o1", split="test")
    rel = make_relation(subj, obj)
    assert rel.split == "test"


def test_relation_document_id():
    subj = make_mention(id="s1", document_id="doc42")
    obj = make_mention(id="o1", document_id="doc42")
    rel = make_relation(subj, obj)
    assert rel.document_id == "doc42"


def test_relation_sent_idx():
    subj = make_mention(id="s1", sent_idx="5")
    obj = make_mention(id="o1", sent_idx="5")
    rel = make_relation(subj, obj)
    assert rel.sent_idx == "5"


def test_relation_token_offsets():
    subj = make_mention(id="s1", begin_token=2, end_token=4)
    obj = make_mention(id="o1", begin_token=6, end_token=8)
    rel = make_relation(subj, obj)
    assert rel.subject_begin_token == 2
    assert rel.subject_end_token == 4
    assert rel.object_begin_token == 6
    assert rel.object_end_token == 8


def test_corpus_post_init_none_to_empty_list():
    c = Corpus(
        sentences=[],
        mentions=[],
        relation=[],
        mentions_predicted=None,
        relations_predicted=None,
    )
    assert c.mentions_predicted == []
    assert c.relations_predicted == []


def test_corpus_post_init_preserves_lists():
    m = make_mention(id="p1")
    c = Corpus(
        sentences=[],
        mentions=[],
        relation=[],
        mentions_predicted=[m],
        relations_predicted=[],
    )
    assert c.mentions_predicted == [m]


def test_corpus_format_relation_includes_sentence():
    subj = make_mention(
        id="s1", label="MLModel", text="BERT", document_id="doc1", sent_idx="0"
    )
    obj = make_mention(
        id="o1",
        label="Dataset",
        text="Arxiv Corpus",
        document_id="doc1",
        sent_idx="0",
    )
    rel = make_relation(subj, obj, label="trainedOn")
    corpus = Corpus(
        sentences=[
            Sentence(
                text="BERT is trained on Arxiv Corpus.",
                doc_id="doc1",
                idx=0,
                split="dev",
            )
        ],
        mentions=[subj, obj],
        relation=[rel],
    )
    formatted = corpus.format_relation(0)
    assert "BERT is trained on Arxiv Corpus." in formatted
    assert '[MLModel: "BERT"] -(trainedOn)-> [Dataset: "Arxiv Corpus"]' in formatted


def test_corpus_format_relation_out_of_range():
    corpus = Corpus(sentences=[], mentions=[], relation=[])
    try:
        corpus.format_relation(0)
    except IndexError as exc:
        assert "relation_id out of range" in str(exc)
    else:
        assert False, "Expected IndexError for out-of-range relation_id"
