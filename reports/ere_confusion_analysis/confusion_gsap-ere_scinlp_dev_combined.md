# Entity Label Confusion Analysis

**Generated:** 2026-04-09 14:33:44

**Split:** dev

**Model 1:** GSAP-ERE

**Model 2:** SCINLP

**Datasets Combined:** SCIER, SCINLP, GSAP-ERE

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.


## Combined Datasets

### Confusion Matrix

Rows: GSAP-ERE labels | Columns: SCINLP labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |   URL |   NIL |
|:--------|-------------:|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|------:|------:|
| dataset |           78 |       445 |              183 |        14 |                1 |       16 |                   2 |               0 |     13 |     6 |    15 |
| method  |           20 |       112 |              241 |       568 |              653 |     1269 |                 786 |               6 |     57 |     8 |    70 |
| metric  |            0 |         1 |               10 |         0 |                0 |      147 |                   0 |               0 |      3 |     0 |   126 |
| task    |            4 |        43 |               80 |         0 |               19 |      265 |                   3 |               0 |    589 |     0 |    16 |
| NIL     |           22 |       128 |             1258 |        79 |              741 |      934 |                 115 |            1400 |    115 |    20 |     0 |

### Statistics

**GSAP-ERE Total Entities per Label:**

- dataset: 773
- method: 3790
- metric: 287
- task: 1019
- NIL: 4812

**SCINLP Total Entities per Label:**

- DataSource: 124
- Dataset: 729
- DatasetGeneric: 1772
- MLModel: 661
- MLModelGeneric: 1414
- Method: 2631
- ModelArchitecture: 906
- ReferenceLink: 1406
- Task: 777
- URL: 34
- NIL: 227

### Label Mappings (Top 15 per Label Pair)

| GSAP-ERE Label | SCINLP Label | Mention Text | Count |
|----------|----------|--------------|-------|
| DataSource | dataset | WordNet | 8 |
| DataSource | dataset | Wikipedia | 8 |
| DataSource | dataset | YouTube | 3 |
| DataSource | dataset | ArXiv | 3 |
| DataSource | dataset | GitHub | 3 |
| DataSource | dataset | PubMed | 3 |
| DataSource | dataset | Reddit | 3 |
| DataSource | dataset | PubMed Abstracts | 3 |
| DataSource | dataset | Wikipedia articles | 2 |
| DataSource | dataset | Twitter | 2 |
| DataSource | dataset | PubMed Central | 2 |
| DataSource | dataset | Stack Exchange | 2 |
| DataSource | dataset | arXiv | 2 |
| DataSource | dataset | PMC | 2 |
| DataSource | dataset | United States Patent and Trademark Office ( USPTO ) | 2 |
| DataSource | method | Common Crawl | 14 |
| DataSource | method | PMC | 2 |
| DataSource | method | Google Cloud Platform | 1 |
| DataSource | method | Stack Exchange | 1 |
| DataSource | method | Project Gutenberg | 1 |
| DataSource | method | OAI - MPH | 1 |
| DataSource | task | autonomous - driving | 1 |
| DataSource | task | Jeopardy ! | 1 |
| DataSource | task | git cloning | 1 |
| DataSource | task | Common Crawl | 1 |
| DataSource | NIL | Facebook | 2 |
| DataSource | NIL | internet | 2 |
| DataSource | NIL | Amazon Web Services | 1 |
| DataSource | NIL | Instagram | 1 |
| DataSource | NIL | Youtube | 1 |
| DataSource | NIL | Census | 1 |
| DataSource | NIL | Twitter | 1 |
| DataSource | NIL | FreeLaw Project | 1 |
| DataSource | NIL | the US Patent and Trademark Office | 1 |
| DataSource | NIL | open - source code repositories | 1 |
| DataSource | NIL | The Free Law Project | 1 |
| DataSource | NIL | CourtListener | 1 |
| DataSource | NIL | Free Law | 1 |
| DataSource | NIL | Center for Digital Philosophy | 1 |
| DataSource | NIL | arXiv | 1 |
| Dataset | dataset | CIFAR-10 | 33 |
| Dataset | dataset | ImageNet | 21 |
| Dataset | dataset | COCO | 15 |
| Dataset | dataset | MNIST | 11 |
| Dataset | dataset | XFUND | 10 |
| Dataset | dataset | Pile | 9 |
| Dataset | dataset | PASCAL VOC | 8 |
| Dataset | dataset | SNLI | 8 |
| Dataset | dataset | Protein | 8 |
| Dataset | dataset | SQuAD | 7 |
| Dataset | dataset | CIFAR-100 | 7 |
| Dataset | dataset | Kinetics | 6 |
| Dataset | dataset | Financial PhraseBank | 6 |
| Dataset | dataset | BookCorpus | 6 |
| Dataset | dataset | Boston | 6 |
| Dataset | method | Pile | 10 |
| Dataset | method | ImageNet | 6 |
| Dataset | method | fsCOCO | 6 |
| Dataset | method | MNIST | 6 |
| Dataset | method | fsPASCAL | 4 |
| Dataset | method | Pile - CC | 4 |
| Dataset | method | COCO | 3 |
| Dataset | method | GLUE | 3 |
| Dataset | method | sim2sim | 3 |
| Dataset | method | sim2real | 3 |
| Dataset | method | Protein | 3 |
| Dataset | method | Kinetics | 2 |
| Dataset | method | PASCAL | 2 |
| Dataset | method | MNLI | 2 |
| Dataset | method | VisualGenome | 2 |
| Dataset | metric | Pile | 1 |
| Dataset | task | CoLA | 7 |
| Dataset | task | GLUE | 4 |
| Dataset | task | MNLI | 4 |
| Dataset | task | MRPC | 4 |
| Dataset | task | TREC | 3 |
| Dataset | task | SQuAD | 3 |
| Dataset | task | QNLI | 2 |
| Dataset | task | SNLI | 2 |
| Dataset | task | CR | 2 |
| Dataset | task | SST - 5 | 1 |
| Dataset | task | QQP | 1 |
| Dataset | task | ImageNet classification | 1 |
| Dataset | task | SST-5 | 1 |
| Dataset | task | MR | 1 |
| Dataset | task | MPQA | 1 |
| Dataset | NIL | FSS - 1 0 0 0 | 33 |
| Dataset | NIL | Pile | 19 |
| Dataset | NIL | PASCAL VOC 2 0 1 2 | 9 |
| Dataset | NIL | the Pile | 5 |
| Dataset | NIL | Amalgam | 4 |
| Dataset | NIL | ImageNet | 3 |
| Dataset | NIL | UCF 1 0 1 | 3 |
| Dataset | NIL | COCO | 3 |
| Dataset | NIL | PASCAL - 5 i | 2 |
| Dataset | NIL | PoseTrack | 2 |
| Dataset | NIL | WMT 2015 | 2 |
| Dataset | NIL | OpenWebText2 | 2 |
| Dataset | NIL | Kinetics | 1 |
| Dataset | NIL | VOC 2 0 1 2 | 1 |
| Dataset | NIL | ILSVRC | 1 |
| DatasetGeneric | dataset | tweets | 18 |
| DatasetGeneric | dataset | tabular data | 7 |
| DatasetGeneric | dataset | black - aligned tweets | 5 |
| DatasetGeneric | dataset | datasets | 5 |
| DatasetGeneric | dataset | white - aligned tweets | 4 |
| DatasetGeneric | dataset | real data | 4 |
| DatasetGeneric | dataset | English Wikipedia | 3 |
| DatasetGeneric | dataset | dataset | 3 |
| DatasetGeneric | dataset | USPTO Backgrounds | 3 |
| DatasetGeneric | dataset | PubMed Abstracts | 3 |
| DatasetGeneric | dataset | Forest Cover | 3 |
| DatasetGeneric | dataset | Wikipedia articles | 2 |
| DatasetGeneric | dataset | Wikipedia | 2 |
| DatasetGeneric | dataset | Standard American English ( SAE ) | 2 |
| DatasetGeneric | dataset | Pile | 2 |
| DatasetGeneric | method | datapoints | 22 |
| DatasetGeneric | method | black - aligned tweets | 10 |
| DatasetGeneric | method | white - aligned tweets | 7 |
| DatasetGeneric | method | datasets | 7 |
| DatasetGeneric | method | dataset | 5 |
| DatasetGeneric | method | Pile | 5 |
| DatasetGeneric | method | attention between datapoints | 5 |
| DatasetGeneric | method | unlabeled data | 4 |
| DatasetGeneric | method | data | 3 |
| DatasetGeneric | method | test data | 3 |
| DatasetGeneric | method | tabular data | 3 |
| DatasetGeneric | method | training datapoints | 3 |
| DatasetGeneric | method | span - based answers | 2 |
| DatasetGeneric | method | SAE | 2 |
| DatasetGeneric | method | blackaligned tweets | 2 |
| DatasetGeneric | metric | datasets | 3 |
| DatasetGeneric | metric | datapoints | 2 |
| DatasetGeneric | metric | Ours - 5 shot | 1 |
| DatasetGeneric | metric | data | 1 |
| DatasetGeneric | metric | regression | 1 |
| DatasetGeneric | metric | missing values | 1 |
| DatasetGeneric | metric | missing | 1 |
| DatasetGeneric | task | reading comprehension | 4 |
| DatasetGeneric | task | datapoints | 4 |
| DatasetGeneric | task | answer types | 2 |
| DatasetGeneric | task | cloze style questions | 2 |
| DatasetGeneric | task | abusive language detection | 2 |
| DatasetGeneric | task | language modeling | 2 |
| DatasetGeneric | task | missing values | 2 |
| DatasetGeneric | task | few - shot segmentation | 1 |
| DatasetGeneric | task | financial sentiment analysis | 1 |
| DatasetGeneric | task | person search | 1 |
| DatasetGeneric | task | detection | 1 |
| DatasetGeneric | task | segmentation | 1 |
| DatasetGeneric | task | vision - language | 1 |
| DatasetGeneric | task | single-sentence tasks | 1 |
| DatasetGeneric | task | read text | 1 |
| DatasetGeneric | NIL | the data | 50 |
| DatasetGeneric | NIL | the dataset | 43 |
| DatasetGeneric | NIL | datapoints | 30 |
| DatasetGeneric | NIL | data | 23 |
| DatasetGeneric | NIL | the Pile | 23 |
| DatasetGeneric | NIL | the training set | 18 |
| DatasetGeneric | NIL | datasets | 17 |
| DatasetGeneric | NIL | these datasets | 16 |
| DatasetGeneric | NIL | tweets | 16 |
| DatasetGeneric | NIL | a dataset | 15 |
| DatasetGeneric | NIL | training data | 15 |
| DatasetGeneric | NIL | the training data | 14 |
| DatasetGeneric | NIL | each dataset | 14 |
| DatasetGeneric | NIL | other datapoints | 13 |
| DatasetGeneric | NIL | the entire dataset | 11 |
| MLModel | dataset | CC-100 | 3 |
| MLModel | dataset | ResNet 1 5 2 | 2 |
| MLModel | dataset | Resnet101 | 2 |
| MLModel | dataset | AlexNet classification | 1 |
| MLModel | dataset | AlexNet | 1 |
| MLModel | dataset | Inception | 1 |
| MLModel | dataset | Hourglass - 5 4 | 1 |
| MLModel | dataset | teacher BERTBASE | 1 |
| MLModel | dataset | GPT series | 1 |
| MLModel | dataset | Pile | 1 |
| MLModel | method | BERT | 45 |
| MLModel | method | TinyBERT | 41 |
| MLModel | method | GPT-3 | 27 |
| MLModel | method | LayoutXLM | 27 |
| MLModel | method | GloVe | 26 |
| MLModel | method | CornerNet | 21 |
| MLModel | method | FinBERT | 17 |
| MLModel | method | ULMFit | 17 |
| MLModel | method | CornerNet - Squeeze | 17 |
| MLModel | method | YOLOv 3 | 14 |
| MLModel | method | ViCo | 14 |
| MLModel | method | CornerNet - Saccade | 11 |
| MLModel | method | CornerNet - Lite | 9 |
| MLModel | method | BERT SMALL | 9 |
| MLModel | method | ELMo | 8 |
| MLModel | NIL | I 3 D | 9 |
| MLModel | NIL | f att | 5 |
| MLModel | NIL | Hourglass - 1 0 4 | 4 |
| MLModel | NIL | Pile | 4 |
| MLModel | NIL | ResNet - 1 0 1 | 3 |
| MLModel | NIL | FSS - 1 0 0 0 | 3 |
| MLModel | NIL | FastPose - 5 0 | 3 |
| MLModel | NIL | vis - w 2 v | 3 |
| MLModel | NIL | T5 | 3 |
| MLModel | NIL | C 3 D | 2 |
| MLModel | NIL | ULMFit | 2 |
| MLModel | NIL | i 3 D | 2 |
| MLModel | NIL | TinyBERT | 2 |
| MLModel | NIL | MobileNet - v 2 | 2 |
| MLModel | NIL | FastPose - 1 0 1 | 2 |
| MLModelGeneric | dataset | YouTube | 1 |
| MLModelGeneric | method | NPTs | 88 |
| MLModelGeneric | method | models | 16 |
| MLModelGeneric | method | NPT | 15 |
| MLModelGeneric | method | RCN | 14 |
| MLModelGeneric | method | language models | 11 |
| MLModelGeneric | method | 3D CNNs | 10 |
| MLModelGeneric | method | attention model | 9 |
| MLModelGeneric | method | non - parametric models | 9 |
| MLModelGeneric | method | GPT-3 | 8 |
| MLModelGeneric | method | 2D CNNs | 7 |
| MLModelGeneric | method | MTN | 7 |
| MLModelGeneric | method | logistic regression model | 7 |
| MLModelGeneric | method | classifiers | 7 |
| MLModelGeneric | method | CNN | 6 |
| MLModelGeneric | method | Faster R - CNN | 6 |
| MLModelGeneric | task | Benchmarking Language Models | 2 |
| MLModelGeneric | task | sentiment analysis | 1 |
| MLModelGeneric | task | pose estimation | 1 |
| MLModelGeneric | task | segmentation | 1 |
| MLModelGeneric | task | Fine-tuning of language models | 1 |
| MLModelGeneric | task | fine-tuning language models | 1 |
| MLModelGeneric | task | text classification | 1 |
| MLModelGeneric | task | natural language generation ( NLG ) | 1 |
| MLModelGeneric | task | occupational classification | 1 |
| MLModelGeneric | task | detection | 1 |
| MLModelGeneric | task | training language models | 1 |
| MLModelGeneric | task | large - scale language models | 1 |
| MLModelGeneric | task | benchmarking language models | 1 |
| MLModelGeneric | task | largescale language models | 1 |
| MLModelGeneric | task | classification models | 1 |
| MLModelGeneric | NIL | the model | 87 |
| MLModelGeneric | NIL | our model | 24 |
| MLModelGeneric | NIL | NPTs | 18 |
| MLModelGeneric | NIL | models | 15 |
| MLModelGeneric | NIL | a model | 15 |
| MLModelGeneric | NIL | these models | 13 |
| MLModelGeneric | NIL | the SK model | 12 |
| MLModelGeneric | NIL | the baselines | 11 |
| MLModelGeneric | NIL | ( 2 + 1 )D | 10 |
| MLModelGeneric | NIL | they | 10 |
| MLModelGeneric | NIL | the models | 9 |
| MLModelGeneric | NIL | the generator | 8 |
| MLModelGeneric | NIL | such models | 7 |
| MLModelGeneric | NIL | our approach | 7 |
| MLModelGeneric | NIL | the network | 6 |
| Method | dataset | Word - Net | 1 |
| Method | dataset | HPSG structures | 1 |
| Method | dataset | Google Cloud Platform | 1 |
| Method | dataset | Microsoft Azure | 1 |
| Method | dataset | Google Cloud Services | 1 |
| Method | dataset | Wikipedia | 1 |
| Method | dataset | Question - answer collection | 1 |
| Method | dataset | Hatebase | 1 |
| Method | dataset | Stack Exchange | 1 |
| Method | dataset | Newspaper scraper | 1 |
| Method | dataset | Newspaper | 1 |
| Method | dataset | CourtListener | 1 |
| Method | dataset | Hacker News API | 1 |
| Method | dataset | YoutubeTranscriptApi | 1 |
| Method | dataset | Poker Hand | 1 |
| Method | method | NPT | 66 |
| Method | method | normalizing flows | 22 |
| Method | method | sparse convolution | 16 |
| Method | method | denoising score matching | 12 |
| Method | method | normalizing flow | 12 |
| Method | method | dense convolution | 10 |
| Method | method | KD | 10 |
| Method | method | IMO | 10 |
| Method | method | Transformer distillation | 9 |
| Method | method | SIFP | 9 |
| Method | method | ABA | 9 |
| Method | method | DKL | 9 |
| Method | method | spin - glass | 8 |
| Method | method | spin - glasses | 8 |
| Method | method | GloVe | 7 |
| Method | metric | accuracy | 19 |
| Method | metric | precision | 17 |
| Method | metric | confidence | 10 |
| Method | metric | WPA | 8 |
| Method | metric | coverage | 8 |
| Method | metric | recall | 8 |
| Method | metric | Precision | 7 |
| Method | metric | tree entropy | 5 |
| Method | metric | KSR | 4 |
| Method | metric | R2 | 3 |
| Method | metric | pxBleu | 3 |
| Method | metric | entropy | 3 |
| Method | metric | Coverage | 3 |
| Method | metric | RMSE | 3 |
| Method | metric | macro F1 | 2 |
| Method | task | KD | 8 |
| Method | task | word embeddings | 8 |
| Method | task | deep learning | 7 |
| Method | task | natural language processing | 7 |
| Method | task | task - specific distillation | 7 |
| Method | task | domain adaptation | 6 |
| Method | task | data augmentation | 5 |
| Method | task | label noise | 5 |
| Method | task | semi - supervised learning | 5 |
| Method | task | denoising score matching | 5 |
| Method | task | NLP | 4 |
| Method | task | hyperparameter optimization | 4 |
| Method | task | unsupervised learning | 4 |
| Method | task | natural language processing ( NLP ) | 3 |
| Method | task | knowledge distillation | 3 |
| Method | NIL | the flow | 19 |
| Method | NIL | the spin - glass phase | 14 |
| Method | NIL | NPT | 11 |
| Method | NIL | the Pile | 9 |
| Method | NIL | stochastic feature masking | 9 |
| Method | NIL | human performance | 7 |
| Method | NIL | the reverse KL divergence | 7 |
| Method | NIL | the annotation vectors | 6 |
| Method | NIL | target masking | 6 |
| Method | NIL | feature extraction | 5 |
| Method | NIL | fine-tuning | 5 |
| Method | NIL | IMO | 5 |
| Method | NIL | annotation vectors | 5 |
| Method | NIL | the KL divergence | 5 |
| Method | NIL | stochastic target masking | 5 |
| ModelArchitecture | dataset | Hatebase | 1 |
| ModelArchitecture | dataset | datapoints | 1 |
| ModelArchitecture | method | attention | 22 |
| ModelArchitecture | method | BERT | 20 |
| ModelArchitecture | method | GCN | 17 |
| ModelArchitecture | method | RCN | 16 |
| ModelArchitecture | method | convolution layers | 15 |
| ModelArchitecture | method | Transformer | 15 |
| ModelArchitecture | method | CNN | 12 |
| ModelArchitecture | method | fully connected layers | 11 |
| ModelArchitecture | method | self - attention | 10 |
| ModelArchitecture | method | LSTM | 9 |
| ModelArchitecture | method | GPT-3 | 9 |
| ModelArchitecture | method | attention model | 9 |
| ModelArchitecture | method | logistic regression model | 7 |
| ModelArchitecture | method | DACNN | 7 |
| ModelArchitecture | method | attention between datapoints | 7 |
| ModelArchitecture | task | robotic manipulators | 1 |
| ModelArchitecture | task | datapoints | 1 |
| ModelArchitecture | task | sparse and efficient attention | 1 |
| ModelArchitecture | NIL | I 3 D | 20 |
| ModelArchitecture | NIL | RCN | 6 |
| ModelArchitecture | NIL | ( 2 + 1 )D | 6 |
| ModelArchitecture | NIL | attention | 6 |
| ModelArchitecture | NIL | ResNet | 4 |
| ModelArchitecture | NIL | S 3 D | 3 |
| ModelArchitecture | NIL | feature - to - activity attention | 3 |
| ModelArchitecture | NIL | logistic regression | 3 |
| ModelArchitecture | NIL | Attention | 3 |
| ModelArchitecture | NIL | RCU | 2 |
| ModelArchitecture | NIL | CNNs | 2 |
| ModelArchitecture | NIL | encoder layers | 2 |
| ModelArchitecture | NIL | AlexNet | 2 |
| ModelArchitecture | NIL | neural network | 2 |
| ModelArchitecture | NIL | heads | 2 |
| ReferenceLink | method | YOLOv | 1 |
| ReferenceLink | method | Tiedemann | 1 |
| ReferenceLink | method | aff | 1 |
| ReferenceLink | method | Rao ( 1961 ) | 1 |
| ReferenceLink | method | Vincent | 1 |
| ReferenceLink | method | Kingma and LeCun ( 2010 ) | 1 |
| ReferenceLink | NIL | 3 | 35 |
| ReferenceLink | NIL | 1 | 26 |
| ReferenceLink | NIL | 5 | 25 |
| ReferenceLink | NIL | 6 | 23 |
| ReferenceLink | NIL | 8 | 22 |
| ReferenceLink | NIL | 2 | 22 |
| ReferenceLink | NIL | 4 | 22 |
| ReferenceLink | NIL | 7 | 20 |
| ReferenceLink | NIL | 4 5 | 18 |
| ReferenceLink | NIL | 24 | 18 |
| ReferenceLink | NIL | 5 2 | 13 |
| ReferenceLink | NIL | 25 | 13 |
| ReferenceLink | NIL | 4 4 | 12 |
| ReferenceLink | NIL | 1 4 | 12 |
| ReferenceLink | NIL | 3 2 | 12 |
| Task | dataset | Protein regression dataset | 3 |
| Task | dataset | existing reading comprehension and question answering ( QA ) datasets | 2 |
| Task | dataset | AlexNet classification | 1 |
| Task | dataset | FiQA sentiment scoring | 1 |
| Task | dataset | previous manually labeled RC datasets | 1 |
| Task | dataset | RC | 1 |
| Task | dataset | Wikidetox Toxic Comment Dataset | 1 |
| Task | dataset | CC | 1 |
| Task | dataset | Protein | 1 |
| Task | dataset | UCI classification | 1 |
| Task | method | few - shot segmentation | 4 |
| Task | method | Re - ID | 4 |
| Task | method | classification and regression | 2 |
| Task | method | person Re - ID | 2 |
| Task | method | classification models | 2 |
| Task | method | HPSG | 2 |
| Task | method | Neural Relational Inference ( NRI ) | 2 |
| Task | method | classification / regression dataset | 2 |
| Task | method | Causal inference | 1 |
| Task | method | binary segmentation | 1 |
| Task | method | pixelwise segmentation | 1 |
| Task | method | per - pixel classification | 1 |
| Task | method | transfer learning | 1 |
| Task | method | object detector | 1 |
| Task | method | bounding boxes | 1 |
| Task | metric | generalization | 2 |
| Task | metric | regression | 1 |
| Task | task | classification | 43 |
| Task | task | pose estimation | 17 |
| Task | task | semantic segmentation | 16 |
| Task | task | localization | 15 |
| Task | task | text classification | 11 |
| Task | task | few - shot segmentation | 9 |
| Task | task | pose tracking | 9 |
| Task | task | segmentation | 8 |
| Task | task | question answering | 8 |
| Task | task | concurrent activity recognition | 8 |
| Task | task | computer vision | 7 |
| Task | task | sentiment analysis | 7 |
| Task | task | image classification | 7 |
| Task | task | binary classification | 7 |
| Task | task | reading comprehension | 7 |
| Task | NIL | classification | 19 |
| Task | NIL | regression | 7 |
| Task | NIL | segmentation | 6 |
| Task | NIL | human detection | 6 |
| Task | NIL | localization | 4 |
| Task | NIL | predict | 3 |
| Task | NIL | multilingual form understanding | 3 |
| Task | NIL | form understanding | 3 |
| Task | NIL | single - activity recognition | 2 |
| Task | NIL | Re - ID | 2 |
| Task | NIL | Neural machine translation | 2 |
| Task | NIL | generalization | 2 |
| Task | NIL | single - target classification | 2 |
| Task | NIL | video feature extraction | 1 |
| Task | NIL | evaluation/classification | 1 |
| URL | dataset | PhraseBank | 1 |
| URL | dataset | https :/ / stanford - qa.com | 1 |
| URL | dataset | stanford - qa.com | 1 |
| URL | dataset | https :/ / www.courtlistener.com / | 1 |
| URL | dataset | wikipedia / 20200301.en | 1 |
| URL | dataset | http :/ / www.statmt.org / europarl / | 1 |
| URL | method | pile | 1 |
| URL | method | stackexchange | 1 |
| URL | method | c4 | 1 |
| URL | method | youtube - transcript - api | 1 |
| URL | method | layoutxlm | 1 |
| URL | method | PyMuPDF | 1 |
| URL | method | BlingFire | 1 |
| URL | method | Non - Parametric - Transformers | 1 |
| URL | NIL | https://nlp.stanford.edu/projects/glove/ | 1 |
| URL | NIL | https://allennlp.org/elmo | 1 |
| URL | NIL | https : // github.com/princeton-nlp/LM-BFF | 1 |
| URL | NIL | https : //www.quora.com/q/quoradata/ numbers | 1 |
| URL | NIL | https : //github.com/UKPLab/ sentence-transformers | 1 |
| URL | NIL | https :/ / www.perspectiveapi.com | 1 |
| URL | NIL | https :/ / hatebase.org / | 1 |
| URL | NIL | https :/ / bulkdata.uspto.gov / | 1 |
| URL | NIL | https :/ / irclogs.ubuntu.com / | 1 |
| URL | NIL | https :/ / philpapers.org / | 1 |
| URL | NIL | https :/ / exporter.nih.gov / | 1 |
| URL | NIL | https :/ / news.ycombinator.com | 1 |
| URL | NIL | http :/ / data.statmt . org / cc-100 / | 1 |
| URL | NIL | https :/ / arxiv.org / help / bulk_data_s3 | 1 |
| URL | NIL | https :/ / www.courtlistener.com / api / bulk - info / | 1 |
| NIL | dataset | Kinetics | 1 |
| NIL | dataset | SSM | 1 |
| NIL | dataset | MRPC-but | 1 |
| NIL | dataset | SST-2 | 1 |
| NIL | dataset | QQP 12 | 1 |
| NIL | dataset | Medical Journal | 1 |
| NIL | dataset | subtitles | 1 |
| NIL | dataset | television shows | 1 |
| NIL | dataset | text | 1 |
| NIL | dataset | ACF | 1 |
| NIL | dataset | AHRQ | 1 |
| NIL | dataset | CDC | 1 |
| NIL | dataset | HRSA | 1 |
| NIL | dataset | benchmarks | 1 |
| NIL | dataset | data statistics | 1 |
| NIL | method | HPSG | 2 |
| NIL | method | bounding box regression | 1 |
| NIL | method | 1D | 1 |
| NIL | method | Our | 1 |
| NIL | method | Separated 3D | 1 |
| NIL | method | OSLSM | 1 |
| NIL | method | - 1 | 1 |
| NIL | method | VLAD | 1 |
| NIL | method | CoViAR | 1 |
| NIL | method | Asynchronous Temporal Fields | 1 |
| NIL | method | activity mapping | 1 |
| NIL | method | teacher BERT BASE | 1 |
| NIL | method | head network | 1 |
| NIL | method | Re - ID | 1 |
| NIL | method | fully - connected | 1 |
| NIL | metric | accuracy | 67 |
| NIL | metric | perplexity | 9 |
| NIL | metric | AP | 8 |
| NIL | metric | F1 | 7 |
| NIL | metric | precision | 4 |
| NIL | metric | F-measure | 3 |
| NIL | metric | mAP | 2 |
| NIL | metric | pxB | 2 |
| NIL | metric | WPA | 2 |
| NIL | metric | recall | 2 |
| NIL | metric | perplexities | 2 |
| NIL | metric | MSE | 2 |
| NIL | metric | RMSE | 2 |
| NIL | metric | speed | 1 |
| NIL | metric | F 1 - score | 1 |
| NIL | task | natural language processing | 2 |
| NIL | task | prompting | 2 |
| NIL | task | concurrent activity predictions | 1 |
| NIL | task | pose estimation | 1 |
| NIL | task | multi-class classification | 1 |
| NIL | task | supervised learning | 1 |
| NIL | task | profanity analysis | 1 |
| NIL | task | fanfiction | 1 |
| NIL | task | robotic manipulators | 1 |
| NIL | task | sampling and inference | 1 |
| NIL | task | identify phases and phase transitions | 1 |
| NIL | task | online learning | 1 |
| NIL | task | computer vision | 1 |
| NIL | task | missing values | 1 |

## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
