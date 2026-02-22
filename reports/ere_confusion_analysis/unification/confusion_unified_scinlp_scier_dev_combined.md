# Unified Label Confusion Analysis

**Generated:** 2026-02-08 11:35:55

**Split:** dev

**Model 1 (Rows):** SCINLP

**Model 2 (Columns):** SCIER

**Datasets Combined:** SCIER, SCINLP, GSAP

## Overview

This report shows confusion matrices comparing entity labels between two models
after applying the complete unification pipeline:

1. Merge stacked mentions (prefer larger spans)
2. Drop unmapped labels (null mappings)
3. Map to unified schema (Dataset, Method, Task)

The confusion matrix uses partial span matching to align entities with overlapping spans.


## Combined Datasets

### Confusion Matrix

Rows: SCINLP labels | Columns: SCIER labels

|         |   Dataset |   Method |   Task |   NIL |
|:--------|----------:|---------:|-------:|------:|
| Dataset |       772 |      129 |     46 |   301 |
| Method  |        48 |     2991 |    188 |   871 |
| Task    |        40 |      169 |    720 |   420 |
| NIL     |       135 |      385 |     70 |     0 |

### Entity Counts per Label

| Label | Gold | SCINLP | SCIER |
|-------|------|------|-----|
| Dataset | 842 | 1248 | 995 |
| Method | 4905 | 4098 | 3674 |
| Task | 824 | 1349 | 1024 |
| NIL | 0 | 590 | 1592 |

### Label Mappings (Top 15 per Label Pair)

| SCINLP Label | SCINLP Original | SCIER Label | SCIER Original | Mention Text | Count |
|----------|----------|----------|----------|--------------|-------|
| Dataset | dataset | Dataset | Dataset | CIFAR-10 | 35 |
| Dataset | dataset | Dataset | Dataset | ImageNet | 29 |
| Dataset | dataset | Dataset | Dataset | Pile | 29 |
| Dataset | dataset | Dataset | Dataset | FSS - 1 0 0 0 | 24 |
| Dataset | dataset | Dataset | Dataset | COCO | 23 |
| Dataset | dataset | Dataset | Dataset | MNIST | 16 |
| Dataset | dataset | Dataset | Dataset | SQuAD | 15 |
| Dataset | dataset | Dataset | Dataset | XFUND | 13 |
| Dataset | dataset | Dataset | Dataset | black - aligned tweets | 12 |
| Dataset | dataset | Dataset | Dataset | BookCorpus | 10 |
| Dataset | dataset | Dataset | Dataset | OpenWebText2 | 10 |
| Dataset | dataset | Dataset | Dataset | Protein | 10 |
| Dataset | dataset | Dataset | Dataset | PASCAL VOC | 9 |
| Dataset | dataset | Dataset | Dataset | Kinetics | 8 |
| Dataset | dataset | Dataset | Dataset | PASCAL VOC 2 0 1 2 | 8 |
| Dataset | dataset | Method | Method | fsCOCO | 4 |
| Dataset | dataset | Method | Method | fsPASCAL | 3 |
| Dataset | dataset | Method | Method | Hourglass - 1 0 4 | 3 |
| Dataset | dataset | Method | Method | ResNet - 1 8 | 2 |
| Dataset | dataset | Method | Method | ResNet - 5 0 | 2 |
| Dataset | dataset | Method | Method | Critch and Krueger , 2020 | 2 |
| Dataset | dataset | Method | Method | Resnet101 | 2 |
| Dataset | dataset | Method | Method | AlexNet | 1 |
| Dataset | dataset | Method | Method | FSS - 1 0 0 0 | 1 |
| Dataset | dataset | Method | Method | MobileNet - v 2 | 1 |
| Dataset | dataset | Method | Method | ResNet 1 8 | 1 |
| Dataset | dataset | Method | Method | PoseTrack | 1 |
| Dataset | dataset | Method | Method | ResNet 5 0 | 1 |
| Dataset | dataset | Method | Method | ResNet 5 0 - GCN | 1 |
| Dataset | dataset | Method | Method | WordNet | 1 |
| Dataset | dataset | Task | Task | tweets | 5 |
| Dataset | dataset | Task | Task | Protein regression | 3 |
| Dataset | dataset | Task | Task | RC | 2 |
| Dataset | dataset | Task | Task | person search | 1 |
| Dataset | dataset | Task | Task | Re - ID | 1 |
| Dataset | dataset | Task | Task | segmentation | 1 |
| Dataset | dataset | Task | Task | stories | 1 |
| Dataset | dataset | Task | Task | naturally occurring data | 1 |
| Dataset | dataset | Task | Task | Question - answer collection | 1 |
| Dataset | dataset | Task | Task | person | 1 |
| Dataset | dataset | Task | Task | all named entities | 1 |
| Dataset | dataset | Task | Task | demographic information | 1 |
| Dataset | dataset | Task | Task | tweets written | 1 |
| Dataset | dataset | Task | Task | classify tweets | 1 |
| Dataset | dataset | Task | Task | hate speech | 1 |
| Dataset | dataset | NIL |  | this dataset | 7 |
| Dataset | dataset | NIL |  | the dataset | 6 |
| Dataset | dataset | NIL |  | datapoints | 5 |
| Dataset | dataset | NIL |  | constituent datasets | 4 |
| Dataset | dataset | NIL |  | The dataset | 3 |
| Dataset | dataset | NIL |  | Waseem | 3 |
| Dataset | dataset | NIL |  | tweets | 3 |
| Dataset | dataset | NIL |  | each dataset | 3 |
| Dataset | dataset | NIL |  | 2020 | 3 |
| Dataset | dataset | NIL |  | data | 2 |
| Dataset | dataset | NIL |  | these datasets | 2 |
| Dataset | dataset | NIL |  | Blodgett et al . ( 2016 ) | 2 |
| Dataset | dataset | NIL |  | datasets | 2 |
| Dataset | dataset | NIL |  | 2019 | 2 |
| Dataset | dataset | NIL |  | benchmarks | 2 |
| Method | method | Dataset | Dataset | Pile | 16 |
| Method | method | Dataset | Dataset | SNLI | 5 |
| Method | method | Dataset | Dataset | ImageNet | 4 |
| Method | method | Dataset | Dataset | MNLI | 4 |
| Method | method | Dataset | Dataset | HPSG | 4 |
| Method | method | Dataset | Dataset | NPTs | 3 |
| Method | method | Dataset | Dataset | NPT - Base | 3 |
| Method | method | Dataset | Dataset | FSS - 1 0 0 0 | 2 |
| Method | method | Dataset | Dataset | MRPC | 2 |
| Method | method | Dataset | Dataset | Common Crawl | 2 |
| Method | method | Dataset | Dataset | PMC | 2 |
| Method | method | Dataset | Dataset | OpenAI API | 2 |
| Method | method | Dataset | Dataset | C4 | 2 |
| Method | method | Dataset | Dataset | mC4 | 2 |
| Method | method | Dataset | Dataset | XFUND | 2 |
| Method | method | Method | Method | NPTs | 106 |
| Method | method | Method | Method | NPT | 85 |
| Method | method | Method | Method | BERT | 50 |
| Method | method | Method | Method | TinyBERT | 45 |
| Method | method | Method | Method | GPT-3 | 41 |
| Method | method | Method | Method | GloVe | 40 |
| Method | method | Method | Method | I 3 D | 38 |
| Method | method | Method | Method | RCN | 36 |
| Method | method | Method | Method | LayoutXLM | 31 |
| Method | method | Method | Method | CornerNet | 25 |
| Method | method | Method | Method | GCN | 24 |
| Method | method | Method | Method | CNN | 22 |
| Method | method | Method | Method | CornerNet - Squeeze | 22 |
| Method | method | Method | Method | ViCo | 22 |
| Method | method | Method | Method | normalizing flows | 19 |
| Method | method | Task | Task | ML | 8 |
| Method | method | Task | Task | MLM | 4 |
| Method | method | Task | Task | few-shot learning | 4 |
| Method | method | Task | Task | NPT | 4 |
| Method | method | Task | Task | target masking | 4 |
| Method | method | Task | Task | few - shot learning | 3 |
| Method | method | Task | Task | few - shot segmentation | 3 |
| Method | method | Task | Task | language models | 3 |
| Method | method | Task | Task | zero - shot reinforcement learning | 3 |
| Method | method | Task | Task | Few - Shot Learning | 2 |
| Method | method | Task | Task | regression | 2 |
| Method | method | Task | Task | Re - ID | 2 |
| Method | method | Task | Task | segmentation | 2 |
| Method | method | Task | Task | masked language modeling | 2 |
| Method | method | Task | Task | in-context learning | 2 |
| Method | method | NIL |  | datapoints | 19 |
| Method | method | NIL |  | the model | 15 |
| Method | method | NIL |  | our model | 10 |
| Method | method | NIL |  | baselines | 9 |
| Method | method | NIL |  | these models | 7 |
| Method | method | NIL |  | a model | 6 |
| Method | method | NIL |  | models | 6 |
| Method | method | NIL |  | attention between datapoints | 6 |
| Method | method | NIL |  | flow | 5 |
| Method | method | NIL |  | phrase-based | 3 |
| Method | method | NIL |  | The model | 3 |
| Method | method | NIL |  | the classifiers | 3 |
| Method | method | NIL |  | Pile | 3 |
| Method | method | NIL |  | model | 3 |
| Method | method | NIL |  | attention | 3 |
| Task | task | Dataset | Dataset | CoLA | 7 |
| Task | task | Dataset | Dataset | MRPC | 4 |
| Task | task | Dataset | Dataset | MNLI | 2 |
| Task | task | Dataset | Dataset | QNLI | 2 |
| Task | task | Dataset | Dataset | SNLI | 2 |
| Task | task | Dataset | Dataset | HPSG | 2 |
| Task | task | Dataset | Dataset | white - aligned tweets | 2 |
| Task | task | Dataset | Dataset | black - aligned tweets | 2 |
| Task | task | Dataset | Dataset | tabular data | 2 |
| Task | task | Dataset | Dataset | GLUE | 1 |
| Task | task | Dataset | Dataset | QQP | 1 |
| Task | task | Dataset | Dataset | ImageNet | 1 |
| Task | task | Dataset | Dataset | SST-5 | 1 |
| Task | task | Dataset | Dataset | CR | 1 |
| Task | task | Dataset | Dataset | MPQA | 1 |
| Task | task | Method | Method | KD | 9 |
| Task | task | Method | Method | denoising score matching | 9 |
| Task | task | Method | Method | data augmentation | 8 |
| Task | task | Method | Method | task - specific distillation | 7 |
| Task | task | Method | Method | domain adaptation | 6 |
| Task | task | Method | Method | semi - supervised learning | 5 |
| Task | task | Method | Method | intermediate layer distillation | 4 |
| Task | task | Method | Method | unsupervised learning | 4 |
| Task | task | Method | Method | feature extraction | 3 |
| Task | task | Method | Method | Semi - supervised learning | 3 |
| Task | task | Method | Method | score matching | 3 |
| Task | task | Method | Method | self - supervised learning | 3 |
| Task | task | Method | Method | Transformer distillation | 2 |
| Task | task | Method | Method | BERT distillation | 2 |
| Task | task | Method | Method | distillation | 2 |
| Task | task | Task | Task | classification | 50 |
| Task | task | Task | Task | pose estimation | 16 |
| Task | task | Task | Task | semantic segmentation | 15 |
| Task | task | Task | Task | segmentation | 13 |
| Task | task | Task | Task | NLP | 12 |
| Task | task | Task | Task | natural language processing | 12 |
| Task | task | Task | Task | text classification | 11 |
| Task | task | Task | Task | localization | 11 |
| Task | task | Task | Task | pose tracking | 10 |
| Task | task | Task | Task | question answering | 9 |
| Task | task | Task | Task | language modeling | 9 |
| Task | task | Task | Task | few - shot segmentation | 8 |
| Task | task | Task | Task | sentiment analysis | 8 |
| Task | task | Task | Task | computer vision | 7 |
| Task | task | Task | Task | activity recognition | 7 |
| Task | task | NIL |  | development set | 3 |
| Task | task | NIL |  | noisy labels | 3 |
| Task | task | NIL |  | datapoints | 3 |
| Task | task | NIL |  | the dataset | 2 |
| Task | task | NIL |  | regression | 2 |
| Task | task | NIL |  | 3D convolution | 1 |
| Task | task | NIL |  | prediction | 1 |
| Task | task | NIL |  | Video - level action recognition | 1 |
| Task | task | NIL |  | text simplification | 1 |
| Task | task | NIL |  | keypointbased object detection | 1 |
| Task | task | NIL |  | GLUE | 1 |
| Task | task | NIL |  | instance identification assignment | 1 |
| Task | task | NIL |  | multiperson pose tracking | 1 |
| Task | task | NIL |  | tracking | 1 |
| Task | task | NIL |  | clas - sification | 1 |
| NIL |  | Dataset | Dataset | Pile | 17 |
| NIL |  | Dataset | Dataset | black - aligned corpus | 7 |
| NIL |  | Dataset | Dataset | datasets | 6 |
| NIL |  | Dataset | Dataset | dataset | 6 |
| NIL |  | Dataset | Dataset | German | 5 |
| NIL |  | Dataset | Dataset | GLUE | 4 |
| NIL |  | Dataset | Dataset | SS1 | 4 |
| NIL |  | Dataset | Dataset | English-German | 4 |
| NIL |  | Dataset | Dataset | Waseem | 4 |
| NIL |  | Dataset | Dataset | white - aligned corpus | 4 |
| NIL |  | Dataset | Dataset | Kinetics | 3 |
| NIL |  | Dataset | Dataset | FSS - 1 0 0 0 | 3 |
| NIL |  | Dataset | Dataset | SS2 | 3 |
| NIL |  | Dataset | Dataset | Davidson et al . ( 2017 ) | 3 |
| NIL |  | Dataset | Dataset | AAE | 3 |
| NIL |  | Method | Method | generator | 25 |
| NIL |  | Method | Method | BERT | 19 |
| NIL |  | Method | Method | ( 2 + 1 )D | 15 |
| NIL |  | Method | Method | NMT | 14 |
| NIL |  | Method | Method | WPA | 11 |
| NIL |  | Method | Method | Amalgam | 9 |
| NIL |  | Method | Method | Pile | 9 |
| NIL |  | Method | Method | machine learning | 7 |
| NIL |  | Method | Method | convolution | 6 |
| NIL |  | Method | Method | tree entropy | 6 |
| NIL |  | Method | Method | spin - glass | 6 |
| NIL |  | Method | Method | SK | 6 |
| NIL |  | Method | Method | RMSE | 6 |
| NIL |  | Method | Method | Transformer | 5 |
| NIL |  | Method | Method | feature extraction | 5 |
| NIL |  | Task | Task | classification | 23 |
| NIL |  | Task | Task | tweets | 22 |
| NIL |  | Task | Task | ML | 12 |
| NIL |  | Task | Task | localization | 7 |
| NIL |  | Task | Task | recall | 7 |
| NIL |  | Task | Task | natural language processing | 5 |
| NIL |  | Task | Task | NLP | 5 |
| NIL |  | Task | Task | precision | 5 |
| NIL |  | Task | Task | reasoning | 5 |
| NIL |  | Task | Task | segmentation | 4 |
| NIL |  | Task | Task | regression | 3 |
| NIL |  | Task | Task | unsupervised clustering | 3 |
| NIL |  | Task | Task | OOD | 3 |
| NIL |  | Task | Task | translation | 3 |
| NIL |  | Task | Task | case assignment | 3 |

## Notes

- **Unified Labels**: All predictions mapped to unified schema (Dataset, Method, Task)
- **Partial Matching**: Uses gsaphub's partial span matching to align entities
- **NIL Class**: Represents entities annotated by one model but not the other
- **Pipeline Applied**: Merge → Drop → Map for both models before comparison

---
*Generated by UnifiedSciERE Unified Confusion Analysis*
