# Fixed-Span NER + RE — GSAP on SCINLP (pruner_augmented_test)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scinlp_pruner_augmented_test.json`  
**Gold NER spans:** 745  
**NER overall accuracy:** 0.000

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| dataset |        11 |               14 |         1 |                0 |       53 |                   0 |      0 |
| method  |         1 |               10 |         4 |               30 |      414 |                  10 |      0 |
| metric  |         4 |                4 |         0 |                1 |       40 |                   0 |      0 |
| task    |         0 |                7 |         0 |                1 |      125 |                   0 |     15 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| dataset | 0.848 / 0.468 | 0.763 / 0.636    | 0.937 / 0.237 | —                | 0.898 / 0.593 | —                   | —             |
| method  | 0.720 / 0.328 | 0.822 / 0.569    | 0.689 / 0.421 | 0.853 / 0.538    | 0.865 / 0.737 | 0.811 / 0.503       | —             |
| metric  | 0.744 / 0.386 | 0.721 / 0.492    | —             | 0.999 / 0.638    | 0.852 / 0.739 | —                   | —             |
| task    | —             | 0.892 / 0.539    | —             | 0.938 / 0.606    | 0.925 / 0.676 | —                   | 0.695 / 0.518 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| method       |     469 |         0 |          0 |
| task         |     148 |         0 |          0 |
| dataset      |      79 |         0 |          0 |
| metric       |      49 |         0 |          0 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                                     |   Freq |
|:-------------|:------------------|:-------------------------------------------------|-------:|
| dataset      | Dataset           | WebNLG                                           |      5 |
| dataset      | Dataset           | E2E                                              |      2 |
| dataset      | Dataset           | DART                                             |      2 |
| dataset      | Dataset           | XSUM                                             |      1 |
| dataset      | Dataset           | WikiSQL                                          |      1 |
| dataset      | DatasetGeneric    | WebNLG                                           |      3 |
| dataset      | DatasetGeneric    | XSUM                                             |      3 |
| dataset      | DatasetGeneric    | XSUM dataset                                     |      2 |
| dataset      | DatasetGeneric    | E2E dataset                                      |      2 |
| dataset      | DatasetGeneric    | Map Task                                         |      2 |
| dataset      | MLModel           | JRC-Acquis                                       |      1 |
| dataset      | Method            | DJD                                              |     10 |
| dataset      | Method            | DART                                             |      6 |
| dataset      | Method            | E2E                                              |      5 |
| dataset      | Method            | Map Task                                         |      5 |
| dataset      | Method            | XSum                                             |      4 |
| method       | Dataset           | Gemma 7B                                         |      1 |
| method       | DatasetGeneric    | LM                                               |      2 |
| method       | DatasetGeneric    | Large Language Models                            |      2 |
| method       | DatasetGeneric    | BART                                             |      1 |
| method       | DatasetGeneric    | E2E                                              |      1 |
| method       | DatasetGeneric    | XSUM                                             |      1 |
| method       | MLModel           | BERT                                             |      1 |
| method       | MLModel           | RoBERTa                                          |      1 |
| method       | MLModel           | AutoPrompt                                       |      1 |
| method       | MLModel           | Llama 2 13B                                      |      1 |
| method       | MLModelGeneric    | LMs                                              |      4 |
| method       | MLModelGeneric    | LM                                               |      4 |
| method       | MLModelGeneric    | large pretrained language models                 |      2 |
| method       | MLModelGeneric    | masked LMs                                       |      2 |
| method       | MLModelGeneric    | LLMs                                             |      2 |
| method       | Method            | prefix-tuning                                    |     51 |
| method       | Method            | M-RAG                                            |     34 |
| method       | Method            | fine-tuning                                      |     24 |
| method       | Method            | RAG                                              |     19 |
| method       | Method            | LLMs                                             |     15 |
| method       | ModelArchitecture | encoder-decoder architecture                     |      1 |
| method       | ModelArchitecture | feedforward neural network                       |      1 |
| method       | ModelArchitecture | Transformer                                      |      1 |
| method       | ModelArchitecture | language models                                  |      1 |
| method       | ModelArchitecture | LM                                               |      1 |
| metric       | Dataset           | BLEU                                             |      1 |
| metric       | Dataset           | CIDEr                                            |      1 |
| metric       | Dataset           | BERTScore                                        |      1 |
| metric       | Dataset           | BLEURT                                           |      1 |
| metric       | DatasetGeneric    | BLEU                                             |      2 |
| metric       | DatasetGeneric    | automatic generation metrics                     |      1 |
| metric       | DatasetGeneric    | METEOR                                           |      1 |
| metric       | MLModelGeneric    | B-1                                              |      1 |
| metric       | Method            | BLEU                                             |      7 |
| metric       | Method            | ROUGE                                            |      4 |
| metric       | Method            | Distinct                                         |      4 |
| metric       | Method            | ROUGE-L                                          |      3 |
| metric       | Method            | ROUGE-1                                          |      2 |
| task         | DatasetGeneric    | table-to-text                                    |      3 |
| task         | DatasetGeneric    | summarization                                    |      2 |
| task         | DatasetGeneric    | generating a textual description of a data table |      1 |
| task         | DatasetGeneric    | vector database management                       |      1 |
| task         | MLModelGeneric    | Es→En translation                                |      1 |
| task         | Method            | summarization                                    |     26 |
| task         | Method            | table-to-text                                    |     17 |
| task         | Method            | dialogue generation                              |     15 |
| task         | Method            | machine translation                              |     12 |
| task         | Method            | text summarization                               |      8 |
| task         | Task              | language generation                              |      4 |
| task         | Task              | table-to-text                                    |      3 |
| task         | Task              | summarization                                    |      3 |
| task         | Task              | generation                                       |      2 |
| task         | Task              | natural language generation ( NLG )              |      1 |

## RE — Relation Confusion Matrix

*No predicted relations found in this file.*
