# ERE Evaluation Metrics

All evaluation is performed through the **gsap-hub** library
(`gsaphub.evaluate`), which provides standardised entity and relation
extraction metrics with partial and exact span matching.

## Entity Metrics (NER)

```python
import gsaphub as gh
from unifiedsciere.evaluate import mention_to_gsaphub

ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]
ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]

# Exact match
results = gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=False)

# Partial match
results = gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=True)
```

### Exact match (`partial=False`)

A predicted entity is correct only if **both** the span boundaries and the
label match the gold entity exactly.

### Partial match (`partial=True`)

A predicted entity is correct if the spans **overlap** (share at least one
token) and the labels match. This is more forgiving of minor boundary
differences between annotation schemes (e.g. "BERT" vs "the BERT model").

### Output

Both modes return per-label and micro-averaged precision, recall, and F1 as
a pandas DataFrame:

| label | precision | recall | f1_score |
|-------|-----------|--------|----------|
| Dataset | 0.82 | 0.79 | 0.80 |
| Method | 0.75 | 0.71 | 0.73 |
| Task | 0.68 | 0.65 | 0.66 |
| micro | 0.76 | 0.73 | 0.74 |

## Relation Metrics (RE)

Relation evaluation requires both the relation triples and their entity
spans, because matching depends on how entity boundaries are resolved.

```python
from gsaphub.evaluate.relations import RelationExtractionMetric, ScoreType
from unifiedsciere.evaluate import relation_to_gsaphub, filter_relations_with_valid_entities

rels_gold = [relation_to_gsaphub(r, i) for i, r in enumerate(gold.relation)]
ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]

rels_pred = [relation_to_gsaphub(r, i) for i, r in enumerate(pred.relations_predicted)]
ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]

# Filter relations whose entities were removed during unification
rels_gold = filter_relations_with_valid_entities(rels_gold, {e["id"] for e in ents_gold})
rels_pred = filter_relations_with_valid_entities(rels_pred, {e["id"] for e in ents_pred})

results = gh.evaluate.relations.precision_recall_f1(
    rels_gold, ents_gold,
    rels_pred, ents_pred,
    re_metrics=[
        RelationExtractionMetric.RELAXED_MATCH,
        RelationExtractionMetric.STRICT_MATCH,
    ],
    score_types=[ScoreType.PRECISION, ScoreType.RECALL, ScoreType.F1],
)
```

### Metric types

gsap-hub provides four relation extraction metrics, from most lenient to
strictest:

| Metric | Entity matching | Label matching | Short name |
|--------|----------------|----------------|------------|
| `RELAXED_PARTIAL_MATCH` | Partial span overlap | Relation label must match | RE~partial |
| `RELAXED_MATCH` | Partial span overlap | Relation + entity labels must match | **RE** |
| `STRICT_PARTIAL_MATCH` | Exact span boundaries | Relation label must match | RE+partial |
| `STRICT_MATCH` | Exact span boundaries | Relation + entity labels must match | **RE+** |

The two most commonly used in this project:

- **RE** (`RELAXED_MATCH`) — Entity spans need only overlap; both the
  relation label and entity type labels must match. This is the standard
  metric for cross-dataset comparison since boundary conventions differ.

- **RE+** (`STRICT_MATCH`) — Entity spans must match exactly in addition to
  all labels matching. Used for in-distribution evaluation where boundary
  conventions are consistent.

### Output

Results are returned as a multi-level DataFrame with columns grouped by
score type and metric:

| (relation, label) | (precision, RE) | (recall, RE) | (f1_score, RE) | (precision, RE+) | ... |
|--------------------|-----------------|--------------|----------------|-------------------|-----|
| appliedTo | 0.72 | 0.68 | 0.70 | 0.65 | ... |
| micro | 0.70 | 0.66 | 0.68 | 0.62 | ... |

## Conversion Helpers

`src/unifiedsciere/evaluate.py` provides functions to convert between the
project's data model and the dict format expected by gsap-hub:

| Function | Purpose |
|----------|---------|
| `mention_to_gsaphub(m)` | Convert a `Mention` to gsap-hub entity dict |
| `relation_to_gsaphub(r, idx)` | Convert a `Relation` to gsap-hub relation dict |
| `filter_relations_with_valid_entities(rels, ent_ids)` | Drop relations referencing removed entities |

## Typical Evaluation Workflow

```python
from unifiedsciere.data_loader import load_corpus
from unifiedsciere.unification.pipeline import apply_unification_pipeline
from unifiedsciere.evaluate import mention_to_gsaphub, relation_to_gsaphub, filter_relations_with_valid_entities
import gsaphub as gh

# 1. Load data
gold = load_corpus("scier", "test", data_type="gold")
pred = load_corpus("scier", "test", data_type="predictions", trained_on="gsap")

# 2. Unify (per origin)
gold, _ = apply_unification_pipeline(gold, "scier", apply_to_gold=True, apply_to_predicted=False)
pred, _ = apply_unification_pipeline(pred, "gsap", apply_to_gold=False, apply_to_predicted=True)

# 3. Convert to gsap-hub format
ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]
ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]
rels_gold = [relation_to_gsaphub(r, i) for i, r in enumerate(gold.relation)]
rels_pred = [relation_to_gsaphub(r, i) for i, r in enumerate(pred.relations_predicted)]
rels_gold = filter_relations_with_valid_entities(rels_gold, {e["id"] for e in ents_gold})
rels_pred = filter_relations_with_valid_entities(rels_pred, {e["id"] for e in ents_pred})

# 4. Evaluate
ner_results = gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=True)
re_results = gh.evaluate.relations.precision_recall_f1(rels_gold, ents_gold, rels_pred, ents_pred)
```
