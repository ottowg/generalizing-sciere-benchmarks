# Fixed-Span NER + RE — GSAP on SCINLP (dev)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scinlp_dev.jsonl`  
**Gold NER spans:** 671  
**NER overall accuracy:** 0.000

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| dataset |        18 |               10 |         0 |                1 |       38 |                   0 |      1 |
| method  |         1 |                8 |        19 |               24 |      260 |                   6 |      0 |
| metric  |         0 |                1 |         0 |                3 |      159 |                   0 |      0 |
| task    |         0 |                4 |         0 |                3 |      101 |                   0 |     14 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| dataset | 0.176 / 0.467 | 0.038 / 0.501    | —             | 0.001 / 0.444    | 0.033 / 0.571 | —                   | 0.199 / 0.434 |
| method  | 0.009 / 0.271 | 0.037 / 0.540    | 0.064 / 0.451 | 0.012 / 0.472    | 0.022 / 0.689 | 0.115 / 0.592       | —             |
| metric  | —             | 0.000 / 0.686    | —             | 0.001 / 0.386    | 0.019 / 0.738 | —                   | —             |
| task    | —             | 0.148 / 0.495    | —             | 0.003 / 0.511    | 0.026 / 0.644 | —                   | 0.115 / 0.616 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| method       |     318 |         0 |          0 |
| metric       |     163 |         0 |          0 |
| task         |     122 |         0 |          0 |
| dataset      |      68 |         0 |          0 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                   |   Freq |
|:-------------|:------------------|:-------------------------------|-------:|
| dataset      | Dataset           | SNLI                           |      2 |
| dataset      | Dataset           | GLUE benchmark                 |      1 |
| dataset      | Dataset           | MNLI datasets                  |      1 |
| dataset      | Dataset           | GLUE                           |      1 |
| dataset      | Dataset           | SST-2                          |      1 |
| dataset      | DatasetGeneric    | WMT 2015                       |      2 |
| dataset      | DatasetGeneric    | MR                             |      1 |
| dataset      | DatasetGeneric    | AG News dataset                |      1 |
| dataset      | DatasetGeneric    | Europarl corpora               |      1 |
| dataset      | DatasetGeneric    | OPUS collection                |      1 |
| dataset      | MLModelGeneric    | Autodesk set                   |      1 |
| dataset      | Method            | SNLI                           |      9 |
| dataset      | Method            | TREC                           |      3 |
| dataset      | Method            | SST-2                          |      2 |
| dataset      | Method            | SST-5                          |      2 |
| dataset      | Method            | NEGRA treebank                 |      2 |
| dataset      | Task              | SocialDial                     |      1 |
| method       | Dataset           | CRL                            |      1 |
| method       | DatasetGeneric    | large language models          |      2 |
| method       | DatasetGeneric    | few-shot setting               |      1 |
| method       | DatasetGeneric    | masked language model          |      1 |
| method       | DatasetGeneric    | Auto T + L                     |      1 |
| method       | DatasetGeneric    | BART                           |      1 |
| method       | MLModel           | RoBERTa                        |      6 |
| method       | MLModel           | BERT                           |      4 |
| method       | MLModel           | GPT                            |      1 |
| method       | MLModel           | SBERT                          |      1 |
| method       | MLModel           | roberta-large-nli-stsb         |      1 |
| method       | MLModelGeneric    | GPT-3 model                    |      2 |
| method       | MLModelGeneric    | BERT                           |      2 |
| method       | MLModelGeneric    | CHAT-GPT                       |      2 |
| method       | MLModelGeneric    | NMT system                     |      2 |
| method       | MLModelGeneric    | Pre-trained Language Models    |      1 |
| method       | Method            | IMO                            |     12 |
| method       | Method            | GPT-3                          |      9 |
| method       | Method            | standard fine-tuning           |      8 |
| method       | Method            | phrase-based system            |      8 |
| method       | Method            | HPSG                           |      8 |
| method       | ModelArchitecture | IMO                            |      2 |
| method       | ModelArchitecture | attention mechanism            |      1 |
| method       | ModelArchitecture | last layer                     |      1 |
| method       | ModelArchitecture | last                           |      1 |
| method       | ModelArchitecture | T5                             |      1 |
| metric       | DatasetGeneric    | accuracy                       |      1 |
| metric       | MLModelGeneric    | macro-F1                       |      1 |
| metric       | MLModelGeneric    | WPA                            |      1 |
| metric       | MLModelGeneric    | accuracy                       |      1 |
| metric       | Method            | accuracy                       |     30 |
| metric       | Method            | precision                      |     22 |
| metric       | Method            | confidence                     |     15 |
| metric       | Method            | recall                         |     14 |
| metric       | Method            | coverage                       |      9 |
| task         | DatasetGeneric    | TREC                           |      1 |
| task         | DatasetGeneric    | MPQA                           |      1 |
| task         | DatasetGeneric    | single-sentence                |      1 |
| task         | DatasetGeneric    | data augmentation              |      1 |
| task         | MLModelGeneric    | sentence realization           |      2 |
| task         | MLModelGeneric    | OOD text classification        |      1 |
| task         | Method            | multi-class classification     |      6 |
| task         | Method            | sentiment analysis             |      4 |
| task         | Method            | text classification            |      4 |
| task         | Method            | sentence realization           |      4 |
| task         | Method            | classification                 |      3 |
| task         | Task              | text classification            |      2 |
| task         | Task              | binary sentence classification |      1 |
| task         | Task              | sentence classification        |      1 |
| task         | Task              | sentence-pair                  |      1 |
| task         | Task              | binary classification          |      1 |

## RE — Relation Confusion Matrix

*No predicted relations found in this file.*
