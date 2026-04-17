# Baseline Results Report

**Generated:** 2026-04-04 22:49:27

This report replicates the baseline results from the original papers for each of the three datasets: GSAP, SciER, and SciNLP. Each model is evaluated on the test split of the same dataset it was trained on (in-distribution evaluation), matching the experimental setup described in the respective publications.

No label unification is applied. All metrics use exact span matching (no partial credit).

## Summary (micro-averaged, exact span match)

_Micro-averaged precision, recall, and F1 for NER (exact span match), RE (relaxed match), and RE+ (strict match) on the test split. Each model is evaluated on the dataset it was trained on._

| Dataset   |   NER P |   NER R |   NER F1 |   RE P |   RE R |   RE F1 |   RE+ P |   RE+ R |   RE+ F1 |
|:----------|--------:|--------:|---------:|-------:|-------:|--------:|--------:|--------:|---------:|
| GSAP      |    83.9 |    82.3 |     83.1 |   59.3 |   51.7 |    55.3 |    51.6 |    45   |     48.1 |
| SCIER     |    89.5 |    87.8 |     88.6 |   70.9 |   64.3 |    67.4 |    68.7 |    62.2 |     65.3 |
| SCINLP    |    89.2 |    85   |     87   |   65.3 |   37.8 |    47.8 |    63.5 |    36.7 |     46.6 |

## Comparison with Paper-Reported Results

_Difference between reproduced F1 scores and the micro-averaged F1 values reported in the original publications. Reported values are sourced from `data/reported_performance.json`. A positive Δ means the reproduction exceeds the paper result._

| Dataset   | Metric   |   Reproduced F1 |   Reported F1 |   Δ (repro − paper) |
|:----------|:---------|----------------:|--------------:|--------------------:|
| GSAP      | NER      |            83.1 |         80.6  |                2.5  |
| GSAP      | RE       |            55.3 |         54    |                1.3  |
| GSAP      | RE+      |            48.1 |         46.9  |                1.2  |
| SCIER     | NER      |            88.6 |         86.85 |                1.75 |
| SCIER     | RE       |            67.4 |         62.32 |                5.08 |
| SCIER     | RE+      |            65.3 |         61.1  |                4.2  |
| SCINLP    | NER      |            87   |         94.15 |               -7.15 |
| SCINLP    | RE       |            47.8 |         61.74 |              -13.94 |
| SCINLP    | RE+      |            46.6 |         60.76 |              -14.16 |

## GSAP

### NER (exact match)

_Per-label NER precision, recall, and F1 for the GSAP model on the GSAP test split. Exact span matching._

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

### RE (relaxed match, exact entities)

_Per-label RE precision, recall, and F1 for the GSAP model on the GSAP test split. Relation counted as correct if entity spans match exactly and relation label matches (entity label not required to match)._

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

### RE+ (strict match, exact entities)

_Per-label RE+ precision, recall, and F1 for the GSAP model on the GSAP test split. Relation counted as correct if entity spans and entity labels match exactly and relation label matches._

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

_Per-label NER precision, recall, and F1 for the SCIER model on the SCIER test split. Exact span matching._

| Label    |    P |    R |   F1 |
|:---------|-----:|-----:|-----:|
| Dataset  | 86.2 | 91.1 | 88.6 |
| Method   | 90.9 | 87.5 | 89.2 |
| Task     | 87.6 | 86.6 | 87.1 |
| micro    | 89.5 | 87.8 | 88.6 |
| macro    | 88.3 | 88.4 | 88.3 |
| weighted | 89.6 | 87.8 | 88.6 |

### RE (relaxed match, exact entities)

_Per-label RE precision, recall, and F1 for the SCIER model on the SCIER test split. Relation counted as correct if entity spans match exactly and relation label matches (entity label not required to match)._

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 70.1 | 64.3 | 66.7 |
| micro          | 70.9 | 64.3 | 67.4 |
| macro          | 72.5 | 66.2 | 69   |
| Used-For       | 68.7 | 70.3 | 69.5 |
| Trained-With   | 68.8 | 62.9 | 65.7 |
| Synonym-Of     | 91.4 | 87.6 | 89.5 |
| SubTask-Of     | 78.1 | 76.9 | 77.5 |
| SubClass-Of    | 67.5 | 64.8 | 66.1 |
| Part-Of        | 56.9 | 36.8 | 44.7 |
| Evaluated-With | 80.7 | 67.2 | 73.3 |
| Compare-With   | 64.3 | 55.3 | 59.4 |
| Benchmark-For  | 75.9 | 74.1 | 75   |

### RE+ (strict match, exact entities)

_Per-label RE+ precision, recall, and F1 for the SCIER model on the SCIER test split. Relation counted as correct if entity spans and entity labels match exactly and relation label matches._

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 68.1 | 62.2 | 64.7 |
| micro          | 68.7 | 62.2 | 65.3 |
| macro          | 70.9 | 64.7 | 67.5 |
| Used-For       | 64.6 | 66.1 | 65.3 |
| Trained-With   | 65.6 | 60   | 62.7 |
| Synonym-Of     | 87.7 | 84.1 | 85.9 |
| SubTask-Of     | 78.1 | 76.9 | 77.5 |
| SubClass-Of    | 66.9 | 64.2 | 65.5 |
| Part-Of        | 56.9 | 36.8 | 44.7 |
| Evaluated-With | 80.7 | 67.2 | 73.3 |
| Compare-With   | 63.3 | 54.4 | 58.5 |
| Benchmark-For  | 74.7 | 72.9 | 73.8 |

## SCINLP

### NER (exact match)

_Per-label NER precision, recall, and F1 for the SCINLP model on the SCINLP test split. Exact span matching._

| Label    |    P |    R |   F1 |
|:---------|-----:|-----:|-----:|
| dataset  | 87.5 | 70.9 | 78.3 |
| method   | 92.8 | 87.4 | 90   |
| metric   | 93.8 | 91.8 | 92.8 |
| task     | 78.2 | 82.4 | 80.3 |
| micro    | 89.2 | 85   | 87   |
| macro    | 88.1 | 83.1 | 85.3 |
| weighted | 89.4 | 85   | 87   |

### RE (relaxed match, exact entities)

_Per-label RE precision, recall, and F1 for the SCINLP model on the SCINLP test split. Relation counted as correct if entity spans match exactly and relation label matches (entity label not required to match)._

| Label       |     P |    R |   F1 |
|:------------|------:|-----:|-----:|
| weighted    |  73   | 37.8 | 46.8 |
| micro       |  65.3 | 37.8 | 47.8 |
| macro       |  72.4 | 36   | 45.9 |
| evaluatedOn |  70   | 43.8 | 53.8 |
| trainedWith |  60   | 27.3 | 37.5 |
| subtaskOf   | 100   | 26.7 | 42.1 |
| subclassOf  | 100   | 32.3 | 48.8 |
| similarWith |  30.8 | 22.2 | 25.8 |
| partOf      |  33.3 | 25   | 28.6 |
| evaluatedBy |  83.3 | 62.5 | 71.4 |
| enhancedBy  |  85.7 | 14   | 24   |
| compareWith |  80.6 | 48.1 | 60.2 |
| UsedFor     |  52.9 | 50   | 51.4 |
| MeasuredBy  | 100   | 44.4 | 61.5 |

### RE+ (strict match, exact entities)

_Per-label RE+ precision, recall, and F1 for the SCINLP model on the SCINLP test split. Relation counted as correct if entity spans and entity labels match exactly and relation label matches._

| Label       |     P |    R |   F1 |
|:------------|------:|-----:|-----:|
| weighted    |  71.6 | 36.7 | 45.6 |
| micro       |  63.5 | 36.7 | 46.6 |
| macro       |  71.3 | 35.2 | 45   |
| evaluatedOn |  70   | 43.8 | 53.8 |
| trainedWith |  60   | 27.3 | 37.5 |
| subtaskOf   | 100   | 26.7 | 42.1 |
| subclassOf  | 100   | 32.3 | 48.8 |
| similarWith |  23.1 | 16.7 | 19.4 |
| partOf      |  33.3 | 25   | 28.6 |
| evaluatedBy |  83.3 | 62.5 | 71.4 |
| enhancedBy  |  85.7 | 14   | 24   |
| compareWith |  77.4 | 46.2 | 57.8 |
| UsedFor     |  51.4 | 48.6 | 50   |
| MeasuredBy  | 100   | 44.4 | 61.5 |
