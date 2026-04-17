# Fixed-Span NER + RE — GSAP on SCINLP (pruner_augmented_dev)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scinlp_pruner_augmented_dev.json`  
**Gold NER spans:** 671  
**NER overall accuracy:** 0.000

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| dataset |        21 |               12 |         0 |                0 |       33 |                   0 |      2 |
| method  |         1 |               19 |        17 |               20 |      253 |                   8 |      0 |
| metric  |         0 |                3 |         0 |                4 |      156 |                   0 |      0 |
| task    |         0 |                8 |         0 |                4 |       95 |                   0 |     15 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| dataset | 0.583 / 0.421 | 0.677 / 0.607    | —             | —                | 0.848 / 0.591 | —                   | 0.438 / 0.510 |
| method  | 0.966 / 0.271 | 0.590 / 0.652    | 0.826 / 0.455 | 0.854 / 0.503    | 0.783 / 0.722 | 0.778 / 0.561       | —             |
| metric  | —             | 0.752 / 0.535    | —             | 0.994 / 0.396    | 0.880 / 0.747 | —                   | —             |
| task    | —             | 0.652 / 0.540    | —             | 0.995 / 0.527    | 0.885 / 0.660 | —                   | 0.726 / 0.656 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| method       |     318 |         0 |          0 |
| metric       |     163 |         0 |          0 |
| task         |     122 |         0 |          0 |
| dataset      |      68 |         0 |          0 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                                   |   Freq |
|:-------------|:------------------|:-----------------------------------------------|-------:|
| dataset      | Dataset           | SNLI                                           |      2 |
| dataset      | Dataset           | GLUE benchmark                                 |      1 |
| dataset      | Dataset           | MNLI datasets                                  |      1 |
| dataset      | Dataset           | GLUE                                           |      1 |
| dataset      | Dataset           | SST-2                                          |      1 |
| dataset      | DatasetGeneric    | WMT 2015                                       |      2 |
| dataset      | DatasetGeneric    | MR                                             |      1 |
| dataset      | DatasetGeneric    | Europarl corpora                               |      1 |
| dataset      | DatasetGeneric    | OPUS collection                                |      1 |
| dataset      | DatasetGeneric    | Common Crawl corpus                            |      1 |
| dataset      | Method            | SNLI                                           |      9 |
| dataset      | Method            | TREC                                           |      3 |
| dataset      | Method            | SST-2                                          |      2 |
| dataset      | Method            | SST-5                                          |      2 |
| dataset      | Method            | NEGRA treebank                                 |      2 |
| dataset      | Task              | AG News dataset                                |      1 |
| dataset      | Task              | SocialDial                                     |      1 |
| method       | Dataset           | CRL                                            |      1 |
| method       | DatasetGeneric    | large language models                          |      3 |
| method       | DatasetGeneric    | T5 model                                       |      2 |
| method       | DatasetGeneric    | better few-shot fine-tuning of language models |      1 |
| method       | DatasetGeneric    | language model                                 |      1 |
| method       | DatasetGeneric    | few-shot setting                               |      1 |
| method       | MLModel           | RoBERTa                                        |      6 |
| method       | MLModel           | BERT                                           |      2 |
| method       | MLModel           | GPT                                            |      1 |
| method       | MLModel           | SBERT                                          |      1 |
| method       | MLModel           | roberta-large-nli-stsb                         |      1 |
| method       | MLModelGeneric    | GPT-3 model                                    |      2 |
| method       | MLModelGeneric    | BERT                                           |      2 |
| method       | MLModelGeneric    | IMO                                            |      2 |
| method       | MLModelGeneric    | CHAT-GPT                                       |      2 |
| method       | MLModelGeneric    | Pre-trained Language Models                    |      1 |
| method       | Method            | IMO                                            |     11 |
| method       | Method            | GPT-3                                          |      9 |
| method       | Method            | standard fine-tuning                           |      8 |
| method       | Method            | phrase-based system                            |      8 |
| method       | Method            | fine-tuning                                    |      7 |
| method       | ModelArchitecture | IMO                                            |      2 |
| method       | ModelArchitecture | LLMs                                           |      1 |
| method       | ModelArchitecture | attention mechanism                            |      1 |
| method       | ModelArchitecture | last layer                                     |      1 |
| method       | ModelArchitecture | last                                           |      1 |
| metric       | DatasetGeneric    | accuracy                                       |      1 |
| metric       | DatasetGeneric    | Precision                                      |      1 |
| metric       | DatasetGeneric    | tree entropy                                   |      1 |
| metric       | MLModelGeneric    | WPA                                            |      2 |
| metric       | MLModelGeneric    | macro-F1                                       |      1 |
| metric       | MLModelGeneric    | accuracy                                       |      1 |
| metric       | Method            | accuracy                                       |     30 |
| metric       | Method            | precision                                      |     22 |
| metric       | Method            | confidence                                     |     15 |
| metric       | Method            | recall                                         |     14 |
| metric       | Method            | coverage                                       |      9 |
| task         | DatasetGeneric    | sentence-pair tasks                            |      2 |
| task         | DatasetGeneric    | data augmentation                              |      2 |
| task         | DatasetGeneric    | TREC                                           |      1 |
| task         | DatasetGeneric    | MPQA                                           |      1 |
| task         | DatasetGeneric    | single-sentence                                |      1 |
| task         | MLModelGeneric    | sentence realization                           |      2 |
| task         | MLModelGeneric    | OOD text classification                        |      1 |
| task         | MLModelGeneric    | French sentence realization                    |      1 |
| task         | Method            | multi-class classification                     |      5 |
| task         | Method            | sentiment analysis                             |      4 |
| task         | Method            | text classification                            |      4 |
| task         | Method            | sentence realization                           |      4 |
| task         | Method            | classification                                 |      3 |
| task         | Task              | multi-class classification                     |      2 |
| task         | Task              | text classification                            |      2 |
| task         | Task              | binary sentence classification                 |      1 |
| task         | Task              | sentence classification                        |      1 |
| task         | Task              | sentence-pair                                  |      1 |

## RE — Relation Confusion Matrix

*No predicted relations found in this file.*
