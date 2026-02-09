# Mention Merging Report

**Generated:** 2026-02-06 17:10:52

**Split:** dev

**Span Preference:** Prefer larger spans when merging

## Overview

This report shows statistics on merging stacked/overlapping mentions in gold annotations
and model predictions. When mentions overlap, we keep the larger span and merge
the others into it. Relations are automatically remapped to merged mention IDs.


## SCIER Dataset

### Gold Annotations

**Mentions:**
- Original: 2234
- After merging: 2234
- Merged: 0

**Relations:**
- Original: 1132
- After merging: 1130
- Self-loops removed: 0
- Duplicates removed: 2

**No overlapping mentions found in gold annotations.**

### SCIER Predictions

**Mentions:**
- Original: 2248
- After merging: 2237
- Merged: 11

**Relations:**
- Original: 997
- After merging: 993
- Self-loops removed: 1
- Duplicates removed: 3

**Self-loop Relation Labels:**

| Relation Label | Count |
|----------------|-------|
| Synonym-Of | 1 |

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| Method | Method | 7 |
| Task | Task | 2 |
| Task | Method | 2 |

### SCINLP Predictions

**Mentions:**
- Original: 2021
- After merging: 1985
- Merged: 36

**Relations:**
- Original: 463
- After merging: 460
- Self-loops removed: 0
- Duplicates removed: 3

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| method | method | 31 |
| dataset | dataset | 2 |
| metric | metric | 2 |
| task | task | 1 |

### GSAP Predictions

**Mentions:**
- Original: 2948
- After merging: 2861
- Merged: 87

**Relations:**
- Original: 1419
- After merging: 1362
- Self-loops removed: 54
- Duplicates removed: 3

**Self-loop Relation Labels:**

| Relation Label | Count |
|----------------|-------|
| architecture | 54 |

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| ModelArchitecture | MLModelGeneric | 64 |
| Method | Method | 9 |
| ModelArchitecture | ModelArchitecture | 4 |
| Task | DatasetGeneric | 3 |
| Dataset | DatasetGeneric | 2 |
| MLModel | MLModel | 2 |
| MLModelGeneric | MLModelGeneric | 1 |
| ModelArchitecture | Method | 1 |
| MLModel | MLModelGeneric | 1 |


## SCINLP Dataset

### Gold Annotations

**Mentions:**
- Original: 671
- After merging: 666
- Merged: 5

**Relations:**
- Original: 179
- After merging: 179
- Self-loops removed: 0
- Duplicates removed: 0

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| method | method | 3 |
| task | task | 1 |
| metric | metric | 1 |

### SCIER Predictions

**Mentions:**
- Original: 910
- After merging: 905
- Merged: 5

**Relations:**
- Original: 162
- After merging: 162
- Self-loops removed: 0
- Duplicates removed: 0

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| Task | Task | 2 |
| Method | Method | 2 |
| Dataset | Dataset | 1 |

### SCINLP Predictions

**Mentions:**
- Original: 634
- After merging: 633
- Merged: 1

**Relations:**
- Original: 101
- After merging: 101
- Self-loops removed: 0
- Duplicates removed: 0

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| task | task | 1 |

### GSAP Predictions

**Mentions:**
- Original: 1218
- After merging: 1211
- Merged: 7

**Relations:**
- Original: 333
- After merging: 331
- Self-loops removed: 1
- Duplicates removed: 1

**Self-loop Relation Labels:**

| Relation Label | Count |
|----------------|-------|
| sourcedFrom | 1 |

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| Dataset | DatasetGeneric | 3 |
| MLModel | MLModelGeneric | 1 |
| ModelArchitecture | MLModelGeneric | 1 |
| DataSource | DatasetGeneric | 1 |
| Method | Method | 1 |


## GSAP Dataset

### Gold Annotations

**Mentions:**
- Original: 6417
- After merging: 6180
- Merged: 237

**Relations:**
- Original: 3818
- After merging: 3305
- Self-loops removed: 505
- Duplicates removed: 8

**Self-loop Relation Labels:**

| Relation Label | Count |
|----------------|-------|
| architecture | 393 |
| benchmarkFor | 23 |
| sourcedFrom | 21 |
| usedFor | 18 |
| isBasedOn | 11 |
| transformedFrom | 10 |
| trainedOn | 7 |
| citation | 7 |
| appliedTo | 5 |
| isPartOf | 3 |
| generatedBy | 3 |
| coreference | 2 |
| hasInstanceType | 1 |
| evaluatedOn | 1 |

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| ModelArchitecture | MLModelGeneric | 129 |
| Task | DatasetGeneric | 19 |
| Dataset | DatasetGeneric | 18 |
| DataSource | DatasetGeneric | 16 |
| MLModel | MLModelGeneric | 11 |
| Method | MLModelGeneric | 7 |
| Dataset | MLModelGeneric | 7 |
| Task | MLModelGeneric | 5 |
| ModelArchitecture | Method | 5 |
| ReferenceLink | Method | 4 |
| DataSource | MLModelGeneric | 3 |
| MLModel | DatasetGeneric | 2 |
| DataSource | Dataset | 2 |
| Method | DatasetGeneric | 2 |
| ReferenceLink | MLModelGeneric | 2 |
| ModelArchitecture | DatasetGeneric | 1 |
| MLModel | MLModel | 1 |
| ModelArchitecture | MLModel | 1 |
| DatasetGeneric | MLModelGeneric | 1 |
| ReferenceLink | DatasetGeneric | 1 |

### SCIER Predictions

**Mentions:**
- Original: 3638
- After merging: 3559
- Merged: 79

**Relations:**
- Original: 727
- After merging: 726
- Self-loops removed: 0
- Duplicates removed: 1

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| Method | Method | 33 |
| Task | Task | 22 |
| Dataset | Dataset | 14 |
| Task | Method | 4 |
| Task | Dataset | 3 |
| Method | Task | 2 |
| Dataset | Method | 1 |

### SCINLP Predictions

**Mentions:**
- Original: 3407
- After merging: 3321
- Merged: 86

**Relations:**
- Original: 337
- After merging: 337
- Self-loops removed: 0
- Duplicates removed: 0

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| method | method | 73 |
| dataset | dataset | 6 |
| task | task | 5 |
| task | dataset | 1 |
| metric | metric | 1 |

### GSAP Predictions

**Mentions:**
- Original: 6373
- After merging: 6068
- Merged: 305

**Relations:**
- Original: 2765
- After merging: 2553
- Self-loops removed: 207
- Duplicates removed: 5

**Self-loop Relation Labels:**

| Relation Label | Count |
|----------------|-------|
| architecture | 121 |
| benchmarkFor | 19 |
| transformedFrom | 18 |
| sourcedFrom | 17 |
| usedFor | 8 |
| trainedOn | 6 |
| citation | 6 |
| isBasedOn | 6 |
| coreference | 2 |
| isPartOf | 2 |
| appliedTo | 1 |
| generatedBy | 1 |

**Label Merge Patterns:**

| Merged Label | Kept Label | Count |
|--------------|------------|-------|
| ModelArchitecture | MLModelGeneric | 132 |
| Method | Method | 35 |
| Dataset | DatasetGeneric | 27 |
| Task | DatasetGeneric | 19 |
| DataSource | DatasetGeneric | 15 |
| DatasetGeneric | DatasetGeneric | 11 |
| Method | MLModelGeneric | 10 |
| ReferenceLink | MLModelGeneric | 7 |
| Dataset | MLModelGeneric | 6 |
| MLModel | MLModelGeneric | 5 |
| MLModelGeneric | MLModelGeneric | 5 |
| DataSource | MLModelGeneric | 4 |
| ReferenceLink | DatasetGeneric | 4 |
| ModelArchitecture | DatasetGeneric | 4 |
| DataSource | Method | 3 |
| ReferenceLink | Method | 3 |
| ModelArchitecture | ModelArchitecture | 3 |
| ModelArchitecture | Method | 3 |
| Dataset | Dataset | 2 |
| Task | Method | 2 |
| Task | MLModelGeneric | 1 |
| ReferenceLink | ReferenceLink | 1 |
| DataSource | Dataset | 1 |
| URL | URL | 1 |
| Method | DatasetGeneric | 1 |


## Notes

- **Overlapping mentions**: Two mentions overlap if they share at least one character position in the same sentence
- **Span preference**: When merging, we keep the preferred span size and discard others
- **Relation remapping**: Relations are automatically updated to reference merged mention objects
- **Self-loop removal**: Relations where subject and object were merged are removed
- **Duplicate removal**: Duplicate relations (same subject-object-label) are removed

---
*Generated by UnifiedSciERE Mention Merging*
