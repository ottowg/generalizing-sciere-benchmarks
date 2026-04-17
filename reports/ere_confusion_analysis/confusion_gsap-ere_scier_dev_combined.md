# Entity Label Confusion Analysis

**Generated:** 2026-04-09 14:33:51

**Split:** dev

**Model 1:** GSAP-ERE

**Model 2:** SCIER

**Datasets Combined:** SCIER, SCINLP, GSAP-ERE

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.


## Combined Datasets

### Confusion Matrix

Rows: GSAP-ERE labels | Columns: SCIER labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |   URL |   NIL |
|:--------|-------------:|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|------:|------:|
| Dataset |           91 |       661 |              366 |        21 |                6 |       58 |                   4 |               8 |     18 |     7 |    65 |
| Method  |           14 |        45 |              152 |       634 |              795 |     1643 |                 850 |             186 |     52 |    19 |   173 |
| Task    |            6 |         3 |              257 |         0 |               32 |      286 |                   4 |               3 |    675 |     0 |    58 |
| NIL     |           13 |        20 |              997 |         6 |              581 |      644 |                  48 |            1209 |     32 |     8 |     0 |

### Statistics

**GSAP-ERE Total Entities per Label:**

- Dataset: 1305
- Method: 4563
- Task: 1324
- NIL: 3558

**SCIER Total Entities per Label:**

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
- NIL: 296

### Label Mappings (Top 15 per Label Pair)

| GSAP-ERE Label | SCIER Label | Mention Text | Count |
|----------|----------|--------------|-------|
| DataSource | Dataset | Common Crawl | 8 |
| DataSource | Dataset | Wikipedia | 8 |
| DataSource | Dataset | WordNet | 7 |
| DataSource | Dataset | Twitter | 4 |
| DataSource | Dataset | YouTube | 3 |
| DataSource | Dataset | PubMed Central | 3 |
| DataSource | Dataset | ArXiv | 3 |
| DataSource | Dataset | GitHub | 3 |
| DataSource | Dataset | PubMed | 3 |
| DataSource | Dataset | Reddit | 3 |
| DataSource | Dataset | arXiv | 3 |
| DataSource | Dataset | Amazon Web Services | 2 |
| DataSource | Dataset | Facebook | 2 |
| DataSource | Dataset | PubMed Abstracts | 2 |
| DataSource | Dataset | PMC | 2 |
| DataSource | Method | Common Crawl | 5 |
| DataSource | Method | PMC | 2 |
| DataSource | Method | WordNet | 1 |
| DataSource | Method | raw and filtered Common Crawl models | 1 |
| DataSource | Method | CourtListener | 1 |
| DataSource | Method | Stack Exchange | 1 |
| DataSource | Method | Hacker News | 1 |
| DataSource | Method | PubMed Abstracts | 1 |
| DataSource | Method | davinci | 1 |
| DataSource | Task | autonomous - driving | 1 |
| DataSource | Task | Stack Exchange | 1 |
| DataSource | Task | Center for Digital Philosophy | 1 |
| DataSource | Task | git cloning | 1 |
| DataSource | Task | Hacker News | 1 |
| DataSource | Task | internet | 1 |
| DataSource | NIL | internet | 2 |
| DataSource | NIL | Census | 1 |
| DataSource | NIL | FreeLaw Project | 1 |
| DataSource | NIL | Stack Exchange | 1 |
| DataSource | NIL | The Free Law Project | 1 |
| DataSource | NIL | Free Law | 1 |
| DataSource | NIL | Common Crawl | 1 |
| DataSource | NIL | GitHub | 1 |
| DataSource | NIL | TripAdvisor | 1 |
| DataSource | NIL | SimplyHired | 1 |
| DataSource | NIL | Facebook | 1 |
| DataSource | NIL | codebase | 1 |
| Dataset | Dataset | Pile | 35 |
| Dataset | Dataset | CIFAR-10 | 33 |
| Dataset | Dataset | ImageNet | 31 |
| Dataset | Dataset | FSS - 1 0 0 0 | 29 |
| Dataset | Dataset | COCO | 22 |
| Dataset | Dataset | MNIST | 16 |
| Dataset | Dataset | XFUND | 14 |
| Dataset | Dataset | SNLI | 13 |
| Dataset | Dataset | SQuAD | 13 |
| Dataset | Dataset | GLUE | 12 |
| Dataset | Dataset | Protein | 11 |
| Dataset | Dataset | BookCorpus | 10 |
| Dataset | Dataset | CoLA | 10 |
| Dataset | Dataset | OpenWebText2 | 10 |
| Dataset | Dataset | Kinetics | 9 |
| Dataset | Method | FSS - 1 0 0 0 | 4 |
| Dataset | Method | Amalgam | 4 |
| Dataset | Method | Pile | 2 |
| Dataset | Method | OWT2 | 2 |
| Dataset | Method | AlexNet | 1 |
| Dataset | Method | VGG - 1 6 | 1 |
| Dataset | Method | Hourglass - 1 0 4 | 1 |
| Dataset | Method | PoseTrack | 1 |
| Dataset | Method | FlowTrack - 1 5 2 | 1 |
| Dataset | Method | FlowTrack - 5 0 | 1 |
| Dataset | Method | Vi - sualGenome | 1 |
| Dataset | Method | TG | 1 |
| Dataset | Method | CHATYUAN | 1 |
| Dataset | Method | pxBleu | 1 |
| Dataset | Method | AAE | 1 |
| Dataset | Task | MNLI | 1 |
| Dataset | Task | QQP | 1 |
| Dataset | Task | XFUND | 1 |
| Dataset | NIL | Pile | 7 |
| Dataset | NIL | PASCAL | 1 |
| Dataset | NIL | VOC | 1 |
| Dataset | NIL | MPQA | 1 |
| Dataset | NIL | TransType2 | 1 |
| Dataset | NIL | Amalgam | 1 |
| Dataset | NIL | LP | 1 |
| Dataset | NIL | LR | 1 |
| Dataset | NIL | Founta et al . ( 2018 ) | 1 |
| Dataset | NIL | white - aligned corpus | 1 |
| Dataset | NIL | GitHub | 1 |
| Dataset | NIL | the Pile | 1 |
| Dataset | NIL | CRISP | 1 |
| Dataset | NIL | Protein | 1 |
| DatasetGeneric | Dataset | Pile | 15 |
| DatasetGeneric | Dataset | black - aligned tweets | 12 |
| DatasetGeneric | Dataset | white - aligned tweets | 9 |
| DatasetGeneric | Dataset | tabular data | 9 |
| DatasetGeneric | Dataset | tweets | 6 |
| DatasetGeneric | Dataset | dataset | 5 |
| DatasetGeneric | Dataset | training data | 5 |
| DatasetGeneric | Dataset | datasets | 5 |
| DatasetGeneric | Dataset | a dataset | 4 |
| DatasetGeneric | Dataset | English Wikipedia | 3 |
| DatasetGeneric | Dataset | blackaligned tweets | 3 |
| DatasetGeneric | Dataset | USPTO Backgrounds | 3 |
| DatasetGeneric | Dataset | data | 3 |
| DatasetGeneric | Dataset | BookCorpus | 3 |
| DatasetGeneric | Dataset | Wikipedia | 2 |
| DatasetGeneric | Method | datapoints | 18 |
| DatasetGeneric | Method | Pile | 3 |
| DatasetGeneric | Method | noisy samples | 3 |
| DatasetGeneric | Method | Attention Between Datapoints | 3 |
| DatasetGeneric | Method | training data | 3 |
| DatasetGeneric | Method | SAE | 2 |
| DatasetGeneric | Method | raw web pages , metadata and text extractions | 2 |
| DatasetGeneric | Method | raw ( pixel ) images | 2 |
| DatasetGeneric | Method | data samples | 2 |
| DatasetGeneric | Method | 100 , 000 samples | 2 |
| DatasetGeneric | Method | tabular data | 2 |
| DatasetGeneric | Method | two datapoints | 2 |
| DatasetGeneric | Method | datapoints on training data | 2 |
| DatasetGeneric | Method | data | 2 |
| DatasetGeneric | Method | Forest Cover | 2 |
| DatasetGeneric | Task | noisy labels | 8 |
| DatasetGeneric | Task | missing values | 6 |
| DatasetGeneric | Task | multilingual form understanding | 4 |
| DatasetGeneric | Task | reading comprehension | 3 |
| DatasetGeneric | Task | wrongly labeled samples | 3 |
| DatasetGeneric | Task | potentially noisy labels | 3 |
| DatasetGeneric | Task | real data | 3 |
| DatasetGeneric | Task | datapoints | 3 |
| DatasetGeneric | Task | answer choices | 2 |
| DatasetGeneric | Task | span - based answers | 2 |
| DatasetGeneric | Task | questions and answer types | 2 |
| DatasetGeneric | Task | cloze style questions | 2 |
| DatasetGeneric | Task | questions whose answers | 2 |
| DatasetGeneric | Task | proportion of tweets | 2 |
| DatasetGeneric | Task | black - aligned tweets | 2 |
| DatasetGeneric | NIL | the data | 49 |
| DatasetGeneric | NIL | the dataset | 43 |
| DatasetGeneric | NIL | datapoints | 31 |
| DatasetGeneric | NIL | each dataset | 20 |
| DatasetGeneric | NIL | the training set | 18 |
| DatasetGeneric | NIL | these datasets | 16 |
| DatasetGeneric | NIL | data | 15 |
| DatasetGeneric | NIL | datasets | 14 |
| DatasetGeneric | NIL | the training data | 14 |
| DatasetGeneric | NIL | tweets | 14 |
| DatasetGeneric | NIL | the Pile | 13 |
| DatasetGeneric | NIL | other datapoints | 13 |
| DatasetGeneric | NIL | the entire dataset | 11 |
| DatasetGeneric | NIL | this dataset | 9 |
| DatasetGeneric | NIL | all samples | 9 |
| MLModel | Dataset | Pile | 6 |
| MLModel | Dataset | Pile - CC | 3 |
| MLModel | Dataset | FSS - 1 0 0 0 | 2 |
| MLModel | Dataset | robocar | 2 |
| MLModel | Dataset | ViCo | 1 |
| MLModel | Dataset | vis - w 2 v | 1 |
| MLModel | Dataset | PET | 1 |
| MLModel | Dataset | ALPACA-7B | 1 |
| MLModel | Dataset | ALPACA-7B-LoRA | 1 |
| MLModel | Dataset | IMO | 1 |
| MLModel | Dataset | IMO-BART | 1 |
| MLModel | Dataset | Pile codebase | 1 |
| MLModel | Method | BERT | 45 |
| MLModel | Method | TinyBERT | 44 |
| MLModel | Method | GPT-3 | 28 |
| MLModel | Method | LayoutXLM | 27 |
| MLModel | Method | GloVe | 26 |
| MLModel | Method | CornerNet | 21 |
| MLModel | Method | ULMFit | 19 |
| MLModel | Method | FinBERT | 18 |
| MLModel | Method | CornerNet - Squeeze | 17 |
| MLModel | Method | YOLOv 3 | 14 |
| MLModel | Method | ViCo | 13 |
| MLModel | Method | CornerNet - Saccade | 11 |
| MLModel | Method | BERT SMALL | 10 |
| MLModel | Method | I 3 D | 9 |
| MLModel | Method | CornerNet - Lite | 9 |
| MLModel | NIL | T5 | 2 |
| MLModel | NIL | res - 5 | 1 |
| MLModel | NIL | vis - w 2 v | 1 |
| MLModel | NIL | uncased | 1 |
| MLModel | NIL | MHSelfAtt | 1 |
| MLModelGeneric | Dataset | NPTs | 2 |
| MLModelGeneric | Dataset | Waseem and Hovy ( 2016 ) | 1 |
| MLModelGeneric | Dataset | Common Crawl - derived | 1 |
| MLModelGeneric | Dataset | Pile - CC | 1 |
| MLModelGeneric | Dataset | CIFAR-10 model | 1 |
| MLModelGeneric | Method | NPTs | 107 |
| MLModelGeneric | Method | RCN | 16 |
| MLModelGeneric | Method | NPT | 16 |
| MLModelGeneric | Method | I 3 D | 13 |
| MLModelGeneric | Method | non - parametric models | 12 |
| MLModelGeneric | Method | language models | 11 |
| MLModelGeneric | Method | 3D CNNs | 10 |
| MLModelGeneric | Method | models | 10 |
| MLModelGeneric | Method | SK | 10 |
| MLModelGeneric | Method | MTN | 9 |
| MLModelGeneric | Method | attention | 8 |
| MLModelGeneric | Method | 2D CNNs | 7 |
| MLModelGeneric | Method | CNN | 7 |
| MLModelGeneric | Method | CNNs | 7 |
| MLModelGeneric | Method | generator | 7 |
| MLModelGeneric | Task | classification | 3 |
| MLModelGeneric | Task | segmentation | 3 |
| MLModelGeneric | Task | sentiment analysis | 1 |
| MLModelGeneric | Task | transfer learning | 1 |
| MLModelGeneric | Task | PLMs | 1 |
| MLModelGeneric | Task | pose estimation | 1 |
| MLModelGeneric | Task | per - pixel classifiers | 1 |
| MLModelGeneric | Task | NLP | 1 |
| MLModelGeneric | Task | text classification | 1 |
| MLModelGeneric | Task | natural language generation | 1 |
| MLModelGeneric | Task | ML architectures | 1 |
| MLModelGeneric | Task | deploying them | 1 |
| MLModelGeneric | Task | various ML architecture | 1 |
| MLModelGeneric | Task | captioning | 1 |
| MLModelGeneric | Task | sentiment classification | 1 |
| MLModelGeneric | NIL | the model | 87 |
| MLModelGeneric | NIL | our model | 24 |
| MLModelGeneric | NIL | models | 16 |
| MLModelGeneric | NIL | these models | 13 |
| MLModelGeneric | NIL | the baselines | 11 |
| MLModelGeneric | NIL | ( 2 + 1 )D | 10 |
| MLModelGeneric | NIL | they | 10 |
| MLModelGeneric | NIL | the models | 9 |
| MLModelGeneric | NIL | such models | 7 |
| MLModelGeneric | NIL | our approach | 7 |
| MLModelGeneric | NIL | the network | 6 |
| MLModelGeneric | NIL | it | 6 |
| MLModelGeneric | NIL | The model | 6 |
| MLModelGeneric | NIL | baselines | 5 |
| MLModelGeneric | NIL | the classifiers | 5 |
| Method | Dataset | IMO | 7 |
| Method | Dataset | OpenAI API | 5 |
| Method | Dataset | ImageNet | 3 |
| Method | Dataset | BDW | 2 |
| Method | Dataset | Hatebase | 2 |
| Method | Dataset | Pile | 2 |
| Method | Dataset | Mongo | 2 |
| Method | Dataset | NPT | 2 |
| Method | Dataset | COCO | 1 |
| Method | Dataset | MLM&NSP+TD | 1 |
| Method | Dataset | MOTA | 1 |
| Method | Dataset | Word - Net | 1 |
| Method | Dataset | NMT | 1 |
| Method | Dataset | pxBleu | 1 |
| Method | Dataset | IBM Watson | 1 |
| Method | Method | NPT | 74 |
| Method | Method | normalizing flows | 23 |
| Method | Method | sparse convolution | 18 |
| Method | Method | KD | 18 |
| Method | Method | normalizing flow | 14 |
| Method | Method | data augmentation | 13 |
| Method | Method | Transformer distillation | 12 |
| Method | Method | word embeddings | 12 |
| Method | Method | denoising score matching | 12 |
| Method | Method | SIFP | 11 |
| Method | Method | DKL | 11 |
| Method | Method | dense convolution | 10 |
| Method | Method | ABA | 10 |
| Method | Method | deep learning | 9 |
| Method | Method | task - specific distillation | 9 |
| Method | Task | natural language processing | 9 |
| Method | Task | NLP | 6 |
| Method | Task | pre - training | 5 |
| Method | Task | denoising score matching | 5 |
| Method | Task | ML | 4 |
| Method | Task | language modeling | 4 |
| Method | Task | against label noise | 4 |
| Method | Task | unsupervised learning | 4 |
| Method | Task | feature extraction | 3 |
| Method | Task | MLM | 3 |
| Method | Task | few-shot learning | 3 |
| Method | Task | iterative filtering | 3 |
| Method | Task | filtering | 3 |
| Method | Task | spin - glass phase transition | 3 |
| Method | Task | word embeddings | 2 |
| Method | NIL | the flow | 19 |
| Method | NIL | the spin - glass phase | 14 |
| Method | NIL | accuracy | 13 |
| Method | NIL | the Pile | 8 |
| Method | NIL | human performance | 7 |
| Method | NIL | the reverse KL divergence | 7 |
| Method | NIL | the annotation vectors | 6 |
| Method | NIL | precision | 5 |
| Method | NIL | the KL divergence | 5 |
| Method | NIL | fine - tuning | 4 |
| Method | NIL | filtering | 4 |
| Method | NIL | recall | 4 |
| Method | NIL | the filtering step | 4 |
| Method | NIL | an unsupervised fashion | 4 |
| Method | NIL | the forward KL divergence | 4 |
| ModelArchitecture | Dataset | I 3 D | 1 |
| ModelArchitecture | Dataset | ImageNet | 1 |
| ModelArchitecture | Dataset | BART | 1 |
| ModelArchitecture | Dataset | Hatebase | 1 |
| ModelArchitecture | Method | RCN | 27 |
| ModelArchitecture | Method | BERT | 22 |
| ModelArchitecture | Method | GCN | 20 |
| ModelArchitecture | Method | CNN | 18 |
| ModelArchitecture | Method | I 3 D | 17 |
| ModelArchitecture | Method | convolution layers | 17 |
| ModelArchitecture | Method | attention | 16 |
| ModelArchitecture | Method | fully connected layers | 13 |
| ModelArchitecture | Method | Transformer | 13 |
| ModelArchitecture | Method | LSTM | 12 |
| ModelArchitecture | Method | self - attention | 11 |
| ModelArchitecture | Method | CNNs | 10 |
| ModelArchitecture | Method | ResNet | 10 |
| ModelArchitecture | Method | DACNN | 9 |
| ModelArchitecture | Method | MTN | 8 |
| ModelArchitecture | Task | vis - w 2 v | 1 |
| ModelArchitecture | Task | causal attention masking | 1 |
| ModelArchitecture | Task | serial - link robotic manipulators | 1 |
| ModelArchitecture | Task | robotic manipulators | 1 |
| ModelArchitecture | NIL | attention | 20 |
| ModelArchitecture | NIL | ( 2 + 1 )D | 6 |
| ModelArchitecture | NIL | attention between datapoints | 6 |
| ModelArchitecture | NIL | encoder layers | 2 |
| ModelArchitecture | NIL | heads | 2 |
| ModelArchitecture | NIL | Markov ones | 1 |
| ModelArchitecture | NIL | recurrent hidden states | 1 |
| ModelArchitecture | NIL | Non - local Neural Network | 1 |
| ModelArchitecture | NIL | embedding layer | 1 |
| ModelArchitecture | NIL | COCO | 1 |
| ModelArchitecture | NIL | attention module | 1 |
| ModelArchitecture | NIL | mask module | 1 |
| ModelArchitecture | NIL | generator | 1 |
| ModelArchitecture | NIL | GPT-2 | 1 |
| ModelArchitecture | NIL | attention maps | 1 |
| ReferenceLink | Dataset | Waseem | 2 |
| ReferenceLink | Dataset | Waseem and Hovy ( 2016 ) | 1 |
| ReferenceLink | Dataset | Obar | 1 |
| ReferenceLink | Dataset | Kobayashi ( 2018 ) | 1 |
| ReferenceLink | Dataset | 2019 | 1 |
| ReferenceLink | Dataset | 30 | 1 |
| ReferenceLink | Dataset | CIFAR-10 [ 55 | 1 |
| ReferenceLink | Method | Song and Ermon ( 2019 ) | 10 |
| ReferenceLink | Method | Waseem , 2016 | 4 |
| ReferenceLink | Method | Waseem and Hovy ( 2016 ) | 4 |
| ReferenceLink | Method | 90 | 4 |
| ReferenceLink | Method | Waseem and Hovy , 2016 | 3 |
| ReferenceLink | Method | Waseem | 3 |
| ReferenceLink | Method | Bostrom | 3 |
| ReferenceLink | Method | Du and Mordatch , 2019 | 3 |
| ReferenceLink | Method | Saremi and Hyvarinen ( 2019 ) | 3 |
| ReferenceLink | Method | 25 | 3 |
| ReferenceLink | Method | 24 | 3 |
| ReferenceLink | Method | Efron and Tibshirani , 1986 | 2 |
| ReferenceLink | Method | Kwok and Wang , 2013 | 2 |
| ReferenceLink | Method | Blodgett and O'Connor ( 2017 ) | 2 |
| ReferenceLink | Method | Rosset , 2019 | 2 |
| ReferenceLink | Task | 18 | 1 |
| ReferenceLink | Task | 90 | 1 |
| ReferenceLink | Task | 64 | 1 |
| ReferenceLink | NIL | 3 | 35 |
| ReferenceLink | NIL | 1 | 26 |
| ReferenceLink | NIL | 5 | 25 |
| ReferenceLink | NIL | 6 | 23 |
| ReferenceLink | NIL | 8 | 22 |
| ReferenceLink | NIL | 4 | 22 |
| ReferenceLink | NIL | 2 | 21 |
| ReferenceLink | NIL | 7 | 20 |
| ReferenceLink | NIL | 4 5 | 18 |
| ReferenceLink | NIL | 5 2 | 13 |
| ReferenceLink | NIL | 24 | 13 |
| ReferenceLink | NIL | 4 4 | 12 |
| ReferenceLink | NIL | 1 4 | 12 |
| ReferenceLink | NIL | 3 2 | 12 |
| ReferenceLink | NIL | Brown et al . , 2020 | 11 |
| Task | Dataset | CC | 2 |
| Task | Dataset | Protein regression | 2 |
| Task | Dataset | FiQA Task 1 sentiment scoring | 1 |
| Task | Dataset | FiQA sentiment scoring | 1 |
| Task | Dataset | PASCAL VOC 2 0 1 2 segmentation | 1 |
| Task | Dataset | HPSG | 1 |
| Task | Dataset | previous manually labeled RC datasets | 1 |
| Task | Dataset | a large reading comprehension dataset | 1 |
| Task | Dataset | Hatebase | 1 |
| Task | Dataset | AAE | 1 |
| Task | Dataset | labeling datasets | 1 |
| Task | Dataset | perplexity evaluation | 1 |
| Task | Dataset | Wikidetox Toxic Comment | 1 |
| Task | Dataset | sim2real transfer | 1 |
| Task | Dataset | Protein | 1 |
| Task | Method | few - shot segmentation | 3 |
| Task | Method | domain generalization | 3 |
| Task | Method | open - domain QA | 3 |
| Task | Method | generalization | 3 |
| Task | Method | unsupervised clustering | 2 |
| Task | Method | supervised partitioning | 2 |
| Task | Method | domain adaptation | 2 |
| Task | Method | NRI | 2 |
| Task | Method | AlexNet classification | 1 |
| Task | Method | few - shot learning | 1 |
| Task | Method | Few - Shot Learning | 1 |
| Task | Method | keypoint - based object detection | 1 |
| Task | Method | object detector | 1 |
| Task | Method | zero - shot - like generalization analysis | 1 |
| Task | Method | visual generalization | 1 |
| Task | Task | classification | 66 |
| Task | Task | pose estimation | 18 |
| Task | Task | semantic segmentation | 17 |
| Task | Task | localization | 17 |
| Task | Task | regression | 15 |
| Task | Task | segmentation | 13 |
| Task | Task | few - shot segmentation | 11 |
| Task | Task | text classification | 11 |
| Task | Task | question answering | 9 |
| Task | Task | pose tracking | 9 |
| Task | Task | person Re - ID | 8 |
| Task | Task | computer vision | 7 |
| Task | Task | sentiment analysis | 7 |
| Task | Task | concurrent activity recognition | 7 |
| Task | Task | image classification | 7 |
| Task | NIL | classification | 4 |
| Task | NIL | regression | 3 |
| Task | NIL | predict | 3 |
| Task | NIL | segmentation | 2 |
| Task | NIL | localization | 2 |
| Task | NIL | Neural machine translation | 2 |
| Task | NIL | evaluation/classification | 1 |
| Task | NIL | short sentence classification | 1 |
| Task | NIL | detection | 1 |
| Task | NIL | instance identification | 1 |
| Task | NIL | zero-shot prediction | 1 |
| Task | NIL | Regression | 1 |
| Task | NIL | prompt-based zero-shot prediction | 1 |
| Task | NIL | neural translation | 1 |
| Task | NIL | suffix prediction | 1 |
| URL | Dataset | PhraseBank | 1 |
| URL | Dataset | https :/ / stanford - qa.com | 1 |
| URL | Dataset | wikipedia / 20200301.en | 1 |
| URL | Dataset | http :/ / data.statmt . org / cc-100 / | 1 |
| URL | Dataset | https :/ / github.com / jdepoix / youtube - transcript - api | 1 |
| URL | Dataset | https :/ / github.com / vphill / pyoaiharvester / | 1 |
| URL | Dataset | https :/ / driving - olympics.ai / | 1 |
| URL | Method | https :/ / www.perspectiveapi.com | 1 |
| URL | Method | https :/ / hatebase.org / | 1 |
| URL | Method | https :/ / github.com / EleutherAI / the - pile | 1 |
| URL | Method | https :/ / archive.org / details / stackexchange | 1 |
| URL | Method | https :/ / bulkdata.uspto.gov / | 1 |
| URL | Method | https :/ / irclogs.ubuntu.com / | 1 |
| URL | Method | https :/ / philpapers.org / | 1 |
| URL | Method | https :/ / exporter.nih.gov / | 1 |
| URL | Method | https :/ / news.ycombinator.com | 1 |
| URL | Method | https :/ / arxiv.org / help / bulk_data_s3 | 1 |
| URL | Method | https :/ / www.courtlistener.com / api / bulk - info / | 1 |
| URL | Method | http :/ / www.statmt.org / europarl / | 1 |
| URL | Method | https :/ / github.com / sdtblck / PDFextract | 1 |
| URL | Method | https :/ / aka.ms / layoutxlm | 1 |
| URL | Method | https :/ / commoncrawl.org | 1 |
| URL | NIL | https://nlp.stanford.edu/projects/glove/ | 1 |
| URL | NIL | https://allennlp.org/elmo | 1 |
| URL | NIL | https : // github.com/princeton-nlp/LM-BFF | 1 |
| URL | NIL | https : //www.quora.com/q/quoradata/ numbers | 1 |
| URL | NIL | https : //github.com/UKPLab/ sentence-transformers | 1 |
| URL | NIL | https :/ / stanford - qa.com | 1 |
| URL | NIL | https :/ / www.courtlistener.com / | 1 |
| URL | NIL | https :/ / www.tensorflow.org / datasets / catalog / c4 | 1 |
| NIL | Dataset | SS1 | 3 |
| NIL | Dataset | NIH | 3 |
| NIL | Dataset | SS2 | 2 |
| NIL | Dataset | German | 2 |
| NIL | Dataset | DNLP | 2 |
| NIL | Dataset | HPSG | 2 |
| NIL | Dataset | Kinetics | 1 |
| NIL | Dataset | Photoshop | 1 |
| NIL | Dataset | MS COCO | 1 |
| NIL | Dataset | WSI | 1 |
| NIL | Dataset | penguin | 1 |
| NIL | Dataset | wild goose | 1 |
| NIL | Dataset | NIST | 1 |
| NIL | Dataset | VLAD | 1 |
| NIL | Dataset | COCO 2 0 1 7 | 1 |
| NIL | Method | generator | 8 |
| NIL | Method | MASK | 5 |
| NIL | Method | AAE | 5 |
| NIL | Method | WPA | 4 |
| NIL | Method | HPSG | 4 |
| NIL | Method | pxB | 3 |
| NIL | Method | NMT | 3 |
| NIL | Method | Amalgam | 3 |
| NIL | Method | S 3 D | 2 |
| NIL | Method | propnets | 2 |
| NIL | Method | DNLP | 2 |
| NIL | Method | MF | 2 |
| NIL | Method | precision | 2 |
| NIL | Method | RECs | 2 |
| NIL | Method | BPB | 2 |
| NIL | Task | NLP | 6 |
| NIL | Task | segmentation | 2 |
| NIL | Task | OOD | 2 |
| NIL | Task | natural language processing | 2 |
| NIL | Task | bounding box regression | 1 |
| NIL | Task | activity mapping | 1 |
| NIL | Task | concurrent activity predictions | 1 |
| NIL | Task | real - time speed | 1 |
| NIL | Task | ID | 1 |
| NIL | Task | Re - ID | 1 |
| NIL | Task | MOTA | 1 |
| NIL | Task | localization | 1 |
| NIL | Task | multi-class classification | 1 |
| NIL | Task | transitive verb | 1 |
| NIL | Task | translation | 1 |

## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
