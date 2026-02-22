# Entity Performance Overview (Partial Match)

- Metric: entity partial match, F1
- Split: test
- Datasets: GSAP, SCIER, SCINLP

| Label   | Train→Test   | GSAP       | SciER      | SciNLP     |
|:--------|:-------------|:-----------|:-----------|:-----------|
| Dataset | GSAP         | **_85.4_** | 60.6       | 58.5       |
|         | SCIER        | 88.5       | **_91.0_** | 86.7       |
|         | SCINLP       | **82.9**   | 66.0       | _79.7_     |
| Method  | GSAP         | **_93.4_** | 73.3       | 69.3       |
|         | SCIER        | 88.6       | **_92.2_** | 85.4       |
|         | SCINLP       | 79.4       | 73.1       | **_93.0_** |
| Task    | GSAP         | **_82.8_** | 46.2       | 41.7       |
|         | SCIER        | 80.7       | **_87.8_** | 80.2       |
|         | SCINLP       | 82.5       | 77.5       | **_82.9_** |
| micro   | GSAP         | **_91.8_** | 67.6       | 64.3       |
|         | SCIER        | 86.9       | **_91.0_** | 84.4       |
|         | SCINLP       | 80.3       | 73.1       | **_89.3_** |
