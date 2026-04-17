# Majority-Vote Ensemble for Unified Entity Extraction

## Overview

To obtain a single, high-confidence set of entity predictions that draws on the
complementary strengths of all three domain models — GSAP, SciER, and SciNLP —
we construct a *majority-vote ensemble* operating in the unified label space.
The ensemble is applied after each model's predictions have been independently
mapped to the shared schema (Dataset, Method, Task) via the unification pipeline.
Only entity mentions that at least two models agree upon are retained in the final
prediction set.

## Motivation

Each of the three ERE models is trained on a dataset with its own annotation
guidelines, label inventory, and domain distribution. After unification, all
models emit predictions in the same three-class schema, which makes their outputs
directly comparable. However, each model still carries systematic biases: a model
trained on GSAP may have strong recall for Method entities in NLP papers, while a
SciNLP-trained model may be more sensitive to Dataset mentions. A prediction that
appears in the output of multiple models is therefore substantially more likely to
correspond to a genuinely annotatable entity than one produced by a single model
alone.

## Algorithm

### Step 1 — Collect unified predictions

For a given test dataset and split, the three models' unified predicted mentions
are pooled into a single candidate set. Each mention retains its origin annotator
tag (the model that produced it) and its unified label.

```
candidates ← []
for model in {GSAP, SciER, SciNLP}:
    unified_preds ← unification_pipeline(predict(model, test_data))
    candidates ← candidates ∪ unified_preds
```

### Step 2 — Group by overlapping span and label

Candidate mentions are grouped using *partial span matching*, the same overlap
criterion used throughout the unification confusion analysis (see
`src/unifiedsciere/unification/unified_confusion.py`). Specifically, two mentions
are considered overlapping if their character-offset intervals share at least one
position within the same document. Overlapping mentions are linked into groups via
Union-Find; the label must additionally agree for two mentions to be merged into
the same group. Overlaps across labels are therefore never collapsed.

```
overlaps ← partial_span_match(candidates, candidates)  # within same doc

# Union-Find grouping: merge only if same label
for (m_i, m_j) in overlaps:
    if m_i.label == m_j.label:
        union(m_i, m_j)

groups ← {find(m): members  for m in candidates}
```

### Step 3 — Apply majority filter

Any group whose members all originate from the same model is discarded: it
represents a unilateral prediction that no other model corroborates. Groups that
contain predictions from at least two distinct models are retained as *consensus
groups*.

```
consensus_groups ← []
for group in groups:
    if |{m.model for m in group}| >= 2:
        consensus_groups ← consensus_groups ∪ {group}
    # else: discard — single-model prediction
```

### Step 4 — Select a representative span

From each consensus group a single representative mention is chosen. By default
the mention with the **longest character span** is preferred, on the grounds that
broader spans tend to capture more complete entity expressions (e.g.
*"bidirectional encoder representations from transformers"* over *"encoder
representations"*). Ties are resolved by prediction score. This selection
criterion can be inverted to prefer shorter, more precise spans if desired.

```
ensemble_mentions ← []
remap ← {}               # mention_id → representative_id

for group in consensus_groups:
    rep ← argmax_{m ∈ group} (m.end - m.begin, m.score)
    ensemble_mentions ← ensemble_mentions ∪ {rep}
    for m in group:
        remap[m.id] ← rep.id
```

### Step 5 — Re-wire relations

Predicted relations from all three models are collected. For each relation, the
subject and object mention identifiers are remapped to their group representatives.
A relation is kept if and only if both its subject and its object survived the
majority filter and have a valid representative. Duplicate relations — identical
(subject, label, object) triples after remapping — are deduplicated. Relations
connected to discarded (single-model) entities are dropped.

```
all_relations ← ⋃_{model} predicted_relations(model)
ensemble_relations ← []
seen ← {}

for rel in all_relations:
    subj' ← remap.get(rel.subject.id)
    obj'  ← remap.get(rel.object.id)
    if subj' is None or obj' is None:
        continue                          # endpoint discarded
    key ← (subj', rel.label, obj')
    if key not in seen:
        seen ← seen ∪ {key}
        ensemble_relations ← ensemble_relations ∪ {rel[subj', obj']}
```

## Properties of the Resulting Prediction Set

**Precision bias.** By construction the ensemble suppresses any mention that only
one model predicts, which reduces the total number of predictions and increases
precision at the potential cost of recall. This trade-off is empirically
characterised in `reports/ere_performance/ensemble_performance_overview.md`.

**Label consistency.** Because the majority filter operates within label groups,
the ensemble never merges a Method prediction from one model with a Task prediction
from another: overlapping spans with conflicting labels are treated as separate
groups and each must independently meet the majority threshold.

**Span representation.** The representative mention is drawn from an actual model
prediction rather than being synthesised, so it inherits the original model's
token offsets, confidence score, and annotator provenance. This preserves
compatibility with downstream evaluation using gsaphub.

**Relation coherence.** The relation re-wiring step ensures that the relational
structure of the prediction set remains coherent: every retained relation connects
two entities that are themselves present in the consensus mention set. No dangling
or self-referential relations can arise.

## Implementation

The ensemble logic is implemented in
`src/unifiedsciere/ensemble/majority_vote.py` and exposed as
`unifiedsciere.ensemble.majority_vote_ensemble(corpora)`.  The function accepts a
list of `Corpus` objects — one per model, each with its predictions already
unified — and returns a new `Corpus` whose `mentions_predicted` and
`relations_predicted` fields contain the consensus predictions. The gold
annotations are inherited from the first corpus in the list unchanged.

The performance evaluation script
`scripts/ere_performance/ensemble_performance_overview.py` applies the ensemble
independently to each test dataset and to the combined UnifiedSciERE set, and
reports partial-match F1 broken down by entity label for both the dev and test
splits.
