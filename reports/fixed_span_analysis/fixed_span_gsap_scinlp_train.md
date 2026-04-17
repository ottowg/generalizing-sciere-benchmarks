# Fixed-Span NER + RE — GSAP on SCINLP (train)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scinlp_train.jsonl`  
**Gold NER spans:** 4993  
**NER overall accuracy:** 0.000

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| dataset |        62 |               99 |         5 |               17 |      630 |                   4 |      1 |
| method  |        11 |               45 |        76 |              232 |     2115 |                 130 |      1 |
| metric  |         1 |               18 |         2 |                9 |      707 |                   2 |      0 |
| task    |        19 |               31 |         1 |                7 |      740 |                   0 |     28 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| dataset | 0.076 / 0.483 | 0.039 / 0.535    | 0.019 / 0.434 | 0.034 / 0.523    | 0.033 / 0.600 | 0.019 / 0.425       | 0.011 / 0.340 |
| method  | 0.049 / 0.383 | 0.013 / 0.456    | 0.095 / 0.527 | 0.023 / 0.495    | 0.030 / 0.681 | 0.085 / 0.650       | 0.132 / 0.355 |
| metric  | 0.029 / 0.476 | 0.050 / 0.551    | 0.026 / 0.407 | 0.005 / 0.445    | 0.020 / 0.706 | 0.049 / 0.419       | —             |
| task    | 0.169 / 0.499 | 0.032 / 0.519    | 0.023 / 0.436 | 0.010 / 0.403    | 0.015 / 0.677 | —                   | 0.058 / 0.525 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| method       |    2610 |         0 |          0 |
| task         |     826 |         0 |          0 |
| dataset      |     818 |         0 |          0 |
| metric       |     739 |         0 |          0 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                           |   Freq |
|:-------------|:------------------|:---------------------------------------|-------:|
| dataset      | Dataset           | WSJ                                    |     11 |
| dataset      | Dataset           | CoQA                                   |      5 |
| dataset      | Dataset           | TRECQA                                 |      2 |
| dataset      | Dataset           | L3CUBE                                 |      2 |
| dataset      | Dataset           | Aksharantar                            |      2 |
| dataset      | DatasetGeneric    | BC                                     |     13 |
| dataset      | DatasetGeneric    | Wikipedia                              |      9 |
| dataset      | DatasetGeneric    | WSJ                                    |      5 |
| dataset      | DatasetGeneric    | WMT12                                  |      3 |
| dataset      | DatasetGeneric    | OVERNIGHT                              |      3 |
| dataset      | MLModel           | Penn Treebank                          |      1 |
| dataset      | MLModel           | CoNLL 2003                             |      1 |
| dataset      | MLModel           | ATOMIC 20 20                           |      1 |
| dataset      | MLModel           | L3CUBE                                 |      1 |
| dataset      | MLModel           | L3CUBE dataset                         |      1 |
| dataset      | MLModelGeneric    | ATIS                                   |      3 |
| dataset      | MLModelGeneric    | Reddit                                 |      1 |
| dataset      | MLModelGeneric    | Penn Treebank                          |      1 |
| dataset      | MLModelGeneric    | SPADES                                 |      1 |
| dataset      | MLModelGeneric    | NYT corpus6                            |      1 |
| dataset      | Method            | Wikipedia                              |     43 |
| dataset      | Method            | PEACOK                                 |     32 |
| dataset      | Method            | WSJ                                    |     27 |
| dataset      | Method            | BC                                     |     24 |
| dataset      | Method            | WORDNET                                |     22 |
| dataset      | ModelArchitecture | WMT ’ 14                               |      1 |
| dataset      | ModelArchitecture | ConvS2S codebase1                      |      1 |
| dataset      | ModelArchitecture | WMT ’ 14 En → Fr task                  |      1 |
| dataset      | ModelArchitecture | SNLI dataset                           |      1 |
| dataset      | Task              | TREC-QA                                |      1 |
| method       | Dataset           | FREQMLM                                |      3 |
| method       | Dataset           | CNM                                    |      2 |
| method       | Dataset           | Word2Vec                               |      1 |
| method       | Dataset           | BiDAF                                  |      1 |
| method       | Dataset           | AHP                                    |      1 |
| method       | DatasetGeneric    | Large Language Models                  |      3 |
| method       | DatasetGeneric    | pretrained language models             |      2 |
| method       | DatasetGeneric    | n-grams                                |      2 |
| method       | DatasetGeneric    | bigram                                 |      2 |
| method       | DatasetGeneric    | BERT                                   |      1 |
| method       | MLModel           | TinyBERT                               |     23 |
| method       | MLModel           | RESBERT                                |      8 |
| method       | MLModel           | mBERT                                  |      7 |
| method       | MLModel           | RNMT +                                 |      4 |
| method       | MLModel           | CNM                                    |      4 |
| method       | MLModelGeneric    | STRUCTVAE                              |     13 |
| method       | MLModelGeneric    | BERT                                   |     10 |
| method       | MLModelGeneric    | Transformer                            |      7 |
| method       | MLModelGeneric    | RNMT +                                 |      7 |
| method       | MLModelGeneric    | CNM                                    |      7 |
| method       | Method            | EM                                     |     46 |
| method       | Method            | BERT                                   |     33 |
| method       | Method            | n-gram                                 |     29 |
| method       | Method            | LLMs                                   |     24 |
| method       | Method            | InstructGPT-3                          |     24 |
| method       | ModelArchitecture | LSTM                                   |     25 |
| method       | ModelArchitecture | RNMT +                                 |     12 |
| method       | ModelArchitecture | Transformer                            |      9 |
| method       | ModelArchitecture | self-attention                         |      6 |
| method       | ModelArchitecture | ConvS2S                                |      4 |
| method       | Task              | LLMs                                   |      1 |
| metric       | Dataset           | MAE                                    |      1 |
| metric       | DatasetGeneric    | accuracy                               |      8 |
| metric       | DatasetGeneric    | LocalE                                 |      2 |
| metric       | DatasetGeneric    | confidence                             |      1 |
| metric       | DatasetGeneric    | precision                              |      1 |
| metric       | DatasetGeneric    | accuracies                             |      1 |
| metric       | MLModel           | BLEU                                   |      1 |
| metric       | MLModel           | NDCG @ 10                              |      1 |
| metric       | MLModelGeneric    | recall                                 |      3 |
| metric       | MLModelGeneric    | precision                              |      2 |
| metric       | MLModelGeneric    | BLEU                                   |      2 |
| metric       | MLModelGeneric    | standard deviation                     |      1 |
| metric       | MLModelGeneric    | GlobalE                                |      1 |
| metric       | Method            | accuracy                               |    147 |
| metric       | Method            | BLEU                                   |     63 |
| metric       | Method            | precision                              |     36 |
| metric       | Method            | recall                                 |     35 |
| metric       | Method            | TER                                    |     35 |
| metric       | ModelArchitecture | BLEU                                   |      2 |
| task         | Dataset           | CoLA                                   |      3 |
| task         | Dataset           | MNLI                                   |      2 |
| task         | Dataset           | QNLI                                   |      2 |
| task         | Dataset           | RTE                                    |      2 |
| task         | Dataset           | QG                                     |      1 |
| task         | DatasetGeneric    | conversational question answering      |      2 |
| task         | DatasetGeneric    | natural language understanding         |      2 |
| task         | DatasetGeneric    | audio data mining                      |      2 |
| task         | DatasetGeneric    | conversational QA                      |      1 |
| task         | DatasetGeneric    | dialogue generation                    |      1 |
| task         | MLModel           | passage reranking                      |      1 |
| task         | MLModelGeneric    | NN-based QG                            |      1 |
| task         | MLModelGeneric    | SQG                                    |      1 |
| task         | MLModelGeneric    | MT system combination                  |      1 |
| task         | MLModelGeneric    | machine translation                    |      1 |
| task         | MLModelGeneric    | candidate generation                   |      1 |
| task         | Method            | punctuation prediction                 |     20 |
| task         | Method            | semantic parsing                       |     19 |
| task         | Method            | SA                                     |     19 |
| task         | Method            | QA                                     |     16 |
| task         | Method            | machine translation                    |     16 |
| task         | Task              | sentiment classification               |      3 |
| task         | Task              | text classification                    |      2 |
| task         | Task              | QA                                     |      2 |
| task         | Task              | selective dissemination of information |      1 |
| task         | Task              | Chinese to English translation         |      1 |

## RE — Relation Confusion Matrix

*No predicted relations found in this file.*
