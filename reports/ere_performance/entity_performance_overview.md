# Entity Performance Overview (Partial Match)

**Generated:** 2026-04-09 11:24:39

- Metric: entity partial match, F1
- Splits: dev, test
- Datasets: GSAP-ERE, SCIER, SCINLP

## Split: dev

| Label   | Train Data   | GSAP (dev)   | SciER (dev)   | SciNLP (dev)   |   Unified (dev) |
|:--------|:-------------|:-------------|:--------------|:---------------|----------------:|
| Dataset | GSAP-ERE     | _83.2_       | **93.4**      | 76.1           |            85.8 |
|         | SCIER        | 60.0         | **_94.3_**    | 72.0           |            70.1 |
|         | SCINLP       | 63.0         | 64.9          | **_81.3_**     |            64.9 |
| Method  | GSAP-ERE     | **_92.8_**   | 92.3          | 59.5           |            89.5 |
|         | SCIER        | 65.4         | **_96.6_**    | 65.8           |            76.7 |
|         | SCINLP       | 60.4         | **84.5**      | _83.1_         |            71.1 |
| Task    | GSAP-ERE     | _75.8_       | **88.7**      | 64.9           |            80.7 |
|         | SCIER        | 45.4         | **_93.9_**    | 65.2           |            67.2 |
|         | SCINLP       | 55.6         | 78.1          | **_83.5_**     |            69.5 |
| micro   | GSAP-ERE     | _89.8_       | **91.8**      | 62.7           |            87.8 |
|         | SCIER        | 61.5         | **_95.8_**    | 66.6           |            74   |
|         | SCINLP       | 60.3         | 81.2          | **_83.0_**     |            70   |

## Split: test

| Label   | Train Data   | GSAP (test)   | SciER (test)   | SciNLP (test)   |   Unified (test) |
|:--------|:-------------|:--------------|:---------------|:----------------|-----------------:|
| Dataset | GSAP-ERE     | _89.2_        | **89.3**       | 83.4            |             88.7 |
|         | SCIER        | 57.5          | **_92.2_**     | 65.5            |             71.7 |
|         | SCINLP       | 56.0          | 74.0           | **_74.8_**      |             65.2 |
| Method  | GSAP-ERE     | **_94.8_**    | 87.2           | 64.7            |             89.1 |
|         | SCIER        | 74.8          | **_94.0_**     | 78.3            |             82.5 |
|         | SCINLP       | 63.3          | 86.2           | **_86.8_**      |             74.6 |
| Task    | GSAP-ERE     | _85.0_        | 83.4           | **87.6**        |             84.4 |
|         | SCIER        | 44.0          | **_89.9_**     | 79.5            |             71.5 |
|         | SCINLP       | 47.3          | **81.0**       | _76.9_          |             68.8 |
| micro   | GSAP-ERE     | **_93.5_**    | 86.6           | 71.8            |             88.4 |
|         | SCIER        | 67.9          | **_92.8_**     | 77.1            |             79   |
|         | SCINLP       | 60.3          | **83.6**       | _83.5_          |             72.5 |
