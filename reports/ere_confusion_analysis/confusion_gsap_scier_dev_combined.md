# Entity Label Confusion Analysis

**Generated:** 2026-02-06 16:40:29

**Split:** dev

**Model 1:** GSAP

**Model 2:** SCIER

**Datasets Combined:** SCIER, SCINLP, GSAP

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.


## Combined Datasets

### Confusion Matrix

Rows: GSAP labels | Columns: SCIER labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |   URL |   NIL |
|:--------|-------------:|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|------:|------:|
| Dataset |           94 |       695 |              260 |        24 |               23 |       54 |                   5 |              27 |     10 |    18 |    98 |
| Method  |           14 |        55 |               72 |       603 |              913 |     1432 |                 843 |              13 |     33 |     4 |   330 |
| Task    |            6 |         3 |              226 |         2 |               47 |      276 |                  10 |               2 |    624 |     0 |   183 |
| NIL     |            9 |        23 |             1271 |         9 |              726 |      626 |                  42 |            1379 |     50 |    16 |     0 |

### Statistics

**GSAP Total Entities per Label:**

- Dataset: 1308
- Method: 4312
- Task: 1379
- NIL: 4151

**SCIER Total Entities per Label:**

- DataSource: 123
- Dataset: 776
- DatasetGeneric: 1829
- MLModel: 638
- MLModelGeneric: 1709
- Method: 2388
- ModelArchitecture: 900
- ReferenceLink: 1421
- Task: 717
- URL: 38
- NIL: 611

### Label Mappings (Top 15 per Label Pair)

| GSAP Label | SCIER Label | Mention Text | Count |
|----------|----------|--------------|-------|
| DataSource | Dataset | Common Crawl | 8 |
| DataSource | Dataset | WordNet | 7 |
| DataSource | Dataset | Wikipedia | 5 |
| DataSource | Dataset | ArXiv | 3 |
| DataSource | Dataset | GitHub | 3 |
| DataSource | Dataset | PubMed | 3 |
| DataSource | Dataset | arXiv | 3 |
| DataSource | Dataset | Wikipedia articles | 2 |
| DataSource | Dataset | English Wikipedia | 2 |
| DataSource | Dataset | Facebook | 2 |
| DataSource | Dataset | YouTube | 2 |
| DataSource | Dataset | PubMed Central | 2 |
| DataSource | Dataset | Stack Exchange | 2 |
| DataSource | Dataset | Ubuntu IRC | 2 |
| DataSource | Dataset | PMC | 2 |
| DataSource | Method | Common Crawl | 4 |
| DataSource | Method | WordNet | 1 |
| DataSource | Method | Google Perspective API | 1 |
| DataSource | Method | SAE | 1 |
| DataSource | Method | raw and filtered Common Crawl models | 1 |
| DataSource | Method | Reddit submissions | 1 |
| DataSource | Method | Stack Exchange | 1 |
| DataSource | Method | Common Crawl - derived | 1 |
| DataSource | Method | Common Crawl - as | 1 |
| DataSource | Method | StackOverflow | 1 |
| DataSource | Method | Facebook | 1 |
| DataSource | Task | Common Crawl | 2 |
| DataSource | Task | Wikipedia | 1 |
| DataSource | Task | Wikipedia articles | 1 |
| DataSource | Task | Twitter | 1 |
| DataSource | Task | Center for Digital Philosophy | 1 |
| DataSource | NIL | Twitter | 2 |
| DataSource | NIL | Wikipedia 's | 1 |
| DataSource | NIL | open - source code repositories | 1 |
| DataSource | NIL | YouTube | 1 |
| DataSource | NIL | Reddit | 1 |
| DataSource | NIL | each repository | 1 |
| DataSource | NIL | Open Archives Initiative | 1 |
| DataSource | NIL | PubMed | 1 |
| Dataset | Dataset | Pile | 41 |
| Dataset | Dataset | CIFAR-10 | 35 |
| Dataset | Dataset | ImageNet | 33 |
| Dataset | Dataset | FSS - 1 0 0 0 | 27 |
| Dataset | Dataset | COCO | 22 |
| Dataset | Dataset | MNIST | 18 |
| Dataset | Dataset | XFUND | 16 |
| Dataset | Dataset | SQuAD | 15 |
| Dataset | Dataset | SNLI | 13 |
| Dataset | Dataset | Kinetics | 10 |
| Dataset | Dataset | BookCorpus | 10 |
| Dataset | Dataset | CoLA | 10 |
| Dataset | Dataset | OpenWebText2 | 10 |
| Dataset | Dataset | MNLI | 9 |
| Dataset | Dataset | Protein | 9 |
| Dataset | Method | FSS - 1 0 0 0 | 6 |
| Dataset | Method | Pile | 6 |
| Dataset | Method | fsCOCO | 4 |
| Dataset | Method | fsPASCAL | 3 |
| Dataset | Method | WPA | 3 |
| Dataset | Method | Pile - CC | 3 |
| Dataset | Method | FlowTrack - 1 5 2 | 2 |
| Dataset | Method | Amalgam | 2 |
| Dataset | Method | CC-100 | 2 |
| Dataset | Method | pycld2 | 2 |
| Dataset | Method | Guided Network - 1 shot | 1 |
| Dataset | Method | VGG - 1 6 | 1 |
| Dataset | Method | Hourglass - 1 0 4 | 1 |
| Dataset | Method | PoseTrack | 1 |
| Dataset | Method | JointFlow | 1 |
| Dataset | Task | instance level segmentation | 1 |
| Dataset | Task | person search | 1 |
| Dataset | Task | Protein | 1 |
| Dataset | NIL | Amalgam | 3 |
| Dataset | NIL | penguin | 2 |
| Dataset | NIL | GLUE | 2 |
| Dataset | NIL | Pile | 2 |
| Dataset | NIL | ImageNet/COCO | 1 |
| Dataset | NIL | wild goose | 1 |
| Dataset | NIL | minival | 1 |
| Dataset | NIL | MOTA | 1 |
| Dataset | NIL | COCO | 1 |
| Dataset | NIL | OASeg | 1 |
| Dataset | NIL | VOC | 1 |
| Dataset | NIL | disamb + | 1 |
| Dataset | NIL | RK-VFIN | 1 |
| Dataset | NIL | NEGRA | 1 |
| Dataset | NIL | stories | 1 |
| DatasetGeneric | Dataset | Pile | 16 |
| DatasetGeneric | Dataset | black - aligned tweets | 15 |
| DatasetGeneric | Dataset | datasets | 12 |
| DatasetGeneric | Dataset | dataset | 8 |
| DatasetGeneric | Dataset | tabular data | 8 |
| DatasetGeneric | Dataset | white - aligned tweets | 7 |
| DatasetGeneric | Dataset | black - aligned corpus | 7 |
| DatasetGeneric | Dataset | white - aligned corpus | 4 |
| DatasetGeneric | Dataset | training data | 4 |
| DatasetGeneric | Dataset | CC | 3 |
| DatasetGeneric | Dataset | BookCorpus | 3 |
| DatasetGeneric | Dataset | labeled data | 3 |
| DatasetGeneric | Dataset | Protein | 3 |
| DatasetGeneric | Dataset | real data | 3 |
| DatasetGeneric | Dataset | English Wikipedia | 2 |
| DatasetGeneric | Method | Pile | 6 |
| DatasetGeneric | Method | I 3 D | 4 |
| DatasetGeneric | Method | white - aligned tweets | 4 |
| DatasetGeneric | Method | GPT-3 | 3 |
| DatasetGeneric | Method | form templates | 2 |
| DatasetGeneric | Method | unlabeled data | 2 |
| DatasetGeneric | Method | noisy samples | 2 |
| DatasetGeneric | Method | minibatches | 2 |
| DatasetGeneric | Method | batch size 512 | 2 |
| DatasetGeneric | Method | I 3 D ResNet | 1 |
| DatasetGeneric | Method | S 3 D | 1 |
| DatasetGeneric | Method | pixelwise segmentation labels | 1 |
| DatasetGeneric | Method | Saccades | 1 |
| DatasetGeneric | Method | detection boxes | 1 |
| DatasetGeneric | Method | NPP | 1 |
| DatasetGeneric | Task | tweets | 29 |
| DatasetGeneric | Task | answer types | 5 |
| DatasetGeneric | Task | datapoints | 5 |
| DatasetGeneric | Task | NLP | 4 |
| DatasetGeneric | Task | reading comprehension | 4 |
| DatasetGeneric | Task | wrongly labeled samples | 4 |
| DatasetGeneric | Task | attention between datapoints | 4 |
| DatasetGeneric | Task | unlabeled data | 3 |
| DatasetGeneric | Task | training datapoints | 3 |
| DatasetGeneric | Task | few - shot segmentation | 2 |
| DatasetGeneric | Task | natural language processing | 2 |
| DatasetGeneric | Task | sentiment analysis | 2 |
| DatasetGeneric | Task | datasets | 2 |
| DatasetGeneric | Task | questions | 2 |
| DatasetGeneric | Task | RC | 2 |
| DatasetGeneric | NIL | datapoints | 46 |
| DatasetGeneric | NIL | the data | 44 |
| DatasetGeneric | NIL | the dataset | 39 |
| DatasetGeneric | NIL | data | 23 |
| DatasetGeneric | NIL | each dataset | 22 |
| DatasetGeneric | NIL | the training set | 22 |
| DatasetGeneric | NIL | datasets | 19 |
| DatasetGeneric | NIL | tweets | 18 |
| DatasetGeneric | NIL | the training data | 15 |
| DatasetGeneric | NIL | these datasets | 15 |
| DatasetGeneric | NIL | a dataset | 14 |
| DatasetGeneric | NIL | other datapoints | 13 |
| DatasetGeneric | NIL | the entire dataset | 11 |
| DatasetGeneric | NIL | training data | 10 |
| DatasetGeneric | NIL | the validation set | 9 |
| MLModel | Dataset | Pile | 3 |
| MLModel | Dataset | NPT - Base | 2 |
| MLModel | Dataset | AlexNet | 1 |
| MLModel | Dataset | FSS - 1 0 0 0 | 1 |
| MLModel | Dataset | FinBERT | 1 |
| MLModel | Dataset | FinBERT - task | 1 |
| MLModel | Dataset | FinBERT - domain | 1 |
| MLModel | Dataset | Vi - sualGenome | 1 |
| MLModel | Dataset | RoBERTa-large | 1 |
| MLModel | Dataset | PET | 1 |
| MLModel | Dataset | ALPACA-7B | 1 |
| MLModel | Dataset | ALPACA-7B-LoRA | 1 |
| MLModel | Dataset | CHATGLM | 1 |
| MLModel | Dataset | Biber | 1 |
| MLModel | Dataset | OWT2 | 1 |
| MLModel | Method | TinyBERT | 44 |
| MLModel | Method | BERT | 43 |
| MLModel | Method | GPT-3 | 26 |
| MLModel | Method | LayoutXLM | 25 |
| MLModel | Method | CornerNet | 20 |
| MLModel | Method | ULMFit | 18 |
| MLModel | Method | FinBERT | 16 |
| MLModel | Method | YOLOv 3 | 15 |
| MLModel | Method | CornerNet - Saccade | 14 |
| MLModel | Method | CornerNet - Squeeze | 13 |
| MLModel | Method | ViCo | 13 |
| MLModel | Method | GloVe | 11 |
| MLModel | Method | CornerNet - Lite | 9 |
| MLModel | Method | BERT SMALL | 9 |
| MLModel | Method | ELMo | 8 |
| MLModel | Task | vis - w 2 v | 1 |
| MLModel | Task | PET | 1 |
| MLModel | NIL | robocar | 2 |
| MLModel | NIL | ResNet 1 0 1 - I 3 D - NL | 1 |
| MLModel | NIL | res - 5 | 1 |
| MLModel | NIL | T5 | 1 |
| MLModel | NIL | BYPAS_VN | 1 |
| MLModel | NIL | VAUX | 1 |
| MLModel | NIL | Minh-Thang Luong | 1 |
| MLModel | NIL | GPyTorch | 1 |
| MLModelGeneric | Dataset | NPTs | 3 |
| MLModelGeneric | Dataset | Founta et al . ( 2018 ) | 2 |
| MLModelGeneric | Dataset | NPT | 2 |
| MLModelGeneric | Dataset | NPT - Small | 2 |
| MLModelGeneric | Dataset | ImageNet | 1 |
| MLModelGeneric | Dataset | PET | 1 |
| MLModelGeneric | Dataset | T5-3B 13 | 1 |
| MLModelGeneric | Dataset | YouTube | 1 |
| MLModelGeneric | Dataset | Pile | 1 |
| MLModelGeneric | Dataset | Cs | 1 |
| MLModelGeneric | Dataset | curie | 1 |
| MLModelGeneric | Dataset | SOTA | 1 |
| MLModelGeneric | Dataset | PyTorch | 1 |
| MLModelGeneric | Dataset | MNIST | 1 |
| MLModelGeneric | Dataset | CIFAR-10 | 1 |
| MLModelGeneric | Method | NPTs | 103 |
| MLModelGeneric | Method | NPT | 60 |
| MLModelGeneric | Method | I 3 D | 24 |
| MLModelGeneric | Method | RCN | 23 |
| MLModelGeneric | Method | MTN | 18 |
| MLModelGeneric | Method | SK | 17 |
| MLModelGeneric | Method | language models | 14 |
| MLModelGeneric | Method | ( 2 + 1 )D | 13 |
| MLModelGeneric | Method | neural network | 12 |
| MLModelGeneric | Method | 3D CNNs | 11 |
| MLModelGeneric | Method | logistic regression | 11 |
| MLModelGeneric | Method | attention model | 10 |
| MLModelGeneric | Method | non - parametric models | 10 |
| MLModelGeneric | Method | CNN | 9 |
| MLModelGeneric | Method | Faster R - CNN | 9 |
| MLModelGeneric | Task | ML | 6 |
| MLModelGeneric | Task | segmentation | 4 |
| MLModelGeneric | Task | natural language processing | 3 |
| MLModelGeneric | Task | classification | 3 |
| MLModelGeneric | Task | language models | 3 |
| MLModelGeneric | Task | semantic segmentation | 2 |
| MLModelGeneric | Task | robotic manipulators | 2 |
| MLModelGeneric | Task | NPT | 2 |
| MLModelGeneric | Task | few - shot segmentation | 1 |
| MLModelGeneric | Task | sentiment analysis | 1 |
| MLModelGeneric | Task | transfer learning | 1 |
| MLModelGeneric | Task | concurrent activity recognition | 1 |
| MLModelGeneric | Task | image recognition | 1 |
| MLModelGeneric | Task | PLMs | 1 |
| MLModelGeneric | Task | pose tracking | 1 |
| MLModelGeneric | NIL | the model | 97 |
| MLModelGeneric | NIL | models | 31 |
| MLModelGeneric | NIL | our model | 22 |
| MLModelGeneric | NIL | a model | 17 |
| MLModelGeneric | NIL | the models | 11 |
| MLModelGeneric | NIL | these models | 11 |
| MLModelGeneric | NIL | classifiers | 10 |
| MLModelGeneric | NIL | the baselines | 10 |
| MLModelGeneric | NIL | the network | 9 |
| MLModelGeneric | NIL | The model | 8 |
| MLModelGeneric | NIL | our approach | 8 |
| MLModelGeneric | NIL | this model | 7 |
| MLModelGeneric | NIL | the model 's | 7 |
| MLModelGeneric | NIL | our method | 6 |
| MLModelGeneric | NIL | language models | 6 |
| Method | Dataset | Pile | 4 |
| Method | Dataset | Google Cloud Platform | 3 |
| Method | Dataset | OpenAI API | 3 |
| Method | Dataset | HPSG | 2 |
| Method | Dataset | pandoc | 2 |
| Method | Dataset | Hacker News | 2 |
| Method | Dataset | scikit - learn | 2 |
| Method | Dataset | ImageNet | 1 |
| Method | Dataset | Photoshop | 1 |
| Method | Dataset | COCO | 1 |
| Method | Dataset | SSM | 1 |
| Method | Dataset | Word - Net | 1 |
| Method | Dataset | ViCo | 1 |
| Method | Dataset | Phrasal | 1 |
| Method | Dataset | mgiza | 1 |
| Method | Method | GloVe | 22 |
| Method | Method | normalizing flows | 22 |
| Method | Method | sparse convolution | 18 |
| Method | Method | denoising score matching | 16 |
| Method | Method | KD | 14 |
| Method | Method | spin - glass | 14 |
| Method | Method | NPT | 14 |
| Method | Method | data augmentation | 12 |
| Method | Method | word embeddings | 11 |
| Method | Method | Transformer distillation | 11 |
| Method | Method | SIFP | 11 |
| Method | Method | spin - glasses | 11 |
| Method | Method | DKL | 11 |
| Method | Method | dense convolution | 10 |
| Method | Method | normalizing flow | 10 |
| Method | Task | human | 7 |
| Method | Task | language modeling | 6 |
| Method | Task | natural language processing | 5 |
| Method | Task | pose tracking | 5 |
| Method | Task | word embeddings | 5 |
| Method | Task | filtering | 5 |
| Method | Task | target masking | 5 |
| Method | Task | few-shot learning | 4 |
| Method | Task | ML | 4 |
| Method | Task | Few - Shot Learning | 3 |
| Method | Task | MLM | 3 |
| Method | Task | label noise | 3 |
| Method | Task | iterative filtering | 3 |
| Method | Task | training | 3 |
| Method | Task | zero - shot reinforcement learning | 3 |
| Method | NIL | the flow | 13 |
| Method | NIL | fine - tuning | 10 |
| Method | NIL | fine-tuning | 9 |
| Method | NIL | the spin - glass phase | 8 |
| Method | NIL | spin - glass | 8 |
| Method | NIL | pre - training | 7 |
| Method | NIL | the annotation vectors | 5 |
| Method | NIL | an unsupervised fashion | 4 |
| Method | NIL | the reverse KL loss | 4 |
| Method | NIL | the reverse KL divergence | 4 |
| Method | NIL | random initialisation | 3 |
| Method | NIL | re - training | 3 |
| Method | NIL | finetuning | 3 |
| Method | NIL | standard finetuning | 3 |
| Method | NIL | crowdworkers | 3 |
| ModelArchitecture | Dataset | FSS - 1 0 0 0 | 1 |
| ModelArchitecture | Dataset | BART | 1 |
| ModelArchitecture | Dataset | NPT - Base | 1 |
| ModelArchitecture | Dataset | NPT - Small | 1 |
| ModelArchitecture | Dataset | Forest Cover | 1 |
| ModelArchitecture | Method | RCN | 29 |
| ModelArchitecture | Method | BERT | 25 |
| ModelArchitecture | Method | NPT | 24 |
| ModelArchitecture | Method | CNN | 23 |
| ModelArchitecture | Method | GCN | 23 |
| ModelArchitecture | Method | GPT-3 | 14 |
| ModelArchitecture | Method | fully connected layers | 13 |
| ModelArchitecture | Method | CNNs | 13 |
| ModelArchitecture | Method | LSTM | 12 |
| ModelArchitecture | Method | Transformer | 11 |
| ModelArchitecture | Method | logistic regression | 11 |
| ModelArchitecture | Method | attention model | 11 |
| ModelArchitecture | Method | attention | 10 |
| ModelArchitecture | Method | convolution layers | 9 |
| ModelArchitecture | Method | DACNN | 9 |
| ModelArchitecture | Task | attention | 2 |
| ModelArchitecture | Task | NPTs | 2 |
| ModelArchitecture | Task | spatial attention | 1 |
| ModelArchitecture | Task | dependency and constituency trees | 1 |
| ModelArchitecture | Task | attention between datapoints | 1 |
| ModelArchitecture | Task | full NPT | 1 |
| ModelArchitecture | Task | Attention between datapoints | 1 |
| ModelArchitecture | Task | NPT | 1 |
| ModelArchitecture | NIL | attention | 13 |
| ModelArchitecture | NIL | VLAD | 2 |
| ModelArchitecture | NIL | Attention | 2 |
| ModelArchitecture | NIL | attention weights | 2 |
| ModelArchitecture | NIL | heads | 2 |
| ModelArchitecture | NIL | trees | 2 |
| ModelArchitecture | NIL | recurrent hidden states | 1 |
| ModelArchitecture | NIL | convolution layers | 1 |
| ModelArchitecture | NIL | recurrent neural network | 1 |
| ModelArchitecture | NIL | tri - axial self - attention encoder - decoder | 1 |
| ModelArchitecture | NIL | temporal attentions | 1 |
| ModelArchitecture | NIL | fully convolutional | 1 |
| ModelArchitecture | NIL | fully - convolutional | 1 |
| ModelArchitecture | NIL | RNN | 1 |
| ModelArchitecture | NIL | ResNet | 1 |
| ReferenceLink | Dataset | Waseem | 6 |
| ReferenceLink | Dataset | Founta et al . ( 2018 ) | 4 |
| ReferenceLink | Dataset | Davidson et al . ( 2017 ) | 3 |
| ReferenceLink | Dataset | Richardson et al . , 2013 | 1 |
| ReferenceLink | Dataset | Hovy | 1 |
| ReferenceLink | Dataset | Waseem ( 2016 ) | 1 |
| ReferenceLink | Dataset | Davidson et al . , 2017 | 1 |
| ReferenceLink | Dataset | Brown et al . ( 2020 ) | 1 |
| ReferenceLink | Dataset | Caswell et al . ( 2020 ) | 1 |
| ReferenceLink | Dataset | aff | 1 |
| ReferenceLink | Dataset | Google | 1 |
| ReferenceLink | Dataset | MacFarlane , - 2020 | 1 |
| ReferenceLink | Dataset | Chi et al . , 2020 | 1 |
| ReferenceLink | Dataset | Vincent | 1 |
| ReferenceLink | Dataset | Song and Ermon ( 2019 ) | 1 |
| ReferenceLink | Method | Saremi | 2 |
| ReferenceLink | Method | 2021a | 1 |
| ReferenceLink | Method | Richardson et al . ( 2013 ) | 1 |
| ReferenceLink | Method | Tatman | 1 |
| ReferenceLink | Method | Rosset | 1 |
| ReferenceLink | Method | Rae | 1 |
| ReferenceLink | Method | Critch and Krueger , 2020 | 1 |
| ReferenceLink | Method | Radford et al . , 2018 | 1 |
| ReferenceLink | Method | Hardin | 1 |
| ReferenceLink | Method | Rao | 1 |
| ReferenceLink | Method | Vincent | 1 |
| ReferenceLink | Method | Lawrence | 1 |
| ReferenceLink | Task | Silva et al . , 2016 | 1 |
| ReferenceLink | Task | Brown et al . ( 2020 ) | 1 |
| ReferenceLink | NIL | 3 | 32 |
| ReferenceLink | NIL | 2 | 27 |
| ReferenceLink | NIL | 6 | 22 |
| ReferenceLink | NIL | 4 5 | 21 |
| ReferenceLink | NIL | 4 | 21 |
| ReferenceLink | NIL | 8 | 20 |
| ReferenceLink | NIL | 5 | 20 |
| ReferenceLink | NIL | 7 | 19 |
| ReferenceLink | NIL | 24 | 18 |
| ReferenceLink | NIL | 1 | 15 |
| ReferenceLink | NIL | 1 4 | 14 |
| ReferenceLink | NIL | 5 2 | 13 |
| ReferenceLink | NIL | 25 | 13 |
| ReferenceLink | NIL | 3 2 | 12 |
| ReferenceLink | NIL | 4 4 | 11 |
| Task | Dataset | HPSG | 2 |
| Task | Dataset | few - shot segmentation | 1 |
| Task | Dataset | FiQA Task 1 sentiment scoring dataset | 1 |
| Task | Dataset | FiQA sentiment scoring | 1 |
| Task | Dataset | PASCAL VOC 2 0 1 2 segmentation | 1 |
| Task | Dataset | English-French | 1 |
| Task | Dataset | cloze queries | 1 |
| Task | Dataset | DeepMind Mathematics | 1 |
| Task | Dataset | duplication task | 1 |
| Task | Method | feature extraction | 2 |
| Task | Method | HPSG parsing | 2 |
| Task | Method | deep syntactic analysis | 2 |
| Task | Method | domain adaptation | 2 |
| Task | Method | OSLSM - 1 shot | 1 |
| Task | Method | few - shot segmentation | 1 |
| Task | Method | object detector | 1 |
| Task | Method | Re - ID head | 1 |
| Task | Method | FastPose | 1 |
| Task | Method | zero - shot - like generalization analysis | 1 |
| Task | Method | zero - shot | 1 |
| Task | Method | Prompt-based prediction | 1 |
| Task | Method | prompt generation | 1 |
| Task | Method | prompt-based zero-shot prediction | 1 |
| Task | Method | zero-shot prediction | 1 |
| Task | Task | classification | 70 |
| Task | Task | localization | 17 |
| Task | Task | semantic segmentation | 15 |
| Task | Task | pose estimation | 13 |
| Task | Task | text classification | 10 |
| Task | Task | question answering | 10 |
| Task | Task | regression | 10 |
| Task | Task | segmentation | 9 |
| Task | Task | few - shot segmentation | 9 |
| Task | Task | person Re - ID | 8 |
| Task | Task | reading comprehension | 8 |
| Task | Task | activity recognition | 7 |
| Task | Task | image classification | 7 |
| Task | Task | Re - ID | 7 |
| Task | Task | binary classification | 7 |
| Task | NIL | temporal reasoning | 3 |
| Task | NIL | language modeling | 3 |
| Task | NIL | regression | 3 |
| Task | NIL | Regression | 2 |
| Task | NIL | classify | 2 |
| Task | NIL | spatial and temporal reasoning | 1 |
| Task | NIL | precipitation forecasting | 1 |
| Task | NIL | Video - level action recognition | 1 |
| Task | NIL | dense prediction | 1 |
| Task | NIL | NLP | 1 |
| Task | NIL | keypointbased object detection | 1 |
| Task | NIL | linguistic generalization | 1 |
| Task | NIL | instance identification | 1 |
| Task | NIL | multiperson pose tracking | 1 |
| Task | NIL | feature extraction | 1 |
| URL | Dataset | PhraseBank | 1 |
| URL | Dataset | https :/ / www.perspectiveapi.com | 1 |
| URL | Dataset | https :/ / hatebase.org / | 1 |
| URL | Dataset | wikipedia / 20200301.en | 1 |
| URL | Dataset | SpamScope | 1 |
| URL | Dataset | https :/ / bulkdata.uspto.gov / | 1 |
| URL | Dataset | https :/ / philpapers.org / | 1 |
| URL | Dataset | https :/ / exporter.nih.gov / | 1 |
| URL | Dataset | https :/ / news.ycombinator.com | 1 |
| URL | Dataset | https :/ / arxiv.org / help / bulk_data_s3 | 1 |
| URL | Dataset | http :/ / www.statmt.org / europarl / | 1 |
| URL | Dataset | https :/ / github.com / sdtblck / PDFextract | 1 |
| URL | Dataset | ekzhu | 1 |
| URL | Dataset | layoutxlm | 1 |
| URL | Dataset | https :/ / commoncrawl.org | 1 |
| URL | Method | stackexchange | 1 |
| URL | Method | vphill | 1 |
| URL | Method | CuriousAI | 1 |
| URL | Method | Non - Parametric - Transformers | 1 |
| URL | NIL | https :/ / stanford - qa.com | 2 |
| URL | NIL | https://nlp.stanford.edu/projects/glove/ | 1 |
| URL | NIL | https://allennlp.org/elmo | 1 |
| URL | NIL | https : // github.com/princeton-nlp/LM-BFF | 1 |
| URL | NIL | https : //github.com/UKPLab/ sentence-transformers | 1 |
| URL | NIL | https :/ / www.courtlistener.com / | 1 |
| URL | NIL | www.fanfiction.net | 1 |
| URL | NIL | https | 1 |
| URL | NIL | https :/ / github.com / EleutherAI / the - pile | 1 |
| URL | NIL | https :/ / irclogs.ubuntu.com / | 1 |
| URL | NIL | http :/ / data.statmt . org / cc-100 / | 1 |
| URL | NIL | https :/ / www.tensorflow.org / datasets / catalog / c4 | 1 |
| URL | NIL | https :/ / www.courtlistener.com / api / bulk - info / | 1 |
| URL | NIL | https :/ / github.com / jdepoix / youtube - transcript - api | 1 |
| URL | NIL | https :/ / driving - olympics.ai / | 1 |
| NIL | Dataset | English-German | 4 |
| NIL | Dataset | German | 4 |
| NIL | Dataset | CLS | 2 |
| NIL | Dataset | SS1 | 2 |
| NIL | Dataset | bitext | 2 |
| NIL | Dataset | Minnesota | 2 |
| NIL | Dataset | DNLP | 2 |
| NIL | Dataset | HPSG | 2 |
| NIL | Dataset | Microsoft Azure | 2 |
| NIL | Dataset | LaTeX | 2 |
| NIL | Dataset | USPTO | 2 |
| NIL | Dataset | datasheet | 2 |
| NIL | Dataset | Pile | 2 |
| NIL | Dataset | fanfiction | 2 |
| NIL | Dataset | autonomous - driving cars | 1 |
| NIL | Method | generator | 17 |
| NIL | Method | NMT | 7 |
| NIL | Method | convolution | 5 |
| NIL | Method | R2 | 4 |
| NIL | Method | machine learning | 4 |
| NIL | Method | ABA | 4 |
| NIL | Method | DG | 3 |
| NIL | Method | SS2 | 3 |
| NIL | Method | WPA | 3 |
| NIL | Method | feature extraction | 3 |
| NIL | Method | confidence measures | 3 |
| NIL | Method | HPSG | 3 |
| NIL | Method | PT | 3 |
| NIL | Method | confidence weights | 3 |
| NIL | Method | n*gga | 3 |
| NIL | Task | ML | 10 |
| NIL | Task | natural language processing | 8 |
| NIL | Task | segmentation | 5 |
| NIL | Task | NLP | 5 |
| NIL | Task | recall | 5 |
| NIL | Task | precision | 5 |
| NIL | Task | classification | 4 |
| NIL | Task | OOD | 3 |
| NIL | Task | translation | 3 |
| NIL | Task | sentence realization | 3 |
| NIL | Task | case assignment | 3 |
| NIL | Task | EMT | 3 |
| NIL | Task | against label noise | 3 |
| NIL | Task | computer vision | 2 |
| NIL | Task | accuracy | 2 |

## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
