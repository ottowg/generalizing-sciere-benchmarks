# UnifiedSciERE

## This project creates a unified dataset out of three document-level Entity and Relation Extraction (ERE) datasets

## Datasets
### SciERE
### SciNLP
### GSAP-ERE

## Predictions
 * We collect predictions on the test set of each dataset from models trained on all three corpora separated

### Overview of `data/predictions`

 * `<training_model_name>_<inference_corpus>_<split>.jsonl`
 * `gsap_gsap_test.jsonl`
 * `gsap_scinlp_test.jsonl`
 * ...


## Data Format
## Optional dependency sets (uv)

This project uses **extras** to install larger / sometimes conflicting stacks only when needed.

### Base install
```bash
uv sync
```

### Paper-map stack
Installs the dependencies from `project.optional-dependencies.paper-map`:

```bash
uv sync --extra paper-map
```

### vLLM serving stack
Installs the dependencies from `project.optional-dependencies.vllm`:

```bash
uv sync --extra vllm
```

### Switching between extras
Syncing with a different extra updates the current `.venv` to match that selection.

Switch to `paper-map` and remove `vllm`:

```bash
uv sync --extra paper-map --no-extra vllm
```

Switch to `vllm` and remove `paper-map`:

```bash
uv sync --extra vllm --no-extra paper-map
```

### Installing both (only if compatible)
```bash
uv sync --extra paper-map --extra vllm
```

