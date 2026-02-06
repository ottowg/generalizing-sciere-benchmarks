import sys
from pathlib import Path

import pytest

# Add src to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unifiedsciere.data_loader import _load_docs, _process_docs, load_corpus
from unifiedsciere.types import Corpus, Mention, Relation, Sentence


@pytest.fixture
def test_data_path() -> Path:
    """Return the path to the test resources directory."""
    return Path(__file__).parent / "resources"


@pytest.fixture
def sample_jsonl_file(test_data_path: Path) -> Path:
    """Return the path to the sample JSONL file."""
    return test_data_path / "test_sample.jsonl"


def test_load_from_path(test_data_path: Path, sample_jsonl_file: Path) -> None:
    """Test that _load_docs correctly loads JSONL documents."""
    docs = _load_docs(test_data_path, ["test_sample.jsonl"])

    # Should load 2 documents (2 lines in the file)
    assert len(docs) == 2

    # Each document should have required fields
    for doc in docs:
        assert "sentences" in doc
        assert "split" in doc
        assert "doc_key" in doc

    # Check that split is correctly set to the file stem
    assert all(doc["split"] == "test_sample" for doc in docs)


def test_load_docs_basic(test_data_path: Path) -> None:
    """Test that _process_docs correctly processes documents into Corpus."""
    docs = _load_docs(test_data_path, ["test_sample.jsonl"])
    corpus = _process_docs(docs)

    # Should create a Corpus object
    assert isinstance(corpus, Corpus)

    # Corpus should have sentences, mentions, and relations
    assert hasattr(corpus, "sentences")
    assert hasattr(corpus, "mentions")
    assert hasattr(corpus, "relation")

    # Sentences should be created
    assert len(corpus.sentences) > 0
    assert all(isinstance(s, Sentence) for s in corpus.sentences)


def test_sentence_structure(test_data_path: Path) -> None:
    """Test that Sentence objects have correct structure."""
    docs = _load_docs(test_data_path, ["test_sample.jsonl"])
    corpus = _process_docs(docs)

    # Check first sentence
    first_sentence = corpus.sentences[0]
    assert isinstance(first_sentence, Sentence)
    assert hasattr(first_sentence, "text")
    assert hasattr(first_sentence, "doc_id")
    assert hasattr(first_sentence, "idx")
    assert hasattr(first_sentence, "split")
    assert hasattr(first_sentence, "n_mentions")

    # Check that sentence ID is properly formatted
    assert first_sentence.id == f"{first_sentence.doc_id} {first_sentence.idx}"

    # Split should be test_sample
    assert first_sentence.split == "test_sample"


def test_mention_structure(test_data_path: Path) -> None:
    """Test that Mention objects have correct structure."""
    docs = _load_docs(test_data_path, ["test_sample.jsonl"])
    corpus = _process_docs(docs)

    # Only test if mentions exist
    if len(corpus.mentions) > 0:
        first_mention = corpus.mentions[0]
        assert isinstance(first_mention, Mention)
        assert hasattr(first_mention, "id")
        assert hasattr(first_mention, "document_id")
        assert hasattr(first_mention, "sent_id")
        assert hasattr(first_mention, "text")
        assert hasattr(first_mention, "label")
        assert hasattr(first_mention, "begin")
        assert hasattr(first_mention, "end")
        assert hasattr(first_mention, "begin_token")
        assert hasattr(first_mention, "end_token")
        assert hasattr(first_mention, "split")


def test_relation_structure(test_data_path: Path) -> None:
    """Test that Relation objects have correct structure."""
    docs = _load_docs(test_data_path, ["test_sample.jsonl"])
    corpus = _process_docs(docs)

    # Only test if relations exist
    if len(corpus.relation) > 0:
        first_relation = corpus.relation[0]
        assert isinstance(first_relation, Relation)
        assert hasattr(first_relation, "subject")
        assert hasattr(first_relation, "label")
        assert hasattr(first_relation, "object")

        # Subject and object should be Mention instances
        assert isinstance(first_relation.subject, Mention)
        assert isinstance(first_relation.object, Mention)

        # Check computed properties
        assert first_relation.signature is not None
        assert first_relation.split == first_relation.subject.split
        assert first_relation.document_id == first_relation.subject.document_id


def test_empty_file_handling(test_data_path: Path, tmp_path: Path) -> None:
    """Test that the loader handles empty files gracefully."""
    # Create an empty JSONL file
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("")

    docs = _load_docs(tmp_path, ["empty.jsonl"])

    # Should return empty list for empty file
    assert len(docs) == 0

    # _process_docs should handle empty docs list
    corpus = _process_docs(docs)
    assert len(corpus.sentences) == 0
    assert len(corpus.mentions) == 0
    assert len(corpus.relation) == 0


def test_doc_key_generation(test_data_path: Path, tmp_path: Path) -> None:
    """Test that doc_key is auto-generated when not present."""
    # Create a simple JSONL without doc_key
    test_file = tmp_path / "no_doc_key.jsonl"
    test_file.write_text(
        '{"sentences": [["Test", "sentence"]], "ner": [[]], "relations": [[]]}\n'
    )

    docs = _load_docs(tmp_path, ["no_doc_key.jsonl"])

    # doc_key should be auto-generated
    assert len(docs) == 1
    assert "doc_key" in docs[0]
    assert docs[0]["doc_key"] == "no_doc_key_0"


def test_load_corpus_with_env() -> None:
    """Test that load_corpus loads data from environment-configured folders."""
    import os

    # Check if environment variables are set
    gold_folder = os.getenv("DATA_GOLD_FOLDER")
    predictions_folder = os.getenv("DATA_PREDICTIONS_FOLDER")

    if not gold_folder or not predictions_folder:
        pytest.skip("Environment variables not set")

    # Check if test data exists
    gold_path = Path(gold_folder)
    predictions_path = Path(predictions_folder)

    if not gold_path.exists() or not predictions_path.exists():
        pytest.skip("Data folders do not exist")

    # Test loading predictions from gsap model evaluated on gsap test set
    try:
        corpus = load_corpus(
            dataset="gsap", split="test", data_type="predictions", trained_on="gsap"
        )
        assert isinstance(corpus, Corpus)
        assert len(corpus.sentences) > 0
    except FileNotFoundError:
        pytest.skip("Test data file not found")


def test_load_corpus_gold() -> None:
    """Test that load_corpus loads gold standard data."""
    import os

    # Check if environment variables are set
    gold_folder = os.getenv("DATA_GOLD_FOLDER")

    if not gold_folder:
        pytest.skip("DATA_GOLD_FOLDER environment variable not set")

    # Check if gold data folder exists
    gold_path = Path(gold_folder)
    if not gold_path.exists():
        pytest.skip("Gold data folder does not exist")

    # Test loading gold standard data for scinlp dev set
    try:
        corpus = load_corpus(dataset="scinlp", split="dev", data_type="gold")
        assert isinstance(corpus, Corpus)
        assert len(corpus.sentences) > 0
    except FileNotFoundError:
        pytest.skip("Gold data file not found")


def test_load_corpus_requires_trained_on_for_predictions() -> None:
    """Test that load_corpus raises error when trained_on is not provided for predictions."""
    import os

    predictions_folder = os.getenv("DATA_PREDICTIONS_FOLDER")
    if not predictions_folder or not Path(predictions_folder).exists():
        pytest.skip("Predictions folder not available")

    # Should raise ValueError when trained_on is not provided for predictions
    with pytest.raises(ValueError, match="trained_on parameter is required"):
        load_corpus(dataset="gsap", split="test", data_type="predictions")
