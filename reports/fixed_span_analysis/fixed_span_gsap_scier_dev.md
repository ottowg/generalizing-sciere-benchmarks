# Fixed-Span NER + RE — GSAP on SCIER (dev)

**Generated:** 2026-03-16 09:30:09

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scier_dev.jsonl`  
**Gold NER spans:** 2234  
**NER overall accuracy:** 0.341

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| Dataset |        32 |               30 |        35 |               28 |      132 |                   7 |      5 |
| Method  |         2 |               15 |       288 |              275 |      693 |                 276 |      0 |
| Task    |         0 |               28 |         6 |               47 |      292 |                   6 |     37 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| Dataset | 0.101 / 0.373 | 0.039 / 0.421    | 0.125 / 0.433 | 0.036 / 0.448    | 0.118 / 0.519 | 0.077 / 0.427       | 0.043 / 0.393 |
| Method  | 0.040 / 0.377 | 0.025 / 0.414    | 0.175 / 0.590 | 0.022 / 0.508    | 0.079 / 0.640 | 0.047 / 0.554       | —             |
| Task    | —             | 0.025 / 0.450    | 0.106 / 0.447 | 0.018 / 0.472    | 0.046 / 0.643 | 0.009 / 0.402       | 0.042 / 0.512 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| Method       |    1549 |       693 |      0.447 |
| Task         |     416 |        37 |      0.089 |
| Dataset      |     269 |        32 |      0.119 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                    |   Freq |
|:-------------|:------------------|:--------------------------------|-------:|
| Dataset      | Dataset           | COCO                            |      7 |
| Dataset      | Dataset           | PASCAL VOC                      |      6 |
| Dataset      | Dataset           | ILSVRC                          |      4 |
| Dataset      | Dataset           | ImageNet                        |      2 |
| Dataset      | Dataset           | CoLA                            |      2 |
| Dataset      | DatasetGeneric    | FSS - 1 0 0 0                   |     23 |
| Dataset      | DatasetGeneric    | ImageNet                        |      2 |
| Dataset      | DatasetGeneric    | PASCAL VOC                      |      2 |
| Dataset      | DatasetGeneric    | Imagenet                        |      1 |
| Dataset      | DatasetGeneric    | Financial PhraseBank            |      1 |
| Dataset      | MLModel           | CoLA                            |      6 |
| Dataset      | MLModel           | COCO                            |      5 |
| Dataset      | MLModel           | MNLI                            |      5 |
| Dataset      | MLModel           | ImageNet                        |      3 |
| Dataset      | MLModel           | MRPC                            |      3 |
| Dataset      | MLModelGeneric    | Kinetics                        |      7 |
| Dataset      | MLModelGeneric    | GLUE                            |      4 |
| Dataset      | MLModelGeneric    | FSS - 1 0 0 0                   |      3 |
| Dataset      | MLModelGeneric    | ImageNet                        |      2 |
| Dataset      | MLModelGeneric    | Financial PhraseBank            |      2 |
| Dataset      | Method            | ImageNet                        |     20 |
| Dataset      | Method            | FSS - 1 0 0 0                   |     10 |
| Dataset      | Method            | COCO                            |      9 |
| Dataset      | Method            | WordNet                         |      8 |
| Dataset      | Method            | PoseTrack                       |      7 |
| Dataset      | ModelArchitecture | ImageNet                        |      2 |
| Dataset      | ModelArchitecture | Kinetics                        |      1 |
| Dataset      | ModelArchitecture | volleyball                      |      1 |
| Dataset      | ModelArchitecture | hockey                          |      1 |
| Dataset      | ModelArchitecture | COCO                            |      1 |
| Dataset      | Task              | GLUE                            |      2 |
| Dataset      | Task              | Open Image                      |      1 |
| Dataset      | Task              | COCO segmentation               |      1 |
| Dataset      | Task              | FiQA sentiment scoring          |      1 |
| Method       | Dataset           | ResNet - 1 0 1                  |      1 |
| Method       | Dataset           | GloVe                           |      1 |
| Method       | DatasetGeneric    | data augmentation               |      3 |
| Method       | DatasetGeneric    | FastPose                        |      3 |
| Method       | DatasetGeneric    | data argumentation operations   |      1 |
| Method       | DatasetGeneric    | I 3 D                           |      1 |
| Method       | DatasetGeneric    | deep learning                   |      1 |
| Method       | MLModel           | TinyBERT                        |     43 |
| Method       | MLModel           | CornerNet                       |     20 |
| Method       | MLModel           | CornerNet - Squeeze             |     19 |
| Method       | MLModel           | FinBERT                         |     17 |
| Method       | MLModel           | BERT                            |     12 |
| Method       | MLModelGeneric    | RCN                             |     26 |
| Method       | MLModelGeneric    | I 3 D                           |     26 |
| Method       | MLModelGeneric    | BERT                            |     18 |
| Method       | MLModelGeneric    | GCN                             |     14 |
| Method       | MLModelGeneric    | ( 2 + 1 )D                      |     12 |
| Method       | Method            | GloVe                           |     33 |
| Method       | Method            | ViCo                            |     21 |
| Method       | Method            | sparse convolution              |     18 |
| Method       | Method            | MTN                             |     17 |
| Method       | Method            | BERT                            |     15 |
| Method       | ModelArchitecture | LSTM                            |     12 |
| Method       | ModelArchitecture | CNNs                            |      9 |
| Method       | ModelArchitecture | fully connected layers          |      8 |
| Method       | ModelArchitecture | AlexNet                         |      8 |
| Method       | ModelArchitecture | BERT                            |      8 |
| Task         | DatasetGeneric    | few - shot segmentation         |      5 |
| Task         | DatasetGeneric    | few - shot learning             |      2 |
| Task         | DatasetGeneric    | instance segmentation           |      2 |
| Task         | DatasetGeneric    | natural language processing     |      2 |
| Task         | DatasetGeneric    | image recognition               |      1 |
| Task         | MLModel           | named entity recognition        |      1 |
| Task         | MLModel           | question answering              |      1 |
| Task         | MLModel           | multi - hop reasoning           |      1 |
| Task         | MLModel           | MLM&NSP+TD                      |      1 |
| Task         | MLModel           | ImageNet classification         |      1 |
| Task         | MLModelGeneric    | classification                  |     10 |
| Task         | MLModelGeneric    | segmentation                    |      6 |
| Task         | MLModelGeneric    | few - shot segmentation         |      2 |
| Task         | MLModelGeneric    | NLP                             |      2 |
| Task         | MLModelGeneric    | next sentence prediction        |      2 |
| Task         | Method            | classification                  |     30 |
| Task         | Method            | pose estimation                 |     18 |
| Task         | Method            | semantic segmentation           |     14 |
| Task         | Method            | localization                    |     12 |
| Task         | Method            | pose tracking                   |      9 |
| Task         | ModelArchitecture | image recognition               |      1 |
| Task         | ModelArchitecture | activity recognition            |      1 |
| Task         | ModelArchitecture | activityspecific features       |      1 |
| Task         | ModelArchitecture | concurrent activity predictions |      1 |
| Task         | ModelArchitecture | semantic segmentation           |      1 |
| Task         | Task              | classification                  |      8 |
| Task         | Task              | localization                    |      4 |
| Task         | Task              | NLP                             |      3 |
| Task         | Task              | visual recognition              |      2 |
| Task         | Task              | question answering              |      2 |

## RE — Relation Confusion Matrix

*No predicted relations found in this file.*
