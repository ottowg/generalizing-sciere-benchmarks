# Span Normalization Report

**Split:** dev

## 1. Motivation

When unifying entity predictions from three different models (SCIER, SCINLP, GSAP), we observed that models frequently agree on *which* text span is an entity but disagree on *where exactly* the span starts or ends. For example, GSAP predicts "the BERT model" as a Method while SCIER predicts just "BERT" for the same entity. These systematic span boundary differences reduce cross-model agreement and complicate downstream analysis.

The goal of span normalization is to identify and correct these systematic patterns so that equivalent mentions receive identical spans regardless of which model produced them.

## 2. Methodology

### 2.1 Identifying Span Differences

To discover systematic patterns, we performed a cross-model partial match analysis on all three dev sets (SCIER, SCINLP, GSAP datasets), comparing every pair of models.

For each **anchor model**, we:

1. Loaded unified predictions from all three datasets (after applying the unification pipeline steps 1--4: merge stacked mentions, drop unmapped labels, map to unified schema, apply dataset-specific corrections).
2. For each **comparison model** (the other two), used `gsaphub.match.entities.partial()` to find overlapping mention spans.
3. Filtered to **non-exact matches only** --- pairs where begin/end character offsets differ.
4. Recorded each pair as `(anchor_text, comparison_text, entity_type, comparison_model)`.
5. Aggregated across all datasets and comparison models, counting frequency of each unique text pair.

Document IDs were normalized by stripping the model prefix (e.g., `gsap_scier_dev_0` becomes `scier_dev_0`) to enable cross-model alignment on the same underlying documents.

### 2.2 Observed Patterns

The analysis (see `reports/analysis/span_differences_dev.md` for the full before/after listing) revealed three categories of systematic span differences:

**GSAP model** predictions systematically include:

- **Leading determiners/possessives** on Method mentions: "the normalizing flow", "a CNN", "our RCN", "an LSTM"
- **Trailing type nouns** on Method mentions: "BERT model", "convolution layers", "LSTM classifiers", "ELMo embeddings"
- **Possessive suffixes** on all mention types: "GPT-3 's", "Pile 's"

**SCINLP model** predictions systematically include:

- **Trailing type nouns** on Dataset mentions: "PoseTrack dataset", "GLUE benchmark", "newstest2015 test set", "TRC 2 - financial corpus"
- **Leading articles** on Dataset mentions: "the Pile", "The Pile"
- **Trailing "model"** on Method mentions: "SK model", "GPT-3 model", "logistic regression model"
- **Leading articles** on Method mentions: "the Pile" (labeled as Method)

**SCIER model** predictions systematically include:

- **Trailing collection nouns** on Dataset mentions: "Enron Emails corpus", "ArXiv papers", "Reddit submissions"

### 2.3 Correction Rules

Based on these patterns, we implemented token-level normalization rules. Since mention text is space-joined tokens, we split on spaces, check the first/last token against a regex pattern, strip if matched, and adjust character and token offsets accordingly.

The rules are applied as **Step 5** of the unification pipeline, after all other steps.

| Model | Entity Type | Position | Tokens Stripped |
|-------|-------------|----------|-----------------|
| GSAP | Method | prefix | the, The, a, A, an, An, our, Our, their, this, This, these, These, its |
| GSAP | Method | suffix | model(s), layer(s), classifier(s), embedding(s), module(s), system(s) |
| GSAP | All | suffix | 's |
| SCINLP | Dataset | prefix | the, The |
| SCINLP | Dataset | suffix | dataset(s), benchmark(s), corpus, set(s) |
| SCINLP | Dataset | suffix (2 tokens) | test set, data set |
| SCINLP | Method | prefix | the, The |
| SCINLP | Method | suffix | model(s) |
| SCIER | Dataset | suffix | corpus, papers, submissions |

**Safeguard:** A mention is never stripped to fewer than 1 token.

## 3. Results

### 3.1 Correction Counts

We applied the normalization rules to all 9 model-dataset combinations on the dev split (3 models x 3 datasets). The following table shows total predicted mention corrections per model across all datasets:

| Model | Corrections | Top Rules |
|-------|-------------|-----------|
| GSAP | 338 (on SCIER dataset alone) | prefix:the (75), suffix:layers (48), suffix:models (47), prefix:a (38), suffix:model (33), suffix:embeddings (31), prefix:our (30) |
| SCINLP | 25 (on SCIER dataset alone) | suffix:dataset (9), suffix:models (6), suffix:model (6), suffix:benchmark (2) |
| SCIER | Low counts | suffix:corpus, suffix:papers, suffix:submissions |

GSAP has significantly more corrections because its annotation scheme systematically includes determiners and type nouns in entity spans.

### 3.2 Examples

| Original | Corrected | Label | Model |
|----------|-----------|-------|-------|
| the S 3 D architecture | S 3 D architecture | Method | GSAP |
| Hidden state models | Hidden state | Method | GSAP |
| a full 3D CNN | full 3D CNN | Method | GSAP |
| our RCN | RCN | Method | GSAP |
| temporal deconvolution layers | temporal deconvolution | Method | GSAP |
| GPT-3 's | GPT-3 | Method | GSAP |
| MultiThumos datasets | MultiThumos | Dataset | SCINLP |
| ImageNet/COCO dataset | ImageNet/COCO | Dataset | SCINLP |
| TRC 2 - financial corpus | TRC 2 - financial | Dataset | SCINLP |
| LSTM model | LSTM | Method | SCINLP |

### 3.3 Impact on Cross-Model Span Agreement

After applying normalization, we re-ran the partial match span difference analysis. The number of non-exact partial matches decreased across all models:

| Anchor Model | Entity Type | Before | After | Reduction |
|--------------|-------------|--------|-------|-----------|
| SCIER | Dataset | 219 | 142 | -77 (35%) |
| SCIER | Method | 1,293 | 1,278 | -15 (1%) |
| SCIER | Task | 297 | 273 | -24 (8%) |
| SCINLP | Dataset | 226 | 147 | -79 (35%) |
| SCINLP | Method | 1,320 | 1,092 | -228 (17%) |
| SCINLP | Task | 229 | 194 | -35 (15%) |
| GSAP | Dataset | 114 | 72 | -42 (37%) |
| GSAP | Method | 1,978 | 1,562 | -416 (21%) |
| GSAP | Task | 102 | 102 | 0 (0%) |
| **Total** | | **3,798** | **3,270** | **-528 (14%)** |

The largest reductions are in **Dataset** mentions (35--37% across all models) and **GSAP Method** mentions (21%). SCIER Method sees only 1% reduction because SCIER already produces relatively minimal spans --- the rules primarily affect the other models' spans that SCIER is compared against.

Task mentions see little change because the identified patterns (determiners, type nouns) are specific to Method and Dataset annotations.

### 3.4 Remaining Span Differences

After normalization, the top remaining span differences are genuinely ambiguous cases that cannot be resolved with simple prefix/suffix rules:

- **Compositional spans**: "I 3 D and ( 2 + 1 )D" vs "I 3 D" --- one model predicts the conjunction as a single entity, the other splits it.
- **Modifier inclusion**: "pre - trained LayoutXLM" vs "LayoutXLM" --- whether to include adjective modifiers.
- **Nested entities**: "Faster R - CNN" vs "R - CNN" --- whether to include the full model name or just the base architecture.
- **Scope differences**: "attention between datapoints" vs "attention" --- fundamentally different span scopes.

These cases reflect genuine annotation disagreements rather than systematic artifacts.

## 4. Implementation

The span normalization is implemented in `src/unifiedsciere/unification/span_corrections.py` and integrated as **Step 5** of the unification pipeline (`src/unifiedsciere/unification/pipeline.py`). It is controlled by the `span_normalization.enabled` flag in `configs/unification_config.yaml`.

The complete unification pipeline is now:

1. Merge stacked mentions (prefer larger spans)
2. Drop unmapped labels (null mappings)
3. Map to unified schema (Dataset, Method, Task)
4. Apply dataset-specific corrections (e.g., GSAP MLModelGeneric filtering)
5. **Normalize spans (strip systematic prefixes/suffixes)**

---
*Generated by UnifiedSciERE Analysis*
