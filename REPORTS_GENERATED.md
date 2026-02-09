# Generated Reports Summary

**Date:** 2026-02-06  
**Dataset:** SciNLP  
**Split:** test

## Files Generated

### 1. Markdown Report
**Location:** `reports/scinlp_test_20260206.md`  
**Size:** 1,288 bytes

Comprehensive analysis report including:
- Results summary table
- Dataset statistics
- Detailed mentions analysis
- Detailed relations analysis
- Coverage metrics for all models (SCIER, SCINLP, GSAP)

### 2. LaTeX Table
**Location:** `reports/tables/latex/scinlp_test_20260206.tex`  
**Size:** 651 bytes

Professional LaTeX table ready for inclusion in papers:
- Formatted with booktabs package
- Column spanners for grouping
- Proper alignment and spacing
- Can be included with `\input{reports/tables/latex/scinlp_test_20260206.tex}`

### 3. HTML Table
**Location:** `reports/scinlp_test_20260206.html`  
**Size:** 10,582 bytes

Interactive HTML table with:
- Styled header and cells
- Column grouping
- Formatted numbers
- Can be opened in any browser

## Key Findings

All three models (SCIER, SCINLP, GSAP) show **perfect coverage** (100%) on the SciNLP test set:

| Model | Mentions (Pred/Gold) | Relations (Pred/Gold) |
|-------|----------------------|------------------------|
| SCIER | 745 / 745 (100%) | 294 / 294 (100%) |
| SCINLP | 745 / 745 (100%) | 294 / 294 (100%) |
| GSAP | 745 / 745 (100%) | 294 / 294 (100%) |

**Note:** These are coverage metrics (predicted/gold ratio). For detailed precision, recall, and F1 scores, gsap-hub integration is needed.

## How to Use

### In LaTeX Documents
```latex
\begin{figure}[ht]
\centering
\input{reports/tables/latex/scinlp_test_20260206.tex}
\caption{Model Performance Comparison on SciNLP Test Set}
\label{fig:scinlp_performance}
\end{figure}
```

### View HTML
```bash
open reports/scinlp_test_20260206.html
# or
firefox reports/scinlp_test_20260206.html
```

### View Markdown
```bash
cat reports/scinlp_test_20260206.md
# or open in your favorite markdown viewer
```

## Regenerating Reports

To regenerate reports for any dataset:

```python
from unifiedsciere.analysis import generate_all_reports
from pathlib import Path

# For SciNLP
paths = generate_all_reports("scinlp", "test", Path("reports"))

# For other datasets (when gold data is available)
paths = generate_all_reports("scier", "test", Path("reports"))
paths = generate_all_reports("gsap", "test", Path("reports"))
```

## Available Datasets

Currently, only **SciNLP** has gold standard test data available in `data/gold/`.

For complete analysis across all datasets, ensure gold standard files exist:
- `data/gold/scier_test.jsonl`
- `data/gold/scinlp_test.jsonl` ✓ (available)
- `data/gold/gsap_test.jsonl`
