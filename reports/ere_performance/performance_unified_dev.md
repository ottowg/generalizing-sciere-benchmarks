# Performance After Unification

**Generated:** 2026-02-08 14:20:06

**Split:** dev

## Overview

This report shows model performance metrics after applying the complete unification pipeline:

1. Merge stacked mentions (prefer larger spans)
2. Drop unmapped labels (null mappings)
3. Map to unified schema (Dataset, Method, Task)
4. Apply dataset-specific corrections (e.g., GSAP MLModelGeneric filtering)
5. Normalize spans (strip systematic prefixes/suffixes)

Performance is measured using strict and partial matching for entity recognition.


## SCIER Dataset

### SCIER Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.911 | 0.911 | 0.911 | 269 |
| Method | 0.905 | 0.894 | 0.899 | 1549 |
| Task | 0.849 | 0.892 | 0.870 | 416 |
| macro | 0.888 | 0.899 | 0.893 | 2234 |
| weighted | 0.895 | 0.896 | 0.895 | 2234 |
| **micro** | **0.895** | **0.896** | **0.895** | **2234** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.929 | 0.929 | 0.929 | 269 |
| Method | 0.958 | 0.946 | 0.952 | 1549 |
| Task | 0.879 | 0.923 | 0.900 | 416 |
| macro | 0.922 | 0.933 | 0.927 | 2234 |
| weighted | 0.939 | 0.940 | 0.940 | 2234 |
| **micro** | **0.939** | **0.940** | **0.939** | **2234** |

**Entity Counts:**

- Gold mentions: 2234
- Predicted mentions: 2237

---

### SCINLP Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.877 | 0.743 | 0.805 | 269 |
| Method | 0.859 | 0.745 | 0.798 | 1549 |
| Task | 0.765 | 0.743 | 0.754 | 416 |
| macro | 0.834 | 0.744 | 0.785 | 2234 |
| weighted | 0.843 | 0.744 | 0.790 | 2234 |
| **micro** | **0.842** | **0.744** | **0.790** | **2234** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.917 | 0.777 | 0.841 | 269 |
| Method | 0.956 | 0.830 | 0.888 | 1549 |
| Task | 0.777 | 0.755 | 0.766 | 416 |
| macro | 0.883 | 0.787 | 0.832 | 2234 |
| weighted | 0.918 | 0.809 | 0.860 | 2234 |
| **micro** | **0.915** | **0.809** | **0.859** | **2234** |

**Entity Counts:**

- Gold mentions: 2234
- Predicted mentions: 1976

---

### GSAP Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.873 | 0.896 | 0.884 | 269 |
| Method | 0.741 | 0.763 | 0.752 | 1549 |
| Task | 0.869 | 0.733 | 0.795 | 416 |
| macro | 0.828 | 0.797 | 0.810 | 2234 |
| weighted | 0.780 | 0.774 | 0.776 | 2234 |
| **micro** | **0.777** | **0.774** | **0.775** | **2234** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.899 | 0.922 | 0.910 | 269 |
| Method | 0.900 | 0.927 | 0.913 | 1549 |
| Task | 0.915 | 0.772 | 0.837 | 416 |
| macro | 0.904 | 0.874 | 0.887 | 2234 |
| weighted | 0.902 | 0.897 | 0.899 | 2234 |
| **micro** | **0.902** | **0.897** | **0.900** | **2234** |

**Entity Counts:**

- Gold mentions: 2234
- Predicted mentions: 2223

---


## SCINLP Dataset

### SCIER Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.391 | 0.868 | 0.539 | 68 |
| Method | 0.394 | 0.692 | 0.502 | 315 |
| Task | 0.380 | 0.628 | 0.474 | 121 |
| macro | 0.388 | 0.729 | 0.505 | 504 |
| weighted | 0.390 | 0.700 | 0.500 | 504 |
| **micro** | **0.390** | **0.700** | **0.501** | **504** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.444 | 0.985 | 0.612 | 68 |
| Method | 0.455 | 0.800 | 0.580 | 315 |
| Task | 0.420 | 0.694 | 0.523 | 121 |
| macro | 0.440 | 0.827 | 0.572 | 504 |
| weighted | 0.445 | 0.800 | 0.571 | 504 |
| **micro** | **0.445** | **0.800** | **0.572** | **504** |

**Entity Counts:**

- Gold mentions: 504
- Predicted mentions: 905

---

### SCINLP Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.788 | 0.765 | 0.776 | 68 |
| Method | 0.884 | 0.848 | 0.865 | 315 |
| Task | 0.790 | 0.810 | 0.800 | 121 |
| macro | 0.821 | 0.807 | 0.814 | 504 |
| weighted | 0.849 | 0.827 | 0.838 | 504 |
| **micro** | **0.848** | **0.827** | **0.837** | **504** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.864 | 0.838 | 0.851 | 68 |
| Method | 0.921 | 0.883 | 0.901 | 315 |
| Task | 0.823 | 0.843 | 0.833 | 121 |
| macro | 0.869 | 0.855 | 0.862 | 504 |
| weighted | 0.889 | 0.867 | 0.878 | 504 |
| **micro** | **0.888** | **0.867** | **0.878** | **504** |

**Entity Counts:**

- Gold mentions: 504
- Predicted mentions: 492

---

### GSAP Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.505 | 0.691 | 0.584 | 68 |
| Method | 0.417 | 0.737 | 0.532 | 315 |
| Task | 0.538 | 0.521 | 0.529 | 121 |
| macro | 0.487 | 0.649 | 0.548 | 504 |
| weighted | 0.458 | 0.679 | 0.538 | 504 |
| **micro** | **0.446** | **0.679** | **0.538** | **504** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.559 | 0.765 | 0.646 | 68 |
| Method | 0.519 | 0.917 | 0.663 | 315 |
| Task | 0.615 | 0.595 | 0.605 | 121 |
| macro | 0.564 | 0.759 | 0.638 | 504 |
| weighted | 0.547 | 0.819 | 0.647 | 504 |
| **micro** | **0.538** | **0.819** | **0.650** | **504** |

**Entity Counts:**

- Gold mentions: 504
- Predicted mentions: 767

---


## GSAP Dataset

### SCIER Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.451 | 0.741 | 0.561 | 505 |
| Method | 0.652 | 0.475 | 0.549 | 2764 |
| Task | 0.290 | 0.725 | 0.414 | 287 |
| macro | 0.464 | 0.647 | 0.508 | 3556 |
| weighted | 0.594 | 0.533 | 0.540 | 3556 |
| **micro** | **0.532** | **0.533** | **0.532** | **3556** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.527 | 0.865 | 0.655 | 505 |
| Method | 0.857 | 0.624 | 0.722 | 2764 |
| Task | 0.326 | 0.815 | 0.466 | 287 |
| macro | 0.570 | 0.768 | 0.614 | 3556 |
| weighted | 0.767 | 0.674 | 0.692 | 3556 |
| **micro** | **0.673** | **0.674** | **0.673** | **3556** |

**Entity Counts:**

- Gold mentions: 3556
- Predicted mentions: 3559

---

### SCINLP Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.481 | 0.667 | 0.559 | 505 |
| Method | 0.686 | 0.504 | 0.581 | 2764 |
| Task | 0.371 | 0.641 | 0.470 | 287 |
| macro | 0.513 | 0.604 | 0.537 | 3556 |
| weighted | 0.632 | 0.538 | 0.569 | 3556 |
| **micro** | **0.593** | **0.538** | **0.564** | **3556** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.531 | 0.737 | 0.617 | 505 |
| Method | 0.794 | 0.582 | 0.672 | 2764 |
| Task | 0.383 | 0.662 | 0.485 | 287 |
| macro | 0.569 | 0.660 | 0.591 | 3556 |
| weighted | 0.723 | 0.611 | 0.649 | 3556 |
| **micro** | **0.673** | **0.611** | **0.641** | **3556** |

**Entity Counts:**

- Gold mentions: 3556
- Predicted mentions: 3225

---

### GSAP Model

**Strict Matching (Exact Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.775 | 0.715 | 0.744 | 505 |
| Method | 0.848 | 0.844 | 0.846 | 2764 |
| Task | 0.786 | 0.613 | 0.689 | 287 |
| macro | 0.803 | 0.724 | 0.760 | 3556 |
| weighted | 0.833 | 0.807 | 0.819 | 3556 |
| **micro** | **0.834** | **0.807** | **0.820** | **3556** |

**Partial Matching (Overlapping Spans):**

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------| 
| Dataset | 0.854 | 0.788 | 0.820 | 505 |
| Method | 0.917 | 0.913 | 0.915 | 2764 |
| Task | 0.866 | 0.676 | 0.759 | 287 |
| macro | 0.879 | 0.792 | 0.831 | 3556 |
| weighted | 0.904 | 0.876 | 0.889 | 3556 |
| **micro** | **0.906** | **0.876** | **0.891** | **3556** |

**Entity Counts:**

- Gold mentions: 3556
- Predicted mentions: 3440

---


## Impact of Span Normalization (Step 5)

Micro-averaged performance comparison: Steps 1--4 only vs. Steps 1--5 (with span normalization).

### Strict Matching (Exact Spans)

| Dataset | Model | P (before) | P (after) | P (diff) | R (before) | R (after) | R (diff) | F1 (before) | F1 (after) | F1 (diff) |
|---------|-------|------------|-----------|----------|------------|-----------|----------|-------------|------------|-----------|
| SCIER | SCIER | 0.895 | 0.895 | +0.000 | 0.896 | 0.896 | +0.000 | 0.895 | 0.895 | +0.000 |
| SCIER | SCINLP | 0.837 | 0.842 | +0.005 | 0.740 | 0.744 | +0.004 | 0.785 | 0.790 | +0.005 |
| SCIER | GSAP | 0.768 | 0.777 | +0.009 | 0.764 | 0.774 | +0.009 | 0.766 | 0.775 | +0.009 |
| SCINLP | SCIER | 0.392 | 0.390 | -0.002 | 0.704 | 0.700 | -0.004 | 0.504 | 0.501 | -0.003 |
| SCINLP | SCINLP | 0.846 | 0.848 | +0.002 | 0.825 | 0.827 | +0.002 | 0.835 | 0.837 | +0.002 |
| SCINLP | GSAP | 0.395 | 0.446 | +0.051 | 0.601 | 0.679 | +0.077 | 0.477 | 0.538 | +0.061 |
| GSAP | SCIER | 0.534 | 0.532 | -0.002 | 0.535 | 0.533 | -0.002 | 0.535 | 0.532 | -0.002 |
| GSAP | SCINLP | 0.557 | 0.593 | +0.036 | 0.505 | 0.538 | +0.033 | 0.530 | 0.564 | +0.035 |
| GSAP | GSAP | 0.813 | 0.834 | +0.022 | 0.786 | 0.807 | +0.021 | 0.799 | 0.820 | +0.021 |

### Partial Matching (Overlapping Spans)

| Dataset | Model | P (before) | P (after) | P (diff) | R (before) | R (after) | R (diff) | F1 (before) | F1 (after) | F1 (diff) |
|---------|-------|------------|-----------|----------|------------|-----------|----------|-------------|------------|-----------|
| SCIER | SCIER | 0.939 | 0.939 | +0.000 | 0.940 | 0.940 | +0.000 | 0.939 | 0.939 | +0.000 |
| SCIER | SCINLP | 0.915 | 0.915 | +0.000 | 0.809 | 0.809 | +0.000 | 0.859 | 0.859 | +0.000 |
| SCIER | GSAP | 0.902 | 0.902 | +0.000 | 0.897 | 0.897 | +0.000 | 0.900 | 0.900 | +0.000 |
| SCINLP | SCIER | 0.445 | 0.445 | +0.000 | 0.800 | 0.800 | +0.000 | 0.572 | 0.572 | +0.000 |
| SCINLP | SCINLP | 0.888 | 0.888 | +0.000 | 0.867 | 0.867 | +0.000 | 0.878 | 0.878 | +0.000 |
| SCINLP | GSAP | 0.538 | 0.538 | +0.000 | 0.819 | 0.819 | +0.000 | 0.650 | 0.650 | +0.000 |
| GSAP | SCIER | 0.674 | 0.673 | -0.001 | 0.675 | 0.674 | -0.001 | 0.674 | 0.673 | -0.001 |
| GSAP | SCINLP | 0.676 | 0.673 | -0.002 | 0.613 | 0.611 | -0.002 | 0.643 | 0.641 | -0.002 |
| GSAP | GSAP | 0.907 | 0.906 | -0.001 | 0.877 | 0.876 | -0.001 | 0.892 | 0.891 | -0.001 |

## Notes

- **Unified Labels**: Performance measured on Dataset, Method, Task labels only
- **Strict Matching**: Exact span and label match required
- **Partial Matching**: Overlapping span with correct label counts as match
- All metrics calculated after complete unification pipeline

---
*Generated by UnifiedSciERE Performance Analysis*
