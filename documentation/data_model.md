# Data Model Documentation

This document describes the core data structures used in UnifiedSciERE for representing scientific entity recognition annotations and predictions.

## Overview

The data model is defined in `src/unifiedsciere/types.py` and consists of four main classes:

1. **Sentence**: Represents a sentence with metadata
2. **Mention**: Represents an entity mention (span) in text
3. **Relation**: Represents a relationship between two entity mentions
4. **Corpus**: Container for sentences, mentions, and relations

## Core Data Structures

### Sentence

Represents a single sentence from a scientific document.

```python
@dataclass
class Sentence:
    text: str          # The sentence text
    doc_id: str        # Document identifier
    idx: int           # Sentence index within document
    split: str         # Data split: "train", "dev", or "test"
    n_mentions: int    # Number of mentions in this sentence (default: 0)
    
    @property
    def id(self):      # Unique identifier: "{doc_id} {idx}"
        return f"{self.doc_id} {self.idx}"
```

**Example:**
```python
sentence = Sentence(
    text="BERT outperforms previous methods on ImageNet.",
    doc_id="paper_123.txt",
    idx=5,
    split="train",
    n_mentions=3
)
```

### Mention

Represents an entity mention (named entity span) within text.

```python
@dataclass
class Mention:
    id: str                # Unique identifier
    document_id: str       # Document identifier
    sent_idx: str          # Sentence index (as string)
    text: str              # Mention surface form
    label: str             # Entity type label
    begin: int             # Character start position
    end: int               # Character end position (exclusive)
    begin_token: int       # Token start position
    end_token: int         # Token end position (exclusive)
    split: str             # Data split
    score: float = 1.0     # Confidence score (1.0 for gold)
    annotator: str = "gold"  # "gold" or model name
    dataset: str = ""      # Source dataset name
    label_original: str = ""  # Original label before unification
```

**Fields Explanation:**

- **id**: Unique identifier, typically `"{document_id} {sent_idx} {begin} {end}"`
- **label**: Current entity label (unified or original)
- **label_original**: Preserves the original label before mapping to unified schema
- **score**: Confidence score from model (1.0 for gold annotations)
- **annotator**: Source of the annotation
  - `"gold"`: Gold standard annotation
  - `"gsap"`, `"scier"`, `"scinlp"`: Model predictions
- **dataset**: Dataset where this mention appears

**Example:**
```python
mention = Mention(
    id="paper_123.txt 5 0 4",
    document_id="paper_123.txt",
    sent_idx="5",
    text="BERT",
    label="Method",                    # Unified label
    label_original="MLModel",          # Original GSAP label
    begin=0,
    end=4,
    begin_token=0,
    end_token=1,
    split="train",
    score=0.95,
    annotator="gsap",
    dataset="gsap"
)
```

### Relation

Represents a typed relationship between two entity mentions.

```python
@dataclass
class Relation:
    subject: Mention       # Subject entity
    label: str             # Relation type
    object: Mention        # Object entity
    score: float = 1.0     # Confidence score
    annotator: str = "gold"  # Source annotator
    dataset: str = ""      # Source dataset
    
    # Convenience properties
    @property
    def signature(self):   # (subject_label, relation_label, object_label)
        return self.subject.label, self.label, self.object.label
    
    @property
    def split(self):       # Inherited from subject
        return self.subject.split
    
    @property
    def document_id(self): # Inherited from subject
        return self.subject.document_id
    
    # ... additional token position properties
```

**Common Relation Types:**

- **GSAP relations**: `usedFor`, `trainedOn`, `evaluatedOn`, `architecture`, etc.
- **SciER relations**: `USED-FOR`, `FEATURE-OF`, `HYPONYM-OF`, etc.
- **SciNLP relations**: Various task-specific relations

**Example:**
```python
bert_mention = Mention(...)  # BERT mention
imagenet_mention = Mention(...)  # ImageNet mention

relation = Relation(
    subject=bert_mention,
    label="evaluatedOn",
    object=imagenet_mention,
    score=0.89,
    annotator="gsap",
    dataset="gsap"
)

# Relation signature
print(relation.signature)  # ("Method", "evaluatedOn", "Dataset")
```

### Corpus

Container class that holds all annotations for a dataset split.

```python
@dataclass
class Corpus:
    sentences: list[Sentence]           # All sentences
    mentions: list[Mention]             # Gold mentions
    relation: list[Relation]            # Gold relations
    mentions_predicted: list[Mention]   # Predicted mentions
    relations_predicted: list[Relation] # Predicted relations
    
    def __post_init__(self):
        # Initialize empty lists if None
        if self.mentions_predicted is None:
            self.mentions_predicted = []
        if self.relations_predicted is None:
            self.relations_predicted = []
```

**Usage Patterns:**

1. **Gold-only corpus** (no predictions):
```python
corpus = Corpus(
    sentences=[...],
    mentions=[...],      # Gold annotations
    relation=[...],      # Gold relations
    mentions_predicted=[],
    relations_predicted=[]
)
```

2. **Prediction corpus** (with gold for comparison):
```python
corpus = Corpus(
    sentences=[...],
    mentions=[...],              # Gold annotations
    relation=[...],              # Gold relations
    mentions_predicted=[...],    # Model predictions
    relations_predicted=[...]    # Predicted relations
)
```

## Label Schemas

### Original Label Sets

#### GSAP Labels
```
Entities:
- Dataset, DatasetGeneric
- MLModel, MLModelGeneric, ModelArchitecture
- Method
- Task
- DataSource
- ReferenceLink
- URL
- ... (and more)
```

#### SciER Labels
```
Entities:
- Dataset
- Method
- Task
- ... (and more)
```

#### SciNLP Labels
```
Entities:
- dataset
- method
- task
- metric
```

### Unified Label Schema

After unification, all labels are mapped to:

```
Unified Labels:
- Dataset: Datasets used for training/evaluation
- Method: Machine learning methods, models, techniques
- Task: Scientific tasks and problems
```

Labels that don't map to the unified schema (e.g., `metric`, `URL`) are dropped during the pipeline.

## Data Flow

### 1. Loading

```python
from src.unifiedsciere.data_loader import load_corpus

# Load with original labels
corpus = load_corpus("gsap", "dev", data_type="predictions", trained_on="gsap")

# At this point:
# - mentions have original labels (e.g., "MLModel")
# - label_original is empty
```

### 2. Unification Pipeline

```python
from src.unifiedsciere.unification.pipeline import apply_unification_pipeline

unified_corpus, stats = apply_unification_pipeline(corpus, "gsap")

# After pipeline:
# - mentions.label has unified labels (e.g., "Method")
# - mentions.label_original preserves original labels (e.g., "MLModel")
# - unmapped labels are removed
# - systematic errors are filtered
```

### 3. Analysis

```python
# Access unified mentions
for mention in unified_corpus.mentions_predicted:
    print(f"Text: {mention.text}")
    print(f"Unified: {mention.label}")
    print(f"Original: {mention.label_original}")
```

## Span Matching

UnifiedSciERE uses **partial span matching** to align entities across different models:

### Matching Criteria

Two mentions match if:
1. They are in the same document and sentence
2. Their character spans overlap (share at least one character)

### Example

```
Text: "We use BERT for classification"
Model 1:     ^^^^          # "BERT" [8:12]
Model 2:     ^^^^^^^^^^^^  # "BERT for classification" [8:28]
```

These are considered matching mentions despite different boundaries.

## File Format

Data files are in JSONL format (one JSON object per line):

### Sentence Format
```json
{
  "doc_key": "paper_123.txt",
  "sentences": [["We", "use", "BERT", "for", "classification"]],
  "ner": [[[2, 2, "MLModel"]]],
  "split": "train"
}
```

### Prediction Format
```json
{
  "doc_key": "paper_123.txt",
  "sentences": [["We", "use", "BERT", "for", "classification"]],
  "predicted_ner": [[[2, 2, "Method", 0.95]]],
  "split": "dev"
}
```

## Best Practices

### 1. Always Preserve Original Labels

When creating or modifying mentions, preserve `label_original`:

```python
# Good
mapped_mention = Mention(
    ...,
    label=unified_label,
    label_original=original_mention.label
)

# Bad - loses original information
mapped_mention = Mention(
    ...,
    label=unified_label
    # Missing label_original!
)
```

### 2. Handle Missing Predictions

Always check for empty prediction lists:

```python
if corpus.mentions_predicted:
    # Process predictions
else:
    # Handle gold-only corpus
```

### 3. Use Convenience Properties

Relations have properties for common access patterns:

```python
# Use properties instead of direct access
split = relation.split  # Instead of relation.subject.split
doc_id = relation.document_id
signature = relation.signature
```

## Schema Validation

The data model enforces:
- Type hints for all fields
- Default values for optional fields
- Automatic initialization of empty lists

To validate a corpus:

```python
assert all(isinstance(m, Mention) for m in corpus.mentions)
assert all(isinstance(r, Relation) for r in corpus.relation)
assert all(m.label in ["Dataset", "Method", "Task"] for m in corpus.mentions)
```

## Related Documentation

- [README.md](README.md): Project overview
- [unification_status.md](unification_status.md): Pipeline details
- `src/unifiedsciere/types.py`: Source code

---
*Last updated: 2026-02-08*
