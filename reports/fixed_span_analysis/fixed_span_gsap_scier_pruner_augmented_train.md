# Fixed-Span NER + RE — GSAP on SCIER (pruner_augmented_train)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scier_pruner_augmented_train.json`  
**Gold NER spans:** 18041  
**NER overall accuracy:** 0.482

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MISSING |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |
|:--------|-------------:|----------:|-----------------:|----------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|
| Dataset |           40 |      1719 |              480 |         0 |        85 |               80 |      716 |                  49 |               0 |     51 |
| Method  |            0 |       150 |              297 |         9 |      1313 |             1191 |     5395 |                2974 |               4 |     91 |
| Task    |            1 |        25 |              233 |         1 |         9 |               84 |     1363 |                  96 |               1 |   1584 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | DataSource    | Dataset       | DatasetGeneric   | MISSING   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | ReferenceLink   | Task          |
|:--------|:--------------|:--------------|:-----------------|:----------|:--------------|:-----------------|:--------------|:--------------------|:----------------|:--------------|
| Dataset | 0.079 / 0.864 | 0.125 / 0.882 | 0.511 / 0.624    | —         | 0.399 / 0.554 | 0.405 / 0.591    | 0.534 / 0.544 | 0.645 / 0.459       | —               | 0.466 / 0.555 |
| Method  | —             | 0.268 / 0.631 | 0.514 / 0.564    | —         | 0.176 / 0.768 | 0.408 / 0.679    | 0.415 / 0.777 | 0.350 / 0.782       | 0.841 / 0.590   | 0.422 / 0.557 |
| Task    | 0.969 / 0.262 | 0.300 / 0.632 | 0.487 / 0.593    | —         | 0.643 / 0.443 | 0.668 / 0.456    | 0.492 / 0.693 | 0.648 / 0.548       | 1.000 / 0.279   | 0.253 / 0.863 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| Method       |   11424 |      5395 |      0.472 |
| Task         |    3397 |      1584 |      0.466 |
| Dataset      |    3220 |      1719 |      0.534 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                   |   Freq |
|:-------------|:------------------|:-------------------------------|-------:|
| Dataset      | DataSource        | Freebase                       |      9 |
| Dataset      | DataSource        | DBpedia                        |      7 |
| Dataset      | DataSource        | ConceptNet                     |      5 |
| Dataset      | DataSource        | Wikipedia                      |      4 |
| Dataset      | DataSource        | WordNet                        |      4 |
| Dataset      | Dataset           | ImageNet                       |    134 |
| Dataset      | Dataset           | Cityscapes                     |     40 |
| Dataset      | Dataset           | MNIST                          |     36 |
| Dataset      | Dataset           | SQuAD                          |     32 |
| Dataset      | Dataset           | Kinetics                       |     32 |
| Dataset      | DatasetGeneric    | Cityscapes                     |     24 |
| Dataset      | DatasetGeneric    | ImageNet                       |     20 |
| Dataset      | DatasetGeneric    | VQA dataset                    |     16 |
| Dataset      | DatasetGeneric    | 3 0 0 - W                      |     12 |
| Dataset      | DatasetGeneric    | D BiDAF                        |      9 |
| Dataset      | MLModel           | Clipart                        |      8 |
| Dataset      | MLModel           | ImageNet                       |      5 |
| Dataset      | MLModel           | ActivityNet                    |      5 |
| Dataset      | MLModel           | AffectNet                      |      4 |
| Dataset      | MLModel           | Cityscapes                     |      3 |
| Dataset      | MLModelGeneric    | D RoBERTa                      |     20 |
| Dataset      | MLModelGeneric    | Kinetics                       |      8 |
| Dataset      | MLModelGeneric    | D BERT                         |      8 |
| Dataset      | MLModelGeneric    | Cityscapes                     |      3 |
| Dataset      | MLModelGeneric    | VQA dataset                    |      3 |
| Dataset      | Method            | COCO                           |     38 |
| Dataset      | Method            | ImageNet                       |     29 |
| Dataset      | Method            | Kinetics                       |     26 |
| Dataset      | Method            | DBpedia                        |     24 |
| Dataset      | Method            | Cityscapes                     |     20 |
| Dataset      | ModelArchitecture | COCO                           |      6 |
| Dataset      | ModelArchitecture | ImageNet                       |      6 |
| Dataset      | ModelArchitecture | HMDB - 5 1                     |      6 |
| Dataset      | ModelArchitecture | IMDb                           |      3 |
| Dataset      | ModelArchitecture | Cityscapes                     |      2 |
| Dataset      | Task              | SIMPLEQUESTIONS                |      3 |
| Dataset      | Task              | ImageNet classification        |      3 |
| Dataset      | Task              | COSMOS QA                      |      3 |
| Dataset      | Task              | CS                             |      3 |
| Dataset      | Task              | CoQA                           |      2 |
| Method       | Dataset           | FlowQA                         |      7 |
| Method       | Dataset           | BiDAF                          |      6 |
| Method       | Dataset           | CIDEr                          |      5 |
| Method       | Dataset           | DenseNet                       |      4 |
| Method       | Dataset           | YOLO                           |      3 |
| Method       | DatasetGeneric    | BERT                           |     15 |
| Method       | DatasetGeneric    | CNN                            |     12 |
| Method       | DatasetGeneric    | data augmentation              |     10 |
| Method       | DatasetGeneric    | domain generalization          |      8 |
| Method       | DatasetGeneric    | domain adaptation              |      7 |
| Method       | MISSING           | Local contrast normalization   |      1 |
| Method       | MISSING           | Cross entropy loss             |      1 |
| Method       | MISSING           | GCN                            |      1 |
| Method       | MISSING           | ResNet 1 5 2                   |      1 |
| Method       | MISSING           | feature network                |      1 |
| Method       | MLModel           | BERT                           |     76 |
| Method       | MLModel           | ResNet                         |     37 |
| Method       | MLModel           | SBERT                          |     32 |
| Method       | MLModel           | RoBERTa                        |     31 |
| Method       | MLModel           | HRNetV 2                       |     22 |
| Method       | MLModelGeneric    | BERT                           |     48 |
| Method       | MLModelGeneric    | Faster R - CNN                 |     44 |
| Method       | MLModelGeneric    | Mask R - CNN                   |     26 |
| Method       | MLModelGeneric    | 3D CNNs                        |     24 |
| Method       | MLModelGeneric    | CNNs                           |     23 |
| Method       | Method            | dropout                        |     89 |
| Method       | Method            | BERT                           |     72 |
| Method       | Method            | Absum                          |     62 |
| Method       | Method            | SSD                            |     55 |
| Method       | Method            | CNN                            |     49 |
| Method       | ModelArchitecture | CNN                            |    136 |
| Method       | ModelArchitecture | CNNs                           |    125 |
| Method       | ModelArchitecture | LSTM                           |    110 |
| Method       | ModelArchitecture | convolutional layer            |     44 |
| Method       | ModelArchitecture | GCN                            |     43 |
| Method       | ReferenceLink     | Chisholm and Hachey            |      1 |
| Method       | ReferenceLink     | Guo and Barbosa                |      1 |
| Method       | ReferenceLink     | Ganea and Hofmann              |      1 |
| Method       | ReferenceLink     | (Res 1 0 1                     |      1 |
| Method       | Task              | domain adaptation              |     12 |
| Method       | Task              | CNN                            |      4 |
| Method       | Task              | DA                             |      3 |
| Method       | Task              | DG                             |      3 |
| Method       | Task              | BERT                           |      3 |
| Task         | DataSource        | power grids                    |      1 |
| Task         | Dataset           | VQA                            |      6 |
| Task         | Dataset           | FER                            |      4 |
| Task         | Dataset           | UVOS                           |      4 |
| Task         | Dataset           | FGVC                           |      2 |
| Task         | Dataset           | VIS                            |      2 |
| Task         | DatasetGeneric    | computer vision                |      8 |
| Task         | DatasetGeneric    | object detection               |      7 |
| Task         | DatasetGeneric    | detection                      |      7 |
| Task         | DatasetGeneric    | recognition                    |      6 |
| Task         | DatasetGeneric    | video description              |      5 |
| Task         | MISSING           | semantic segmentation          |      1 |
| Task         | MLModel           | FGVC                           |      2 |
| Task         | MLModel           | SISR                           |      1 |
| Task         | MLModel           | semantic textual similarity    |      1 |
| Task         | MLModel           | AutoML                         |      1 |
| Task         | MLModel           | FGVC - 5 0                     |      1 |
| Task         | MLModelGeneric    | QA                             |      8 |
| Task         | MLModelGeneric    | object detection               |      5 |
| Task         | MLModelGeneric    | recognition                    |      3 |
| Task         | MLModelGeneric    | detection                      |      3 |
| Task         | MLModelGeneric    | NLP                            |      3 |
| Task         | Method            | semantic segmentation          |     83 |
| Task         | Method            | instance segmentation          |     50 |
| Task         | Method            | segmentation                   |     35 |
| Task         | Method            | classification                 |     31 |
| Task         | Method            | computer vision                |     31 |
| Task         | ModelArchitecture | semantic segmentation          |      7 |
| Task         | ModelArchitecture | classification                 |      7 |
| Task         | ModelArchitecture | graph reconstruction           |      7 |
| Task         | ModelArchitecture | image - to - image translation |      4 |
| Task         | ModelArchitecture | QA                             |      3 |
| Task         | ReferenceLink     | against SFA                    |      1 |
| Task         | Task              | semantic segmentation          |     88 |
| Task         | Task              | object detection               |     85 |
| Task         | Task              | classification                 |     58 |
| Task         | Task              | image classification           |     39 |
| Task         | Task              | segmentation                   |     38 |

## RE — Relation Confusion Matrix

**Gold relations:** 8743  
**Predicted relations:** 2118  

Rows = gold labels · Columns = predicted labels · NIL = unmatched on the respective side.

|                |   appliedTo |   architecture |   benchmarkFor |   citation |   coreference |   evaluatedOn |   generatedBy |   isBasedOn |   isComparedTo |   isHyponymOf |   isPartOf |   processed |   sourcedFrom |   trainedOn |   transformedFrom |   usedFor |   versionOf |   NIL |
|:---------------|------------:|---------------:|---------------:|-----------:|--------------:|--------------:|--------------:|------------:|---------------:|--------------:|-----------:|------------:|--------------:|------------:|------------------:|----------:|------------:|------:|
| Benchmark-For  |           2 |              0 |             59 |          0 |             0 |             0 |             0 |           0 |              0 |             0 |          0 |           0 |             0 |           0 |                 0 |         0 |           0 |   490 |
| Compare-With   |           0 |              3 |              0 |          0 |             2 |             0 |             0 |           0 |             70 |             0 |          0 |           0 |             0 |           0 |                 1 |         0 |           0 |   799 |
| Evaluated-With |           2 |              0 |              0 |          0 |             0 |           119 |             0 |           0 |              1 |             0 |          1 |           1 |             0 |           7 |                 0 |         0 |           0 |   732 |
| Part-Of        |           1 |              4 |              0 |          0 |             0 |             0 |             0 |           0 |              3 |             0 |         39 |           0 |             0 |           1 |                 0 |        83 |           0 |  1734 |
| SubClass-Of    |           0 |             23 |              0 |          0 |             0 |             0 |             0 |           1 |              0 |            35 |          9 |           0 |             2 |           1 |                 0 |         4 |           3 |   619 |
| SubTask-Of     |           0 |              0 |              1 |          0 |             0 |             0 |             0 |           0 |              0 |            15 |          0 |           0 |             0 |           0 |                 0 |         0 |           0 |   194 |
| Synonym-Of     |           0 |              2 |              1 |          0 |           343 |             0 |             0 |           0 |              0 |             4 |          0 |           0 |             0 |           0 |                 0 |         4 |           0 |   526 |
| Trained-With   |           0 |              0 |              0 |          0 |             4 |             6 |             0 |           0 |              0 |             0 |          0 |           0 |             0 |          66 |                 1 |         0 |           0 |   327 |
| Used-For       |         280 |              1 |              3 |          0 |             0 |             3 |             0 |           0 |              0 |             3 |          0 |           0 |             0 |           0 |                 0 |        11 |           0 |  2097 |
| NIL            |         109 |            186 |             13 |          1 |           332 |            43 |             3 |          19 |             36 |            11 |         13 |           0 |             1 |          22 |                 4 |        99 |           1 |     0 |

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

| Gold Label     | Pred Label      | Subject → Object                                         |   Freq |
|:---------------|:----------------|:---------------------------------------------------------|-------:|
| Benchmark-For  | appliedTo       | MS COCO → object detection                               |      1 |
| Benchmark-For  | appliedTo       | MS COCO → instance segmentation                          |      1 |
| Benchmark-For  | benchmarkFor    | Cityscapes → semantic segmentation                       |      3 |
| Benchmark-For  | benchmarkFor    | LIP → semantic segmentation                              |      2 |
| Benchmark-For  | benchmarkFor    | ImageNet → image classification                          |      2 |
| Benchmark-For  | benchmarkFor    | SQuAD 1. 1 → Question answering                          |      2 |
| Benchmark-For  | benchmarkFor    | PAS - CAL Context → semantic segmentation                |      1 |
| Benchmark-For  | NIL             | Cityscapes → semantic segmentation                       |      8 |
| Benchmark-For  | NIL             | CoQA → conversational question answering                 |      5 |
| Benchmark-For  | NIL             | QuAC → conversational question answering                 |      5 |
| Benchmark-For  | NIL             | SentEval → sentence embeddings                           |      5 |
| Benchmark-For  | NIL             | ADE 2 0 K → semantic segmentation                        |      4 |
| Compare-With   | architecture    | SPP → R - CNN                                            |      1 |
| Compare-With   | architecture    | Fast - RCNN → R - CNN                                    |      1 |
| Compare-With   | architecture    | Transformer → GPT - 2                                    |      1 |
| Compare-With   | coreference     | OCNet → OCNet                                            |      1 |
| Compare-With   | coreference     | CPM → CPM                                                |      1 |
| Compare-With   | isComparedTo    | HRNetV 2 → HRNetV 1                                      |      3 |
| Compare-With   | isComparedTo    | SBERT → Universal Sentence Encoder                       |      2 |
| Compare-With   | isComparedTo    | CuBERT → BiLSTM                                          |      2 |
| Compare-With   | isComparedTo    | XDC → AVTS                                               |      2 |
| Compare-With   | isComparedTo    | FSSD → SSD                                               |      2 |
| Compare-With   | transformedFrom | CIFAR 1 0 0 → CIFAR - 1 0                                |      1 |
| Compare-With   | NIL             | FSSD → SSD                                               |     10 |
| Compare-With   | NIL             | Absum → SNC                                              |      8 |
| Compare-With   | NIL             | Absum → L 1                                              |      7 |
| Compare-With   | NIL             | SNC → L 1                                                |      7 |
| Compare-With   | NIL             | Absum → WD                                               |      6 |
| Evaluated-With | appliedTo       | GPT 2 → COSMOS QA                                        |      1 |
| Evaluated-With | appliedTo       | GPT 2 - FT → COSMOS QA                                   |      1 |
| Evaluated-With | evaluatedOn     | PGD → CIFAR 1 0                                          |      3 |
| Evaluated-With | evaluatedOn     | XDC → UCF 1 0 1                                          |      3 |
| Evaluated-With | evaluatedOn     | XDC → HMDB 5 1                                           |      3 |
| Evaluated-With | evaluatedOn     | XDC → ESC 5 0                                            |      2 |
| Evaluated-With | evaluatedOn     | XDC → DCASE                                              |      2 |
| Evaluated-With | isComparedTo    | RoBERTa → D RoBERTa                                      |      1 |
| Evaluated-With | isPartOf        | AQA → Yahoo/Case 1                                       |      1 |
| Evaluated-With | processed       | PGD → FMNIST                                             |      1 |
| Evaluated-With | trainedOn       | PGD → MNIST                                              |      1 |
| Evaluated-With | trainedOn       | PGD → FMNIST                                             |      1 |
| Evaluated-With | trainedOn       | SGGAN → CelebA                                           |      1 |
| Evaluated-With | trainedOn       | 3D CNNs → Kinetics                                       |      1 |
| Evaluated-With | trainedOn       | ResNets → ImageNet                                       |      1 |
| Evaluated-With | NIL             | VQA model → VQA dataset                                  |     12 |
| Evaluated-With | NIL             | SRGAN → ImageNet                                         |      6 |
| Evaluated-With | NIL             | CNNs → ImageNet                                          |      6 |
| Evaluated-With | NIL             | VQA model → GBQD                                         |      6 |
| Evaluated-With | NIL             | HED → BSDS 5 0 0                                         |      6 |
| Part-Of        | appliedTo       | policy gradient → QA                                     |      1 |
| Part-Of        | architecture    | ResNet - 5 0 → FPN                                       |      1 |
| Part-Of        | architecture    | PointRend → CNN                                          |      1 |
| Part-Of        | architecture    | discriminators D → PatchGAN                              |      1 |
| Part-Of        | architecture    | deep layer aggregation → CNNs                            |      1 |
| Part-Of        | isComparedTo    | CARAFE → Faster RCNN                                     |      1 |
| Part-Of        | isComparedTo    | CARAFE → Mask RCNN                                       |      1 |
| Part-Of        | isComparedTo    | ResNet → PSPNet                                          |      1 |
| Part-Of        | isPartOf        | downsampling blocks → FCN                                |      3 |
| Part-Of        | isPartOf        | convolutional block → FCN                                |      2 |
| Part-Of        | isPartOf        | generator → GANs                                         |      2 |
| Part-Of        | isPartOf        | convolutional layers → CNNs                              |      1 |
| Part-Of        | isPartOf        | Inception module → GoogLeNet                             |      1 |
| Part-Of        | trainedOn       | ResNet 5 0 → ImageNet                                    |      1 |
| Part-Of        | usedFor         | drop - path → CNNs                                       |      2 |
| Part-Of        | usedFor         | RLSC → GoogLeNet                                         |      2 |
| Part-Of        | usedFor         | KS graph → KSSNet                                        |      2 |
| Part-Of        | usedFor         | word embeddings → logistic regression                    |      1 |
| Part-Of        | usedFor         | 1 × 1 convolution → R - ASPP                             |      1 |
| Part-Of        | NIL             | Absum → adversarial training                             |     10 |
| Part-Of        | NIL             | momentum → SGD                                           |      9 |
| Part-Of        | NIL             | drop - channel → CNNs                                    |      9 |
| Part-Of        | NIL             | PointRend → Mask R - CNN                                 |      7 |
| Part-Of        | NIL             | dropout → CNNs                                           |      7 |
| SubClass-Of    | architecture    | GoogLeNet → CNNs                                         |      2 |
| SubClass-Of    | architecture    | AlexNet → CNNs                                           |      2 |
| SubClass-Of    | architecture    | R - ASPP → Atrous Spatial Pyramid Pooling module         |      1 |
| SubClass-Of    | architecture    | Se - manticFPN → encoder - decoder                       |      1 |
| SubClass-Of    | architecture    | Region - based CNN → CNN                                 |      1 |
| SubClass-Of    | isBasedOn       | MnasNet → MobileNetV 2                                   |      1 |
| SubClass-Of    | isHyponymOf     | Skip - Gram → deep learning                              |      1 |
| SubClass-Of    | isHyponymOf     | Convolutional Neural Network → deep neural network       |      1 |
| SubClass-Of    | isHyponymOf     | deep learning → machine learning                         |      1 |
| SubClass-Of    | isHyponymOf     | ResNeXt → CNNs                                           |      1 |
| SubClass-Of    | isHyponymOf     | recurrent neural networks → neural networks              |      1 |
| SubClass-Of    | isPartOf        | group convolution → CNNs                                 |      1 |
| SubClass-Of    | isPartOf        | VGG - 1 1 → CNN                                          |      1 |
| SubClass-Of    | isPartOf        | WRN - 4 0 - 4 → CNN                                      |      1 |
| SubClass-Of    | isPartOf        | DenseNet - L 1 0 0 - K 1 2 → CNN                         |      1 |
| SubClass-Of    | isPartOf        | YTVOS - moving → YTVOS                                   |      1 |
| SubClass-Of    | sourcedFrom     | SIMPLEQUESTIONS → Freebase                               |      1 |
| SubClass-Of    | sourcedFrom     | WNED - WIKI → Wikipedia                                  |      1 |
| SubClass-Of    | trainedOn       | YOLOv 2 → YOLO                                           |      1 |
| SubClass-Of    | usedFor         | factorization based → graph embedding                    |      1 |
| SubClass-Of    | usedFor         | drop - neuron → drop - operations                        |      1 |
| SubClass-Of    | usedFor         | dropchannel → drop - operations                          |      1 |
| SubClass-Of    | usedFor         | random cropping → data augmentation                      |      1 |
| SubClass-Of    | versionOf       | HRNetV 2 → HRNetV 1                                      |      1 |
| SubClass-Of    | versionOf       | HRNetV 2 p → HRNetV 1                                    |      1 |
| SubClass-Of    | versionOf       | iCWT → iCubWorld                                         |      1 |
| SubClass-Of    | NIL             | IDE - ResNet → feature extraction                        |      7 |
| SubClass-Of    | NIL             | drop - path → dropout                                    |      5 |
| SubClass-Of    | NIL             | RTN → domain adaptation                                  |      4 |
| SubClass-Of    | NIL             | JAN → domain adaptation                                  |      4 |
| SubClass-Of    | NIL             | drop - layer → dropout                                   |      4 |
| SubTask-Of     | benchmarkFor    | UVOS → Video Object Segmentation                         |      1 |
| SubTask-Of     | isHyponymOf     | anomaly detection → spatial - temporal problems          |      1 |
| SubTask-Of     | isHyponymOf     | missing data imputation → spatial - temporal problems    |      1 |
| SubTask-Of     | isHyponymOf     | time series clustering → spatial - temporal problems     |      1 |
| SubTask-Of     | isHyponymOf     | time series classification → spatial - temporal problems |      1 |
| SubTask-Of     | isHyponymOf     | holistic edge detection → edge detection                 |      1 |
| SubTask-Of     | NIL             | object detection → computer vision                       |      6 |
| SubTask-Of     | NIL             | visual recognition → robotics                            |      5 |
| SubTask-Of     | NIL             | image segmentation → computer vision                     |      4 |
| SubTask-Of     | NIL             | 3D semantic mapping → 3D mapping                         |      2 |
| SubTask-Of     | NIL             | semantic segmentation → computer vision                  |      2 |
| Synonym-Of     | architecture    | Denoising autoencoder → C - CNN - LSTM - DA              |      1 |
| Synonym-Of     | architecture    | MLP → multi - layer perceptron                           |      1 |
| Synonym-Of     | benchmarkFor    | iCubWorld identification → iCWT i d                      |      1 |
| Synonym-Of     | coreference     | Pyramid Attention Network → PAN                          |      6 |
| Synonym-Of     | coreference     | region proposal network → RPN                            |      5 |
| Synonym-Of     | coreference     | Recurrent Neural Network → RNN                           |      4 |
| Synonym-Of     | coreference     | stochastic gradient descent → SGD                        |      4 |
| Synonym-Of     | coreference     | Generative Adversarial Networks → GANs                   |      4 |
| Synonym-Of     | isHyponymOf     | neuron level dropout → drop - neuron                     |      1 |
| Synonym-Of     | isHyponymOf     | Video description → story telling                        |      1 |
| Synonym-Of     | isHyponymOf     | LSTMs → Long Short - Term Memory Networks                |      1 |
| Synonym-Of     | isHyponymOf     | graph convolutional network → GCN                        |      1 |
| Synonym-Of     | usedFor         | Quasi - Hyperbolic Adam → QHAdam                         |      1 |
| Synonym-Of     | usedFor         | AggMo → Aggregated Momentum                              |      1 |
| Synonym-Of     | usedFor         | QHM → Quasi - Hyperbolic Momentum                        |      1 |
| Synonym-Of     | usedFor         | GConv → Graph Convolution                                |      1 |
| Synonym-Of     | NIL             | convolutional neural networks → CNNs                     |      9 |
| Synonym-Of     | NIL             | Convolutional Neural Networks → CNNs                     |      9 |
| Synonym-Of     | NIL             | part spatial co - occurrence → PSC                       |      6 |
| Synonym-Of     | NIL             | stochastic gradient descent → SGD                        |      5 |
| Synonym-Of     | NIL             | region proposal network → RPN                            |      5 |
| Trained-With   | coreference     | CIFAR 1 0 0 -VGG 1 6 → CIFAR 1 0 0                       |      1 |
| Trained-With   | coreference     | PTB -LSTM → PTB                                          |      1 |
| Trained-With   | coreference     | MNIST -VAE → MNIST                                       |      1 |
| Trained-With   | coreference     | CIFAR 1 0 -NCSN → CIFAR 1 0                              |      1 |
| Trained-With   | evaluatedOn     | 2D ResNets → ImageNet                                    |      2 |
| Trained-With   | evaluatedOn     | VGG 1 9 → ImageNet                                       |      1 |
| Trained-With   | evaluatedOn     | CPM → BBC Pose                                           |      1 |
| Trained-With   | evaluatedOn     | BERT - CDPT → Yelp P.                                    |      1 |
| Trained-With   | evaluatedOn     | BERT - CDPT → AG                                         |      1 |
| Trained-With   | trainedOn       | XDC → IG 6 5 M                                           |      4 |
| Trained-With   | trainedOn       | 3D CNNs → Kinetics                                       |      2 |
| Trained-With   | trainedOn       | 3D CNNs → UCF - 1 0 1                                    |      2 |
| Trained-With   | trainedOn       | 3D CNNs → HMDB - 5 1                                     |      2 |
| Trained-With   | trainedOn       | 3D CNNs → ActivityNet                                    |      2 |
| Trained-With   | transformedFrom | S 3 D - G RGB+Flow streams → Kinetics                    |      1 |
| Trained-With   | NIL             | VGG - 1 6 → ImageNet                                     |     16 |
| Trained-With   | NIL             | 3D CNNs → Kinetics                                       |     14 |
| Trained-With   | NIL             | XDC → Kinetics                                           |      7 |
| Trained-With   | NIL             | VGG → ImageNet                                           |      6 |
| Trained-With   | NIL             | ResNet - 1 8 → Kinetics                                  |      5 |
| Used-For       | appliedTo       | HRNetV 2 → semantic segmentation                         |      4 |
| Used-For       | appliedTo       | CNN → semantic segmentation                              |      3 |
| Used-For       | appliedTo       | BERT → question answering                                |      3 |
| Used-For       | appliedTo       | UniPose → pose estimation                                |      3 |
| Used-For       | appliedTo       | GALD → object detection                                  |      3 |
| Used-For       | architecture    | PAN → multi - scale convolutional feature pyramid        |      1 |
| Used-For       | benchmarkFor    | COCO → object detection                                  |      1 |
| Used-For       | benchmarkFor    | Modanet → object detection                               |      1 |
| Used-For       | benchmarkFor    | Kinetics → action recognition                            |      1 |
| Used-For       | evaluatedOn     | GPT - 2 → SQuAD                                          |      1 |
| Used-For       | evaluatedOn     | AlexNet → remote sensing image captioning                |      1 |
| Used-For       | evaluatedOn     | ComboGAN → PACS                                          |      1 |
| Used-For       | isHyponymOf     | quantization → model compression                         |      1 |
| Used-For       | isHyponymOf     | pruning → model compression                              |      1 |
| Used-For       | isHyponymOf     | low - rank decomposition → model compression             |      1 |
| Used-For       | usedFor         | data augmentation → CNNs                                 |      2 |
| Used-For       | usedFor         | average BERT embeddings → sentence embeddings            |      1 |
| Used-For       | usedFor         | selective search → R - CNN                               |      1 |
| Used-For       | usedFor         | max - pooling → unpooling                                |      1 |
| Used-For       | usedFor         | deep learning → computer vision                          |      1 |
| Used-For       | NIL             | CNN → semantic segmentation                              |     13 |
| Used-For       | NIL             | Mask R - CNN → instance segmentation                     |     10 |
| Used-For       | NIL             | GPT - 2 → question generation                            |      9 |
| Used-For       | NIL             | BERT → entity embeddings                                 |      9 |
| Used-For       | NIL             | Mask R - CNN → text detection                            |      8 |
| NIL            | appliedTo       | DNNs → computer vision                                   |      2 |
| NIL            | appliedTo       | FCNs → semantic segmentation                             |      2 |
| NIL            | appliedTo       | CNNs → object detection                                  |      2 |
| NIL            | appliedTo       | CARAFE → semantic segmentation                           |      2 |
| NIL            | appliedTo       | CARAFE → image inpainting                                |      2 |
| NIL            | architecture    | Mask R - CNN → Pyramid Attention Network                 |      3 |
| NIL            | architecture    | VGG 1 6 → fully connected layers                         |      3 |
| NIL            | architecture    | GridNet → U - Nets                                       |      2 |
| NIL            | architecture    | LSTM → LSTM                                              |      2 |
| NIL            | architecture    | VGG 1 6 - MC → convolutional layer                       |      2 |
| NIL            | benchmarkFor    | WFLW → semantic segmentation                             |      1 |
| NIL            | benchmarkFor    | MR → Sentiment prediction                                |      1 |
| NIL            | benchmarkFor    | CR → Sentiment prediction                                |      1 |
| NIL            | benchmarkFor    | SUBJ → Subjectivity prediction                           |      1 |
| NIL            | benchmarkFor    | MPII → pose estimation                                   |      1 |
| NIL            | citation        | DANet → Res 1 0 1                                        |      1 |
| NIL            | coreference     | BERT → BERT                                              |     11 |
| NIL            | coreference     | ImageNet → ImageNet                                      |      8 |
| NIL            | coreference     | LSTM → LSTM                                              |      8 |
| NIL            | coreference     | CNN → CNN                                                |      6 |
| NIL            | coreference     | Mask R - CNN → Mask R - CNN                              |      5 |
| NIL            | evaluatedOn     | ResNet → LIP                                             |      1 |
| NIL            | evaluatedOn     | HRNetV 1 - W 3 2 → COCO val                              |      1 |
| NIL            | evaluatedOn     | sentence embeddings → SentEval                           |      1 |
| NIL            | evaluatedOn     | SBERT → MR                                               |      1 |
| NIL            | evaluatedOn     | SBERT → CR                                               |      1 |
| NIL            | generatedBy     | PDB → data augmentation                                  |      1 |
| NIL            | generatedBy     | COCO test - dev → BN                                     |      1 |
| NIL            | generatedBy     | BN → Momentum                                            |      1 |
| NIL            | isBasedOn       | MobileNetV 3 - Small → MobileNetV 2                      |      1 |
| NIL            | isBasedOn       | SemanticFusion → deconvolutional neural networks         |      1 |
| NIL            | isBasedOn       | R - FCN → ResNet 1 0 1                                   |      1 |
| NIL            | isBasedOn       | ResNeXt → Wide Residual Networks                         |      1 |
| NIL            | isBasedOn       | OCNet → SuperNet                                         |      1 |
| NIL            | isComparedTo    | 3D CNNs → 2D CNNs                                        |      2 |
| NIL            | isComparedTo    | HRNet - Wx - C → HRNet - Wx - Ci                         |      1 |
| NIL            | isComparedTo    | HRNet - Wx - C → HRNet - Wx - Cii                        |      1 |
| NIL            | isComparedTo    | BiGRU → BiLSTM                                           |      1 |
| NIL            | isComparedTo    | CM → AdamW                                               |      1 |
| NIL            | isHyponymOf     | holistic edge detection → edge detection                 |      1 |
| NIL            | isHyponymOf     | LSTM → recurrent neural network                          |      1 |
| NIL            | isHyponymOf     | ArtGAN - AE → autoencoder - based discriminator          |      1 |
| NIL            | isHyponymOf     | ArtGAN - DFM → autoencoder - based discriminator         |      1 |
| NIL            | isHyponymOf     | convolutional networks → FCNs                            |      1 |
| NIL            | isPartOf        | GTA 2 CS → GTA 5                                         |      1 |
| NIL            | isPartOf        | GTA 2 CS → GTA 2 CS                                      |      1 |
| NIL            | isPartOf        | convolutional layer → CNNs                               |      1 |
| NIL            | isPartOf        | SYN - THIA → ImageNet                                    |      1 |
| NIL            | isPartOf        | Occlusion - FERPlus → RAF - DB                           |      1 |
| NIL            | sourcedFrom     | SIMPLEDBPEDIAQA → Freebase                               |      1 |
| NIL            | trainedOn       | generative modeling → MNIST                              |      1 |
| NIL            | trainedOn       | generative modeling → CIFAR 1 0                          |      1 |
| NIL            | trainedOn       | Sketch - 2 5 0 → Caltech 2 5 6                           |      1 |
| NIL            | trainedOn       | HRNetV 2 - W 3 2 → ImageNet                              |      1 |
| NIL            | trainedOn       | sentence embeddings → SNLI                               |      1 |
| NIL            | transformedFrom | ImageNet → VGG - 1 6                                     |      1 |
| NIL            | transformedFrom | SFEW → AFEW                                              |      1 |
| NIL            | transformedFrom | CIFAR - 1 0 → CIFAR - 1 0                                |      1 |
| NIL            | transformedFrom | NaturalQuestions → SQuAD                                 |      1 |
| NIL            | usedFor         | entity embeddings → BERT                                 |      2 |
| NIL            | usedFor         | Kinetics → 3D CNNs                                       |      2 |
| NIL            | usedFor         | Word 2 Vec → GrOVLE                                      |      2 |
| NIL            | usedFor         | global pooling → HRNet - Wx - Cii                        |      1 |
| NIL            | usedFor         | SGD → DNNs                                               |      1 |
| NIL            | versionOf       | Deconvnet → VGG 1 6                                      |      1 |
