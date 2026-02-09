# Schema Definitions

This directory contains YAML schema definitions for the entity and relation types used in each dataset.

## Files

- **scinlp.yaml**: SciNLP dataset schema
- **scier.yaml**: SciERC dataset schema  
- **gsap.yaml**: GSAP (Generic Scholarly Article Processing) dataset schema

## Schema Format

Each YAML file contains:

```yaml
dataset: <dataset_name>
description: <brief description>

entities:
  <entity_type>:
    description: <what this entity represents>
    examples:
      - <example 1>
      - <example 2>

relations:
  <relation_type>:
    description: <what this relation represents>
    arguments: [<subject_types>, <object_types>]
    examples:
      - <example usage>
```

## Key Differences Between Schemas

### Entity Types

| SciNLP | SciERC | GSAP |
|--------|--------|------|
| dataset | Dataset | DataSource, Dataset, DatasetGeneric |
| method | Method | MLModel, MLModelGeneric, Method, ModelArchitecture |
| metric | - | - |
| task | Task | Task |
| - | - | ReferenceLink, URL |

**Granularity:**
- **SciNLP**: 4 entity types (lowercase)
- **SciERC**: 3 entity types (capitalized)
- **GSAP**: 10 entity types (fine-grained, distinguishing specific vs. generic mentions)

### Relation Types

**SciNLP**: 11 relation types (mixed case: camelCase and PascalCase)
- MeasuredBy, UsedFor, compareWith, enhancedBy, evaluatedBy, evaluatedOn, partOf, similarWith, subclassOf, subtaskOf, trainedWith

**SciERC**: 9 relation types (PascalCase with hyphens)
- Benchmark-For, Compare-With, Evaluated-With, Part-Of, SubClass-Of, SubTask-Of, Synonym-Of, Trained-With, Used-For

**GSAP**: 20 relation types (camelCase, fine-grained)
- appliedTo, architecture, benchmarkFor, citation, coreference, evaluatedOn, generatedBy, hasInstanceType, isBasedOn, isComparedTo, isHyponymOf, isPartOf, processed, size, sourcedFrom, trainedOn, transformedFrom, url, usedFor, versionOf

## Alignment Challenges

The datasets use different:
1. **Naming conventions**: lowercase vs. Capitalized vs. camelCase
2. **Granularity**: GSAP distinguishes specific vs. generic entities (MLModel vs. MLModelGeneric)
3. **Type inventories**: Different numbers and types of labels
4. **Semantic coverage**: GSAP includes citations and URLs; SciNLP includes metrics

To enable cross-dataset evaluation, a mapping system is needed to align semantically equivalent labels.
