# Paper Map — Interactive Publication Visualization

The paper map provides a 2D scatter visualization of all papers in the unified
corpus, letting you explore topical clusters, dataset overlaps, and publication
venue distributions.

## How It Works

1. **Embeddings** — Paper abstracts are encoded with
   [SPECTER2](https://huggingface.co/allenai/specter2_base) (a SciBERT-based
   model fine-tuned for scientific document similarity).
2. **Dimensionality reduction** — The high-dimensional embeddings are projected
   to 2D using either UMAP or a k-nearest-neighbour force layout.
3. **Visualization** — A Streamlit app renders the map as an interactive Plotly
   scatter plot with colour coding by dataset, year, venue, topic, etc.

## Requirements

Install the `paper-map` optional dependencies:

```bash
uv sync --extra paper-map
```

This adds `torch`, `transformers`, `adapters`, `umap-learn`, `scikit-learn`,
`plotly`, `streamlit`, and related packages.

## Computing Embeddings

```bash
uv run python scripts/paper_map/paper_map_embed.py
```

This reads the unified metadata from `data/metadata/unified/all_papers.jsonl`,
computes SPECTER2 embeddings, and saves them to `data/doc_embeddings/`.

Configuration in `scripts/paper_map/paper_map_config.yaml`:

```yaml
data_path: data/metadata/unified/all_papers.jsonl
model_name: allenai/specter2_base
adapter_name: allenai/specter2
batch_size: 32
artifacts_dir: data/doc_embeddings

umap:
    n_neighbors: 15
    min_dist: 0.1
    metric: cosine
    random_state: 42

knn:
    k: 12
    symmetrize: true
```

## Running the App

```bash
uv run streamlit run scripts/paper_map/streamlit_paper_map.py
```

### Colour-by options

The sidebar lets you colour points by:

| Option | Description |
|--------|-------------|
| `dataset_detail` | Dataset + split (e.g. "gsap_train", "scier_dev") |
| `dataset` | Source dataset (GSAP, SciER, SciNLP) |
| `year` | Publication year |
| `article_type` | Conference, journal, preprint |
| `outlet_type` | Conference, journal, workshop, preprint |
| `outlet_topic` | Research area (NLP, CV, ML, ...) |
| `outlet_abbr` | Venue abbreviation (ACL, CVPR, NeurIPS, ...) |
| `split` | Train / dev / test |

### Layout options

- **UMAP** — Non-linear projection preserving local neighbourhood structure
- **kNN force layout** — Spring-based layout from a k-nearest-neighbour graph;
  can be more interpretable for cluster separation

## Data Requirements

The paper map depends on the unified metadata file. To build it:

```bash
uv run python scripts/paper_metadata/build_unified_metadata.py
uv run python scripts/paper_metadata/enrich_unified_metadata.py
```

This produces `data/metadata/unified/all_papers.jsonl` with `PaperMetadata`
records for all papers across the three datasets.
