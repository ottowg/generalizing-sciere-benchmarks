# Relation Extraction Performance Report

_Unified and vanilla (comparison)_

## GSAP→GSAP (test)

### Unified

- Filtered gold relations (missing mentions): 0
- Filtered predicted relations (missing mentions): 0
- Missing gold relations (unmatched spans): 0
- Missing predicted relations (unmatched spans): 0

Metrics: F1, Precision, Recall

| group         | label              | gold_relations   | pred_relations   |   f1_score |   precision |   recall |
|:--------------|:-------------------|:-----------------|:-----------------|-----------:|------------:|---------:|
| _average      | weighted           |                  |                  |     0.6016 |      0.6743 |   0.5462 |
| _average      | micro              |                  |                  |     0.6062 |      0.6809 |   0.5462 |
| _average      | macro              |                  |                  |     0.6201 |      0.6960 |   0.5628 |
| Task Binding  | benchmarkFor       | 17.0             | 14.0             |     0.6452 |      0.7143 |   0.5882 |
| Task Binding  | appliedTo          | 126.0            | 90.0             |     0.6019 |      0.7222 |   0.5159 |
| Peer Relating | isHyponymOf        | 170.0            | 106.0            |     0.4493 |      0.5849 |   0.3647 |
| Peer Relating | isComparedTo       | 154.0            | 126.0            |     0.6380 |      0.7063 |   0.5817 |
| Peer Relating | coreference        | 243.0            | 227.0            |     0.7915 |      0.8194 |   0.7654 |
| Model Design  | usedFor            | 626.0            | 496.0            |     0.5455 |      0.6169 |   0.4888 |
|               | trainedEvaluatedOn | 126.0            | 113.0            |     0.6695 |      0.7080 |   0.6349 |

### Ambiguity Summary (Gold Relations, Unified)

| selected_label   | not_selected_label   | relation_label   | role   | count   |
|------------------|----------------------|------------------|--------|---------|

### Ambiguity Summary (Predicted Relations, Unified)

| selected_label   | not_selected_label   | relation_label   | role   | count   |
|------------------|----------------------|------------------|--------|---------|

### Vanilla

- Filtered gold relations (missing mentions): 0
- Filtered predicted relations (missing mentions): 13
- Missing gold relations (unmatched spans): 0
- Missing predicted relations (unmatched spans): 32

Metrics: F1, Precision, Recall

| group           | label           | gold_relations   | pred_relations   |   f1_score |   precision |   recall |
|:----------------|:----------------|:-----------------|:-----------------|-----------:|------------:|---------:|
| _average        | weighted        |                  |                  |     0.5335 |      0.6020 |   0.4854 |
| _average        | micro           |                  |                  |     0.5360 |      0.5984 |   0.4854 |
| _average        | macro           |                  |                  |     0.5140 |      0.6004 |   0.4640 |
| Task Binding    | benchmarkFor    | 62.0             | 52.0             |     0.6140 |      0.6731 |   0.5645 |
| Task Binding    | appliedTo       | 157.0            | 114.0            |     0.6052 |      0.7193 |   0.5223 |
| Referencing     | url             | 3.0              | 3.0              |     1.0000 |      1.0000 |   1.0000 |
| Referencing     | citation        | 677.0            | 590.0            |     0.7656 |      0.8220 |   0.7164 |
| Peer Relating   | isPartOf        | 224.0            | 171.0            |     0.4608 |      0.5322 |   0.4062 |
| Peer Relating   | isHyponymOf     | 208.0            | 115.0            |     0.3963 |      0.5565 |   0.3077 |
| Peer Relating   | isComparedTo    | 181.0            | 148.0            |     0.3526 |      0.3919 |   0.3204 |
| Peer Relating   | coreference     | 327.0            | 316.0            |     0.3204 |      0.3259 |   0.3150 |
| Model Design    | usedFor         | 558.0            | 441.0            |     0.5305 |      0.6009 |   0.4749 |
| Model Design    | isBasedOn       | 80.0             | 68.0             |     0.3108 |      0.3382 |   0.2875 |
| Model Design    | architecture    | 251.0            | 182.0            |     0.5774 |      0.6868 |   0.4980 |
| Data Usage      | trainedOn       | 234.0            | 240.0            |     0.5570 |      0.5500 |   0.5641 |
| Data Usage      | evaluatedOn     | 315.0            | 266.0            |     0.6196 |      0.6767 |   0.5714 |
| Data Provenance | transformedFrom | 150.0            | 115.0            |     0.3094 |      0.3565 |   0.2733 |
| Data Provenance | sourcedFrom     | 57.0             | 41.0             |     0.6531 |      0.7805 |   0.5614 |
| Data Provenance | generatedBy     | 81.0             | 63.0             |     0.4167 |      0.4762 |   0.3704 |
| Data Properties | size            | 36.0             | 27.0             |     0.5079 |      0.5926 |   0.4444 |
| Data Properties | hasInstanceType | 52.0             | 11.0             |     0.2540 |      0.7273 |   0.1538 |

### Ambiguity Summary (Gold Relations, Vanilla)

| selected_label    | not_selected_label   | relation_label   | role    |   count |
|:------------------|:---------------------|:-----------------|:--------|--------:|
| ModelArchitecture | MLModelGeneric       | architecture     | object  |      48 |
| MLModelGeneric    | ModelArchitecture    | architecture     | subject |      47 |
| MLModelGeneric    | Method               | usedFor          | object  |      35 |
| Method            | MLModelGeneric       | usedFor          | subject |      31 |
| MLModelGeneric    | ModelArchitecture    | usedFor          | object  |      12 |
| DataSource        | DatasetGeneric       | sourcedFrom      | object  |       9 |
| DatasetGeneric    | DataSource           | sourcedFrom      | subject |       9 |
| MLModelGeneric    | Method               | isComparedTo     | subject |       9 |
| MLModelGeneric    | Method               | evaluatedOn      | subject |       7 |
| MLModelGeneric    | Method               | trainedOn        | subject |       7 |
| MLModelGeneric    | ModelArchitecture    | coreference      | subject |       7 |
| MLModelGeneric    | ModelArchitecture    | trainedOn        | subject |       7 |
| DataSource        | DatasetGeneric       | trainedOn        | object  |       6 |
| MLModelGeneric    | Method               | isComparedTo     | object  |       6 |
| MLModelGeneric    | ModelArchitecture    | appliedTo        | subject |       6 |
| MLModelGeneric    | ModelArchitecture    | evaluatedOn      | subject |       6 |
| MLModelGeneric    | Method               | citation         | subject |       5 |
| MLModelGeneric    | ModelArchitecture    | coreference      | object  |       5 |
| MLModelGeneric    | ModelArchitecture    | isHyponymOf      | subject |       5 |
| MLModelGeneric    | ModelArchitecture    | citation         | subject |       3 |
| MLModelGeneric    | ModelArchitecture    | isBasedOn        | object  |       3 |
| MLModelGeneric    | ModelArchitecture    | isComparedTo     | subject |       3 |
| MLModelGeneric    | ModelArchitecture    | isBasedOn        | subject |       2 |
| MLModelGeneric    | ModelArchitecture    | isPartOf         | subject |       2 |
| DataSource        | DatasetGeneric       | coreference      | object  |       1 |
| DataSource        | DatasetGeneric       | coreference      | subject |       1 |
| DataSource        | DatasetGeneric       | generatedBy      | subject |       1 |
| DataSource        | DatasetGeneric       | isPartOf         | object  |       1 |
| DataSource        | DatasetGeneric       | transformedFrom  | object  |       1 |
| MLModel           | ModelArchitecture    | isBasedOn        | object  |       1 |
| MLModelGeneric    | Method               | coreference      | subject |       1 |
| MLModelGeneric    | Method               | isHyponymOf      | object  |       1 |
| MLModelGeneric    | ModelArchitecture    | isComparedTo     | object  |       1 |
| MLModelGeneric    | ModelArchitecture    | isHyponymOf      | object  |       1 |

### Ambiguity Summary (Predicted Relations, Vanilla)

| selected_label   | not_selected_label   | relation_label   | role   | count   |
|------------------|----------------------|------------------|--------|---------|

### F1 Comparison (Unified vs Vanilla)

| relation_group   | relation_label     |   Unified F1 |   Vanilla F1 |   Delta (Unified - Vanilla) |
|:-----------------|:-------------------|-------------:|-------------:|----------------------------:|
| Data Properties  | hasInstanceType    |     nan      |       0.2540 |                    nan      |
| Data Properties  | size               |     nan      |       0.5079 |                    nan      |
| Data Provenance  | generatedBy        |     nan      |       0.4167 |                    nan      |
| Data Provenance  | sourcedFrom        |     nan      |       0.6531 |                    nan      |
| Data Provenance  | transformedFrom    |     nan      |       0.3094 |                    nan      |
| Data Usage       | evaluatedOn        |     nan      |       0.6196 |                    nan      |
| Data Usage       | trainedOn          |     nan      |       0.5570 |                    nan      |
| Model Design     | architecture       |     nan      |       0.5774 |                    nan      |
| Model Design     | isBasedOn          |     nan      |       0.3108 |                    nan      |
| Model Design     | usedFor            |       0.5455 |       0.5305 |                      0.0149 |
| Peer Relating    | coreference        |       0.7915 |       0.3204 |                      0.4711 |
| Peer Relating    | isComparedTo       |       0.6380 |       0.3526 |                      0.2854 |
| Peer Relating    | isHyponymOf        |       0.4493 |       0.3963 |                      0.0530 |
| Peer Relating    | isPartOf           |     nan      |       0.4608 |                    nan      |
| Referencing      | citation           |     nan      |       0.7656 |                    nan      |
| Referencing      | url                |     nan      |       1.0000 |                    nan      |
| Task Binding     | appliedTo          |       0.6019 |       0.6052 |                     -0.0033 |
| Task Binding     | benchmarkFor       |       0.6452 |       0.6140 |                      0.0311 |
| _average         | macro              |       0.6201 |       0.5140 |                      0.1061 |
| _average         | micro              |       0.6062 |       0.5360 |                      0.0702 |
| _average         | weighted           |       0.6016 |       0.5335 |                      0.0681 |
|                  | trainedEvaluatedOn |       0.6695 |     nan      |                    nan      |
