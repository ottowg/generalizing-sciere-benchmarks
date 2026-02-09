# UnifiedSciERE Documentation

**Unified Scientific Entity Recognition and Extraction**

Welcome to the UnifiedSciERE project documentation. This project aims to unify and analyze scientific entity recognition predictions across multiple models and datasets.

## Project Overview

### Goal

The primary goal of UnifiedSciERE is to create a unified framework for analyzing and comparing scientific entity recognition predictions from different models and annotation schemes. The project addresses the challenge that different scientific NER systems use incompatible label sets and annotation guidelines, making direct comparison difficult.

Key objectives:

1. **Unification**: Standardize entity labels across different annotation schemes (GSAP, SciER, SciNLP) into a common unified schema
2. **Analysis**: Provide comprehensive tools for comparing model predictions and understanding disagreements
3. **Correction**: Identify and filter systematic errors in model predictions
4. **Evaluation**: Enable fair comparison of different models by normalizing their outputs

### Motivation

Scientific literature contains valuable entities such as:
- **Datasets**: Training/evaluation datasets (e.g., ImageNet, COCO)
- **Methods**: Machine learning models and techniques (e.g., BERT, ResNet)
- **Tasks**: Scientific problems and objectives (e.g., image classification, question answering)

Different annotation projects have created entity recognition models with varying:
- Label taxonomies (e.g., "method" vs "Method" vs "MLModel")
- Annotation granularity
- Domain coverage
- Systematic biases

UnifiedSciERE bridges these differences to enable meaningful cross-model analysis.

## Architecture

### Components

The project consists of several key components:

1. **Data Loader** (`src/unifiedsciere/data_loader.py`)
   - Loads gold annotations and model predictions
   - Supports multiple datasets: GSAP, SciER, SciNLP
   - Handles both entity mentions and relations

2. **Unification Pipeline** (`src/unifiedsciere/unification/`)
   - Merges overlapping entity mentions
   - Drops unmapped labels
   - Maps labels to unified schema
   - Applies dataset-specific corrections

3. **Analysis Tools** (`src/unifiedsciere/analysis/`)
   - Confusion matrix generation
   - Performance metrics
   - Label-specific analysis

4. **Configuration** (`configs/`)
   - YAML-based pipeline configuration
   - Label mapping definitions
   - Correction thresholds

### Supported Datasets

- **GSAP**: Graph-based Scientific Abstract Processing dataset
- **SciER**: Scientific Entity Recognition dataset
- **SciNLP**: Scientific NLP dataset

Each dataset provides:
- Gold standard annotations
- Model predictions (trained on each dataset)
- Train/dev/test splits

## Documentation Structure

- **[README.md](README.md)** (this file): Project overview and getting started
- **[data_model.md](data_model.md)**: Detailed data structures and types
- **[unification_status.md](unification_status.md)**: Current pipeline implementation status
- **[label_mappings.md](label_mappings.md)**: Label mapping definitions and rationale (TODO)
- **[analysis_guide.md](analysis_guide.md)**: Guide to analysis tools and reports (TODO)

## Quick Start

### Installation

```bash
# Clone the repository
cd /path/to/UnifiedSciERE

# Install dependencies using uv
uv sync
```

### Basic Usage

#### 1. Load Data

```python
from src.unifiedsciere.data_loader import load_corpus

# Load gold annotations
corpus = load_corpus("gsap", "dev", data_type="gold")

# Load model predictions
corpus_pred = load_corpus("scier", "dev", data_type="predictions", trained_on="gsap")
```

#### 2. Apply Unification Pipeline

```python
from src.unifiedsciere.unification.pipeline import apply_unification_pipeline

# Apply complete unification pipeline
unified_corpus, stats = apply_unification_pipeline(
    corpus_pred,
    dataset="gsap",
    apply_to_predicted=True
)

print(f"Original: {stats['drop']['predicted_mentions_original']}")
print(f"Unified: {stats['drop']['predicted_mentions_kept']}")
```

#### 3. Generate Analysis Reports

```python
from src.unifiedsciere.unification.unified_confusion import generate_unified_confusion_report

# Generate confusion matrix comparing two models
report_path = generate_unified_confusion_report(
    datasets=["scier", "scinlp", "gsap"],
    split="dev",
    model1="gsap",
    model2="scier",
    combine_datasets=True
)
```

## Key Features

### 1. Label Unification

The pipeline maps diverse label sets to a unified schema:

```
GSAP:    Dataset, MLModel, Method, Task, ...
SciER:   Dataset, Method, Task
SciNLP:  dataset, method, task, metric
         ↓
Unified: Dataset, Method, Task
```

### 2. Span Matching

Uses partial span matching (via gsaphub) to align entities across models:
- Handles overlapping mentions
- Accounts for annotation boundary differences
- Supports one-to-many and many-to-one matches

### 3. Systematic Error Correction

Identifies and filters systematic errors:
- Generic references ("the model", "our approach")
- Over-predicted entities (GSAP MLModelGeneric)
- Configurable threshold-based filtering

### 4. Comprehensive Reporting

Generates multiple report types:
- Confusion matrices with original labels
- Entity count comparisons (Gold vs. predictions)
- Label-specific performance metrics
- Unmatched entity analysis

## Workflow Example

A typical analysis workflow:

```python
from src.unifiedsciere.data_loader import load_corpus
from src.unifiedsciere.unification.pipeline import apply_unification_pipeline
from src.unifiedsciere.unification.unified_confusion import generate_unified_confusion_report

# 1. Load data
corpus_gsap = load_corpus("gsap", "dev", data_type="predictions", trained_on="gsap")
corpus_scier = load_corpus("scier", "dev", data_type="predictions", trained_on="scier")

# 2. Apply unification
unified_gsap, _ = apply_unification_pipeline(corpus_gsap, "gsap")
unified_scier, _ = apply_unification_pipeline(corpus_scier, "scier")

# 3. Generate comparison report
report = generate_unified_confusion_report(
    datasets=["gsap", "scier"],
    split="dev",
    model1="gsap",
    model2="scier",
    combine_datasets=True
)
```

## Configuration

The pipeline behavior is controlled via `configs/unification_config.yaml`:

```yaml
merge_stacked:
  enabled: true
  prefer_larger: true

drop_unmapped:
  enabled: true

map_labels:
  enabled: true

dataset_corrections:
  gsap:
    enabled: true
    min_count: 2
```

See [unification_status.md](unification_status.md) for detailed pipeline documentation.

## Project Structure

```
UnifiedSciERE/
├── configs/                    # Configuration files
│   └── unification_config.yaml
├── data/                       # Dataset files
│   └── predictions/
├── documentation/              # Project documentation
│   ├── README.md              # This file
│   ├── data_model.md          # Data structures
│   └── unification_status.md # Pipeline status
├── reports/                    # Generated reports
│   └── unification/
├── src/unifiedsciere/         # Source code
│   ├── analysis/              # Analysis modules
│   ├── unification/           # Pipeline modules
│   ├── data_loader.py         # Data loading
│   └── types.py               # Data structures
└── tests/                     # Unit tests
```

## Contributing

When adding new features or modifying the pipeline:

1. Update relevant documentation in `documentation/`
2. Add/update tests in `tests/`
3. Update `unification_status.md` if pipeline changes
4. Regenerate example reports

## References

- **GSAP Dataset**: [Link to paper/repository]
- **SciER Dataset**: [Link to paper/repository]
- **SciNLP Dataset**: [Link to paper/repository]
- **gsaphub**: Entity matching library

## License

[Add license information]

## Contact

[Add contact information]

---
*Last updated: 2026-02-08*
