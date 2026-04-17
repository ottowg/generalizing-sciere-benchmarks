# Fixed-Span NER + RE — GSAP on SCIER (test)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scier_test.jsonl`  
**Gold NER spans:** 2948  
**NER overall accuracy:** 0.395

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MISSING |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|----------:|-----------------:|---------:|--------------------:|-------:|
| Dataset |        60 |               30 |         0 |        17 |               10 |      234 |                  15 |      4 |
| Method  |         4 |               24 |        39 |        96 |              263 |     1023 |                 436 |      5 |
| Task    |         0 |               33 |         3 |         0 |               82 |      460 |                  28 |     82 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MISSING   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:----------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| Dataset | 0.076 / 0.440 | 0.042 / 0.454    | —         | 0.059 / 0.358 | 0.019 / 0.346    | 0.066 / 0.539 | 0.074 / 0.407       | 0.044 / 0.298 |
| Method  | 0.037 / 0.263 | 0.043 / 0.442    | —         | 0.235 / 0.499 | 0.073 / 0.517    | 0.074 / 0.645 | 0.102 / 0.596       | 0.554 / 0.695 |
| Task    | —             | 0.047 / 0.522    | —         | —             | 0.029 / 0.496    | 0.038 / 0.621 | 0.048 / 0.468       | 0.133 / 0.566 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| Method       |    1890 |      1023 |      0.541 |
| Task         |     688 |        82 |      0.119 |
| Dataset      |     370 |        60 |      0.162 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                       |   Freq |
|:-------------|:------------------|:-----------------------------------|-------:|
| Dataset      | Dataset           | OULU - NPU                         |      9 |
| Dataset      | Dataset           | PASCAL VOC                         |      6 |
| Dataset      | Dataset           | Indian Pines                       |      5 |
| Dataset      | Dataset           | ReplayAttack                       |      3 |
| Dataset      | Dataset           | ImageNet                           |      3 |
| Dataset      | DatasetGeneric    | KITTI                              |      5 |
| Dataset      | DatasetGeneric    | Indian Pines                       |      4 |
| Dataset      | DatasetGeneric    | Internet Movie Database            |      1 |
| Dataset      | DatasetGeneric    | Large Movie Review Dataset v 1 . 0 |      1 |
| Dataset      | DatasetGeneric    | Wikipedia dumps                    |      1 |
| Dataset      | MLModel           | N - Cars                           |      4 |
| Dataset      | MLModel           | PASCAL                             |      3 |
| Dataset      | MLModel           | ImageNet                           |      2 |
| Dataset      | MLModel           | KITTI                              |      2 |
| Dataset      | MLModel           | N - Calthec 1 0 1                  |      1 |
| Dataset      | MLModelGeneric    | N - Caltech 1 0 1                  |      2 |
| Dataset      | MLModelGeneric    | MultiNLI                           |      1 |
| Dataset      | MLModelGeneric    | German - English WMT 1 5 Task 3    |      1 |
| Dataset      | MLModelGeneric    | BioASQ                             |      1 |
| Dataset      | MLModelGeneric    | N - MNIST                          |      1 |
| Dataset      | Method            | OULU - NPU                         |     29 |
| Dataset      | Method            | Replay - Attack                    |     18 |
| Dataset      | Method            | N - Cars                           |     11 |
| Dataset      | Method            | FlyingChairs                       |      9 |
| Dataset      | Method            | Sintel                             |      9 |
| Dataset      | ModelArchitecture | Weibo                              |      4 |
| Dataset      | ModelArchitecture | KITTI                              |      4 |
| Dataset      | ModelArchitecture | RCV 1                              |      1 |
| Dataset      | ModelArchitecture | MVSEC                              |      1 |
| Dataset      | ModelArchitecture | Caltech - 1 0 1                    |      1 |
| Dataset      | Task              | IMDb                               |      2 |
| Dataset      | Task              | VOC                                |      1 |
| Dataset      | Task              | University of Pavia                |      1 |
| Method       | Dataset           | MatConvNet                         |      1 |
| Method       | Dataset           | CAD - GCN                          |      1 |
| Method       | Dataset           | GCN                                |      1 |
| Method       | Dataset           | SDP+CRC                            |      1 |
| Method       | DatasetGeneric    | LBP                                |      4 |
| Method       | DatasetGeneric    | CAD - GCN                          |      3 |
| Method       | DatasetGeneric    | generator                          |      2 |
| Method       | DatasetGeneric    | Data augmentation                  |      2 |
| Method       | DatasetGeneric    | Nearest Neighbors classifiers      |      1 |
| Method       | MISSING           | Conv                               |      8 |
| Method       | MISSING           | BN                                 |      6 |
| Method       | MISSING           | lReLU                              |      4 |
| Method       | MISSING           | Residual                           |      2 |
| Method       | MISSING           | feature extraction                 |      2 |
| Method       | MLModel           | AlexNet                            |      9 |
| Method       | MLModel           | ResNet - EST                       |      8 |
| Method       | MLModel           | ResNet                             |      7 |
| Method       | MLModel           | ResNet - Ev 2 Vid                  |      7 |
| Method       | MLModel           | Matrix - LSTM                      |      5 |
| Method       | MLModelGeneric    | BERT                               |     17 |
| Method       | MLModelGeneric    | CNN                                |     17 |
| Method       | MLModelGeneric    | Transformer                        |      6 |
| Method       | MLModelGeneric    | Matching Nets                      |      5 |
| Method       | MLModelGeneric    | Faster R - CNN                     |      5 |
| Method       | Method            | word embeddings                    |     39 |
| Method       | Method            | CAD - GCN                          |     33 |
| Method       | Method            | CNN                                |     24 |
| Method       | Method            | BERT                               |     23 |
| Method       | Method            | SVM                                |     23 |
| Method       | ModelArchitecture | LSTM                               |     36 |
| Method       | ModelArchitecture | CNN                                |     18 |
| Method       | ModelArchitecture | Matrix - LSTM                      |     16 |
| Method       | ModelArchitecture | AlexNet                            |     12 |
| Method       | ModelArchitecture | BN                                 |     12 |
| Method       | Task              | OCR                                |      2 |
| Method       | Task              | machine learning                   |      1 |
| Method       | Task              | fastText                           |      1 |
| Method       | Task              | Perspectiveaware scene parsing     |      1 |
| Task         | DatasetGeneric    | medical image analysis             |      3 |
| Task         | DatasetGeneric    | image segmentation                 |      2 |
| Task         | DatasetGeneric    | next sentence prediction           |      1 |
| Task         | DatasetGeneric    | face PAD                           |      1 |
| Task         | DatasetGeneric    | classification of scene images     |      1 |
| Task         | MISSING           | computer vision                    |      1 |
| Task         | MISSING           | image segmentation                 |      1 |
| Task         | MISSING           | segmentation                       |      1 |
| Task         | MLModelGeneric    | segmentation                       |      9 |
| Task         | MLModelGeneric    | classification                     |      6 |
| Task         | MLModelGeneric    | object detection                   |      6 |
| Task         | MLModelGeneric    | computer vision                    |      5 |
| Task         | MLModelGeneric    | sentiment analysis                 |      4 |
| Task         | Method            | classification                     |     46 |
| Task         | Method            | HTC                                |     25 |
| Task         | Method            | semantic segmentation              |     17 |
| Task         | Method            | face PAD                           |     17 |
| Task         | Method            | gesture recognition                |     17 |
| Task         | ModelArchitecture | segmentation                       |      7 |
| Task         | ModelArchitecture | face PAD                           |      4 |
| Task         | ModelArchitecture | semantic segmentation              |      2 |
| Task         | ModelArchitecture | classification                     |      2 |
| Task         | ModelArchitecture | HTC                                |      1 |
| Task         | Task              | classification                     |     22 |
| Task         | Task              | image segmentation                 |      5 |
| Task         | Task              | TC                                 |      4 |
| Task         | Task              | image classification               |      4 |
| Task         | Task              | segmentation                       |      4 |

## RE — Relation Confusion Matrix

**Gold relations:** 1626  
**Predicted relations:** 18  

Rows = gold labels · Columns = predicted labels · NIL = unmatched on the respective side.

|                |   appliedTo |   architecture |   coreference |   isBasedOn |   isHyponymOf |   NIL |
|:---------------|------------:|---------------:|--------------:|------------:|--------------:|------:|
| Benchmark-For  |           0 |              0 |             0 |           0 |             0 |    85 |
| Compare-With   |           0 |              0 |             0 |           0 |             0 |   114 |
| Evaluated-With |           0 |              0 |             0 |           0 |             0 |   131 |
| Part-Of        |           0 |              0 |             0 |           0 |             0 |   304 |
| SubClass-Of    |           0 |              0 |             0 |           0 |             0 |   176 |
| SubTask-Of     |           0 |              0 |             0 |           0 |             0 |    65 |
| Synonym-Of     |           1 |              0 |             8 |           0 |             0 |   161 |
| Trained-With   |           0 |              0 |             0 |           0 |             0 |    35 |
| Used-For       |           3 |              0 |             0 |           0 |             0 |   543 |
| NIL            |           0 |              2 |             1 |           1 |             2 |     0 |

## RE — Per-Label Accuracy

| Gold Label     |   Total |   Correct |   Accuracy |
|:---------------|--------:|----------:|-----------:|
| Used-For       |     546 |         0 |          0 |
| Part-Of        |     304 |         0 |          0 |
| SubClass-Of    |     176 |         0 |          0 |
| Synonym-Of     |     170 |         0 |          0 |
| Evaluated-With |     131 |         0 |          0 |
| Compare-With   |     114 |         0 |          0 |
| Benchmark-For  |      85 |         0 |          0 |
| SubTask-Of     |      65 |         0 |          0 |
| Trained-With   |      35 |         0 |          0 |

## RE — Examples (top 5 per cell)

| Gold Label     | Pred Label   | Subject → Object                                                |   Freq |
|:---------------|:-------------|:----------------------------------------------------------------|-------:|
| Benchmark-For  | NIL          | OULU - NPU → face PAD                                           |      5 |
| Benchmark-For  | NIL          | Replay - Attack → face PAD                                      |      4 |
| Benchmark-For  | NIL          | LSHTC → HTC                                                     |      2 |
| Benchmark-For  | NIL          | Internet Movie Database → classification                        |      2 |
| Benchmark-For  | NIL          | MVSEC → optical flow estimation                                 |      2 |
| Compare-With   | NIL          | GS - EC → GS - GR                                               |      4 |
| Compare-With   | NIL          | LSTM → BERT                                                     |      4 |
| Compare-With   | NIL          | S 2 GCN → CAD - GCN                                             |      3 |
| Compare-With   | NIL          | GCN → CAD - GCN                                                 |      3 |
| Compare-With   | NIL          | GS - GR → GS - EC attacks                                       |      2 |
| Evaluated-With | NIL          | face PAD algorithm → Replay - Attack                            |      4 |
| Evaluated-With | NIL          | face PAD algorithm → OULU - NPU                                 |      4 |
| Evaluated-With | NIL          | CAD - GCN → Indian Pines                                        |      4 |
| Evaluated-With | NIL          | CAD - GCN → University of Pavia                                 |      4 |
| Evaluated-With | NIL          | CAD - GCN → Salinas                                             |      4 |
| Part-Of        | NIL          | Conv → Residual                                                 |     18 |
| Part-Of        | NIL          | BN → Residual                                                   |     16 |
| Part-Of        | NIL          | lReLU → Residual                                                |      9 |
| Part-Of        | NIL          | dropout → Glynn CNN                                             |      4 |
| Part-Of        | NIL          | convolutional layers → color - liked space generator            |      4 |
| SubClass-Of    | NIL          | FastText → word embedding generator                             |      2 |
| SubClass-Of    | NIL          | word 2 vec → word embeddings                                    |      2 |
| SubClass-Of    | NIL          | LSTM → convolutional filter                                     |      2 |
| SubClass-Of    | NIL          | AlexNet → CNN                                                   |      2 |
| SubClass-Of    | NIL          | GoogLeNet → CNN                                                 |      2 |
| SubTask-Of     | NIL          | sentiment analysis → classification                             |      3 |
| SubTask-Of     | NIL          | machine translation → natural language processing               |      2 |
| SubTask-Of     | NIL          | action recognition → computer vision                            |      2 |
| SubTask-Of     | NIL          | text classification → natural language processing               |      1 |
| SubTask-Of     | NIL          | sequence - to - sequence problems → NLP                         |      1 |
| Synonym-Of     | appliedTo    | FoveaNet → Perspectiveaware scene parsing                       |      1 |
| Synonym-Of     | coreference  | Expectation - Maximization Attention → EMANet                   |      1 |
| Synonym-Of     | coreference  | Criss - Cross Attention Network → CCNet                         |      1 |
| Synonym-Of     | coreference  | discriminative feature network → DFN                            |      1 |
| Synonym-Of     | coreference  | Exfuse → enhancing low - level and high - level features fusion |      1 |
| Synonym-Of     | coreference  | dual image segmentation → DIS                                   |      1 |
| Synonym-Of     | NIL          | generative adversarial network → GAN                            |      4 |
| Synonym-Of     | NIL          | Support Vector Machine → SVM                                    |      4 |
| Synonym-Of     | NIL          | region proposal network → RPN                                   |      4 |
| Synonym-Of     | NIL          | Long Short - Term Memory → LSTM                                 |      3 |
| Synonym-Of     | NIL          | stochastic gradient descent → SGD                               |      3 |
| Trained-With   | NIL          | word embeddings → BioASQ                                        |      2 |
| Trained-With   | NIL          | ResNet → ImageNet                                               |      2 |
| Trained-With   | NIL          | BERT → masked word prediction                                   |      2 |
| Trained-With   | NIL          | BERT → next sentence prediction                                 |      2 |
| Trained-With   | NIL          | generator → OULU - NPU                                          |      2 |
| Used-For       | appliedTo    | R - CNN based models → instance segmentation                    |      1 |
| Used-For       | appliedTo    | OCNet → semantic segmentation                                   |      1 |
| Used-For       | appliedTo    | pointwise spatial attention network → scene parsing             |      1 |
| Used-For       | NIL          | CAD - GCN → classification                                      |     10 |
| Used-For       | NIL          | word embeddings → classification                                |      6 |
| Used-For       | NIL          | fastText → classification                                       |      5 |
| Used-For       | NIL          | word embeddings → TC                                            |      4 |
| Used-For       | NIL          | face PAD algorithm → face PAD                                   |      4 |
| NIL            | architecture | OCNet → Expectation - Maximization Attention                    |      1 |
| NIL            | architecture | OCNet → GANs                                                    |      1 |
| NIL            | coreference  | EMA - Net → EMA - Net                                           |      1 |
| NIL            | isBasedOn    | Convolutional models → active contour models                    |      1 |
| NIL            | isHyponymOf  | Criss - Cross Attention Network → GANs                          |      1 |
| NIL            | isHyponymOf  | drones → segmentation models                                    |      1 |
