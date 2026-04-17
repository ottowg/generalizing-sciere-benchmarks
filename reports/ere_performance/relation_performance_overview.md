# Relation Performance Overview (RE Partial)

- Metric: RE partial (relaxed partial match), F1
- Split: test
- Datasets: GSAP-ERE, SCIER, SCINLP

| Label              | Train→Test   | GSAP       | SciER      | SciNLP     |
|:-------------------|:-------------|:-----------|:-----------|:-----------|
| appliedTo          | GSAP-ERE     | **_59.3_** | 40.7       | 56.5       |
| appliedTo          | SCIER        | 32.1       | **_72.3_** | 50.0       |
| appliedTo          | SCINLP       | 35.6       | **56.7**   | _49.1_     |
| benchmarkFor       | GSAP-ERE     | _51.4_     | 35.8       | **56.0**   |
| benchmarkFor       | SCIER        | 29.4       | **_81.2_** | 9.5        |
| benchmarkFor       | SCINLP       | 40.0       | 30.9       | **_53.8_** |
| trainedEvaluatedOn | GSAP-ERE     | **_68.0_** | 30.2       | 40.0       |
| trainedEvaluatedOn | SCIER        | 48.7       | **_76.9_** | 25.8       |
| trainedEvaluatedOn | SCINLP       | 30.3       | 38.9       | **_50.0_** |
| coreference        | GSAP-ERE     | **_76.7_** | 65.1       | 46.2       |
| coreference        | SCIER        | 46.6       | **_93.0_** | 50.8       |
| coreference        | SCINLP       | 7.7        | 5.7        | **_34.5_** |
| isHyponymOf        | GSAP-ERE     | **_44.7_** | 34.5       | 30.2       |
| isHyponymOf        | SCIER        | 32.7       | **_70.2_** | 43.7       |
| isHyponymOf        | SCINLP       | 11.4       | 38.9       | **_54.4_** |
| isComparedTo       | GSAP-ERE     | **_68.0_** | 37.7       | 13.8       |
| isComparedTo       | SCIER        | 57.5       | **_69.4_** | 47.4       |
| isComparedTo       | SCINLP       | 52.3       | 46.2       | **_57.7_** |
| usedFor            | GSAP-ERE     | **_55.1_** | 28.7       | 3.5        |
| usedFor            | SCIER        | 22.5       | **_50.0_** | 0.0        |
| usedFor            | SCINLP       | 4.4        | 4.6        | **_31.2_** |
| micro              | GSAP-ERE     | **_61.3_** | 40.2       | 36.0       |
| micro              | SCIER        | 36.8       | **_71.2_** | 40.4       |
| micro              | SCINLP       | 21.3       | 38.9       | **_49.0_** |
