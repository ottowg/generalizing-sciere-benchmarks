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

## Experiment Structure

There are four analysis tracks, each corresponding to a view in the webapp:

### 1. Reproduction (`results/Reproduction`)
One model is trained per dataset (in-distribution). Results are compared against
numbers reported in the original papers to verify reproducibility. These individual
models also serve as the **baselines in the MultiSciERE comparison**.

Prediction directory per dataset: `pred_{dataset}/` (e.g. `pred_gsap-ere/`,
`pred_scier/`, `pred_scinlp/`). Evaluated in each dataset's **original label space**.

### 2. Cross-Dataset (`results/Cross-Dataset`)
All single-dataset models (+ a `unified-sciere` model trained on the full unified
corpus) are evaluated on every dataset using the **unified label space**. Covers all
train→test combinations.

### 3. MultiSciERE (`results/MultiSciERE`)
A **multi-head model** trained on 2 or 3 datasets simultaneously, using the original
label sets with one output head per dataset.

**Comparison**: 3 individual baselines (from Reproduction) vs. 4 multi-head variants:
- 3 × two-dataset combinations: GSAP-ERE+SciER, GSAP-ERE+SciNLP, SciER+SciNLP
- 1 × three-dataset model (all three)

**Tabs in the webapp:**
- *Summary* — in-distribution comparison on original labels (baselines vs. multi-head)
- *Seeded Models* — mean ± std across multiple training seeds for each multi-head variant
- *Generalization* (planned, moved from Cross-Dataset) — multi-head models evaluated
  across all datasets in unified label space; filterable by which datasets the model
  was trained on

### Multi-head prediction directory layout

```
$DATA_DATASETS_FOLDER/{test_dataset}/
  pred_multi-sciere/{label_set}/{split}.jsonl          # 3-dataset model (old convention)
  pred_multi-sciere-{ds1}-{ds2}/{label_set}/{split}.jsonl        # 2-dataset model
  pred_multi-sciere-{ds1}-{ds2}/{label_set}/{seed}/{split}.jsonl # seeded runs
```

- `{label_set}` matches the test dataset's native label space (e.g. `gsap` for gsap-ere)
- `{seed}` is an integer directory name (e.g. `41`, `42`, …); seeds are discovered
  automatically by scanning for integer-named subdirectories — do **not** hard-code them
- The model trained on datasets {ds1}+{ds2} is only evaluated on those datasets
  (in-distribution); cross-dataset generalization uses the unified label space

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

## Webapp UI Conventions

### Filter controls
All filter/selector controls in the webapp use `v-btn-toggle`, never `v-select` dropdowns.
Structure: a wrapping `div` with a `.text-caption.text-medium-emphasis.mb-1` label above,
then `v-btn-toggle(mandatory density="compact" variant="outlined" color="primary")`.
Multiple filter groups sit in a `.d-flex.flex-wrap.ga-4.mb-3` (or `mb-4`) row.

```pug
.d-flex.flex-wrap.ga-4.mb-3
  div
    .text-caption.text-medium-emphasis.mb-1 Dataset
    v-btn-toggle(v-model="ds" mandatory density="compact" variant="outlined" color="primary")
      v-btn(value="(all)" size="small") All
      v-btn(value="gsap-ere" size="small") GSAP-ERE
      v-btn(value="scier" size="small") SciER
      v-btn(value="scinlp" size="small") SciNLP
  div
    .text-caption.text-medium-emphasis.mb-1 Split
    v-btn-toggle(v-model="split" mandatory density="compact" variant="outlined" color="primary")
      v-btn(value="(both)" size="small") Both
      v-btn(value="dev" size="small") Dev
      v-btn(value="test" size="small") Test
```

`v-select` is only acceptable for free-text search, document pickers, or dropdowns with
more than ~6 dynamic options. Never use it for a known fixed set of filter values.

## Environment

- Node.js managed via **nvm** (current: node v24.14.0, npm v11.9.0)
- Data paths are configured via `.env` file (loaded by `python-dotenv`)
- `.env.example` documents available variables; copy to `.env` and adjust
- Current variables:
  - `DATA_DATASETS_FOLDER` — absolute path to the datasets root (the HGERE datasets folder)
- The `.env` file is gitignored; never commit secrets or machine-specific paths

## Data Model

Core types are defined in `src/unifiedsciere/types.py`:
- `Sentence` — a sentence with doc_id, index, split
- `Mention` — an entity span (id, text, label, character/token offsets, score, annotator, dataset, label_original)
- `Relation` — a typed link between two Mentions (subject, label, object)
- `Corpus` — container with `sentences`, `mentions`, `relation` (gold) and `mentions_predicted`, `relations_predicted`
- `PaperMetadata` — bibliographic metadata (title, authors, year, venue, identifiers, outlet)
  - `doi` — preferred published-venue DOI (e.g. `10.18653/v1/2020.acl-main.21`); empty for preprint-only papers
  - `doi_preprint` — arXiv preprint DOI (e.g. `10.48550/arXiv.1910.09700`); derivable from `arxiv_id` as `10.48550/arXiv.{arxiv_id}`
  - `dblp_id` — preferred published-venue DBLP key (e.g. `conf/cvpr/LiWCTT20`, `journals/jmlr/SmithJ20`); empty for preprint-only papers
  - `dblp_preprint_id` — DBLP corr key for the arXiv version (e.g. `journals/corr/abs-1910-09700`); derivable from `arxiv_id` as `journals/corr/abs-{arxiv_id with . replaced by -}`
- `Outlet` — publication venue (conference, journal, workshop, preprint)

## Data Access

Three datasets: **GSAP-ERE**, **SciER**, **SciNLP**. Each has train/dev/test splits.
Models: one per dataset (individual/reproduction), plus multi-head models trained on
2 or 3 datasets. See *Experiment Structure* above for the full model taxonomy.

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
- Gold data lives in `$DATA_DATASETS_FOLDER/{dataset}/{split}.jsonl`
- Predictions live in `$DATA_DATASETS_FOLDER/{dataset}/pred_{trained_on}/{split}.jsonl`
- Multi-label models: `$DATA_DATASETS_FOLDER/{dataset}/pred_multi-sciere/{label_set}/{split}.jsonl` — use `trained_on="multi-sciere-{label_set}"`

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
