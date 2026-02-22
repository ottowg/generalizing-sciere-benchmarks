# UnifiedSciERE Documentation

This project compares three Entity and Relation Extraction (ERE) datasets in the
ML/AI/CS domain — **GSAP**, **SciER**, and **SciNLP** — and provides tools to
unify their label schemes, evaluate cross-dataset transfer, and build a combined
corpus.

## Documentation Index

| Document | Contents |
|----------|----------|
| [datasets.md](datasets.md) | Dataset descriptions, label schemes, entity/relation mappings, data format |
| [setup.md](setup.md) | Installation, dependencies, environment configuration |
| [ere_metrics.md](ere_metrics.md) | ERE evaluation metrics (NER exact/partial, RE relaxed/strict) via gsap-hub |
| [unification.md](unification.md) | Unification pipeline steps, configuration, label/relation mappings |
| [data_model.md](data_model.md) | Core data structures (`Corpus`, `Mention`, `Relation`, `PaperMetadata`) |
| [paper_map.md](paper_map.md) | Interactive paper visualization tool (SPECTER2 embeddings, Streamlit) |

## Quick Start

```bash
# Install
uv sync

# Copy .env and adjust paths
cp .env.example .env

# Run a script
uv run python scripts/ere_performance/entity_performance_overview.py
```

See [setup.md](setup.md) for full details.
