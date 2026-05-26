"""Shared test fixtures for UnifiedSciERE tests."""

import sys
from pathlib import Path

import pytest

# Add src to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unifiedsciere.types import Corpus, Mention, Relation, Sentence


def make_mention(
    id="m1",
    document_id="doc1",
    sent_idx="0",
    text="BERT",
    label="Method",
    begin=0,
    end=4,
    begin_token=0,
    end_token=1,
    split="dev",
    score=1.0,
    annotator="gold",
    dataset="test",
    label_original="",
) -> Mention:
    """Factory for creating Mention objects with sensible defaults."""
    return Mention(
        id=id,
        document_id=document_id,
        sent_idx=sent_idx,
        text=text,
        label=label,
        begin=begin,
        end=end,
        begin_token=begin_token,
        end_token=end_token,
        split=split,
        score=score,
        annotator=annotator,
        dataset=dataset,
        label_original=label_original,
    )


def make_relation(
    subject: Mention,
    object: Mention,
    label="Used-for",
    score=1.0,
    annotator="gold",
    dataset="test",
) -> Relation:
    """Factory for creating Relation objects."""
    return Relation(
        subject=subject,
        label=label,
        object=object,
        score=score,
        annotator=annotator,
        dataset=dataset,
    )


def make_corpus(
    mentions=None,
    relations=None,
    mentions_predicted=None,
    relations_predicted=None,
    sentences=None,
) -> Corpus:
    """Factory for creating Corpus objects with defaults."""
    if sentences is None:
        sentences = [
            Sentence(text="BERT is a model.", doc_id="doc1", idx=0, split="dev"),
            Sentence(text="GLUE is a benchmark.", doc_id="doc1", idx=1, split="dev"),
        ]
    if mentions is None:
        mentions = []
    if relations is None:
        relations = []
    return Corpus(
        sentences=sentences,
        mentions=mentions,
        relation=relations,
        mentions_predicted=mentions_predicted,
        relations_predicted=relations_predicted,
    )


@pytest.fixture
def sample_corpus() -> Corpus:
    """A small corpus with overlapping mentions and varied labels for testing.

    Gold mentions (doc1, sent 0):
      g1: "the BERT model" (0-14, Method) — overlaps g2
      g2: "BERT" (4-8, Method) — overlaps g1
      g3: "GLUE" (20-24, Dataset)
      g4: "NER" (30-33, Task)

    Predicted mentions (doc1, sent 0):
      p1: "the BERT model" (0-14, MLModel) — overlaps p2
      p2: "BERT" (4-8, MLModel) — overlaps p1
      p3: "GLUE benchmark" (20-35, dataset)
      p4: "NER" (30-33, Task)

    Gold relations: g1 -> Used-for -> g3, g1 -> Used-for -> g4
    Predicted relations: p1 -> Used-for -> p3, p1 -> Used-for -> p4
    """
    g1 = make_mention(
        id="g1",
        text="the BERT model",
        label="Method",
        begin=0,
        end=14,
        begin_token=0,
        end_token=3,
    )
    g2 = make_mention(
        id="g2", text="BERT", label="Method", begin=4, end=8, begin_token=1, end_token=2
    )
    g3 = make_mention(
        id="g3",
        text="GLUE",
        label="Dataset",
        begin=20,
        end=24,
        begin_token=5,
        end_token=6,
    )
    g4 = make_mention(
        id="g4", text="NER", label="Task", begin=30, end=33, begin_token=8, end_token=9
    )

    p1 = make_mention(
        id="p1",
        text="the BERT model",
        label="MLModel",
        begin=0,
        end=14,
        begin_token=0,
        end_token=3,
        annotator="gsap-ere",
    )
    p2 = make_mention(
        id="p2",
        text="BERT",
        label="MLModel",
        begin=4,
        end=8,
        begin_token=1,
        end_token=2,
        annotator="gsap-ere",
    )
    p3 = make_mention(
        id="p3",
        text="GLUE benchmark",
        label="dataset",
        begin=20,
        end=35,
        begin_token=5,
        end_token=7,
        annotator="gsap-ere",
    )
    p4 = make_mention(
        id="p4",
        text="NER",
        label="Task",
        begin=30,
        end=33,
        begin_token=8,
        end_token=9,
        annotator="gsap-ere",
    )

    gr1 = make_relation(g1, g3, label="Used-for")
    gr2 = make_relation(g1, g4, label="Used-for")

    pr1 = make_relation(p1, p3, label="Used-for", annotator="gsap-ere")
    pr2 = make_relation(p1, p4, label="Used-for", annotator="gsap-ere")

    return Corpus(
        sentences=[
            Sentence(
                text="the BERT model is evaluated on GLUE and NER tasks.",
                doc_id="doc1",
                idx=0,
                split="dev",
            ),
        ],
        mentions=[g1, g2, g3, g4],
        relation=[gr1, gr2],
        mentions_predicted=[p1, p2, p3, p4],
        relations_predicted=[pr1, pr2],
    )
