# UnifiedSciERE

This project compares three Entity and Relation Extraction (ERE) datasets in the
ML/AI/CS domain — **GSAP**, **SciER**, and **SciNLP** — covering topics such as
Machine Learning, NLP, Multimodal Approaches, Modeling, Computer Vision, and
Pattern Recognition.

**Goals:**

1. **Cross-dataset comparison** — Evaluate how models trained on one dataset
   perform on the others, revealing annotation differences and dataset biases.
2. **Unification** — Map dataset-specific label schemes to a shared schema so
   extraction results become comparable. This includes tools to identify label
   mappings, detect dataset-dependent annotation patterns, and apply deletions
   or transformations per dataset.
3. **Unified dataset creation** — Combine all three sources into a single
   unified corpus using the shared schema.
4. **Analysis & reporting** — Generate performance reports (NER/RE metrics via
   gsap-hub) and confusion analyses to understand where models and annotation
   guidelines agree or diverge.

# Project Conventions

- Use `uv` as the package manager and script runner (e.g. `uv run`, `uv add`, `uv sync`)
- Use `git mv` / `git rm` for file operations (not plain `mv` / `rm`)
- For NER and RE (ERE) performance metrics, use the `gsap-hub` library
- Keep `scripts/` and `reports/` subfolder structures aligned:
  - `paper_classification/` — classification experiments and speed comparisons
  - `paper_map/` — embedding, layout, and visualization
  - `paper_metadata/` — metadata building, enrichment, publications
  - `ere_performance/` — entity/relation performance, false predictions, reproduction
  - `ere_confusion_analysis/` — cross-model confusion, span analysis, unification reports

## Environment

- Node.js managed via **nvm** (current: node v24.14.0, npm v11.9.0)
- Data paths are configured via `.env` file (loaded by `python-dotenv`)
- `.env.example` documents available variables; copy to `.env` and adjust
- Current variables:
  - `DATA_GOLD_FOLDER` — path to gold standard data (default: `data/gold`)
  - `DATA_PREDICTIONS_FOLDER` — path to model predictions (default: `data/predictions`)
- The `.env` file is gitignored; never commit secrets or machine-specific paths

## Data Model

Core types are defined in `src/unifiedsciere/types.py`:
- `Sentence` — a sentence with doc_id, index, split
- `Mention` — an entity span (id, text, label, character/token offsets, score, annotator, dataset, label_original)
- `Relation` — a typed link between two Mentions (subject, label, object)
- `Corpus` — container with `sentences`, `mentions`, `relation` (gold) and `mentions_predicted`, `relations_predicted`
- `PaperMetadata` — bibliographic metadata (title, authors, year, venue, identifiers, outlet)
  - `dblp_id` — preferred published-venue DBLP key (e.g. `conf/cvpr/LiWCTT20`, `journals/jmlr/SmithJ20`); empty for preprint-only papers
  - `dblp_preprint_id` — DBLP corr key for the arXiv version (e.g. `journals/corr/abs-1910-09700`); derivable from `arxiv_id` as `journals/corr/abs-{arxiv_id with `.` → `-`}`
- `Outlet` — publication venue (conference, journal, workshop, preprint)

## Data Access

Three datasets: **GSAP**, **SciER**, **SciNLP**. Each has train/dev/test splits.
Three models (one per dataset), each with predictions on all three datasets.

### Loading gold and predictions

```python
from unifiedsciere.data_loader import load_corpus

# Gold annotations for SciER dev
gold = load_corpus("scier", "dev", data_type="gold")

# Predictions: model trained on SciER, inference on GSAP dev
pred = load_corpus("gsap", "dev", data_type="predictions", trained_on="scier")
```

- `dataset` = the test data (what is being evaluated on)
- `trained_on` = the model / training source (who made the predictions)
- Gold data lives in `$DATA_GOLD_FOLDER/{dataset}_{split}.jsonl`
- Predictions live in `$DATA_PREDICTIONS_FOLDER/{trained_on}_{dataset}_{split}.jsonl`

### Unification

Unification maps dataset-specific label schemes to a shared schema. It is applied
**per origin**, not per test data:
- **Predictions** are unified using the **trained_on** dataset's scheme (the model's label space)
- **Gold data** is unified using the **dataset's own** scheme (the annotation label space)

Example: evaluating a GSAP model on SciER dev:

```python
from unifiedsciere.unification.pipeline import apply_unification_pipeline

gold = load_corpus("scier", "dev", data_type="gold")
pred = load_corpus("scier", "dev", data_type="predictions", trained_on="gsap")

# Gold: unify using scier scheme (the annotation source)
gold, _ = apply_unification_pipeline(gold, "scier", apply_to_gold=True, apply_to_predicted=False)

# Predictions: unify using gsap scheme (the model source)
pred, _ = apply_unification_pipeline(pred, "gsap", apply_to_gold=False, apply_to_predicted=True)
```

The `dataset` parameter of `apply_unification_pipeline` selects which label mappings
and dataset-specific corrections to apply — it refers to the **origin** of the data
being transformed, not the test set.

## Common Patterns

### Path resolution — use `unifiedsciere.paths`

```python
from unifiedsciere.paths import project_root, reports_dir, ensure_output

# Get project root (where .env / pyproject.toml lives)
root = project_root()

# Get a reports subdirectory (creates it if needed)
out_dir = reports_dir("ere_performance")

# Ensure parent dirs exist before writing; returns the path
path = ensure_output("reports/ere_performance/my_report.md")
path.write_text(content)
```

### Markdown report writing — use `unifiedsciere.reporting`

```python
from unifiedsciere.reporting import MarkdownReport

report = MarkdownReport("My Report Title")
report.text("Some intro paragraph.")
report.heading("Results", level=2)
report.table(df)                           # pandas DataFrame -> markdown table
report.text(f"Total: {n} items")

report.write("reports/ere_performance/my_report.md")  # ensures dirs, prints status
```

### Data loading

```python
from unifiedsciere.data_loader import load_corpus

gold = load_corpus("gsap", "dev", data_type="gold")
pred = load_corpus("gsap", "dev", data_type="predictions", trained_on="scier")
```

### gsap-hub evaluation

```python
from unifiedsciere.evaluate import mention_to_gsaphub, relation_to_gsaphub, filter_relations_with_valid_entities
import gsaphub as gh

ents_gold = [mention_to_gsaphub(m) for m in gold.mentions]
ents_pred = [mention_to_gsaphub(m) for m in pred.mentions_predicted]
results = gh.evaluate.entities.precision_recall_f1(ents_gold, ents_pred, partial=True)
```

### Script structure

Scripts live in `scripts/<subfolder>/` and should:
1. Use the package normally (`from unifiedsciere.paths import ...`) — the package is installed editable via `uv`
2. Not use `sys.path` hacks
3. Use `paths.reports_dir()` / `paths.ensure_output()` for output paths
4. Use `MarkdownReport` for report generation
