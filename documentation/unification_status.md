# Unification Pipeline Status

This document describes the current implementation status of the UnifiedSciERE unification pipeline, including all steps, configurations, and results.

## Overview

The unification pipeline standardizes entity annotations across different models and datasets through a series of configurable steps. The pipeline is controlled via `configs/unification_config.yaml` and can be applied to both gold annotations and model predictions.

## Pipeline Architecture

```
┌─────────────────┐
│  Load Corpus    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ 1. Merge Stacked       │
│    Overlapping Mentions │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────┐
│ 2. Drop Unmapped    │
│    Labels           │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 3. Map Labels to    │
│    Unified Schema   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ 4. Dataset-Specific │
│    Corrections      │
└────────┬────────────┘
         │
         ▼
┌─────────────────┐
│ Unified Corpus  │
└─────────────────┘
```

## Pipeline Steps

### Step 1: Merge Stacked Mentions

**Module**: `src/unifiedsciere/unification/merge_stacked.py`

**Purpose**: Handle overlapping entity mentions by merging them into a single mention.

**Configuration**:
```yaml
merge_stacked:
  enabled: true
  prefer_larger: true  # Keep larger spans when merging
```

**Algorithm**:
1. Group mentions by document and sentence
2. For each sentence, find overlapping mentions (sharing ≥1 character)
3. Merge overlapping mentions:
   - If `prefer_larger=true`: Keep the mention with the longest span
   - If `prefer_larger=false`: Keep the mention with the shortest span
4. Update relations to reference merged mentions
5. Remove self-loop relations (subject == object after merging)
6. Remove duplicate relations

**Example**:
```
Original:
  "BERT model" [0:10] - MLModel
  "BERT" [0:4] - Method

After merge (prefer_larger=true):
  "BERT model" [0:10] - MLModel
```

**Statistics Tracked**:
- Number of mentions merged
- Self-loop relations removed
- Duplicate relations removed
- Label merge patterns

**Status**: ✅ **Fully Implemented**

### Step 2: Drop Unmapped Labels

**Module**: `src/unifiedsciere/unification/label_mapper.py` (`drop_unmapped_mentions`)

**Purpose**: Remove mentions whose labels don't map to the unified schema.

**Configuration**:
```yaml
drop_unmapped:
  enabled: true
```

**Label Mappings** (defined in `label_mappings.yaml`):

| Dataset | Dropped Labels | Reason |
|---------|----------------|--------|
| GSAP | URL, ReferenceLink, DataSource, DatasetGeneric | Don't fit unified schema |
| SciER | (none currently) | All labels map to unified schema |
| SciNLP | metric | Not in unified schema |

**Algorithm**:
1. Load label mappings for the dataset
2. Identify labels that map to `null`
3. Filter out mentions with null-mapped labels
4. Remove relations referencing dropped mentions

**Example**:
```
Before:
  "ImageNet" - Dataset ✓
  "http://..." - URL ✗
  "BERT" - Method ✓

After:
  "ImageNet" - Dataset
  "BERT" - Method
```

**Statistics Tracked**:
- Mentions dropped (predicted/gold)
- Relations dropped (predicted/gold)
- List of dropped labels

**Status**: ✅ **Fully Implemented**

### Step 3: Map to Unified Schema

**Module**: `src/unifiedsciere/unification/label_mapper.py` (`map_labels_to_unified`)

**Purpose**: Transform dataset-specific labels to unified label set.

**Configuration**:
```yaml
map_labels:
  enabled: true
```

**Unified Schema**:
- **Dataset**: Training/evaluation datasets
- **Method**: ML models, architectures, techniques
- **Task**: Scientific problems and objectives

**Label Mappings**:

#### GSAP → Unified
```
Dataset → Dataset
MLModel → Method
MLModelGeneric → Method
ModelArchitecture → Method
Method → Method
Task → Task
DataSource → (dropped)
URL → (dropped)
ReferenceLink → (dropped)
DatasetGeneric → (dropped)
```

#### SciER → Unified
```
Dataset → Dataset
Method → Method
Task → Task
```

#### SciNLP → Unified
```
dataset → Dataset
method → Method
task → Task
metric → (dropped)
```

**Algorithm**:
1. Load label mappings for the dataset
2. For each mention:
   - Look up unified label in mapping
   - Create new mention with unified label
   - Preserve original label in `label_original` field
3. Update relations to reference new mention objects
4. Track label change statistics

**Example**:
```
Before:
  text="BERT", label="MLModel", label_original=""

After:
  text="BERT", label="Method", label_original="MLModel"
```

**Statistics Tracked**:
- Mentions mapped (predicted/gold)
- Label change patterns (original → unified)

**Status**: ✅ **Fully Implemented**

### Step 4: Dataset-Specific Corrections

**Module**: Various correction modules per dataset

**Purpose**: Apply dataset-specific error corrections based on empirical analysis.

**Configuration**:
```yaml
dataset_corrections:
  gsap:
    enabled: true
    mlmodelgeneric_analysis_file: "reports/.../analysis.json"
    min_count: 2
  scier:
    enabled: false
  scinlp:
    enabled: false
```

#### GSAP Corrections

**Module**: `src/unifiedsciere/unification/gsap_specific_corrections.py`

**Purpose**: Filter generic MLModelGeneric predictions that GSAP over-predicts.

**Analysis**: `src/unifiedsciere/unification/gsap_specific_analysis.py`
- Identifies GSAP predictions with no match in SciER or SciNLP
- Focuses on Method+MLModelGeneric mentions
- Generates JSON list of unmatched entities

**Filtering Strategy**:
1. Load analysis JSON file
2. Extract texts appearing ≥ `min_count` times
3. Remove mentions matching those texts
4. Update relations accordingly

**Common Filtered Texts** (dev set, min_count=2):
- "the model" (80 occurrences)
- "models" (23 occurrences)
- "our model" (12 occurrences)
- "a model" (11 occurrences)
- "the models" (10 occurrences)
- ... and 61 more

**Statistics Tracked**:
- Mentions filtered (predicted/gold)
- Relations filtered
- Total unique texts filtered

**Status**: ✅ **Fully Implemented**

#### SciER Corrections

**Status**: 🔄 **Placeholder** - No corrections currently implemented

Future corrections could include:
- Dataset-specific systematic errors
- Boundary adjustment rules
- Label-specific filtering

#### SciNLP Corrections

**Status**: 🔄 **Placeholder** - No corrections currently implemented

Future corrections could include:
- Lowercase normalization issues
- Metric label handling
- Domain-specific errors

## Configuration System

### Configuration File

**Location**: `configs/unification_config.yaml`

**Structure**:
```yaml
# Enable/disable each pipeline step
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
    mlmodelgeneric_analysis_file: "path/to/analysis.json"
    min_count: 2
  scier:
    enabled: false
  scinlp:
    enabled: false

# Pipeline settings
pipeline:
  verbose: true
  generate_reports: true
  report_output_dir: "reports/unification/pipeline"
```

### Label Mapping File

**Location**: `src/unifiedsciere/unification/label_mappings.yaml`

**Structure**:
```yaml
mappings:
  gsap:
    Dataset: Dataset
    MLModel: Method
    MLModelGeneric: Method
    URL: null  # Will be dropped
    # ...
  
  scier:
    Dataset: Dataset
    Method: Method
    Task: Task
  
  scinlp:
    dataset: Dataset
    method: Method
    task: Task
    metric: null  # Will be dropped
```

## Usage

### Basic Pipeline Application

```python
from src.unifiedsciere.data_loader import load_corpus
from src.unifiedsciere.unification.pipeline import apply_unification_pipeline

# Load corpus
corpus = load_corpus("gsap", "dev", data_type="predictions", trained_on="gsap")

# Apply pipeline
unified_corpus, stats = apply_unification_pipeline(
    corpus,
    dataset="gsap",
    apply_to_predicted=True,
    apply_to_gold=False
)

# Access results
print(f"Original: {len(corpus.mentions_predicted)}")
print(f"Unified: {len(unified_corpus.mentions_predicted)}")
```

### Custom Configuration

```python
from pathlib import Path

# Use custom config file
unified_corpus, stats = apply_unification_pipeline(
    corpus,
    dataset="gsap",
    config_path=Path("custom_config.yaml")
)
```

### Generate Pipeline Report

```python
from src.unifiedsciere.unification.pipeline import generate_pipeline_report

generate_pipeline_report(
    stats,
    output_path=Path("reports/my_pipeline_report.md")
)
```

## Current Results (Dev Set)

### GSAP Predictions

**Original**: 6,373 mentions

**After Pipeline**: 3,440 mentions (46% reduction)

**Breakdown**:
- **Merge**: 305 mentions merged
- **Drop**: 2,348 mentions dropped
  - Dropped labels: URL, DatasetGeneric, ReferenceLink
- **Map**: 1,566 mentions had label changes
  - MLModelGeneric → Method
  - MLModel → Method
  - ModelArchitecture → Method
- **GSAP Corrections**: 280 mentions filtered
  - 66 unique text patterns filtered
  - Generic references removed

### SciER Predictions

**Original**: ~3,638 mentions (GSAP dataset)

**After Pipeline**: ~3,559 mentions

**Breakdown**:
- **Merge**: 79 mentions merged
- **Drop**: 0 mentions (all labels map to unified schema)
- **Map**: Minimal changes (labels already close to unified)
- **Corrections**: None applied

### SciNLP Predictions

**Original**: ~3,407 mentions (GSAP dataset)

**After Pipeline**: ~3,321 mentions

**Breakdown**:
- **Merge**: 86 mentions merged
- **Drop**: Metric labels removed
- **Map**: All labels uppercased (dataset → Dataset)
- **Corrections**: None applied

## Analysis Tools

### Confusion Matrices

**Module**: `src/unifiedsciere/unification/unified_confusion.py`

Generates confusion matrices comparing model predictions after unification:

```python
from src.unifiedsciere.unification.unified_confusion import generate_unified_confusion_report

report_path = generate_unified_confusion_report(
    datasets=["scier", "scinlp", "gsap"],
    split="dev",
    model1="gsap",
    model2="scier",
    combine_datasets=True,
    top_n=15
)
```

**Features**:
- Partial span matching between models
- Shows both unified and original labels
- Displays gold/prediction entity counts
- Top N most frequent label pairs
- Combined or per-dataset analysis

**Generated Reports**:
- `confusion_unified_gsap_scier_dev_combined.md`
- `confusion_unified_gsap_scinlp_dev_combined.md`
- `confusion_unified_scinlp_scier_dev_combined.md`

### GSAP-Specific Analysis

**Module**: `src/unifiedsciere/unification/gsap_specific_analysis.py`

Identifies unmatched GSAP MLModelGeneric predictions:

```python
from src.unifiedsciere.unification.gsap_specific_analysis import analyze_gsap_unmatched_mlmodelgeneric

json_path, report_path = analyze_gsap_unmatched_mlmodelgeneric(
    datasets=["scier", "scinlp", "gsap"],
    split="dev"
)
```

**Outputs**:
- JSON file with all unmatched mentions
- Markdown report with top 50 unmatched
- Statistics on coverage

## Future Enhancements

### Planned Features

1. **Additional Corrections**
   - SciER-specific error patterns
   - SciNLP lowercase/uppercase handling
   - Context-aware generic reference detection

2. **Improved Matching**
   - Fuzzy string matching for near-duplicates
   - Semantic similarity-based matching
   - Configurable matching thresholds

3. **Extended Analysis**
   - Per-label F1 scores after unification
   - Error analysis by document type
   - Temporal trends in predictions

4. **Pipeline Optimization**
   - Caching intermediate results
   - Parallel processing for large datasets
   - Memory-efficient streaming

### Configuration Extensions

Future configuration options:

```yaml
# Advanced matching (TODO)
matching:
  strategy: "partial"  # or "exact", "fuzzy"
  threshold: 0.8       # for fuzzy matching

# Additional filters (TODO)
filters:
  min_mention_length: 2
  max_mention_length: 100
  blacklist_patterns: ["^the$", "^our$"]
```

## Testing

### Unit Tests

Test coverage for pipeline components:

```bash
# Run pipeline tests
uv run pytest tests/test_pipeline.py

# Run specific test
uv run pytest tests/test_pipeline.py::test_merge_stacked
```

### Integration Tests

End-to-end pipeline tests:

```bash
uv run pytest tests/test_integration.py
```

### Validation

Validate pipeline output:

```python
from src.unifiedsciere.unification.pipeline import apply_unification_pipeline

corpus = load_corpus("gsap", "dev", data_type="predictions", trained_on="gsap")
unified, stats = apply_unification_pipeline(corpus, "gsap")

# Validate all labels are unified
assert all(
    m.label in ["Dataset", "Method", "Task"]
    for m in unified.mentions_predicted
)

# Validate original labels preserved
assert all(
    m.label_original != ""
    for m in unified.mentions_predicted
)
```

## Related Documentation

- [README.md](README.md): Project overview
- [data_model.md](data_model.md): Data structures
- `configs/unification_config.yaml`: Pipeline configuration
- `src/unifiedsciere/unification/label_mappings.yaml`: Label mappings

## Changelog

### 2026-02-08
- ✅ Implemented complete 4-step pipeline
- ✅ Added GSAP-specific MLModelGeneric correction
- ✅ Created YAML-based configuration system
- ✅ Added pipeline reporting
- ✅ Integrated label_original field preservation
- ✅ Generated confusion matrices with original labels

### Future
- 🔄 Add SciER/SciNLP specific corrections
- 🔄 Implement fuzzy matching options
- 🔄 Add caching for performance
- 🔄 Extend test coverage

---
*Last updated: 2026-02-08*
