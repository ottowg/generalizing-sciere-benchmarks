# Datasets

## Overview

UnifiedSciERE works with three ERE datasets from the ML/AI/CS domain. Each
provides gold entity and relation annotations plus train/dev/test splits. A
model trained on each dataset produces predictions on all three, yielding a 3x3
evaluation matrix.

| Dataset | Domain focus | Entity labels | Relation labels |
|---------|-------------|---------------|-----------------|
| **GSAP** | ML, CV, NLP (HuggingFace + arXiv) | 9 | 18 |
| **SciER** | AI/CS (Semantic Scholar) | 3 | 8 |
| **SciNLP** | NLP (ACL Anthology) | 4 | 12 |

## GSAP

Graph-based Scientific Abstract Processing. Broadest label set of the three.

**Entity labels:** Dataset, DatasetGeneric, DataSource, Method, MLModel,
MLModelGeneric, ModelArchitecture, Task, URL, ReferenceLink

**Relation labels:** appliedTo, architecture, benchmarkFor, citation,
coreference, evaluatedOn, generatedBy, hasInstanceType, isBasedOn,
isComparedTo, isHyponymOf, isPartOf, processed, size, sourcedFrom,
trainedOn, transformedFrom, url, usedFor, versionOf

## SciER (SciERC)

Scientific Entity and Relation Corpus. Compact label set, close to the
unified schema.

**Entity labels:** Dataset, Method, Task

**Relation labels:** Benchmark-For, Compare-With, Evaluated-With, Part-Of,
SubClass-Of, SubTask-Of, Synonym-Of, Trained-With, Used-For

## SciNLP

Scientific NLP dataset. Uses lowercase labels; includes a `metric` type not
present in the other two.

**Entity labels:** dataset, method, task, metric

**Relation labels:** MeasuredBy, UsedFor, compareWith, enhancedBy,
evaluatedBy, evaluatedOn, partOf, similarWith, subclassOf, subtaskOf,
trainedWith, UsedFor_if_object_is_Method

## Unified Schema

### Entity labels

| Unified | GSAP | SciER | SciNLP |
|---------|------|-------|--------|
| **Dataset** | Dataset, DataSource | Dataset | dataset |
| **Method** | Method, MLModel, MLModelGeneric, ModelArchitecture | Method | method |
| **Task** | Task | Task | task |
| *(dropped)* | DatasetGeneric, URL, ReferenceLink | — | metric |

### Relation labels

| Unified | GSAP | SciER | SciNLP |
|---------|------|-------|--------|
| **appliedTo** | appliedTo | Used-For | UsedFor |
| **benchmarkFor** | benchmarkFor | Benchmark-For | evaluatedOn (inverted) |
| **trainedEvaluatedOn** | trainedOn, evaluatedOn | Trained-With, Evaluated-With | trainedWith |
| **coreference** | coreference | Synonym-Of | similarWith |
| **isHyponymOf** | isHyponymOf, isPartOf | SubClass-Of, SubTask-Of | subclassOf, subtaskOf, partOf |
| **isComparedTo** | isComparedTo | Compare-With | compareWith |
| **usedFor** | usedFor, architecture (inv.), isBasedOn (inv.) | Part-Of | enhancedBy (inv.), UsedFor_if_object_is_Method |
| *(dropped)* | citation, generatedBy, hasInstanceType, processed, size, sourcedFrom, transformedFrom, url, versionOf | — | MeasuredBy, evaluatedBy |

Relations marked *(inv.)* are mapped with subject/object swapped.

Undirected relations (order does not matter): coreference, isComparedTo.

Mapping definitions: `src/unifiedsciere/unification/label_mappings.yaml` (entities),
`src/unifiedsciere/unification/relation_mappings.yaml` (relations).

## Data Format

All data is stored as JSONL (one JSON object per document per line).

### File naming

- **Gold:** `{dataset}_{split}.jsonl` (e.g. `scier_dev.jsonl`)
- **Predictions:** `{trained_on}_{dataset}_{split}.jsonl` (e.g. `gsap_scier_dev.jsonl`)

### Document structure

```json
{
  "doc_key": "paper_123",
  "sentences": [["We", "train", "BERT", "on", "ImageNet"]],
  "ner": [[[2, 2, "Method"], [4, 4, "Dataset"]]],
  "relations": [[[2, 2, 4, 4, "trainedOn"]]],
  "predicted_ner_proba": [[[2, 2, "Method", 0.95], [4, 4, "Dataset", 0.88]]],
  "predicted_rel_proba": [[[2, 2, 4, 4, "trainedOn", 0.82]]],
  "split": "dev"
}
```

- Token indices in `ner` and `relations` are inclusive (begin, end).
- Predicted fields include a confidence score as the last element.

## Loading Data

```python
from unifiedsciere.data_loader import load_corpus

# Gold annotations
gold = load_corpus("scier", "dev", data_type="gold")

# Predictions: GSAP model evaluated on SciER dev
pred = load_corpus("scier", "dev", data_type="predictions", trained_on="gsap")
```

- `dataset` = the evaluation data (where the annotations come from)
- `trained_on` = the model source (who made the predictions)

## Unification Rules

Unification is applied **per origin**, not per test set:

- **Gold data** is unified using its own dataset's scheme
- **Predictions** are unified using the `trained_on` dataset's scheme

```python
from unifiedsciere.unification.pipeline import apply_unification_pipeline

# GSAP model predictions -> unify with gsap mappings
pred, _ = apply_unification_pipeline(pred, "gsap", apply_to_gold=False, apply_to_predicted=True)

# SciER gold data -> unify with scier mappings
gold, _ = apply_unification_pipeline(gold, "scier", apply_to_gold=True, apply_to_predicted=False)
```

See [unification.md](unification.md) for pipeline details.
