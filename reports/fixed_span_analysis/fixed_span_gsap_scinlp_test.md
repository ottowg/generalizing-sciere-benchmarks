# Fixed-Span NER + RE — GSAP on SCINLP (test)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scinlp_test.jsonl`  
**Gold NER spans:** 745  
**NER overall accuracy:** 0.000

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| dataset |        11 |                9 |         1 |                0 |       58 |                   0 |      0 |
| method  |         2 |                5 |         4 |               32 |      421 |                   5 |      0 |
| metric  |         4 |                4 |         0 |                1 |       40 |                   0 |      0 |
| task    |         0 |                4 |         0 |                1 |      134 |                   0 |      9 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| dataset | 0.060 / 0.479 | 0.072 / 0.566    | 0.015 / 0.237 | —                | 0.021 / 0.574 | —                   | —             |
| method  | 0.046 / 0.275 | 0.050 / 0.661    | 0.144 / 0.469 | 0.017 / 0.516    | 0.032 / 0.722 | 0.028 / 0.396       | —             |
| metric  | 0.048 / 0.434 | 0.018 / 0.376    | —             | 0.001 / 0.638    | 0.073 / 0.747 | —                   | —             |
| task    | —             | 0.063 / 0.466    | —             | 0.038 / 0.606    | 0.023 / 0.676 | —                   | 0.074 / 0.539 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| method       |     469 |         0 |          0 |
| task         |     148 |         0 |          0 |
| dataset      |      79 |         0 |          0 |
| metric       |      49 |         0 |          0 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                     |   Freq |
|:-------------|:------------------|:---------------------------------|-------:|
| dataset      | Dataset           | WebNLG                           |      4 |
| dataset      | Dataset           | XSUM                             |      2 |
| dataset      | Dataset           | DART                             |      2 |
| dataset      | Dataset           | E2E                              |      1 |
| dataset      | Dataset           | WikiSQL                          |      1 |
| dataset      | DatasetGeneric    | XSUM                             |      2 |
| dataset      | DatasetGeneric    | WebNLG                           |      2 |
| dataset      | DatasetGeneric    | XSUM dataset                     |      2 |
| dataset      | DatasetGeneric    | E2E                              |      1 |
| dataset      | DatasetGeneric    | BBC news                         |      1 |
| dataset      | MLModel           | JRC-Acquis                       |      1 |
| dataset      | Method            | DJD                              |     10 |
| dataset      | Method            | Map Task                         |      7 |
| dataset      | Method            | DART                             |      6 |
| dataset      | Method            | E2E                              |      6 |
| dataset      | Method            | WebNLG                           |      4 |
| method       | Dataset           | Mixtral 8×7B                     |      1 |
| method       | Dataset           | Gemma 7B                         |      1 |
| method       | DatasetGeneric    | Large Language Models            |      2 |
| method       | DatasetGeneric    | E2E                              |      1 |
| method       | DatasetGeneric    | XSUM                             |      1 |
| method       | DatasetGeneric    | fine-tuning                      |      1 |
| method       | MLModel           | BERT                             |      1 |
| method       | MLModel           | RoBERTa                          |      1 |
| method       | MLModel           | AutoPrompt                       |      1 |
| method       | MLModel           | Llama 2 13B                      |      1 |
| method       | MLModelGeneric    | LM                               |      6 |
| method       | MLModelGeneric    | LMs                              |      3 |
| method       | MLModelGeneric    | large pretrained language models |      2 |
| method       | MLModelGeneric    | masked LMs                       |      2 |
| method       | MLModelGeneric    | RAG                              |      2 |
| method       | Method            | prefix-tuning                    |     51 |
| method       | Method            | M-RAG                            |     34 |
| method       | Method            | fine-tuning                      |     24 |
| method       | Method            | RAG                              |     18 |
| method       | Method            | LM                               |     15 |
| method       | ModelArchitecture | encoder-decoder architecture     |      1 |
| method       | ModelArchitecture | encoder-decoder framework        |      1 |
| method       | ModelArchitecture | MKDS                             |      1 |
| method       | ModelArchitecture | transformer attention mechanism  |      1 |
| method       | ModelArchitecture | RAGs                             |      1 |
| metric       | Dataset           | BLEU                             |      1 |
| metric       | Dataset           | CIDEr                            |      1 |
| metric       | Dataset           | BERTScore                        |      1 |
| metric       | Dataset           | BLEURT                           |      1 |
| metric       | DatasetGeneric    | BLEU                             |      2 |
| metric       | DatasetGeneric    | automatic generation metrics     |      1 |
| metric       | DatasetGeneric    | METEOR                           |      1 |
| metric       | MLModelGeneric    | B-1                              |      1 |
| metric       | Method            | BLEU                             |      7 |
| metric       | Method            | ROUGE                            |      4 |
| metric       | Method            | Distinct                         |      4 |
| metric       | Method            | ROUGE-L                          |      3 |
| metric       | Method            | ROUGE-1                          |      2 |
| task         | DatasetGeneric    | table-to-text                    |      3 |
| task         | DatasetGeneric    | generation                       |      1 |
| task         | MLModelGeneric    | Es→En translation                |      1 |
| task         | Method            | summarization                    |     30 |
| task         | Method            | table-to-text                    |     17 |
| task         | Method            | dialogue generation              |     15 |
| task         | Method            | machine translation              |     12 |
| task         | Method            | text summarization               |      8 |
| task         | Task              | language generation              |      4 |
| task         | Task              | table-to-text                    |      3 |
| task         | Task              | generation                       |      1 |
| task         | Task              | summarization                    |      1 |

## RE — Relation Confusion Matrix

*No predicted relations found in this file.*
