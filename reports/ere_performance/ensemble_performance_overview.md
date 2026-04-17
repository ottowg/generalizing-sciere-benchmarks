# Ensemble Performance Overview (Majority Vote, Partial Match)

**Generated:** 2026-02-26 16:35:28

- Metric: entity partial match, F1 (Precision)
- Method: majority vote across all three models (GSAP, SciER, SciNLP)
- Splits: dev, test
- Datasets: GSAP, SCIER, SCINLP

## Split: dev

| Label   | GSAP (dev)   | SciER (dev)     | SciNLP (dev)   | Unified (dev)   |
|:--------|:-------------|:----------------|:---------------|:----------------|
| Dataset | 73.4 (71.3)  | **86.3 (95.9)** | 85.7 (87.7)    | 78.2 (79.2)     |
| Method  | 76.6 (93.4)  | **94.0 (98.2)** | 85.0 (82.0)    | 83.5 (94.2)     |
| Task    | 61.2 (57.7)  | **83.0 (93.4)** | 77.3 (85.9)    | 73.8 (77.1)     |
| micro   | 74.6 (85.0)  | **91.1 (97.2)** | 83.4 (83.5)    | 81.4 (89.4)     |

## Split: test

| Label   | GSAP (test)   | SciER (test)    | SciNLP (test)   | Unified (test)   |
|:--------|:--------------|:----------------|:----------------|:-----------------|
| Dataset | 70.0 (59.7)   | **88.2 (95.6)** | 80.9 (91.9)     | 78.6 (75.4)      |
| Method  | 77.3 (96.4)   | 91.1 (97.6)     | **92.0 (93.2)** | 84.0 (96.5)      |
| Task    | 55.1 (45.7)   | 80.5 (94.2)     | **84.6 (90.1)** | 73.5 (75.8)      |
| micro   | 74.2 (83.5)   | 88.4 (96.6)     | **89.3 (92.5)** | 81.6 (90.0)      |
