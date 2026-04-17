# Baseline Results Report

**Generated:** 2026-04-17 15:02:07

Replicates baseline results from the original papers. Each model is evaluated on the test split of the dataset it was trained on (in-distribution). No label unification applied. All metrics use exact span matching.

## Summary

| Dataset   |   NER P |   NER R |   NER F1 |   RE P |   RE R |   RE F1 |   RE+ P |   RE+ R |   RE+ F1 |
|:----------|--------:|--------:|---------:|-------:|-------:|--------:|--------:|--------:|---------:|
| GSAP-ERE  |    83.9 |    82.3 |     83.1 |   59.3 |   51.7 |    55.3 |    51.6 |    45   |     48.1 |
| SCIER     |    89.4 |    87.5 |     88.4 |   70.6 |   62.2 |    66.2 |    69.4 |    61.1 |     65   |
| SCINLP    |    86.4 |    78.7 |     82.4 |   55.8 |   40.8 |    47.2 |    55.8 |    40.8 |     47.2 |

## Comparison with Paper-Reported Results

| Dataset   | Metric   |   Reproduced F1 |   Reported F1 |   Δ (repro − paper) |
|:----------|:---------|----------------:|--------------:|--------------------:|
| GSAP-ERE  | NER      |            83.1 |         80.6  |                2.5  |
| GSAP-ERE  | RE       |            55.3 |         54    |                1.3  |
| GSAP-ERE  | RE+      |            48.1 |         46.9  |                1.2  |
| SCIER     | NER      |            88.4 |         86.85 |                1.55 |
| SCIER     | RE       |            66.2 |         62.32 |                3.88 |
| SCIER     | RE+      |            65   |         61.1  |                3.9  |
| SCINLP    | NER      |            82.4 |         79.53 |                2.87 |
| SCINLP    | RE       |            47.2 |         49.28 |               -2.08 |
| SCINLP    | RE+      |            47.2 |         47.64 |               -0.44 |

## GSAP-ERE

### NER (exact match)

| Label             |     P |    R |   F1 |
|:------------------|------:|-----:|-----:|
| DataSource        |  62.4 | 77.9 | 69.3 |
| Dataset           |  85.8 | 93.2 | 89.4 |
| DatasetGeneric    |  89   | 83.7 | 86.3 |
| MLModel           |  55.7 | 87.3 | 68   |
| MLModelGeneric    |  89.7 | 80.3 | 84.8 |
| Method            |  77.9 | 77.1 | 77.5 |
| ModelArchitecture |  80.1 | 60.1 | 68.7 |
| ReferenceLink     |  99.5 | 99.6 | 99.5 |
| Task              |  88.7 | 79.3 | 83.7 |
| URL               | 100   | 45.5 | 62.5 |
| micro             |  83.9 | 82.3 | 83.1 |
| macro             |  82.9 | 78.4 | 79   |
| weighted          |  84.9 | 82.3 | 83.2 |

### RE (relaxed match)

| Label           |     P |    R |   F1 |
|:----------------|------:|-----:|-----:|
| weighted        |  59.1 | 51.7 | 54.7 |
| micro           |  59.3 | 51.7 | 55.3 |
| macro           |  56.6 | 46.9 | 50.7 |
| benchmarkFor    |  49.3 | 59.7 | 54   |
| appliedTo       |  59.2 | 49   | 53.7 |
| url             | 100   | 66.7 | 80   |
| citation        |  71.9 | 66   | 68.8 |
| isPartOf        |  44.3 | 36.2 | 39.8 |
| isHyponymOf     |  61.3 | 35.1 | 44.6 |
| isComparedTo    |  71   | 56.9 | 63.2 |
| coreference     |  62.2 | 63.9 | 63   |
| usedFor         |  52.8 | 49.5 | 51.1 |
| isBasedOn       |  38.4 | 35   | 36.6 |
| architecture    |  72.5 | 51.4 | 60.1 |
| trainedOn       |  56   | 51.7 | 53.8 |
| evaluatedOn     |  59.3 | 63.5 | 61.3 |
| transformedFrom |  42   | 19.3 | 26.5 |
| sourcedFrom     |  55.3 | 45.6 | 50   |
| generatedBy     |  35.7 | 30.9 | 33.1 |
| size            |  43.8 | 38.9 | 41.2 |
| hasInstanceType |  43.3 | 25   | 31.7 |

### RE+ (strict match)

| Label           |     P |    R |   F1 |
|:----------------|------:|-----:|-----:|
| weighted        |  51.5 | 45   | 47.6 |
| micro           |  51.6 | 45   | 48.1 |
| macro           |  51.3 | 42.4 | 45.9 |
| benchmarkFor    |  48   | 58.1 | 52.6 |
| appliedTo       |  48.5 | 40.1 | 43.9 |
| url             | 100   | 66.7 | 80   |
| citation        |  61.6 | 56.6 | 59   |
| isPartOf        |  38.3 | 31.2 | 34.4 |
| isHyponymOf     |  53.8 | 30.8 | 39.1 |
| isComparedTo    |  55.9 | 44.8 | 49.7 |
| coreference     |  50   | 51.4 | 50.7 |
| usedFor         |  45.7 | 42.8 | 44.2 |
| isBasedOn       |  38.4 | 35   | 36.6 |
| architecture    |  65.7 | 46.6 | 54.5 |
| trainedOn       |  51.4 | 47.4 | 49.3 |
| evaluatedOn     |  53.1 | 56.8 | 54.9 |
| transformedFrom |  40.6 | 18.7 | 25.6 |
| sourcedFrom     |  51.1 | 42.1 | 46.2 |
| generatedBy     |  34.3 | 29.6 | 31.8 |
| size            |  43.8 | 38.9 | 41.2 |
| hasInstanceType |  43.3 | 25   | 31.7 |

## SCIER

### NER (exact match)

| Label    |    P |    R |   F1 |
|:---------|-----:|-----:|-----:|
| Dataset  | 87   | 88.6 | 87.8 |
| Method   | 90.2 | 87.6 | 88.9 |
| Task     | 88.3 | 86.8 | 87.5 |
| micro    | 89.4 | 87.5 | 88.4 |
| macro    | 88.5 | 87.7 | 88.1 |
| weighted | 89.4 | 87.5 | 88.4 |

### RE (relaxed match)

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 70.2 | 62.2 | 65.7 |
| micro          | 70.6 | 62.2 | 66.2 |
| macro          | 72.6 | 63.6 | 67.6 |
| Used-For       | 69.1 | 67   | 68   |
| Trained-With   | 73.1 | 54.3 | 62.3 |
| Synonym-Of     | 91.1 | 84.7 | 87.8 |
| SubTask-Of     | 75   | 73.8 | 74.4 |
| SubClass-Of    | 61.4 | 59.7 | 60.5 |
| Part-Of        | 60   | 39.5 | 47.6 |
| Evaluated-With | 75.7 | 61.8 | 68.1 |
| Compare-With   | 65.7 | 58.8 | 62   |
| Benchmark-For  | 82.7 | 72.9 | 77.5 |

### RE+ (strict match)

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 69   | 61.1 | 64.5 |
| micro          | 69.4 | 61.1 | 65   |
| macro          | 71.9 | 62.9 | 66.8 |
| Used-For       | 66.6 | 64.7 | 65.6 |
| Trained-With   | 73.1 | 54.3 | 62.3 |
| Synonym-Of     | 89.9 | 83.5 | 86.6 |
| SubTask-Of     | 75   | 73.8 | 74.4 |
| SubClass-Of    | 61.4 | 59.7 | 60.5 |
| Part-Of        | 60   | 39.5 | 47.6 |
| Evaluated-With | 75.7 | 61.8 | 68.1 |
| Compare-With   | 63.7 | 57   | 60.2 |
| Benchmark-For  | 81.3 | 71.8 | 76.2 |

## SCINLP

### NER (exact match)

| Label    |    P |    R |   F1 |
|:---------|-----:|-----:|-----:|
| dataset  | 89.1 | 72.2 | 79.7 |
| method   | 88.5 | 80.4 | 84.2 |
| metric   | 82.7 | 87.8 | 85.1 |
| task     | 80.1 | 73.6 | 76.8 |
| micro    | 86.4 | 78.7 | 82.4 |
| macro    | 85.1 | 78.5 | 81.5 |
| weighted | 86.5 | 78.7 | 82.3 |

### RE (relaxed match)

| Label       |    P |    R |   F1 |
|:------------|-----:|-----:|-----:|
| weighted    | 63.4 | 40.8 | 46.7 |
| micro       | 55.8 | 40.8 | 47.2 |
| macro       | 60.2 | 40.4 | 46.4 |
| evaluatedOn | 63.6 | 43.8 | 51.9 |
| trainedWith | 50   | 36.4 | 42.1 |
| subtaskOf   | 90.9 | 66.7 | 76.9 |
| subclassOf  | 65   | 41.9 | 51   |
| similarWith | 20   | 16.7 | 18.2 |
| partOf      | 13.3 | 25   | 17.4 |
| evaluatedBy | 66.7 | 50   | 57.1 |
| enhancedBy  | 88.9 | 18.6 | 30.8 |
| compareWith | 70.8 | 32.7 | 44.7 |
| UsedFor     | 50   | 56.8 | 53.2 |
| MeasuredBy  | 83.3 | 55.6 | 66.7 |

### RE+ (strict match)

| Label       |    P |    R |   F1 |
|:------------|-----:|-----:|-----:|
| weighted    | 63.4 | 40.8 | 46.7 |
| micro       | 55.8 | 40.8 | 47.2 |
| macro       | 60.2 | 40.4 | 46.4 |
| evaluatedOn | 63.6 | 43.8 | 51.9 |
| trainedWith | 50   | 36.4 | 42.1 |
| subtaskOf   | 90.9 | 66.7 | 76.9 |
| subclassOf  | 65   | 41.9 | 51   |
| similarWith | 20   | 16.7 | 18.2 |
| partOf      | 13.3 | 25   | 17.4 |
| evaluatedBy | 66.7 | 50   | 57.1 |
| enhancedBy  | 88.9 | 18.6 | 30.8 |
| compareWith | 70.8 | 32.7 | 44.7 |
| UsedFor     | 50   | 56.8 | 53.2 |
| MeasuredBy  | 83.3 | 55.6 | 66.7 |
