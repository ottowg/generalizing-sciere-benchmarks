# GSAP MLModelGeneric Unmatched Analysis

**Generated:** 2026-02-08 12:28:54

**Split:** dev

**Datasets:** SCIER, SCINLP, GSAP

## Methodology

This analysis identifies GSAP predictions that are likely to be systematic errors or noise.
The methodology is as follows:

1. **Data Loading**: Load predictions from GSAP, SciER, and SciNLP models across all datasets
   (SCIER, SCINLP, GSAP) for the dev split.

2. **Unification Pipeline**: Apply the complete unification pipeline to all predictions:
   - Merge stacked/overlapping mentions (prefer larger spans)
   - Drop unmapped labels (those mapping to null in unified schema)
   - Map labels to unified schema (Dataset, Method, Task)

3. **GSAP Filtering**: Select only GSAP predictions with:
   - **Unified label**: Method
   - **Original label**: MLModelGeneric

4. **Matching**: Use partial span matching (gsaphub) to find overlapping entities between:
   - GSAP vs SciER predictions
   - GSAP vs SciNLP predictions

5. **Unmatched Identification**: Identify GSAP predictions that have **no match** in either
   SciER or SciNLP. These represent potential systematic errors where GSAP predicts
   an entity that neither of the other two models recognize.

6. **Aggregation**: Group unmatched mentions by text and count occurrences.

## Summary Statistics

- **Total GSAP MLModelGeneric predictions**: 1,703
- **Total unmatched predictions**: 571 (33.5%)
- **Unique unmatched texts**: 320

## Top 50 Unmatched Mentions

The following table shows the most frequent GSAP MLModelGeneric predictions that have no
corresponding entity in either SciER or SciNLP predictions. These are likely candidates
for systematic error correction.

| Rank | Mention Text | GSAP Label | GSAP Original | SciER Label | SciNLP Label | Count |
|------|--------------|------------|---------------|-------------|--------------|-------|
| 1 | the model | Method | MLModelGeneric | NIL | NIL | 80 |
| 2 | models | Method | MLModelGeneric | NIL | NIL | 23 |
| 3 | our model | Method | MLModelGeneric | NIL | NIL | 12 |
| 4 | a model | Method | MLModelGeneric | NIL | NIL | 11 |
| 5 | the models | Method | MLModelGeneric | NIL | NIL | 10 |
| 6 | the network | Method | MLModelGeneric | NIL | NIL | 8 |
| 7 | classifiers | Method | MLModelGeneric | NIL | NIL | 8 |
| 8 | this model | Method | MLModelGeneric | NIL | NIL | 7 |
| 9 | the model 's | Method | MLModelGeneric | NIL | NIL | 7 |
| 10 | our method | Method | MLModelGeneric | NIL | NIL | 6 |
| 11 | language models | Method | MLModelGeneric | NIL | NIL | 6 |
| 12 | our approach | Method | MLModelGeneric | NIL | NIL | 6 |
| 13 | the best model | Method | MLModelGeneric | NIL | NIL | 5 |
| 14 | a language model | Method | MLModelGeneric | NIL | NIL | 4 |
| 15 | the language model | Method | MLModelGeneric | NIL | NIL | 4 |
| 16 | The model | Method | MLModelGeneric | NIL | NIL | 4 |
| 17 | these models | Method | MLModelGeneric | NIL | NIL | 4 |
| 18 | our network | Method | MLModelGeneric | NIL | NIL | 3 |
| 19 | it | Method | MLModelGeneric | NIL | NIL | 3 |
| 20 | baselines | Method | MLModelGeneric | NIL | NIL | 3 |
| 21 | two models | Method | MLModelGeneric | NIL | NIL | 3 |
| 22 | L | Method | MLModelGeneric | NIL | NIL | 3 |
| 23 | the generator | Method | MLModelGeneric | NIL | NIL | 3 |
| 24 | subnetworks | Method | MLModelGeneric | NIL | NIL | 3 |
| 25 | our models | Method | MLModelGeneric | NIL | NIL | 3 |
| 26 | each classifier | Method | MLModelGeneric | NIL | NIL | 3 |
| 27 | the classifier | Method | MLModelGeneric | NIL | NIL | 3 |
| 28 | The classifier | Method | MLModelGeneric | NIL | NIL | 3 |
| 29 | a multimodal pre - trained model | Method | MLModelGeneric | NIL | NIL | 3 |
| 30 | they | Method | MLModelGeneric | NIL | NIL | 3 |
| 31 | the baselines | Method | MLModelGeneric | NIL | NIL | 3 |
| 32 | 3D networks | Method | MLModelGeneric | NIL | NIL | 2 |
| 33 | the base model | Method | MLModelGeneric | NIL | NIL | 2 |
| 34 | ( 2 + 1 )D | Method | MLModelGeneric | NIL | NIL | 2 |
| 35 | different models | Method | MLModelGeneric | NIL | NIL | 2 |
| 36 | our baseline model | Method | MLModelGeneric | NIL | NIL | 2 |
| 37 | one | Method | MLModelGeneric | NIL | NIL | 2 |
| 38 | the other | Method | MLModelGeneric | NIL | NIL | 2 |
| 39 | the baseline methods | Method | MLModelGeneric | NIL | NIL | 2 |
| 40 | our system | Method | MLModelGeneric | NIL | NIL | 2 |
| 41 | Our model | Method | MLModelGeneric | NIL | NIL | 2 |
| 42 | the student model | Method | MLModelGeneric | NIL | NIL | 2 |
| 43 | teacher model | Method | MLModelGeneric | NIL | NIL | 2 |
| 44 | the student models | Method | MLModelGeneric | NIL | NIL | 2 |
| 45 | the pretrained model | Method | MLModelGeneric | NIL | NIL | 2 |
| 46 | such models | Method | MLModelGeneric | NIL | NIL | 2 |
| 47 | a single model | Method | MLModelGeneric | NIL | NIL | 2 |
| 48 | All models | Method | MLModelGeneric | NIL | NIL | 2 |
| 49 | the best performing model | Method | MLModelGeneric | NIL | NIL | 2 |
| 50 | These models | Method | MLModelGeneric | NIL | NIL | 2 |


## Interpretation

The unmatched mentions often fall into these categories:

1. **Generic references**: Terms like "the model", "our model", "models" that are too
   generic or context-dependent to be useful entities.

2. **Procedural terms**: References to modeling processes rather than specific models
   (e.g., "fine-tuning", "training").

3. **False positives**: Text spans that GSAP incorrectly identifies as model mentions.

These unmatched mentions represent opportunities for improving GSAP's predictions through
systematic filtering or correction rules.

## Data Files

- **JSON Resource**: gsap_unmatched_mlmodelgeneric_dev_20260208_122854.json
- **Report**: gsap_unmatched_mlmodelgeneric_dev_20260208_122854.md

---
*Generated by UnifiedSciERE GSAP-Specific Analysis*
