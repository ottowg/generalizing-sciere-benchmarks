# Setup & Dependencies

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
cd UnifiedSciERE

# Install core dependencies (editable mode)
uv sync

# Optional: paper map visualization (torch, transformers, streamlit, ...)
uv sync --extra paper-map

# Optional: vLLM backend for paper classification experiments
uv sync --extra vllm

# Development tools (ruff, pytest, jupyterlab)
uv sync --extra dev
```

## Environment Configuration

Data paths are configured via a `.env` file in the project root (loaded
automatically by `python-dotenv`).

```bash
cp .env.example .env
```

Variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DATASETS_FOLDER` | — | Absolute path to the HGERE datasets folder (gold + predictions) |

The `.env` file is gitignored. Never commit machine-specific paths.

## Core Dependencies

| Package | Purpose |
|---------|---------|
| `gsaphub` | Entity and relation extraction evaluation (partial/exact matching) |
| `python-dotenv` | `.env` file loading |
| `pandas` | Data manipulation and report tables |
| `great-tables` | LaTeX/HTML table generation |
| `pyyaml` (via dependencies) | Configuration files |
| `bibtexparser` | BibTeX metadata parsing |
| `matplotlib` | Publication charts |

## Running Scripts

All scripts are run from the project root via `uv run`:

```bash
# ERE performance reports
uv run python scripts/ere_performance/entity_performance_overview.py
uv run python scripts/ere_performance/reproduce_results_report.py

# Confusion analysis
uv run python scripts/ere_confusion_analysis/cross_model_mention_report.py

# Paper classification (requires Ollama or vLLM)
uv run python scripts/paper_classification/classify_papers.py --config configs/experiments/...

# Paper map (requires paper-map extra)
uv run streamlit run scripts/paper_map/streamlit_paper_map.py
```

## Running Tests

```bash
uv run pytest
```

## Project Structure

```
UnifiedSciERE/
├── configs/                        # YAML configuration
│   ├── unification_config.yaml     # Unification pipeline settings
│   └── experiments/                # Paper classification experiment configs
├── data/
│   ├── gold/                       # Gold-standard annotations (JSONL)
│   ├── predictions/                # Model predictions (JSONL)
│   └── metadata/                   # Paper metadata, BibTeX, outlet catalogue
├── documentation/                  # Project documentation
├── reports/                        # Generated reports (markdown, HTML, LaTeX)
│   ├── ere_performance/
│   ├── ere_confusion_analysis/
│   ├── paper_classification/
│   └── paper_metadata/
├── scripts/                        # Runnable analysis scripts
│   ├── ere_performance/
│   ├── ere_confusion_analysis/
│   ├── paper_classification/
│   ├── paper_map/
│   └── paper_metadata/
├── src/unifiedsciere/              # Core library
│   ├── types.py                    # Data model (Corpus, Mention, Relation, ...)
│   ├── data_loader.py              # Corpus loading from JSONL
│   ├── evaluate.py                 # gsap-hub conversion helpers
│   ├── paths.py                    # Project path resolution
│   ├── reporting.py                # MarkdownReport builder
│   ├── analysis/                   # Performance & confusion analysis
│   ├── unification/                # Label mapping, pipeline, corrections
│   ├── metadata/                   # Paper metadata enrichment
│   ├── paper_classifier/           # LLM-based paper classification
│   └── paper_map/                  # Embedding & layout for visualization
├── tests/
├── .env.example
└── pyproject.toml
```
