# Reports Directory

This directory contains generated analysis reports and tables.

## Structure

```
reports/
├── tables/
│   └── latex/          # LaTeX format tables
│       └── *.tex       # LaTeX table files
├── *.html             # HTML format tables
└── *.md               # Markdown analysis reports
```

## File Naming Convention

Files are named with the following pattern:
```
{dataset}_{split}_{date}.{extension}
```

Example:
- `scinlp_test_20260206.tex` - LaTeX table for SciNLP test set
- `scinlp_test_20260206.html` - HTML table for SciNLP test set  
- `scinlp_test_20260206.md` - Markdown report for SciNLP test set

## Generating Reports

Use the analysis module to generate reports:

```python
from unifiedsciere.analysis import generate_all_reports

# Generate all report formats
output_paths = generate_all_reports(
    target_dataset="scinlp",
    split="test",
)

print(f"LaTeX: {output_paths['latex']}")
print(f"HTML: {output_paths['html']}")
print(f"Markdown: {output_paths['markdown']}")
```

## Report Types

### 1. LaTeX Tables (`tables/latex/*.tex`)
- Formatted tables suitable for inclusion in LaTeX documents
- Contains model performance comparison data
- Can be included with `\input{path/to/table.tex}`

### 2. HTML Tables (`*.html`)
- Interactive HTML tables with styling
- Can be opened directly in a browser
- Suitable for sharing or embedding in web pages

### 3. Markdown Reports (`*.md`)
- Comprehensive analysis reports in Markdown format
- Includes:
  - Summary statistics
  - Detailed mention analysis
  - Detailed relation analysis
  - Coverage metrics
- Easy to read and version control friendly

## Viewing Reports

### LaTeX Tables
Include in your LaTeX document:
```latex
\begin{table}[ht]
\centering
\input{reports/ere_performance/tables/latex/scinlp_test_20260206.tex}
\caption{Model Performance on SciNLP Test Set}
\label{tab:scinlp_performance}
\end{table}
```

### HTML Tables
Open directly in your browser:
```bash
open reports/scinlp_test_20260206.html
```

### Markdown Reports
View in any text editor or Markdown viewer:
```bash
cat reports/scinlp_test_20260206.md
```

Or render with tools like `grip` or in GitHub.

## Automated Generation

See `example_analysis.py` for examples of:
- Generating reports for all datasets
- Customizing output directories
- Creating specific report types
