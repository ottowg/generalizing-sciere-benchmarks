# Data Loader API Reference

## Overview

The `load_corpus` function provides a convenient way to load scientific entity and relation extraction datasets with support for three datasets: **SciER**, **SciNLP**, and **GSAP**.

## Function Signature

```python
def load_corpus(
    dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"],
    data_type: Literal["gold", "predictions"] = "gold",
    trained_on: Literal["scier", "scinlp", "gsap"] | None = None,
    ner_field: str = "ner",
    rel_field: str = "relations",
) -> Corpus
```

## Parameters

- **`dataset`**: The dataset to load
  - `"scier"` - SciER dataset
  - `"scinlp"` - SciNLP dataset  
  - `"gsap"` - GSAP dataset

- **`split`**: The data split to load
  - `"train"` - Training set
  - `"dev"` - Development/validation set
  - `"test"` - Test set

- **`data_type`**: Type of data to load (default: `"gold"`)
  - `"gold"` - Gold standard annotations
  - `"predictions"` - Model predictions

- **`trained_on`**: For predictions, which dataset the model was trained on
  - Required when `data_type="predictions"`
  - Must be one of: `"scier"`, `"scinlp"`, `"gsap"`

- **`ner_field`**: Field name for NER data (default: `"ner"`)

- **`rel_field`**: Field name for relations data (default: `"relations"`)

## Returns

A `Corpus` object containing:
- `sentences`: List of `Sentence` objects
- `mentions`: List of `Mention` objects (named entities)
- `relation`: List of `Relation` objects

## File Naming Convention

The function automatically constructs filenames based on parameters:

- **Gold data**: `{dataset}_{split}.jsonl`
  - Example: `scinlp_dev.jsonl`

- **Predictions**: `{trained_on}_{dataset}_{split}.jsonl`
  - Example: `gsap_scinlp_test.jsonl` (GSAP model evaluated on SciNLP test set)

## Environment Setup

Create a `.env` file in the project root:

```env
DATA_GOLD_FOLDER=data/gold
DATA_PREDICTIONS_FOLDER=data/predictions
```

## Usage Examples

### Load Gold Standard Data

```python
from unifiedsciere.data_loader import load_corpus

# Load SciNLP development set
corpus = load_corpus(
    dataset="scinlp",
    split="dev",
    data_type="gold"
)

print(f"Loaded {len(corpus.sentences)} sentences")
print(f"Found {len(corpus.mentions)} mentions")
print(f"Found {len(corpus.relation)} relations")
```

### Load Model Predictions

```python
# Load predictions from a model trained on GSAP, evaluated on SciNLP test set
corpus = load_corpus(
    dataset="scinlp",      # Dataset to evaluate on
    split="test",          # Test set
    data_type="predictions",
    trained_on="gsap"      # Model was trained on GSAP
)
```

### Compare Models

```python
# Load predictions from different models on the same test set
gsap_model = load_corpus("scinlp", "test", "predictions", trained_on="gsap")
scier_model = load_corpus("scinlp", "test", "predictions", trained_on="scier")
gold = load_corpus("scinlp", "test", "gold")

print(f"GSAP model: {len(gsap_model.mentions)} mentions")
print(f"SciER model: {len(scier_model.mentions)} mentions")
print(f"Gold standard: {len(gold.mentions)} mentions")
```

### Access Corpus Data

```python
corpus = load_corpus("gsap", "test", "gold")

# Access sentences
for sentence in corpus.sentences[:5]:
    print(f"Sentence {sentence.id}: {sentence.text}")
    print(f"  Contains {sentence.n_mentions} mentions")

# Access mentions (named entities)
for mention in corpus.mentions[:5]:
    print(f"Mention: '{mention.text}' - Label: {mention.label}")

# Access relations
for relation in corpus.relation[:5]:
    print(f"Relation: {relation.subject.text} --[{relation.label}]--> {relation.object.text}")
```

## Dataset Matrix

All possible combinations for predictions:

| Trained On | Evaluated On | Split | Example Usage |
|------------|--------------|-------|---------------|
| gsap | gsap | train/dev/test | `load_corpus("gsap", "test", "predictions", trained_on="gsap")` |
| gsap | scinlp | train/dev/test | `load_corpus("scinlp", "test", "predictions", trained_on="gsap")` |
| gsap | scier | train/dev/test | `load_corpus("scier", "test", "predictions", trained_on="gsap")` |
| scinlp | gsap | train/dev/test | `load_corpus("gsap", "test", "predictions", trained_on="scinlp")` |
| scinlp | scinlp | train/dev/test | `load_corpus("scinlp", "test", "predictions", trained_on="scinlp")` |
| scinlp | scier | train/dev/test | `load_corpus("scier", "test", "predictions", trained_on="scinlp")` |
| scier | gsap | train/dev/test | `load_corpus("gsap", "test", "predictions", trained_on="scier")` |
| scier | scinlp | train/dev/test | `load_corpus("scinlp", "test", "predictions", trained_on="scier")` |
| scier | scier | train/dev/test | `load_corpus("scier", "test", "predictions", trained_on="scier")` |

## Error Handling

The function raises `ValueError` in these cases:
- Environment variables not set
- Data folder doesn't exist
- `trained_on` not provided when loading predictions
- Invalid `data_type`, `dataset`, or `split` values

```python
try:
    corpus = load_corpus("gsap", "test", "predictions")  # Missing trained_on
except ValueError as e:
    print(f"Error: {e}")
    # Error: trained_on parameter is required when data_type='predictions'
```

## Data Classes

### Sentence
```python
@dataclass
class Sentence:
    text: str          # Sentence text
    doc_id: str        # Document ID
    idx: int           # Sentence index in document
    split: str         # Data split (train/dev/test)
    n_mentions: int    # Number of mentions in sentence
    
    @property
    def id(self) -> str:  # Returns "{doc_id} {idx}"
```

### Mention
```python
@dataclass
class Mention:
    id: str            # Unique mention ID
    document_id: str   # Document ID
    sent_id: str       # Sentence ID
    text: str          # Mention text
    label: str         # Entity type label
    begin: int         # Character start position
    end: int           # Character end position
    begin_token: int   # Token start position
    end_token: int     # Token end position
    split: str         # Data split
```

### Relation
```python
@dataclass
class Relation:
    subject: Mention   # Subject entity
    label: str         # Relation type
    object: Mention    # Object entity
    
    @property
    def signature(self) -> tuple[str, str, str]:  # (subject_label, rel_label, object_label)
    @property
    def split(self) -> str:  # Data split
    @property
    def document_id(self) -> str:  # Document ID
```

### Corpus
```python
@dataclass
class Corpus:
    sentences: list[Sentence]
    mentions: list[Mention]
    relation: list[Relation]
```
