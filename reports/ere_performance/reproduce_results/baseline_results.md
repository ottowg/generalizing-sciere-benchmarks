# Baseline Results Report

**Generated:** 2026-02-22 17:25:01

This report replicates the baseline results from the original papers for each of the three datasets: GSAP, SciER, and SciNLP. Each model is evaluated on the test split of the same dataset it was trained on (in-distribution evaluation), matching the experimental setup described in the respective publications.

No label unification is applied. All metrics use exact span matching (no partial credit).

## Summary (micro-averaged, exact span match)

_Micro-averaged precision, recall, and F1 for NER (exact span match), RE (relaxed match), and RE+ (strict match) on the test split. Each model is evaluated on the dataset it was trained on._

| Dataset   |   NER P |   NER R |   NER F1 |   RE P |   RE R |   RE F1 |   RE+ P |   RE+ R |   RE+ F1 |
|:----------|--------:|--------:|---------:|-------:|-------:|--------:|--------:|--------:|---------:|
| GSAP      |    80.9 |    78   |     79.4 |   53.7 |   43.5 |    48.1 |    46.1 |    37.4 |     41.3 |
| SCIER     |    85.9 |    83.6 |     84.7 |   63.9 |   54.7 |    58.9 |    61.4 |    52.6 |     56.7 |
| SCINLP    |    89.2 |    85   |     87   |   65.3 |   37.8 |    47.8 |    63.5 |    36.7 |     46.6 |

## Comparison with Paper-Reported Results

_Difference between reproduced F1 scores and the micro-averaged F1 values reported in the original publications. Reported values are sourced from `data/reported_performance.json`. A positive Δ means the reproduction exceeds the paper result._

| Dataset   | Metric   |   Reproduced F1 |   Reported F1 |   Δ (repro − paper) |
|:----------|:---------|----------------:|--------------:|--------------------:|
| GSAP      | NER      |            79.4 |         80.6  |               -1.2  |
| GSAP      | RE       |            48.1 |         54    |               -5.9  |
| GSAP      | RE+      |            41.3 |         46.9  |               -5.6  |
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
| DataSource        |  75   | 75   | 75   |
| Dataset           |  80.9 | 93.5 | 86.7 |
| DatasetGeneric    |  86.8 | 78.6 | 82.5 |
| MLModel           |  53.9 | 69.8 | 60.9 |
| MLModelGeneric    |  83.7 | 79.3 | 81.5 |
| Method            |  74   | 69.7 | 71.8 |
| ModelArchitecture |  71.9 | 57.4 | 63.8 |
| ReferenceLink     |  99.2 | 99.4 | 99.3 |
| Task              |  80.6 | 76.3 | 78.4 |
| URL               | 100   | 90.9 | 95.2 |
| micro             |  80.9 | 78   | 79.4 |
| macro             |  80.6 | 79   | 79.5 |
| weighted          |  81.2 | 78   | 79.4 |

### RE (relaxed match, exact entities)

_Per-label RE precision, recall, and F1 for the GSAP model on the GSAP test split. Relation counted as correct if entity spans match exactly and relation label matches (entity label not required to match)._

| Label           |    P |    R |   F1 |
|:----------------|-----:|-----:|-----:|
| weighted        | 54.1 | 43.5 | 47.8 |
| micro           | 53.7 | 43.5 | 48.1 |
| macro           | 52.5 | 40.1 | 44.5 |
| benchmarkFor    | 63.5 | 53.2 | 57.9 |
| appliedTo       | 59.6 | 43.3 | 50.2 |
| url             | 66.7 | 66.7 | 66.7 |
| citation        | 72   | 62.8 | 67.1 |
| isPartOf        | 45   | 34.4 | 39   |
| isHyponymOf     | 53.9 | 29.8 | 38.4 |
| isComparedTo    | 36.5 | 29.8 | 32.8 |
| coreference     | 31   | 30   | 30.5 |
| usedFor         | 54.6 | 43.2 | 48.2 |
| isBasedOn       | 30.9 | 26.2 | 28.4 |
| architecture    | 61.5 | 44.6 | 51.7 |
| trainedOn       | 50.8 | 52.1 | 51.5 |
| evaluatedOn     | 61.3 | 51.7 | 56.1 |
| transformedFrom | 33   | 25.3 | 28.7 |
| sourcedFrom     | 65.9 | 47.4 | 55.1 |
| generatedBy     | 44.4 | 34.6 | 38.9 |
| size            | 40.7 | 30.6 | 34.9 |
| hasInstanceType | 72.7 | 15.4 | 25.4 |

### RE+ (strict match, exact entities)

_Per-label RE+ precision, recall, and F1 for the GSAP model on the GSAP test split. Relation counted as correct if entity spans and entity labels match exactly and relation label matches._

| Label           |    P |    R |   F1 |
|:----------------|-----:|-----:|-----:|
| weighted        | 46.6 | 37.4 | 41.2 |
| micro           | 46.1 | 37.4 | 41.3 |
| macro           | 47.6 | 36.2 | 40.2 |
| benchmarkFor    | 63.5 | 53.2 | 57.9 |
| appliedTo       | 50.9 | 36.9 | 42.8 |
| url             | 66.7 | 66.7 | 66.7 |
| citation        | 61.2 | 53.3 | 57   |
| isPartOf        | 39.8 | 30.4 | 34.4 |
| isHyponymOf     | 39.1 | 21.6 | 27.9 |
| isComparedTo    | 27.7 | 22.7 | 24.9 |
| coreference     | 22.2 | 21.4 | 21.8 |
| usedFor         | 46.5 | 36.7 | 41   |
| isBasedOn       | 29.4 | 25   | 27   |
| architecture    | 59.3 | 43   | 49.9 |
| trainedOn       | 45.8 | 47   | 46.4 |
| evaluatedOn     | 51.1 | 43.2 | 46.8 |
| transformedFrom | 33   | 25.3 | 28.7 |
| sourcedFrom     | 63.4 | 45.6 | 53.1 |
| generatedBy     | 42.9 | 33.3 | 37.5 |
| size            | 40.7 | 30.6 | 34.9 |
| hasInstanceType | 72.7 | 15.4 | 25.4 |

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
