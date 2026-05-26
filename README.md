# UnifiedSciERE

Research repository comparing and unifying three document-level **Entity and Relation Extraction (ERE)** datasets in the ML/AI/CS domain:

| Dataset | Domain focus | Splits |
|---------|-------------|--------|
| **GSAP-ERE** | ML/AI (broad) | train / dev / test |
| **SciER** | NLP | train / dev / test |
| **SciNLP** | NLP | train / dev / test |

The project covers four analysis tracks — reproduction, cross-dataset evaluation, multi-head training (MultiSciERE), and a domain-shift auxiliary transfer experiment — all visualised in an interactive webapp.

---

## Quick start

```bash
# 1. Copy environment config and set your data path
cp .env.example .env
# Edit .env: set DATA_DATASETS_FOLDER to the root of your HGERE datasets folder

# 2. Install Python dependencies
uv sync

# 3. Start the webapp (dev mode)
bash start_webapp.sh
# → http://localhost:5173
```

> **Node.js**: managed via nvm. `start_webapp.sh` picks up the latest installed version automatically.

---

## Repository layout

```
configs/              Schema and experiment configs (unification, paper map, …)
data/
  gold/               Gold annotations per dataset (gitignored except parquet/static)
  annotation_lookup/  Pre-built lookup tables for the Lookup tab
  webapp/             Pre-generated JSON/YAML served by the webapp API (gitignored)
  webapp/static/      Manually curated static files (reported_performance.json, …)
docs/                 Internal documentation
paper/                Manuscript drafts and appendix sections
reports/              Generated markdown reports (sidebar in webapp)
scripts/              Analysis and data-generation scripts (see below)
src/unifiedsciere/    Core Python package
  data_loader.py      load_corpus() — gold and prediction loading
  evaluate.py         gsap-hub conversion helpers
  unification/        Label mapping and unification pipeline
  paths.py            project_root(), reports_dir(), ensure_output()
  reporting.py        MarkdownReport helper
tests/                pytest suite
webapp/               Vue 3 + Vuetify frontend + Node.js API server
  src/components/     One .vue file per view/tab
  server/api/         API middleware handlers (mirrored in vite.config.js for dev)
  server.js           Production server (used by Docker / HF Spaces)
```

---

## Experiment tracks

### 1. Reproduction
One model trained per dataset in its original label space. Results are compared against numbers reported in the original papers.

Prediction directory: `$DATA_DATASETS_FOLDER/{dataset}/pred_{dataset}/`

### 2. Cross-Dataset
All single-dataset models (plus a `unified-sciere` model) evaluated on every dataset using the **unified label space**. Covers all train→test combinations.

### 3. MultiSciERE
Multi-head models trained simultaneously on 2 or 3 datasets (one output head per dataset). Compared against the single-dataset baselines.

Variants: `gsap-ere+scier`, `gsap-ere+scinlp`, `scier+scinlp`, all-three.

Prediction layout:
```
$DATA_DATASETS_FOLDER/{test_dataset}/
  pred_multi-sciere-{ds1}-{ds2}/{label_set}/{seed}/{split}.jsonl
  pred_multi-sciere/{label_set}/{split}.jsonl   # 3-dataset (older convention)
```

### 4. Auxiliary Transfer (Domain Shift)
SciER is split by NLP / non-NLP domain (cluster from publication map). Four training runs (A–D) examine whether GSAP-ERE auxiliary data helps generalise to the NLP domain.

| Run | Training data |
|-----|--------------|
| A | SciER baseline (non-NLP only) |
| B | SciER + non-NLP GSAP-ERE auxiliary |
| C | SciER + NLP GSAP-ERE auxiliary |
| D | SciER + mixed GSAP-ERE auxiliary |

Prediction layout: `$DATA_DATASETS_FOLDER/domain-shift-scier/pred_{run_id}/{seed}/{split}.jsonl`

---

## Scripts

All scripts are run via `uv run python scripts/...`.

### Performance reports (`scripts/ere_performance/`)
| Script | Output |
|--------|--------|
| `label_statistics.py` | `data/webapp/label_statistics.json` |
| `cross_dataset_performance.py` | `data/webapp/cross_dataset_performance.json` |
| `reproduce_results_report.py` | `data/webapp/reproduce_results.json` |
| `multi_sciere_results_report.py` | `data/webapp/multi_sciere_results.json` |
| `domain_shift_results_report.py` | `data/webapp/domain_shift_results.json` |
| `build_annotation_lookup.py` | `data/annotation_lookup/` |

### Dataset creation (`scripts/paper_map/`)
| Script | Purpose |
|--------|---------|
| `create_auxiliary_transfer_splits.py` | Creates domain-shift JSONL splits and webapp manifest |
| `compute_paper_clustering.py` | NLP / non-NLP cluster assignments |
| `paper_map_embed.py` | Paper embeddings and UMAP layout |

### Webapp data (`scripts/ere_quality/`, `scripts/paper_metadata/`)
| Script | Output |
|--------|--------|
| `relation_signatures.py` | `data/webapp/relation_signatures.json` + `semantic_groups.json` |
| `allowed_signatures.py` | `data/webapp/allowed_signatures.yaml` |
| `build_example_papers.py` | `data/webapp/example_papers.json` |
| `build_webapp_metadata.py` | `data/webapp/static/webapp_metadata.json` |

### Regenerate all webapp data at once
```bash
uv run python scripts/build_webapp_data.py
```

---

## Environment variables (`.env`)

| Variable | Description |
|----------|-------------|
| `DATA_DATASETS_FOLDER` | Absolute path to the HGERE datasets root |
| `WEBAPP_HOST` | Dev server host (default `localhost`; set to a LAN IP to expose) |
| `OPENALEX_EMAIL` | Your e-mail for the OpenAlex polite pool (10 req/s vs 1 req/s) |
| `HF_TOKEN` | HuggingFace write token (deployment only) |
| `HF_SPACE_USERNAME` | HF username for the target Space |
| `HF_SPACE_NAME` | HF Space name (default `unifiedsciere`) |

---

## Python package extras

```bash
uv sync                          # base install
uv sync --extra paper-map        # + torch, sentence-transformers, UMAP
uv sync --extra vllm             # + vLLM serving stack
uv sync --extra paper-map --extra vllm   # both (only if compatible)
uv sync --extra dev              # + ruff, pytest, jupyterlab
```

---

## Deploying to HuggingFace Spaces

```bash
# Full build + deploy
bash deploy_hf.sh

# Skip metric regeneration (reuse existing data/webapp/*.json)
bash deploy_hf.sh --skip-data

# Skip metric regeneration AND frontend build
bash deploy_hf.sh --skip-build

# Build and assemble without pushing (inspect $DEPLOY_DIR)
bash deploy_hf.sh --dry-run
```

The script:
1. Regenerates all `data/webapp/` JSON files from predictions
2. Builds the Vite frontend with `VITE_DOCKER_MODE=true`
3. Assembles a deployment directory (`webapp/`, `data/`, `reports/`, `configs/`, `Dockerfile`)
4. Force-pushes to the HF Space git remote

---

## Development notes

- **Package manager**: `uv` — use `uv run`, `uv add`, `uv sync`
- **File operations**: `git mv` / `git rm` (not plain `mv` / `rm`)
- **ERE metrics**: always via the `gsaphub` library (`gh.evaluate.entities`, `gh.evaluate.relations`)
- **Unification direction**: predictions are unified using the *trained-on* dataset's scheme; gold is unified using the *test* dataset's scheme
- **Webapp filter controls**: always `v-btn-toggle`, never `v-select` for a fixed set of options
