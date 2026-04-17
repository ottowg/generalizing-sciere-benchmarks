# Fixed-Span NER + RE — GSAP on SCIER (pruner_augmented_test)

**Generated:** 2026-03-16 09:30:09

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scier_pruner_augmented_test.json`  
**Gold NER spans:** 2948  
**NER overall accuracy:** 0.436

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MISSING |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |
|:--------|-------------:|----------:|-----------------:|----------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|
| Dataset |            9 |       173 |               32 |         0 |         6 |                2 |      130 |                   8 |               1 |      9 |
| Method  |            0 |         6 |               26 |        39 |       187 |              249 |      753 |                 619 |               0 |     11 |
| Task    |            0 |         0 |               29 |         3 |         0 |               34 |      234 |                  30 |               0 |    358 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | DataSource    | Dataset       | DatasetGeneric   | MISSING   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | ReferenceLink   | Task          |
|:--------|:--------------|:--------------|:-----------------|:----------|:--------------|:-----------------|:--------------|:--------------------|:----------------|:--------------|
| Dataset | 0.332 / 0.911 | 0.143 / 0.865 | 0.457 / 0.541    | —         | 0.721 / 0.349 | 0.654 / 0.283    | 0.495 / 0.558 | 0.542 / 0.473       | 1.000 / 0.336   | 0.470 / 0.623 |
| Method  | —             | 0.136 / 0.753 | 0.537 / 0.567    | —         | 0.164 / 0.754 | 0.355 / 0.738    | 0.406 / 0.794 | 0.364 / 0.797       | —               | 0.186 / 0.839 |
| Task    | —             | —             | 0.568 / 0.604    | —         | —             | 0.618 / 0.561    | 0.471 / 0.728 | 0.685 / 0.499       | —               | 0.232 / 0.889 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| Method       |    1890 |       753 |      0.398 |
| Task         |     688 |       358 |      0.52  |
| Dataset      |     370 |       173 |      0.468 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                        |   Freq |
|:-------------|:------------------|:------------------------------------|-------:|
| Dataset      | DataSource        | Best of the Web                     |      1 |
| Dataset      | DataSource        | DMOZ                                |      1 |
| Dataset      | DataSource        | Wikipedia topic classifications     |      1 |
| Dataset      | DataSource        | Medical Subject Headings            |      1 |
| Dataset      | DataSource        | Internet Movie Database             |      1 |
| Dataset      | Dataset           | OULU - NPU                          |     16 |
| Dataset      | Dataset           | Salinas                             |     10 |
| Dataset      | Dataset           | Indian Pines                        |      8 |
| Dataset      | Dataset           | RCV 1                               |      7 |
| Dataset      | Dataset           | N - Cars                            |      7 |
| Dataset      | DatasetGeneric    | Replay - Attack                     |      4 |
| Dataset      | DatasetGeneric    | KITTI                               |      4 |
| Dataset      | DatasetGeneric    | OULU - NPU                          |      3 |
| Dataset      | DatasetGeneric    | Indian Pines                        |      3 |
| Dataset      | DatasetGeneric    | Chinese OntoNotes v 5 . 0           |      2 |
| Dataset      | MLModel           | N - Cars                            |      2 |
| Dataset      | MLModel           | ImageNet                            |      1 |
| Dataset      | MLModel           | MiniImagenet                        |      1 |
| Dataset      | MLModel           | MIBURI                              |      1 |
| Dataset      | MLModel           | KITTI                               |      1 |
| Dataset      | MLModelGeneric    | MultiNLI                            |      1 |
| Dataset      | MLModelGeneric    | N - Cars                            |      1 |
| Dataset      | Method            | OULU - NPU                          |     19 |
| Dataset      | Method            | Replay - Attack                     |     15 |
| Dataset      | Method            | FlyingChairs                        |      7 |
| Dataset      | Method            | Weibo                               |      6 |
| Dataset      | Method            | N - Caltech 1 0 1                   |      5 |
| Dataset      | ModelArchitecture | KITTI                               |      4 |
| Dataset      | ModelArchitecture | Weibo                               |      1 |
| Dataset      | ModelArchitecture | COCO                                |      1 |
| Dataset      | ModelArchitecture | JFT                                 |      1 |
| Dataset      | ModelArchitecture | Grass - trees                       |      1 |
| Dataset      | ReferenceLink     | Reuters - 2 2 1 7 3                 |      1 |
| Dataset      | Task              | German - English WMT 1 5 Task 3     |      1 |
| Dataset      | Task              | Library of Congress Classification  |      1 |
| Dataset      | Task              | United States Patent Classification |      1 |
| Dataset      | Task              | Large Scale HTC                     |      1 |
| Dataset      | Task              | LSHTC                               |      1 |
| Method       | Dataset           | Events - to - Video                 |      2 |
| Method       | Dataset           | LCPN + VC                           |      1 |
| Method       | Dataset           | EST                                 |      1 |
| Method       | Dataset           | VGG 1 6                             |      1 |
| Method       | Dataset           | SDP+CRC                             |      1 |
| Method       | DatasetGeneric    | generator                           |      2 |
| Method       | DatasetGeneric    | LBP                                 |      2 |
| Method       | DatasetGeneric    | CAD - GCN                           |      2 |
| Method       | DatasetGeneric    | Faster R - CNN                      |      2 |
| Method       | DatasetGeneric    | bigrams                             |      1 |
| Method       | MISSING           | Conv                                |      8 |
| Method       | MISSING           | BN                                  |      6 |
| Method       | MISSING           | lReLU                               |      4 |
| Method       | MISSING           | Residual                            |      2 |
| Method       | MISSING           | feature extraction                  |      2 |
| Method       | MLModel           | BERT                                |     19 |
| Method       | MLModel           | AlexNet                             |     11 |
| Method       | MLModel           | ResNet - Ev 2 Vid                   |      7 |
| Method       | MLModel           | ResNet - EST                        |      7 |
| Method       | MLModel           | CAD - GCN                           |      7 |
| Method       | MLModelGeneric    | BERT                                |      8 |
| Method       | MLModelGeneric    | CAD - GCN                           |      8 |
| Method       | MLModelGeneric    | CNN                                 |      7 |
| Method       | MLModelGeneric    | Matching Nets                       |      7 |
| Method       | MLModelGeneric    | GCN                                 |      6 |
| Method       | Method            | word embeddings                     |     39 |
| Method       | Method            | fastText                            |     19 |
| Method       | Method            | LBP                                 |     16 |
| Method       | Method            | deep learning                       |     14 |
| Method       | Method            | word 2 vec                          |     12 |
| Method       | ModelArchitecture | CNN                                 |     44 |
| Method       | ModelArchitecture | LSTM                                |     42 |
| Method       | ModelArchitecture | Matrix - LSTM                       |     22 |
| Method       | ModelArchitecture | CAD - GCN                           |     16 |
| Method       | ModelArchitecture | R - CNN                             |     14 |
| Method       | Task              | OCR                                 |      2 |
| Method       | Task              | Transformer translation             |      1 |
| Method       | Task              | classification algorithms           |      1 |
| Method       | Task              | binary sentiment TC                 |      1 |
| Method       | Task              | flat classification                 |      1 |
| Task         | DatasetGeneric    | image segmentation                  |      3 |
| Task         | DatasetGeneric    | classification                      |      2 |
| Task         | DatasetGeneric    | region proposal                     |      2 |
| Task         | DatasetGeneric    | segmentation map                    |      2 |
| Task         | DatasetGeneric    | object detection                    |      2 |
| Task         | MISSING           | computer vision                     |      1 |
| Task         | MISSING           | image segmentation                  |      1 |
| Task         | MISSING           | segmentation                        |      1 |
| Task         | MLModelGeneric    | computer vision                     |      4 |
| Task         | MLModelGeneric    | segmentation                        |      3 |
| Task         | MLModelGeneric    | NER                                 |      2 |
| Task         | MLModelGeneric    | classification                      |      2 |
| Task         | MLModelGeneric    | machine translation                 |      1 |
| Task         | Method            | face PAD                            |     21 |
| Task         | Method            | classification                      |     16 |
| Task         | Method            | HTC                                 |     13 |
| Task         | Method            | gesture recognition                 |     10 |
| Task         | Method            | computer vision                     |      9 |
| Task         | ModelArchitecture | segmentation                        |      6 |
| Task         | ModelArchitecture | semantic segmentation               |      5 |
| Task         | ModelArchitecture | classification                      |      4 |
| Task         | ModelArchitecture | HTC                                 |      3 |
| Task         | ModelArchitecture | image segmentation                  |      2 |
| Task         | Task              | classification                      |     53 |
| Task         | Task              | image segmentation                  |     15 |
| Task         | Task              | segmentation                        |     14 |
| Task         | Task              | HTC                                 |     12 |
| Task         | Task              | sentiment analysis                  |     11 |

## RE — Relation Confusion Matrix

**Gold relations:** 1626  
**Predicted relations:** 396  

Rows = gold labels · Columns = predicted labels · NIL = unmatched on the respective side.

|                |   appliedTo |   architecture |   benchmarkFor |   coreference |   evaluatedOn |   generatedBy |   isBasedOn |   isComparedTo |   isHyponymOf |   isPartOf |   processed |   sourcedFrom |   trainedOn |   usedFor |   versionOf |   NIL |
|:---------------|------------:|---------------:|---------------:|--------------:|--------------:|--------------:|------------:|---------------:|--------------:|-----------:|------------:|--------------:|------------:|----------:|------------:|------:|
| Benchmark-For  |           0 |              0 |              7 |             0 |             0 |             1 |           0 |              0 |             0 |          0 |           0 |             0 |           0 |         0 |           0 |    77 |
| Compare-With   |           0 |              0 |              0 |             0 |             0 |             0 |           0 |             14 |             0 |          0 |           0 |             0 |           0 |         0 |           0 |   100 |
| Evaluated-With |           0 |              0 |              1 |             0 |             9 |             0 |           0 |              0 |             0 |          0 |           1 |             0 |           1 |         0 |           0 |   119 |
| Part-Of        |           0 |              2 |              0 |             0 |             0 |             0 |           0 |              0 |             0 |          1 |           0 |             0 |           0 |        10 |           0 |   291 |
| SubClass-Of    |           0 |              3 |              0 |             0 |             0 |             0 |           1 |              0 |            17 |          2 |           0 |             0 |           0 |         0 |           1 |   152 |
| SubTask-Of     |           0 |              0 |              0 |             0 |             0 |             0 |           0 |              0 |             2 |          0 |           0 |             0 |           0 |         0 |           0 |    63 |
| Synonym-Of     |           1 |              0 |              0 |            91 |             0 |             0 |           0 |              0 |             0 |          0 |           0 |             0 |           0 |         0 |           0 |    78 |
| Trained-With   |           2 |              0 |              0 |             0 |             0 |             0 |           0 |              0 |             0 |          0 |           0 |             0 |           4 |         0 |           0 |    29 |
| Used-For       |          76 |              0 |              0 |             4 |             0 |             0 |           2 |              0 |             0 |          0 |           0 |             0 |           0 |         1 |           0 |   463 |
| NIL            |          18 |             34 |              0 |            57 |             4 |             0 |           3 |              2 |             2 |          0 |           0 |             1 |           0 |        21 |           0 |     0 |

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

| Gold Label     | Pred Label   | Subject → Object                                                                          |   Freq |
|:---------------|:-------------|:------------------------------------------------------------------------------------------|-------:|
| Benchmark-For  | benchmarkFor | Yelp → binary sentiment analysis                                                          |      1 |
| Benchmark-For  | benchmarkFor | Large Movie Review Dataset v 1 . 0 → binary sentiment TC                                  |      1 |
| Benchmark-For  | benchmarkFor | RCV 1 → topic categorization                                                              |      1 |
| Benchmark-For  | benchmarkFor | N - Cars → object classification                                                          |      1 |
| Benchmark-For  | benchmarkFor | CIFAR - 1 0 0 → 5 - way - 1 - shot image recognition                                      |      1 |
| Benchmark-For  | generatedBy  | ScanNet → surface reconstructions                                                         |      1 |
| Benchmark-For  | NIL          | OULU - NPU → face PAD                                                                     |      5 |
| Benchmark-For  | NIL          | Replay - Attack → face PAD                                                                |      4 |
| Benchmark-For  | NIL          | LSHTC → HTC                                                                               |      2 |
| Benchmark-For  | NIL          | Internet Movie Database → classification                                                  |      2 |
| Benchmark-For  | NIL          | MVSEC → optical flow estimation                                                           |      2 |
| Compare-With   | isComparedTo | GCN → CAD - GCN                                                                           |      3 |
| Compare-With   | isComparedTo | S 2 GCN → CAD - GCN                                                                       |      2 |
| Compare-With   | isComparedTo | GS - EC → GS - GR                                                                         |      1 |
| Compare-With   | isComparedTo | LSTM → Transformers                                                                       |      1 |
| Compare-With   | isComparedTo | hierarchical classification → flat classification                                         |      1 |
| Compare-With   | NIL          | LSTM → BERT                                                                               |      4 |
| Compare-With   | NIL          | GS - EC → GS - GR                                                                         |      3 |
| Compare-With   | NIL          | GS - GR → GS - EC attacks                                                                 |      2 |
| Compare-With   | NIL          | Transformer - based model → LSTM - based model                                            |      2 |
| Compare-With   | NIL          | deep meta - learning → vanilla meta - learning                                            |      2 |
| Evaluated-With | benchmarkFor | MVSEC → optical flow prediction                                                           |      1 |
| Evaluated-With | evaluatedOn  | LSTM → Yelp                                                                               |      1 |
| Evaluated-With | evaluatedOn  | BERT → Yelp                                                                               |      1 |
| Evaluated-With | evaluatedOn  | BERT NOPT → Yelp                                                                          |      1 |
| Evaluated-With | evaluatedOn  | classification systems → LSHTC                                                            |      1 |
| Evaluated-With | evaluatedOn  | ResNet - EST → N - Cars                                                                   |      1 |
| Evaluated-With | processed    | scale dependent pooling → KITTI                                                           |      1 |
| Evaluated-With | trainedOn    | ResNet - Ev 2 Vid → N - Cars                                                              |      1 |
| Evaluated-With | NIL          | face PAD algorithm → Replay - Attack                                                      |      4 |
| Evaluated-With | NIL          | face PAD algorithm → OULU - NPU                                                           |      4 |
| Evaluated-With | NIL          | CAD - GCN → Indian Pines                                                                  |      4 |
| Evaluated-With | NIL          | CAD - GCN → University of Pavia                                                           |      4 |
| Evaluated-With | NIL          | CAD - GCN → Salinas                                                                       |      4 |
| Part-Of        | architecture | MatConvNet → SVM                                                                          |      1 |
| Part-Of        | architecture | VGG 1 9 → R - CNN                                                                         |      1 |
| Part-Of        | isPartOf     | conv 5 3 → CNN                                                                            |      1 |
| Part-Of        | usedFor      | meta - learning → deep meta - learning                                                    |      2 |
| Part-Of        | usedFor      | deep learning → deep meta - learning                                                      |      2 |
| Part-Of        | usedFor      | softmax → XGBoost                                                                         |      1 |
| Part-Of        | usedFor      | word 2 vec → XGBoost                                                                      |      1 |
| Part-Of        | usedFor      | max - pooling → SegNet                                                                    |      1 |
| Part-Of        | NIL          | Conv → Residual                                                                           |     18 |
| Part-Of        | NIL          | BN → Residual                                                                             |     16 |
| Part-Of        | NIL          | lReLU → Residual                                                                          |      9 |
| Part-Of        | NIL          | dropout → Glynn CNN                                                                       |      4 |
| Part-Of        | NIL          | convolutional layers → color - liked space generator                                      |      4 |
| SubClass-Of    | architecture | BERT → Transformer                                                                        |      1 |
| SubClass-Of    | architecture | Matrix - LSTM → Long Short - Term Memory                                                  |      1 |
| SubClass-Of    | architecture | ParseNet → FCN                                                                            |      1 |
| SubClass-Of    | isBasedOn    | GloVe → count - based models                                                              |      1 |
| SubClass-Of    | isHyponymOf  | AlexNet → CNN                                                                             |      2 |
| SubClass-Of    | isHyponymOf  | BERT → Self - attentive models                                                            |      1 |
| SubClass-Of    | isHyponymOf  | BERT NOPT → Self - attentive models                                                       |      1 |
| SubClass-Of    | isHyponymOf  | SGD → task - agnostic learning algorithms                                                 |      1 |
| SubClass-Of    | isHyponymOf  | CNN → task - specific models                                                              |      1 |
| SubClass-Of    | isPartOf     | MobileNet → CNN                                                                           |      1 |
| SubClass-Of    | isPartOf     | DenseNet → CNN                                                                            |      1 |
| SubClass-Of    | versionOf    | ShapeNetCore → ShapeNet                                                                   |      1 |
| SubClass-Of    | NIL          | FastText → word embedding generator                                                       |      2 |
| SubClass-Of    | NIL          | word 2 vec → word embeddings                                                              |      2 |
| SubClass-Of    | NIL          | LSTM → convolutional filter                                                               |      2 |
| SubClass-Of    | NIL          | Bidirectional Encoder Representations from Transformers → self - attention - based models |      1 |
| SubClass-Of    | NIL          | Transformer → self - attention - based models                                             |      1 |
| SubTask-Of     | isHyponymOf  | Panoptic segmentation → segmentation                                                      |      1 |
| SubTask-Of     | isHyponymOf  | 3D object classification → 3D scene understanding                                         |      1 |
| SubTask-Of     | NIL          | sentiment analysis → classification                                                       |      3 |
| SubTask-Of     | NIL          | machine translation → natural language processing                                         |      2 |
| SubTask-Of     | NIL          | action recognition → computer vision                                                      |      2 |
| SubTask-Of     | NIL          | text classification → natural language processing                                         |      1 |
| SubTask-Of     | NIL          | sequence - to - sequence problems → NLP                                                   |      1 |
| Synonym-Of     | appliedTo    | FoveaNet → Perspectiveaware scene parsing                                                 |      1 |
| Synonym-Of     | coreference  | recurrent neural networks → RNN                                                           |      2 |
| Synonym-Of     | coreference  | latent Dirichlet allocation → LDA                                                         |      2 |
| Synonym-Of     | coreference  | long short - term memory → LSTM                                                           |      2 |
| Synonym-Of     | coreference  | Long Short - Term Memory → LSTM                                                           |      2 |
| Synonym-Of     | coreference  | convolutional neural networks → CNNs                                                      |      2 |
| Synonym-Of     | NIL          | Support Vector Machine → SVM                                                              |      4 |
| Synonym-Of     | NIL          | stochastic gradient descent → SGD                                                         |      3 |
| Synonym-Of     | NIL          | generative adversarial network → GAN                                                      |      3 |
| Synonym-Of     | NIL          | human - robot interaction → HRI                                                           |      3 |
| Synonym-Of     | NIL          | hierarchical text classification → HTC                                                    |      2 |
| Trained-With   | appliedTo    | BERT → masked word prediction                                                             |      1 |
| Trained-With   | appliedTo    | BERT → next sentence prediction                                                           |      1 |
| Trained-With   | trainedOn    | word embeddings → BioASQ                                                                  |      1 |
| Trained-With   | trainedOn    | BERT - BiLSTM - CRF → Weibo NAM                                                           |      1 |
| Trained-With   | trainedOn    | BERT - BiLSTM - CRF → Weibo                                                               |      1 |
| Trained-With   | trainedOn    | strided CNN → Weibo                                                                       |      1 |
| Trained-With   | NIL          | ResNet → ImageNet                                                                         |      2 |
| Trained-With   | NIL          | generator → OULU - NPU                                                                    |      2 |
| Trained-With   | NIL          | LSTM → German - English WMT 1 5 Task 3                                                    |      1 |
| Trained-With   | NIL          | LSTM → common crawl                                                                       |      1 |
| Trained-With   | NIL          | LSTM → news - commentary                                                                  |      1 |
| Used-For       | appliedTo    | CAD - GCN → classification                                                                |      3 |
| Used-For       | appliedTo    | BERT → classification                                                                     |      2 |
| Used-For       | appliedTo    | deep meta - learning → few - shot image recognition                                       |      2 |
| Used-For       | appliedTo    | face PAD methods → detect fake faces                                                      |      2 |
| Used-For       | appliedTo    | self - attentive architectures → sentiment analysis                                       |      1 |
| Used-For       | coreference  | face PAD algorithm → face PAD                                                             |      3 |
| Used-For       | coreference  | classification → TC                                                                       |      1 |
| Used-For       | isBasedOn    | Fast R - CNN → image classifiers                                                          |      1 |
| Used-For       | isBasedOn    | Fast R - CNN → bounding - box regressors                                                  |      1 |
| Used-For       | usedFor      | deep reinforcement learning → Seednet                                                     |      1 |
| Used-For       | NIL          | CAD - GCN → classification                                                                |      7 |
| Used-For       | NIL          | word embeddings → classification                                                          |      6 |
| Used-For       | NIL          | fastText → classification                                                                 |      4 |
| Used-For       | NIL          | DL → segmentation                                                                         |      4 |
| Used-For       | NIL          | CAD - GCN → HSI classification                                                            |      4 |
| NIL            | appliedTo    | GS - GR → sentiment analysis                                                              |      1 |
| NIL            | appliedTo    | CNNs → image classification                                                               |      1 |
| NIL            | appliedTo    | CNNs → object detection                                                                   |      1 |
| NIL            | appliedTo    | CNNs → semantic segmentation                                                              |      1 |
| NIL            | appliedTo    | SNNs → edge detection                                                                     |      1 |
| NIL            | architecture | recurrent neural networks → attention                                                     |      1 |
| NIL            | architecture | self - attentive architectures → attention                                                |      1 |
| NIL            | architecture | Transformer → multiheaded attention                                                       |      1 |
| NIL            | architecture | convolutional filter → LSTM                                                               |      1 |
| NIL            | architecture | Matrix - LSTM → LSTM                                                                      |      1 |
| NIL            | coreference  | CNN → CNN                                                                                 |      6 |
| NIL            | coreference  | CAD - GCN → CAD - GCN                                                                     |      5 |
| NIL            | coreference  | AlexNet → AlexNet                                                                         |      4 |
| NIL            | coreference  | fastText → fastText                                                                       |      3 |
| NIL            | coreference  | BERT → BERT                                                                               |      2 |
| NIL            | evaluatedOn  | SVM - based classifiers → RCV 1                                                           |      1 |
| NIL            | evaluatedOn  | word 2 vec → BioASQ                                                                       |      1 |
| NIL            | evaluatedOn  | CAD - GCN → Indian Pines                                                                  |      1 |
| NIL            | evaluatedOn  | CAD - GCN → University of Pavia                                                           |      1 |
| NIL            | isBasedOn    | CNN → autoencoders                                                                        |      1 |
| NIL            | isBasedOn    | Convolutional models → active contour models                                              |      1 |
| NIL            | isBasedOn    | Faster R - CNN → region proposal network                                                  |      1 |
| NIL            | isComparedTo | N - Caltech 1 0 1 → Caltech - 1 0 1                                                       |      1 |
| NIL            | isComparedTo | GCN → S 2 GCN                                                                             |      1 |
| NIL            | isHyponymOf  | Criss - Cross Attention Network → GANs                                                    |      1 |
| NIL            | isHyponymOf  | drones → segmentation models                                                              |      1 |
| NIL            | sourcedFrom  | N - Caltech 1 0 1 → EST                                                                   |      1 |
| NIL            | usedFor      | word embeddings → word 2 vec                                                              |      2 |
| NIL            | usedFor      | word embeddings → XGBoost                                                                 |      2 |
| NIL            | usedFor      | meta - learning → DEML                                                                    |      2 |
| NIL            | usedFor      | self - attentive structure → Transformer                                                  |      1 |
| NIL            | usedFor      | word embeddings → document embeddings                                                     |      1 |
