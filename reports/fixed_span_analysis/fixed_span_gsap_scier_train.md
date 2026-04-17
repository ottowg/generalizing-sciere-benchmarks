# Fixed-Span NER + RE — GSAP on SCIER (train)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scier_train.jsonl`  
**Gold NER spans:** 18041  
**NER overall accuracy:** 0.430

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MISSING |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |
|:--------|-------------:|----------:|-----------------:|----------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|
| Dataset |            1 |       607 |              485 |         0 |       212 |               92 |     1723 |                  84 |               0 |     16 |
| Method  |            0 |       136 |              346 |         9 |       775 |             1285 |     6771 |                2073 |               1 |     28 |
| Task    |            0 |        17 |              222 |         1 |        20 |              201 |     2452 |                 102 |               0 |    382 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | DataSource    | Dataset       | DatasetGeneric   | MISSING   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | ReferenceLink   | Task          |
|:--------|:--------------|:--------------|:-----------------|:----------|:--------------|:-----------------|:--------------|:--------------------|:----------------|:--------------|
| Dataset | 0.784 / 0.787 | 0.180 / 0.492 | 0.068 / 0.499    | —         | 0.060 / 0.430 | 0.022 / 0.372    | 0.076 / 0.526 | 0.070 / 0.421       | —               | 0.128 / 0.414 |
| Method  | —             | 0.100 / 0.367 | 0.032 / 0.486    | —         | 0.152 / 0.463 | 0.036 / 0.477    | 0.074 / 0.650 | 0.084 / 0.596       | 0.317 / 0.499   | 0.060 / 0.378 |
| Task    | —             | 0.060 / 0.464 | 0.042 / 0.492    | —         | 0.051 / 0.369 | 0.013 / 0.435    | 0.048 / 0.633 | 0.037 / 0.485       | —               | 0.135 / 0.553 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| Method       |   11424 |      6771 |      0.593 |
| Task         |    3397 |       382 |      0.112 |
| Dataset      |    3220 |       607 |      0.189 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                      |   Freq |
|:-------------|:------------------|:----------------------------------|-------:|
| Dataset      | DataSource        | IMDb                              |      1 |
| Dataset      | Dataset           | ImageNet                          |     48 |
| Dataset      | Dataset           | MNIST                             |     28 |
| Dataset      | Dataset           | QuAC                              |     28 |
| Dataset      | Dataset           | CoQA                              |     20 |
| Dataset      | Dataset           | SQuAD                             |     20 |
| Dataset      | DatasetGeneric    | ImageNet                          |     29 |
| Dataset      | DatasetGeneric    | Cityscapes                        |     17 |
| Dataset      | DatasetGeneric    | BSDS 5 0 0                        |     15 |
| Dataset      | DatasetGeneric    | 3 0 0 - W                         |     12 |
| Dataset      | DatasetGeneric    | Kinetics                          |     12 |
| Dataset      | MLModel           | D RoBERTa                         |     23 |
| Dataset      | MLModel           | ImageNet                          |     18 |
| Dataset      | MLModel           | Cityscapes                        |     10 |
| Dataset      | MLModel           | D BiDAF                           |      9 |
| Dataset      | MLModel           | ImageNet classification           |      8 |
| Dataset      | MLModelGeneric    | Kinetics                          |     14 |
| Dataset      | MLModelGeneric    | CIFAR - 1 0                       |      7 |
| Dataset      | MLModelGeneric    | Cityscapes                        |      4 |
| Dataset      | MLModelGeneric    | STL - 1 0                         |      4 |
| Dataset      | MLModelGeneric    | HMDB - 5 1                        |      4 |
| Dataset      | Method            | ImageNet                          |     90 |
| Dataset      | Method            | Cityscapes                        |     47 |
| Dataset      | Method            | COCO                              |     46 |
| Dataset      | Method            | Kinetics                          |     44 |
| Dataset      | Method            | DBpedia                           |     32 |
| Dataset      | ModelArchitecture | ImageNet                          |      9 |
| Dataset      | ModelArchitecture | HMDB - 5 1                        |      9 |
| Dataset      | ModelArchitecture | Cityscapes                        |      8 |
| Dataset      | ModelArchitecture | COCO                              |      5 |
| Dataset      | ModelArchitecture | UCF - 1 0 1                       |      3 |
| Dataset      | Task              | Visual Genome                     |      2 |
| Dataset      | Task              | DBpedia                           |      1 |
| Dataset      | Task              | CoQA                              |      1 |
| Dataset      | Task              | -CUBS birds                       |      1 |
| Dataset      | Task              | Stanford Cars                     |      1 |
| Method       | Dataset           | FlowQA                            |      5 |
| Method       | Dataset           | RTN                               |      5 |
| Method       | Dataset           | DenseNet                          |      5 |
| Method       | Dataset           | AlexNet                           |      5 |
| Method       | Dataset           | SFA                               |      4 |
| Method       | DatasetGeneric    | BERT                              |     17 |
| Method       | DatasetGeneric    | data augmentation                 |     16 |
| Method       | DatasetGeneric    | CNN                               |     12 |
| Method       | DatasetGeneric    | domain generalization             |     11 |
| Method       | DatasetGeneric    | domain adaptation                 |      9 |
| Method       | MISSING           | Local contrast normalization      |      1 |
| Method       | MISSING           | Cross entropy loss                |      1 |
| Method       | MISSING           | GCN                               |      1 |
| Method       | MISSING           | ResNet 1 5 2                      |      1 |
| Method       | MISSING           | feature network                   |      1 |
| Method       | MLModel           | ResNet                            |     40 |
| Method       | MLModel           | SBERT                             |     33 |
| Method       | MLModel           | RoBERTa                           |     32 |
| Method       | MLModel           | AlexNet                           |     16 |
| Method       | MLModel           | HRNetV 2                          |     14 |
| Method       | MLModelGeneric    | BERT                              |     72 |
| Method       | MLModelGeneric    | CNN                               |     48 |
| Method       | MLModelGeneric    | CNNs                              |     39 |
| Method       | MLModelGeneric    | GAN                               |     29 |
| Method       | MLModelGeneric    | 3D CNNs                           |     24 |
| Method       | Method            | BERT                              |    131 |
| Method       | Method            | CNN                               |    121 |
| Method       | Method            | Mask R - CNN                      |     88 |
| Method       | Method            | dropout                           |     86 |
| Method       | Method            | Absum                             |     62 |
| Method       | ModelArchitecture | LSTM                              |     97 |
| Method       | ModelArchitecture | CNNs                              |     93 |
| Method       | ModelArchitecture | convolutional layer               |     42 |
| Method       | ModelArchitecture | CNN                               |     41 |
| Method       | ModelArchitecture | CycleGAN                          |     40 |
| Method       | ReferenceLink     | (Res 1 0 1                        |      1 |
| Method       | Task              | object detectors                  |      2 |
| Method       | Task              | domain adaptation                 |      2 |
| Method       | Task              | siamese network                   |      2 |
| Method       | Task              | SVO                               |      2 |
| Method       | Task              | BERT                              |      2 |
| Task         | Dataset           | VQA                               |     10 |
| Task         | Dataset           | classification                    |      1 |
| Task         | Dataset           | ImageNet classification           |      1 |
| Task         | Dataset           | FGVC                              |      1 |
| Task         | Dataset           | image - to - image translation    |      1 |
| Task         | DatasetGeneric    | object detection                  |     11 |
| Task         | DatasetGeneric    | computer vision                   |      7 |
| Task         | DatasetGeneric    | detection                         |      7 |
| Task         | DatasetGeneric    | action recognition                |      6 |
| Task         | DatasetGeneric    | conversational question answering |      5 |
| Task         | MISSING           | semantic segmentation             |      1 |
| Task         | MLModel           | FGVC                              |      2 |
| Task         | MLModel           | SOP                               |      2 |
| Task         | MLModel           | SISR                              |      1 |
| Task         | MLModel           | scene parsing                     |      1 |
| Task         | MLModel           | QG                                |      1 |
| Task         | MLModelGeneric    | QA                                |     13 |
| Task         | MLModelGeneric    | object detection                  |      8 |
| Task         | MLModelGeneric    | recognition                       |      6 |
| Task         | MLModelGeneric    | classification                    |      6 |
| Task         | MLModelGeneric    | question generation               |      6 |
| Task         | Method            | semantic segmentation             |    156 |
| Task         | Method            | instance segmentation             |     78 |
| Task         | Method            | object detection                  |     74 |
| Task         | Method            | classification                    |     64 |
| Task         | Method            | segmentation                      |     62 |
| Task         | ModelArchitecture | semantic segmentation             |     11 |
| Task         | ModelArchitecture | graph reconstruction              |      9 |
| Task         | ModelArchitecture | classification                    |      6 |
| Task         | ModelArchitecture | image - to - image translation    |      5 |
| Task         | ModelArchitecture | FER                               |      4 |
| Task         | Task              | object detection                  |     32 |
| Task         | Task              | image classification              |     20 |
| Task         | Task              | classification                    |     20 |
| Task         | Task              | text detection                    |     18 |
| Task         | Task              | text classification               |     14 |

## RE — Relation Confusion Matrix

**Gold relations:** 8743  
**Predicted relations:** 90  

Rows = gold labels · Columns = predicted labels · NIL = unmatched on the respective side.

|                |   appliedTo |   architecture |   benchmarkFor |   citation |   coreference |   evaluatedOn |   isComparedTo |   trainedOn |   usedFor |   versionOf |   NIL |
|:---------------|------------:|---------------:|---------------:|-----------:|--------------:|--------------:|---------------:|------------:|----------:|------------:|------:|
| Benchmark-For  |           0 |              0 |              0 |          0 |             0 |             0 |              0 |           0 |         0 |           0 |   551 |
| Compare-With   |           0 |              0 |              0 |          0 |             0 |             0 |              2 |           0 |         0 |           0 |   873 |
| Evaluated-With |           2 |              0 |              0 |          0 |             0 |             6 |              0 |           0 |         0 |           0 |   855 |
| Part-Of        |           0 |              0 |              0 |          0 |             0 |             0 |              0 |           0 |         2 |           0 |  1863 |
| SubClass-Of    |           0 |              0 |              0 |          0 |             0 |             0 |              0 |           0 |         0 |           0 |   697 |
| SubTask-Of     |           0 |              0 |              0 |          0 |             0 |             0 |              0 |           0 |         0 |           0 |   210 |
| Synonym-Of     |           0 |              0 |              0 |          0 |            24 |             0 |              0 |           0 |         0 |           0 |   856 |
| Trained-With   |           0 |              0 |              0 |          0 |             0 |             1 |              0 |           3 |         0 |           0 |   400 |
| Used-For       |           4 |              0 |              0 |          0 |             0 |             1 |              0 |           0 |         0 |           0 |  2393 |
| NIL            |           2 |              3 |              3 |          1 |            18 |            11 |              1 |           0 |         5 |           1 |     0 |

## RE — Per-Label Accuracy

| Gold Label     |   Total |   Correct |   Accuracy |
|:---------------|--------:|----------:|-----------:|
| Used-For       |    2398 |         0 |          0 |
| Part-Of        |    1865 |         0 |          0 |
| Synonym-Of     |     880 |         0 |          0 |
| Compare-With   |     875 |         0 |          0 |
| Evaluated-With |     863 |         0 |          0 |
| SubClass-Of    |     697 |         0 |          0 |
| Benchmark-For  |     551 |         0 |          0 |
| Trained-With   |     404 |         0 |          0 |
| SubTask-Of     |     210 |         0 |          0 |

## RE — Examples (top 5 per cell)

| Gold Label     | Pred Label   | Subject → Object                                     |   Freq |
|:---------------|:-------------|:-----------------------------------------------------|-------:|
| Benchmark-For  | NIL          | Cityscapes → semantic segmentation                   |     11 |
| Benchmark-For  | NIL          | CoQA → conversational question answering             |      5 |
| Benchmark-For  | NIL          | QuAC → conversational question answering             |      5 |
| Benchmark-For  | NIL          | SentEval → sentence embeddings                       |      5 |
| Benchmark-For  | NIL          | Cityscapes → segmentation                            |      4 |
| Compare-With   | isComparedTo | XDC → AVTS                                           |      2 |
| Compare-With   | NIL          | FSSD → SSD                                           |     12 |
| Compare-With   | NIL          | Absum → SNC                                          |      8 |
| Compare-With   | NIL          | CuBERT → BiLSTM                                      |      8 |
| Compare-With   | NIL          | Absum → L 1                                          |      7 |
| Compare-With   | NIL          | SNC → L 1                                            |      7 |
| Evaluated-With | appliedTo    | GPT 2 → COSMOS QA                                    |      1 |
| Evaluated-With | appliedTo    | GPT 2 - FT → COSMOS QA                               |      1 |
| Evaluated-With | evaluatedOn  | AVTS → UCF 1 0 1                                     |      1 |
| Evaluated-With | evaluatedOn  | XDC → UCF 1 0 1                                      |      1 |
| Evaluated-With | evaluatedOn  | XDC → HMDB 5 1                                       |      1 |
| Evaluated-With | evaluatedOn  | AVTS → HMDB 5 1                                      |      1 |
| Evaluated-With | evaluatedOn  | ResNeXt - 1 0 1 → UCF - 1 0 1                        |      1 |
| Evaluated-With | NIL          | VQA model → VQA dataset                              |     12 |
| Evaluated-With | NIL          | SRGAN → ImageNet                                     |      6 |
| Evaluated-With | NIL          | CNNs → ImageNet                                      |      6 |
| Evaluated-With | NIL          | VQA model → GBQD                                     |      6 |
| Evaluated-With | NIL          | HED → BSDS 5 0 0                                     |      6 |
| Part-Of        | usedFor      | SGD → DeeplabV 3                                     |      1 |
| Part-Of        | usedFor      | RLSC → GoogLeNet                                     |      1 |
| Part-Of        | NIL          | Absum → adversarial training                         |     10 |
| Part-Of        | NIL          | momentum → SGD                                       |      9 |
| Part-Of        | NIL          | drop - channel → CNNs                                |      9 |
| Part-Of        | NIL          | dropout → CNNs                                       |      8 |
| Part-Of        | NIL          | PointRend → Mask R - CNN                             |      7 |
| SubClass-Of    | NIL          | IDE - ResNet → feature extraction                    |      7 |
| SubClass-Of    | NIL          | drop - path → dropout                                |      5 |
| SubClass-Of    | NIL          | RTN → domain adaptation                              |      4 |
| SubClass-Of    | NIL          | JAN → domain adaptation                              |      4 |
| SubClass-Of    | NIL          | drop - layer → dropout                               |      4 |
| SubTask-Of     | NIL          | object detection → computer vision                   |      6 |
| SubTask-Of     | NIL          | visual recognition → robotics                        |      5 |
| SubTask-Of     | NIL          | image segmentation → computer vision                 |      4 |
| SubTask-Of     | NIL          | 3D semantic mapping → 3D mapping                     |      2 |
| SubTask-Of     | NIL          | semantic segmentation → computer vision              |      2 |
| Synonym-Of     | coreference  | Fashion - MNIST → FMNIST                             |      1 |
| Synonym-Of     | coreference  | Scale Invariant Feature Transform → SIFT             |      1 |
| Synonym-Of     | coreference  | Deformable Parts Model → DPM                         |      1 |
| Synonym-Of     | coreference  | Histogram of Oriented Optical Flow → HOOF            |      1 |
| Synonym-Of     | coreference  | Bayesian Networks → BN                               |      1 |
| Synonym-Of     | NIL          | Convolutional Neural Networks → CNNs                 |     12 |
| Synonym-Of     | NIL          | region proposal network → RPN                        |     10 |
| Synonym-Of     | NIL          | convolutional neural networks → CNNs                 |     10 |
| Synonym-Of     | NIL          | stochastic gradient descent → SGD                    |      9 |
| Synonym-Of     | NIL          | part spatial co - occurrence → PSC                   |      7 |
| Trained-With   | evaluatedOn  | 2D ResNets → ImageNet                                |      1 |
| Trained-With   | trainedOn    | VGG 1 6 → ILSVRC                                     |      1 |
| Trained-With   | trainedOn    | Deconvnet → ILSVRC                                   |      1 |
| Trained-With   | trainedOn    | XDC → IG 6 5 M                                       |      1 |
| Trained-With   | NIL          | VGG - 1 6 → ImageNet                                 |     16 |
| Trained-With   | NIL          | 3D CNNs → Kinetics                                   |     16 |
| Trained-With   | NIL          | XDC → Kinetics                                       |      8 |
| Trained-With   | NIL          | VGG → ImageNet                                       |      7 |
| Trained-With   | NIL          | ResNet - 1 8 → Kinetics                              |      5 |
| Used-For       | appliedTo    | FastText → sentiment analysis                        |      1 |
| Used-For       | appliedTo    | FastText → question answering                        |      1 |
| Used-For       | appliedTo    | ELMo → question answering                            |      1 |
| Used-For       | appliedTo    | BERT → question answering                            |      1 |
| Used-For       | evaluatedOn  | ComboGAN → PACS                                      |      1 |
| Used-For       | NIL          | CNN → semantic segmentation                          |     16 |
| Used-For       | NIL          | Mask R - CNN → instance segmentation                 |     12 |
| Used-For       | NIL          | GPT - 2 → question generation                        |     10 |
| Used-For       | NIL          | BERT → question answering                            |      9 |
| Used-For       | NIL          | Mask R - CNN → text detection                        |      9 |
| NIL            | appliedTo    | Dynamic Bayesian Networks → activity detection       |      1 |
| NIL            | appliedTo    | ULMFiT → text classification                         |      1 |
| NIL            | architecture | FC - DenseNet → DensNet                              |      1 |
| NIL            | architecture | ResNet 1 0 1 → Gated - SCNN                          |      1 |
| NIL            | architecture | DANet → Res 5 0                                      |      1 |
| NIL            | benchmarkFor | MR → Sentiment prediction                            |      1 |
| NIL            | benchmarkFor | CR → Sentiment prediction                            |      1 |
| NIL            | benchmarkFor | SUBJ → Subjectivity prediction                       |      1 |
| NIL            | citation     | DANet → Res 1 0 1                                    |      1 |
| NIL            | coreference  | SST → Stanford Sentiment Treebank                    |      1 |
| NIL            | coreference  | MRPC → Microsoft Research Paraphrase Corpus          |      1 |
| NIL            | coreference  | FCN → FCN                                            |      1 |
| NIL            | coreference  | EncNet → Res 1 0 1                                   |      1 |
| NIL            | coreference  | DAG - RNN → DAG - RNN                                |      1 |
| NIL            | evaluatedOn  | Absum → MNIST                                        |      1 |
| NIL            | evaluatedOn  | Absum → Fashion - MNIST                              |      1 |
| NIL            | evaluatedOn  | Absum → CIFAR 1 0                                    |      1 |
| NIL            | evaluatedOn  | Absum → SVHN                                         |      1 |
| NIL            | evaluatedOn  | SNC → MNIST                                          |      1 |
| NIL            | isComparedTo | SNC → SNC                                            |      1 |
| NIL            | usedFor      | cross - entropy loss → Deconvnet                     |      1 |
| NIL            | usedFor      | Data augmentation → DialateNet                       |      1 |
| NIL            | usedFor      | Data augmentation → ResNet                           |      1 |
| NIL            | usedFor      | feature - based transfer learning → rigion embedding |      1 |
| NIL            | usedFor      | feature - based transfer learning → CoVe             |      1 |
| NIL            | versionOf    | Deconvnet → VGG 1 6                                  |      1 |
