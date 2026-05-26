# Baseline Results Report

**Generated:** 2026-05-18 15:49:39

Replicates baseline results from the original papers. Each model is evaluated on the test split of the dataset it was trained on (in-distribution). No label unification applied. All metrics use exact span matching.

## Summary

| Dataset   |   NER P |   NER R |   NER F1 |   RE P |   RE R |   RE F1 |   RE+ P |   RE+ R |   RE+ F1 |
|:----------|--------:|--------:|---------:|-------:|-------:|--------:|--------:|--------:|---------:|
| GSAP-ERE  |    83.2 |    82.4 |     82.8 |   58   |   53.6 |    55.7 |    49.8 |    46.1 |     47.9 |
| SCIER     |    88.1 |    86.2 |     87.2 |   69.7 |   60.8 |    64.9 |    67.1 |    58.6 |     62.6 |
| SCINLP    |    84.1 |    76.8 |     80.3 |   54.1 |   39.7 |    45.7 |    53.7 |    39.5 |     45.4 |

## Comparison with Paper-Reported Results

| Dataset   | Metric   |   Reproduced F1 |   Reported F1 |   Δ (repro − paper) |
|:----------|:---------|----------------:|--------------:|--------------------:|
| GSAP-ERE  | NER      |            82.8 |         80.6  |                2.2  |
| GSAP-ERE  | RE       |            55.7 |         54    |                1.7  |
| GSAP-ERE  | RE+      |            47.9 |         46.9  |                1    |
| SCIER     | NER      |            87.2 |         86.85 |                0.35 |
| SCIER     | RE       |            64.9 |         62.32 |                2.58 |
| SCIER     | RE+      |            62.6 |         61.1  |                1.5  |
| SCINLP    | NER      |            80.3 |         79.53 |                0.77 |
| SCINLP    | RE       |            45.7 |         49.28 |               -3.58 |
| SCINLP    | RE+      |            45.4 |         47.64 |               -2.24 |

## GSAP-ERE

### NER (exact match)

| Label             |     P |    R |   F1 |
|:------------------|------:|-----:|-----:|
| DataSource        |  65.3 | 72.1 | 68.5 |
| Dataset           |  87   | 92.9 | 89.9 |
| DatasetGeneric    |  85.9 | 86.5 | 86.2 |
| MLModel           |  58.7 | 65.1 | 61.7 |
| MLModelGeneric    |  86.4 | 81.9 | 84.1 |
| Method            |  72.3 | 76.3 | 74.3 |
| ModelArchitecture |  77.2 | 65.8 | 71.1 |
| ReferenceLink     |  99.4 | 99.6 | 99.5 |
| Task              |  89.5 | 80.1 | 84.5 |
| URL               | 100   | 45.5 | 62.5 |
| micro             |  82   | 82.1 | 82.1 |
| macro             |  82.2 | 76.6 | 78.2 |
| weighted          |  82.3 | 82.1 | 82.1 |

### RE (relaxed match)

| Label           |    P |    R |   F1 |
|:----------------|-----:|-----:|-----:|
| weighted        | 56.2 | 54.3 | 54.5 |
| micro           | 56   | 54.3 | 55.1 |
| macro           | 51.9 | 47.1 | 47.9 |
| benchmarkFor    | 52.5 | 50   | 51.2 |
| appliedTo       | 68.8 | 47.8 | 56.4 |
| url             | 40   | 66.7 | 50   |
| citation        | 61.2 | 71.6 | 66   |
| isPartOf        | 52.3 | 34.8 | 41.8 |
| isHyponymOf     | 52.9 | 38.9 | 44.9 |
| isComparedTo    | 69.6 | 56.9 | 62.6 |
| coreference     | 68.6 | 66.7 | 67.6 |
| usedFor         | 51.3 | 52.9 | 52.1 |
| isBasedOn       | 41.7 | 31.2 | 35.7 |
| architecture    | 70.6 | 55.4 | 62.1 |
| trainedOn       | 51   | 56.8 | 53.7 |
| evaluatedOn     | 53.5 | 64.8 | 58.6 |
| transformedFrom | 28.4 | 29.3 | 28.9 |
| sourcedFrom     | 45.8 | 47.4 | 46.6 |
| generatedBy     | 32.4 | 29.6 | 31   |
| size            | 42.9 | 41.7 | 42.3 |
| hasInstanceType | 50   |  5.8 | 10.3 |

### RE+ (strict match)

| Label           |    P |    R |   F1 |
|:----------------|-----:|-----:|-----:|
| weighted        | 48   | 46.3 | 46.5 |
| micro           | 47.8 | 46.3 | 47.1 |
| macro           | 45.7 | 41.6 | 42.1 |
| benchmarkFor    | 49.2 | 46.8 | 47.9 |
| appliedTo       | 52.3 | 36.3 | 42.9 |
| url             | 40   | 66.7 | 50   |
| citation        | 52.8 | 61.9 | 57   |
| isPartOf        | 47.7 | 31.7 | 38.1 |
| isHyponymOf     | 44.4 | 32.7 | 37.7 |
| isComparedTo    | 43.9 | 35.9 | 39.5 |
| coreference     | 54.7 | 53.2 | 54   |
| usedFor         | 42.6 | 43.9 | 43.2 |
| isBasedOn       | 41.7 | 31.2 | 35.7 |
| architecture    | 68.5 | 53.8 | 60.3 |
| trainedOn       | 45.6 | 50.9 | 48.1 |
| evaluatedOn     | 45.7 | 55.2 | 50   |
| transformedFrom | 27.7 | 28.7 | 28.2 |
| sourcedFrom     | 44.1 | 45.6 | 44.8 |
| generatedBy     | 29.7 | 27.2 | 28.4 |
| size            | 42.9 | 41.7 | 42.3 |
| hasInstanceType | 50   |  5.8 | 10.3 |

## SCIER

### NER (exact match)

| Label    |    P |    R |   F1 |
|:---------|-----:|-----:|-----:|
| Dataset  | 83.7 | 88.9 | 86.2 |
| Method   | 89.4 | 85.2 | 87.2 |
| Task     | 86.3 | 85.2 | 85.7 |
| micro    | 87.9 | 85.7 | 86.8 |
| macro    | 86.5 | 86.4 | 86.4 |
| weighted | 88   | 85.7 | 86.8 |

### RE (relaxed match)

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 68.7 | 58.1 | 61.9 |
| micro          | 68.9 | 58.1 | 63   |
| macro          | 71.7 | 59.5 | 64.3 |
| Used-For       | 63.7 | 67   | 65.3 |
| Trained-With   | 75   | 60   | 66.7 |
| Synonym-Of     | 83.1 | 84.1 | 83.6 |
| SubTask-Of     | 78.3 | 72.3 | 75.2 |
| SubClass-Of    | 69.2 | 51.1 | 58.8 |
| Part-Of        | 63.8 | 31.9 | 42.5 |
| Evaluated-With | 74.4 | 51.1 | 60.6 |
| Compare-With   | 67.5 | 47.4 | 55.7 |
| Benchmark-For  | 70.6 | 70.6 | 70.6 |

### RE+ (strict match)

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 66.3 | 55.7 | 59.5 |
| micro          | 66   | 55.7 | 60.4 |
| macro          | 70   | 57.9 | 62.7 |
| Used-For       | 58.6 | 61.7 | 60.1 |
| Trained-With   | 71.4 | 57.1 | 63.5 |
| Synonym-Of     | 80.2 | 81.2 | 80.7 |
| SubTask-Of     | 78.3 | 72.3 | 75.2 |
| SubClass-Of    | 67.7 | 50   | 57.5 |
| Part-Of        | 63.8 | 31.9 | 42.5 |
| Evaluated-With | 74.4 | 51.1 | 60.6 |
| Compare-With   | 66.2 | 46.5 | 54.6 |
| Benchmark-For  | 69.4 | 69.4 | 69.4 |

## SCINLP

### NER (exact match)

| Label    |    P |    R |   F1 |
|:---------|-----:|-----:|-----:|
| dataset  | 85.5 | 74.7 | 79.7 |
| method   | 84.2 | 81.9 | 83   |
| metric   | 63.9 | 93.9 | 76   |
| task     | 85   | 73   | 78.5 |
| micro    | 82.5 | 80.1 | 81.3 |
| macro    | 79.7 | 80.9 | 79.3 |
| weighted | 83.2 | 80.1 | 81.3 |

### RE (relaxed match)

| Label       |    P |    R |   F1 |
|:------------|-----:|-----:|-----:|
| weighted    | 57   | 44.9 | 48.2 |
| micro       | 53   | 44.9 | 48.6 |
| macro       | 56.7 | 44.6 | 48.4 |
| evaluatedOn | 70   | 43.8 | 53.8 |
| trainedWith | 35.7 | 45.5 | 40   |
| subtaskOf   | 81.8 | 60   | 69.2 |
| subclassOf  | 60   | 29   | 39.1 |
| similarWith | 17.6 | 16.7 | 17.1 |
| partOf      | 15.4 | 25   | 19   |
| evaluatedBy | 85.7 | 75   | 80   |
| enhancedBy  | 56.2 | 20.9 | 30.5 |
| compareWith | 68.6 | 46.2 | 55.2 |
| UsedFor     | 47.4 | 62.2 | 53.8 |
| MeasuredBy  | 85.7 | 66.7 | 75   |

### RE+ (strict match)

| Label       |    P |    R |   F1 |
|:------------|-----:|-----:|-----:|
| weighted    | 56.1 | 44.2 | 47.4 |
| micro       | 52.2 | 44.2 | 47.9 |
| macro       | 55.3 | 43.5 | 47.2 |
| evaluatedOn | 70   | 43.8 | 53.8 |
| trainedWith | 35.7 | 45.5 | 40   |
| subtaskOf   | 72.7 | 53.3 | 61.5 |
| subclassOf  | 60   | 29   | 39.1 |
| similarWith | 17.6 | 16.7 | 17.1 |
| partOf      | 15.4 | 25   | 19   |
| evaluatedBy | 85.7 | 75   | 80   |
| enhancedBy  | 56.2 | 20.9 | 30.5 |
| compareWith | 68.6 | 46.2 | 55.2 |
| UsedFor     | 47.4 | 62.2 | 53.8 |
| MeasuredBy  | 78.6 | 61.1 | 68.8 |
