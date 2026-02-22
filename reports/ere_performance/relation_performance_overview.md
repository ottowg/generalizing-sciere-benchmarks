# Relation Performance Overview (RE Partial)

- Metric: RE partial (relaxed partial match), F1
- Split: test
- Datasets: GSAP, SCIER, SCINLP

| Label              | Train→Test   | GSAP       | SciER      | SciNLP     |
|:-------------------|:-------------|:-----------|:-----------|:-----------|
| appliedTo          | GSAP         | **_60.2_** | 39.5       | 33.2       |
| benchmarkFor       | GSAP         | **_64.5_** | 30.8       | 21.6       |
| trainedEvaluatedOn | GSAP         | **_66.9_** | 42.1       | 34.4       |
| coreference        | GSAP         | **_79.1_** | 51.6       | 22.4       |
| isHyponymOf        | GSAP         | **_44.9_** | 30.7       | 4.1        |
| isComparedTo       | GSAP         | **_63.8_** | 57.8       | 47.1       |
| usedFor            | GSAP         | **_54.5_** | 18.2       | 2.7        |
| micro              | GSAP         | **_60.6_** | 36.2       | 19.4       |
| appliedTo          | SCIER        | 45.1       | **_66.4_** | 39.9       |
| benchmarkFor       | SCIER        | 31.8       | **_81.2_** | 33.0       |
| trainedEvaluatedOn | SCIER        | 34.1       | **_78.6_** | 34.9       |
| coreference        | SCIER        | 64.6       | **_92.6_** | 36.4       |
| isHyponymOf        | SCIER        | 44.9       | **_68.4_** | 20.3       |
| isComparedTo       | SCIER        | 44.6       | **_62.0_** | 47.7       |
| usedFor            | SCIER        | 30.6       | **_43.8_** | 3.7        |
| micro              | SCIER        | 43.6       | **_67.7_** | 30.8       |
| appliedTo          | SCINLP       | **65.6**   | 50.3       | _56.1_     |
| benchmarkFor       | SCINLP       | **61.5**   | 60.6       | _53.8_     |
| trainedEvaluatedOn | SCINLP       | 14.3       | 31.2       | **_37.5_** |
| coreference        | SCINLP       | 43.5       | **45.9**   | _25.8_     |
| isHyponymOf        | SCINLP       | 29.9       | **47.3**   | _43.2_     |
| isComparedTo       | SCINLP       | **72.1**   | 58.4       | _60.2_     |
| usedFor            | SCINLP       | **32.2**   | 26.0       | _25.5_     |
| micro              | SCINLP       | **48.9**   | 46.9       | _47.6_     |
