# Fixed-Span NER + RE — GSAP on SCIER (pruner_augmented_dev)

**Generated:** 2026-03-16 09:30:09

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scier_pruner_augmented_dev.json`  
**Gold NER spans:** 2234  
**NER overall accuracy:** 0.419

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|-------------:|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| Dataset |            5 |       142 |               32 |        15 |                7 |       59 |                   2 |      7 |
| Method  |            0 |        12 |               14 |       301 |              216 |      596 |                 397 |     13 |
| Task    |            0 |         3 |               23 |         2 |               21 |      163 |                   7 |    197 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | DataSource    | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| Dataset | 0.173 / 0.907 | 0.078 / 0.906 | 0.376 / 0.660    | 0.471 / 0.430 | 0.537 / 0.517    | 0.516 / 0.528 | 0.629 / 0.547       | 0.596 / 0.521 |
| Method  | —             | 0.061 / 0.799 | 0.652 / 0.521    | 0.275 / 0.741 | 0.434 / 0.681    | 0.427 / 0.748 | 0.396 / 0.770       | 0.393 / 0.803 |
| Task    | —             | 0.667 / 0.517 | 0.585 / 0.606    | 0.536 / 0.584 | 0.623 / 0.465    | 0.511 / 0.678 | 0.612 / 0.458       | 0.216 / 0.901 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| Method       |    1549 |       596 |      0.385 |
| Task         |     416 |       197 |      0.474 |
| Dataset      |     269 |       142 |      0.528 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                |   Freq |
|:-------------|:------------------|:----------------------------|-------:|
| Dataset      | DataSource        | WordNet                     |      2 |
| Dataset      | DataSource        | StockTwits                  |      1 |
| Dataset      | DataSource        | Word - Net                  |      1 |
| Dataset      | DataSource        | Wikipedia                   |      1 |
| Dataset      | Dataset           | ImageNet                    |     21 |
| Dataset      | Dataset           | COCO                        |     15 |
| Dataset      | Dataset           | FSS - 1 0 0 0               |     12 |
| Dataset      | Dataset           | Kinetics                    |      7 |
| Dataset      | Dataset           | GLUE                        |      7 |
| Dataset      | DatasetGeneric    | FSS - 1 0 0 0               |     20 |
| Dataset      | DatasetGeneric    | Financial PhraseBank        |      2 |
| Dataset      | DatasetGeneric    | English Wikipedia           |      2 |
| Dataset      | DatasetGeneric    | UCF 1 0 1                   |      1 |
| Dataset      | DatasetGeneric    | PASCAL VOC                  |      1 |
| Dataset      | MLModel           | COCO                        |      2 |
| Dataset      | MLModel           | MNLI                        |      2 |
| Dataset      | MLModel           | ImageNet                    |      1 |
| Dataset      | MLModel           | fsCOCO                      |      1 |
| Dataset      | MLModel           | SST - 5                     |      1 |
| Dataset      | MLModelGeneric    | Kinetics                    |      3 |
| Dataset      | MLModelGeneric    | ImageNet                    |      1 |
| Dataset      | MLModelGeneric    | FSS - 1 0 0 0               |      1 |
| Dataset      | MLModelGeneric    | ILSRVC                      |      1 |
| Dataset      | MLModelGeneric    | Cityscapes                  |      1 |
| Dataset      | Method            | ImageNet                    |      6 |
| Dataset      | Method            | PASCAL VOC 2 0 1 2          |      5 |
| Dataset      | Method            | WordNet                     |      5 |
| Dataset      | Method            | COCO                        |      4 |
| Dataset      | Method            | fsCOCO                      |      4 |
| Dataset      | ModelArchitecture | ImageNet                    |      1 |
| Dataset      | ModelArchitecture | charades                    |      1 |
| Dataset      | Task              | PASCAL VOC                  |      2 |
| Dataset      | Task              | GLUE                        |      2 |
| Dataset      | Task              | Open Image                  |      1 |
| Dataset      | Task              | COCO segmentation           |      1 |
| Dataset      | Task              | FiQA sentiment scoring      |      1 |
| Method       | Dataset           | ResNet - 1 0 1              |      1 |
| Method       | Dataset           | Guided Network - 1 shot     |      1 |
| Method       | Dataset           | VGG - 1 6                   |      1 |
| Method       | Dataset           | YOLOv 3                     |      1 |
| Method       | Dataset           | PoseTrack                   |      1 |
| Method       | DatasetGeneric    | I 3 D                       |      3 |
| Method       | DatasetGeneric    | S 3 D                       |      1 |
| Method       | DatasetGeneric    | deep learning               |      1 |
| Method       | DatasetGeneric    | VGG - 1 6                   |      1 |
| Method       | DatasetGeneric    | Inception                   |      1 |
| Method       | MLModel           | TinyBERT                    |     42 |
| Method       | MLModel           | BERT                        |     20 |
| Method       | MLModel           | CornerNet - Squeeze         |     18 |
| Method       | MLModel           | FinBERT                     |     17 |
| Method       | MLModel           | CornerNet                   |     17 |
| Method       | MLModelGeneric    | I 3 D                       |     22 |
| Method       | MLModelGeneric    | RCN                         |     14 |
| Method       | MLModelGeneric    | ( 2 + 1 )D                  |     12 |
| Method       | MLModelGeneric    | GCN                         |     11 |
| Method       | MLModelGeneric    | 3D CNNs                     |     10 |
| Method       | Method            | GloVe                       |     34 |
| Method       | Method            | sparse convolution          |     18 |
| Method       | Method            | ViCo                        |     18 |
| Method       | Method            | word embeddings             |     14 |
| Method       | Method            | MTN                         |     13 |
| Method       | ModelArchitecture | RCN                         |     17 |
| Method       | ModelArchitecture | convolution layers          |     15 |
| Method       | ModelArchitecture | BERT                        |     15 |
| Method       | ModelArchitecture | CNN                         |     13 |
| Method       | ModelArchitecture | LSTM                        |     13 |
| Method       | Task              | unsupervised clustering     |      2 |
| Method       | Task              | supervised partitioning     |      2 |
| Method       | Task              | Causal inference            |      1 |
| Method       | Task              | OSLSM - 1 shot              |      1 |
| Method       | Task              | OSLSM - 5 shot              |      1 |
| Task         | Dataset           | Person search               |      1 |
| Task         | Dataset           | classification              |      1 |
| Task         | Dataset           | segmentation                |      1 |
| Task         | DatasetGeneric    | few - shot learning         |      3 |
| Task         | DatasetGeneric    | few - shot segmentation     |      3 |
| Task         | DatasetGeneric    | segmentation                |      2 |
| Task         | DatasetGeneric    | semantic segmentation       |      1 |
| Task         | DatasetGeneric    | object class recognition    |      1 |
| Task         | MLModel           | MLM&NSP+TD                  |      1 |
| Task         | MLModel           | ImageNet classification     |      1 |
| Task         | MLModelGeneric    | segmentation                |      4 |
| Task         | MLModelGeneric    | natural language processing |      2 |
| Task         | MLModelGeneric    | next sentence prediction    |      2 |
| Task         | MLModelGeneric    | classification              |      2 |
| Task         | MLModelGeneric    | action detection            |      1 |
| Task         | Method            | classification              |     16 |
| Task         | Method            | pose estimation             |     10 |
| Task         | Method            | pose tracking               |      8 |
| Task         | Method            | Re - ID                     |      6 |
| Task         | Method            | localization                |      5 |
| Task         | ModelArchitecture | classification              |      3 |
| Task         | ModelArchitecture | image recognition           |      1 |
| Task         | ModelArchitecture | NLP                         |      1 |
| Task         | ModelArchitecture | activity recognition        |      1 |
| Task         | ModelArchitecture | semantic segmentation       |      1 |
| Task         | Task              | classification              |     28 |
| Task         | Task              | semantic segmentation       |     12 |
| Task         | Task              | localization                |     12 |
| Task         | Task              | pose estimation             |      8 |
| Task         | Task              | few - shot segmentation     |      6 |

## RE — Relation Confusion Matrix

**Gold relations:** 1132  
**Predicted relations:** 268  

Rows = gold labels · Columns = predicted labels · NIL = unmatched on the respective side.

|                |   appliedTo |   architecture |   benchmarkFor |   coreference |   evaluatedOn |   generatedBy |   isBasedOn |   isComparedTo |   isHyponymOf |   isPartOf |   trainedOn |   usedFor |   versionOf |   NIL |
|:---------------|------------:|---------------:|---------------:|--------------:|--------------:|--------------:|------------:|---------------:|--------------:|-----------:|------------:|----------:|------------:|------:|
| Benchmark-For  |           0 |              0 |              8 |             0 |             0 |             0 |           0 |              0 |             0 |          0 |           0 |         0 |           0 |    56 |
| Compare-With   |           0 |              0 |              0 |             0 |             0 |             0 |           0 |             16 |             0 |          0 |           0 |         1 |           0 |   158 |
| Evaluated-With |           0 |              0 |              0 |             0 |            12 |             0 |           0 |              0 |             0 |          6 |           3 |         0 |           0 |    57 |
| Part-Of        |           0 |              1 |              0 |             0 |             0 |             0 |           0 |              0 |             0 |          3 |           0 |         3 |           0 |   207 |
| SubClass-Of    |           0 |              4 |              0 |             1 |             0 |             0 |           0 |              1 |            10 |          3 |           0 |         0 |           1 |    94 |
| SubTask-Of     |           0 |              0 |              0 |             0 |             0 |             0 |           0 |              0 |             3 |          0 |           0 |         0 |           0 |    28 |
| Synonym-Of     |           0 |              0 |              0 |            24 |             0 |             0 |           0 |              0 |             0 |          0 |           0 |         0 |           0 |    52 |
| Trained-With   |           0 |              0 |              0 |             0 |             0 |             0 |           0 |              0 |             0 |          0 |           8 |         0 |           0 |    29 |
| Used-For       |          39 |              0 |              0 |             0 |             0 |             0 |           0 |              0 |             0 |          0 |           0 |         5 |           0 |   299 |
| NIL            |          12 |             27 |              3 |            34 |            14 |             1 |           5 |              2 |             5 |          0 |           2 |        11 |           0 |     0 |

## RE — Per-Label Accuracy

| Gold Label     |   Total |   Correct |   Accuracy |
|:---------------|--------:|----------:|-----------:|
| Used-For       |     343 |         0 |          0 |
| Part-Of        |     214 |         0 |          0 |
| Compare-With   |     175 |         0 |          0 |
| SubClass-Of    |     114 |         0 |          0 |
| Evaluated-With |      78 |         0 |          0 |
| Synonym-Of     |      76 |         0 |          0 |
| Benchmark-For  |      64 |         0 |          0 |
| Trained-With   |      37 |         0 |          0 |
| SubTask-Of     |      31 |         0 |          0 |

## RE — Examples (top 5 per cell)

| Gold Label     | Pred Label   | Subject → Object                                                              |   Freq |
|:---------------|:-------------|:------------------------------------------------------------------------------|-------:|
| Benchmark-For  | benchmarkFor | Kinetics → action recognition                                                 |      1 |
| Benchmark-For  | benchmarkFor | PASCAL VOC → few - shot segmentation                                          |      1 |
| Benchmark-For  | benchmarkFor | FSS - 1 0 0 0 → few - shot segmentation                                       |      1 |
| Benchmark-For  | benchmarkFor | FSS - 1 0 0 0 → instance segmentation                                         |      1 |
| Benchmark-For  | benchmarkFor | FSS - 1 0 0 0 → large - scale segmentation                                    |      1 |
| Benchmark-For  | NIL          | FSS - 1 0 0 0 → few - shot segmentation                                       |      6 |
| Benchmark-For  | NIL          | PoseTrack → pose estimation                                                   |      3 |
| Benchmark-For  | NIL          | SSM → person Re - ID                                                          |      3 |
| Benchmark-For  | NIL          | COCO → Pose estimation                                                        |      2 |
| Benchmark-For  | NIL          | Sports 1 M → video action recognition                                         |      1 |
| Compare-With   | isComparedTo | sparse convolution → dense convolution                                        |      2 |
| Compare-With   | isComparedTo | CornerNet - Saccade → CornerNet                                               |      2 |
| Compare-With   | isComparedTo | TinyBERT → BERT SMALL                                                         |      2 |
| Compare-With   | isComparedTo | 3D convolutions → 3D ( spatiotemporal ) convolutions                          |      1 |
| Compare-With   | isComparedTo | 3D CNNs → 2D CNNs                                                             |      1 |
| Compare-With   | usedFor      | TinyBERT → BERT distillation                                                  |      1 |
| Compare-With   | NIL          | RCN → I 3 D                                                                   |      9 |
| Compare-With   | NIL          | RCN → ( 2 + 1 )D                                                              |      6 |
| Compare-With   | NIL          | ViCo → GloVe                                                                  |      6 |
| Compare-With   | NIL          | sparse convolution → dense convolution                                        |      5 |
| Compare-With   | NIL          | CornerNet - Squeeze → YOLOv 3                                                 |      5 |
| Evaluated-With | evaluatedOn  | TinyBERT → GLUE                                                               |      2 |
| Evaluated-With | evaluatedOn  | FastPose → PoseTrack                                                          |      2 |
| Evaluated-With | evaluatedOn  | 3D CNNs → Sports 1 M                                                          |      1 |
| Evaluated-With | evaluatedOn  | 2D CNNs → Sports 1 M                                                          |      1 |
| Evaluated-With | evaluatedOn  | recurrent convolutional network → Kinetics                                    |      1 |
| Evaluated-With | isPartOf     | i 3 D → charades                                                              |      1 |
| Evaluated-With | isPartOf     | PoseTrack → PoseTrack                                                         |      1 |
| Evaluated-With | isPartOf     | JointFlow → PoseTrack                                                         |      1 |
| Evaluated-With | isPartOf     | PoseFlow → PoseTrack                                                          |      1 |
| Evaluated-With | isPartOf     | Detect - and - Track → PoseTrack                                              |      1 |
| Evaluated-With | trainedOn    | CornerNet - Saccade → COCO                                                    |      1 |
| Evaluated-With | trainedOn    | CornerNet → COCO                                                              |      1 |
| Evaluated-With | trainedOn    | TinyBERT → MNLI                                                               |      1 |
| Evaluated-With | NIL          | RCN → Kinetics                                                                |      5 |
| Evaluated-With | NIL          | I 3 D → Kinetics                                                              |      3 |
| Evaluated-With | NIL          | YOLOv 3 → COCO                                                                |      3 |
| Evaluated-With | NIL          | ( 2 + 1 )D → Kinetics                                                         |      2 |
| Evaluated-With | NIL          | CornerNet - Squeeze → COCO                                                    |      2 |
| Part-Of        | architecture | 2D CNN → LSTMs                                                                |      1 |
| Part-Of        | isPartOf     | convolution layers → CNN                                                      |      1 |
| Part-Of        | isPartOf     | stem block → DenseNet                                                         |      1 |
| Part-Of        | isPartOf     | Hourglass - 1 0 4 → CornerNet                                                 |      1 |
| Part-Of        | usedFor      | ReLU → RNNs                                                                   |      1 |
| Part-Of        | usedFor      | sparse convolution → sparse CNN                                               |      1 |
| Part-Of        | usedFor      | denseCRF → Deeplab                                                            |      1 |
| Part-Of        | NIL          | convolution layers → AlexNet                                                  |      4 |
| Part-Of        | NIL          | ResNet - 1 8 → I 3 D                                                          |      3 |
| Part-Of        | NIL          | ResNet - 3 4 → I 3 D                                                          |      3 |
| Part-Of        | NIL          | ResNet - 3 4 → ( 2 + 1 )D                                                     |      3 |
| Part-Of        | NIL          | convolution layers → sparse CNN                                               |      3 |
| SubClass-Of    | architecture | Holistic SparseCNN → sparse CNNs                                              |      1 |
| SubClass-Of    | architecture | FinBERT → BERT                                                                |      1 |
| SubClass-Of    | architecture | Tri - axial Self - Attention → temporal attentions                            |      1 |
| SubClass-Of    | architecture | TinyBERT → BERT                                                               |      1 |
| SubClass-Of    | coreference  | CornerNetSqueeze → CornerNet - Lite                                           |      1 |
| SubClass-Of    | isComparedTo | CornerNet - Saccade → CornerNet                                               |      1 |
| SubClass-Of    | isHyponymOf  | CNNs → Deep neural networks                                                   |      1 |
| SubClass-Of    | isHyponymOf  | AlexNet → CNNs                                                                |      1 |
| SubClass-Of    | isHyponymOf  | VGG - 1 6 → feature extractor                                                 |      1 |
| SubClass-Of    | isHyponymOf  | BERT → Pre - trained language models                                          |      1 |
| SubClass-Of    | isHyponymOf  | XLNet → Pre - trained language models                                         |      1 |
| SubClass-Of    | isPartOf     | MNLI → GLUE                                                                   |      1 |
| SubClass-Of    | isPartOf     | MRPC → GLUE                                                                   |      1 |
| SubClass-Of    | isPartOf     | CoLA → GLUE                                                                   |      1 |
| SubClass-Of    | versionOf    | CornerNet - Saccade → CornerNet - Lite                                        |      1 |
| SubClass-Of    | NIL          | TinyBERT → BERT                                                               |      6 |
| SubClass-Of    | NIL          | CornerNet - Saccade → CornerNet                                               |      4 |
| SubClass-Of    | NIL          | FinBERT → BERT                                                                |      3 |
| SubClass-Of    | NIL          | CornerNet - Squeeze → CornerNet                                               |      3 |
| SubClass-Of    | NIL          | GloVe → word embeddings                                                       |      2 |
| SubTask-Of     | isHyponymOf  | face detection → computer vision                                              |      1 |
| SubTask-Of     | isHyponymOf  | object detection → computer vision                                            |      1 |
| SubTask-Of     | isHyponymOf  | pose estimation → computer vision                                             |      1 |
| SubTask-Of     | NIL          | localization → semantic segmentation                                          |      2 |
| SubTask-Of     | NIL          | online action detection → video understanding                                 |      1 |
| SubTask-Of     | NIL          | future action label prediction → video understanding                          |      1 |
| SubTask-Of     | NIL          | future representation prediction → video understanding                        |      1 |
| SubTask-Of     | NIL          | image recognition → computer vision                                           |      1 |
| Synonym-Of     | coreference  | recurrent convolutional network → RCN                                         |      2 |
| Synonym-Of     | coreference  | Convolutional neural networks → CNN                                           |      1 |
| Synonym-Of     | coreference  | 2D residual networks → ResNets                                                |      1 |
| Synonym-Of     | coreference  | recurrent neural networks → RNN                                               |      1 |
| Synonym-Of     | coreference  | long short - term memory → LSTM                                               |      1 |
| Synonym-Of     | NIL          | multi - task network → MTN                                                    |      3 |
| Synonym-Of     | NIL          | Global Convolutional Network → GCN                                            |      3 |
| Synonym-Of     | NIL          | Recurrent Convolutional Network → RCN                                         |      2 |
| Synonym-Of     | NIL          | natural language processing → NLP                                             |      2 |
| Synonym-Of     | NIL          | convolutional neural networks → CNNs                                          |      1 |
| Trained-With   | trainedOn    | 3D CNNs → ImageNet                                                            |      1 |
| Trained-With   | trainedOn    | 2D CNNs → ImageNet                                                            |      1 |
| Trained-With   | trainedOn    | 3D networks → Kinetics                                                        |      1 |
| Trained-With   | trainedOn    | OSLSM → FSS - 1 0 0 0                                                         |      1 |
| Trained-With   | trainedOn    | Guided Network → FSS - 1 0 0 0                                                |      1 |
| Trained-With   | NIL          | I 3 D → ImageNet                                                              |      4 |
| Trained-With   | NIL          | RCN → ImageNet                                                                |      4 |
| Trained-With   | NIL          | ( 2 + 1 )D → ImageNet                                                         |      2 |
| Trained-With   | NIL          | inflated 3D CNNs → ImageNet                                                   |      1 |
| Trained-With   | NIL          | recurrent convolutional network → ImageNet                                    |      1 |
| Used-For       | appliedTo    | sparse CNN → classification                                                   |      2 |
| Used-For       | appliedTo    | AlexNet → classification                                                      |      2 |
| Used-For       | appliedTo    | Global Convolutional Network → classification                                 |      2 |
| Used-For       | appliedTo    | Global Convolutional Network → localization                                   |      2 |
| Used-For       | appliedTo    | Global Convolutional Network → semantic segmentation                          |      2 |
| Used-For       | usedFor      | transfer learning → 3D CNN                                                    |      1 |
| Used-For       | usedFor      | doc 2 vec → sentence embeddings                                               |      1 |
| Used-For       | usedFor      | intermediate layer distillation → task - specific distillation                |      1 |
| Used-For       | usedFor      | General Distillation → TinyBERT                                               |      1 |
| Used-For       | usedFor      | GD → TinyBERT                                                                 |      1 |
| Used-For       | NIL          | GCN → segmentation                                                            |      5 |
| Used-For       | NIL          | KD → BERT                                                                     |      4 |
| Used-For       | NIL          | Transformer distillation → TinyBERT                                           |      4 |
| Used-For       | NIL          | CNN → classification                                                          |      3 |
| Used-For       | NIL          | CNNs → classification                                                         |      3 |
| NIL            | appliedTo    | FCN → semantic segmentation                                                   |      2 |
| NIL            | appliedTo    | CNN → action recognition                                                      |      1 |
| NIL            | appliedTo    | CNN → image recognition                                                       |      1 |
| NIL            | appliedTo    | ImageNet → video classification                                               |      1 |
| NIL            | appliedTo    | Deep neural networks → image recognition                                      |      1 |
| NIL            | architecture | sparse CNN → convolution layers                                               |      2 |
| NIL            | architecture | RCN → RCU unit                                                                |      1 |
| NIL            | architecture | sparse CNN → fully connected layers                                           |      1 |
| NIL            | architecture | AlexNet → fully connected layers                                              |      1 |
| NIL            | architecture | AlexNet → convolution layers                                                  |      1 |
| NIL            | benchmarkFor | COCO → visual recognition                                                     |      1 |
| NIL            | benchmarkFor | FSS - 1 0 0 0 → instance - level segmentation                                 |      1 |
| NIL            | benchmarkFor | GLUE → natural language understanding                                         |      1 |
| NIL            | coreference  | TinyBERT → TinyBERT                                                           |      6 |
| NIL            | coreference  | BERT → BERT                                                                   |      3 |
| NIL            | coreference  | COCO → COCO                                                                   |      2 |
| NIL            | coreference  | GCN → GCN                                                                     |      2 |
| NIL            | coreference  | 2D CNNs → 3D CNNs                                                             |      1 |
| NIL            | evaluatedOn  | TinyBERT → CoLA                                                               |      3 |
| NIL            | evaluatedOn  | BERT SMALL → GLUE                                                             |      2 |
| NIL            | evaluatedOn  | FinBERT → Financial PhraseBank                                                |      1 |
| NIL            | evaluatedOn  | BERT BASE → GLUE                                                              |      1 |
| NIL            | evaluatedOn  | TinyBERT → GLUE                                                               |      1 |
| NIL            | generatedBy  | wiki → vis - w 2 v                                                            |      1 |
| NIL            | isBasedOn    | 3D networks → 2D CNNs                                                         |      1 |
| NIL            | isBasedOn    | 3D CNNs → 2D CNNs                                                             |      1 |
| NIL            | isBasedOn    | RCN → 2D/ 3 D networks                                                        |      1 |
| NIL            | isBasedOn    | single - activity recognition models → multiple single - activity recognizers |      1 |
| NIL            | isBasedOn    | CornerNet - Squeeze → SqueezeNet                                              |      1 |
| NIL            | isComparedTo | 3D CNNs → 3D CNNs                                                             |      1 |
| NIL            | isComparedTo | R - FCN → R - FCN                                                             |      1 |
| NIL            | isHyponymOf  | PASCAL VOC → deep neural networks                                             |      1 |
| NIL            | isHyponymOf  | ILSVRC → deep neural networks                                                 |      1 |
| NIL            | isHyponymOf  | COCO → deep neural networks                                                   |      1 |
| NIL            | isHyponymOf  | feature - to - activity attention → Tri - axial Self - Attention              |      1 |
| NIL            | isHyponymOf  | BERT → PLMs                                                                   |      1 |
| NIL            | trainedOn    | 3D networks → ImageNet                                                        |      1 |
| NIL            | trainedOn    | few - shot segmentation → FSS - 1 0 0 0                                       |      1 |
| NIL            | usedFor      | separable convolution → R - FCN                                               |      2 |
| NIL            | usedFor      | word embeddings → GloVe                                                       |      2 |
| NIL            | usedFor      | GEMM → fully connected layers                                                 |      1 |
| NIL            | usedFor      | discriminative fine - tuning → Universal Language Model Fine - tuning         |      1 |
| NIL            | usedFor      | slanted triangular learning rates → Universal Language Model Fine - tuning    |      1 |
