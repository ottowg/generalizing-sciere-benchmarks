# Baseline Results Report

**Generated:** 2026-02-26 17:20:32

This report replicates the baseline results from the original papers for each of the three datasets: GSAP, SciER, and SciNLP. Each model is evaluated on the test split of the same dataset it was trained on (in-distribution evaluation), matching the experimental setup described in the respective publications.

No label unification is applied. All metrics use exact span matching (no partial credit).

## Summary (micro-averaged, exact span match)

_Micro-averaged precision, recall, and F1 for NER (exact span match), RE (relaxed match), and RE+ (strict match) on the test split. Each model is evaluated on the dataset it was trained on._

| Dataset   |   NER P |   NER R |   NER F1 |   RE P |   RE R |   RE F1 |   RE+ P |   RE+ R |   RE+ F1 |
|:----------|--------:|--------:|---------:|-------:|-------:|--------:|--------:|--------:|---------:|
| GSAP      |    78.3 |    69.7 |     73.7 |   55.2 |   33.5 |    41.7 |    47.6 |    28.9 |     35.9 |
| SCIER     |    85.9 |    83.6 |     84.7 |   63.9 |   54.7 |    58.9 |    61.4 |    52.6 |     56.7 |
| SCINLP    |    89.2 |    85   |     87   |   65.3 |   37.8 |    47.8 |    63.5 |    36.7 |     46.6 |

## Comparison with Paper-Reported Results

_Difference between reproduced F1 scores and the micro-averaged F1 values reported in the original publications. Reported values are sourced from `data/reported_performance.json`. A positive Δ means the reproduction exceeds the paper result._

| Dataset   | Metric   |   Reproduced F1 |   Reported F1 |   Δ (repro − paper) |
|:----------|:---------|----------------:|--------------:|--------------------:|
| GSAP      | NER      |            73.7 |         80.6  |               -6.9  |
| GSAP      | RE       |            41.7 |         54    |              -12.3  |
| GSAP      | RE+      |            35.9 |         46.9  |              -11    |
| SCIER     | NER      |            84.7 |         86.85 |               -2.15 |
| SCIER     | RE       |            58.9 |         62.32 |               -3.42 |
| SCIER     | RE+      |            56.7 |         61.1  |               -4.4  |
| SCINLP    | NER      |            87   |         94.15 |               -7.15 |
| SCINLP    | RE       |            47.8 |         61.74 |              -13.94 |
| SCINLP    | RE+      |            46.6 |         60.76 |              -14.16 |

## GSAP

### NER (exact match)

_Per-label NER precision, recall, and F1 for the GSAP model on the GSAP test split. Exact span matching._

| Label             |     P |    R |   F1 |
|:------------------|------:|-----:|-----:|
| DataSource        |  68.3 | 63.2 | 65.6 |
| Dataset           |  86.9 | 85.8 | 86.4 |
| DatasetGeneric    |  82   | 67.2 | 73.8 |
| MLModel           |  54.4 | 83.8 | 66   |
| MLModelGeneric    |  83.3 | 61.4 | 70.7 |
| Method            |  66.8 | 61.8 | 64.2 |
| ModelArchitecture |  78.3 | 48.6 | 60   |
| ReferenceLink     |  99.5 | 98.8 | 99.2 |
| Task              |  83.8 | 73.7 | 78.4 |
| URL               | 100   | 81.8 | 90   |
| micro             |  78.3 | 69.7 | 73.7 |
| macro             |  80.3 | 72.6 | 75.4 |
| weighted          |  79.2 | 69.7 | 73.5 |

### RE (relaxed match, exact entities)

_Per-label RE precision, recall, and F1 for the GSAP model on the GSAP test split. Relation counted as correct if entity spans match exactly and relation label matches (entity label not required to match)._

| Label           |     P |    R |   F1 |
|:----------------|------:|-----:|-----:|
| weighted        |  53.6 | 33.5 | 40.3 |
| micro           |  55.2 | 33.5 | 41.7 |
| macro           |  53.6 | 30.1 | 37.7 |
| benchmarkFor    |  51.1 | 38.7 | 44   |
| appliedTo       |  61.3 | 46.5 | 52.9 |
| url             | 100   | 66.7 | 80   |
| citation        |  67   | 60   | 63.3 |
| isPartOf        |  57.5 | 22.3 | 32.2 |
| isHyponymOf     |  47.6 | 18.8 | 26.9 |
| isComparedTo    |  36   | 22.1 | 27.4 |
| coreference     |  36.4 | 24.2 | 29   |
| usedFor         |  48.4 | 29.2 | 36.4 |
| isBasedOn       |  42.5 | 21.2 | 28.3 |
| architecture    |  66.4 | 33.1 | 44.1 |
| trainedOn       |  58.2 | 30.3 | 39.9 |
| evaluatedOn     |  60.6 | 39   | 47.5 |
| transformedFrom |  40   |  6.7 | 11.4 |
| sourcedFrom     |  60   | 26.3 | 36.6 |
| generatedBy     |  33.3 | 14.8 | 20.5 |
| size            |  55   | 30.6 | 39.3 |
| hasInstanceType |  42.9 | 11.5 | 18.2 |

### RE+ (strict match, exact entities)

_Per-label RE+ precision, recall, and F1 for the GSAP model on the GSAP test split. Relation counted as correct if entity spans and entity labels match exactly and relation label matches._

| Label           |     P |    R |   F1 |
|:----------------|------:|-----:|-----:|
| weighted        |  46.5 | 28.9 | 34.8 |
| micro           |  47.6 | 28.9 | 35.9 |
| macro           |  48.6 | 27.1 | 34   |
| benchmarkFor    |  48.9 | 37.1 | 42.2 |
| appliedTo       |  47.9 | 36.3 | 41.3 |
| url             | 100   | 66.7 | 80   |
| citation        |  57.1 | 51.1 | 53.9 |
| isPartOf        |  54   | 21   | 30.2 |
| isHyponymOf     |  40.2 | 15.9 | 22.8 |
| isComparedTo    |  26.1 | 16   | 19.9 |
| coreference     |  30.4 | 20.2 | 24.3 |
| usedFor         |  41.2 | 24.9 | 31.1 |
| isBasedOn       |  42.5 | 21.2 | 28.3 |
| architecture    |  58.4 | 29.1 | 38.8 |
| trainedOn       |  50   | 26.1 | 34.3 |
| evaluatedOn     |  54.2 | 34.9 | 42.5 |
| transformedFrom |  36   |  6   | 10.3 |
| sourcedFrom     |  56   | 24.6 | 34.1 |
| generatedBy     |  33.3 | 14.8 | 20.5 |
| size            |  55   | 30.6 | 39.3 |
| hasInstanceType |  42.9 | 11.5 | 18.2 |

## SCIER

### NER (exact match)

_Per-label NER precision, recall, and F1 for the SCIER model on the SCIER test split. Exact span matching._

| Label    |    P |    R |   F1 |
|:---------|-----:|-----:|-----:|
| Dataset  | 81.2 | 90.8 | 85.7 |
| Method   | 87.3 | 82.3 | 84.7 |
| Task     | 84.9 | 83.1 | 84   |
| micro    | 85.9 | 83.6 | 84.7 |
| macro    | 84.4 | 85.4 | 84.8 |
| weighted | 86   | 83.6 | 84.7 |

### RE (relaxed match, exact entities)

_Per-label RE precision, recall, and F1 for the SCIER model on the SCIER test split. Relation counted as correct if entity spans match exactly and relation label matches (entity label not required to match)._

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 62.9 | 54.7 | 58.2 |
| micro          | 63.9 | 54.7 | 58.9 |
| macro          | 65.1 | 58   | 61.1 |
| Used-For       | 61.6 | 57.5 | 59.5 |
| Trained-With   | 60   | 60   | 60   |
| Synonym-Of     | 92.9 | 85.3 | 89   |
| SubTask-Of     | 72.4 | 64.6 | 68.3 |
| SubClass-Of    | 54.9 | 51.1 | 52.9 |
| Part-Of        | 49.7 | 28.6 | 36.3 |
| Evaluated-With | 70.5 | 60.3 | 65   |
| Compare-With   | 53.9 | 48.2 | 50.9 |
| Benchmark-For  | 70   | 65.9 | 67.9 |

### RE+ (strict match, exact entities)

_Per-label RE+ precision, recall, and F1 for the SCIER model on the SCIER test split. Relation counted as correct if entity spans and entity labels match exactly and relation label matches._

| Label          |    P |    R |   F1 |
|:---------------|-----:|-----:|-----:|
| weighted       | 60.7 | 52.6 | 56   |
| micro          | 61.4 | 52.6 | 56.7 |
| macro          | 63.1 | 56.1 | 59.2 |
| Used-For       | 57.5 | 53.7 | 55.5 |
| Trained-With   | 60   | 60   | 60   |
| Synonym-Of     | 91   | 83.5 | 87.1 |
| SubTask-Of     | 72.4 | 64.6 | 68.3 |
| SubClass-Of    | 54.9 | 51.1 | 52.9 |
| Part-Of        | 49.7 | 28.6 | 36.3 |
| Evaluated-With | 70.5 | 60.3 | 65   |
| Compare-With   | 52   | 46.5 | 49.1 |
| Benchmark-For  | 60   | 56.5 | 58.2 |

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
