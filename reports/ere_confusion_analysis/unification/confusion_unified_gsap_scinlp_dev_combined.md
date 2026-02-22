# Unified Label Confusion Analysis

**Generated:** 2026-02-08 11:36:00

**Split:** dev

**Model 1 (Rows):** GSAP

**Model 2 (Columns):** SCINLP

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

Rows: GSAP labels | Columns: SCINLP labels

|         |   Dataset |   Method |   Task |   NIL |
|:--------|----------:|---------:|-------:|------:|
| Dataset |       608 |       58 |      9 |   323 |
| Method  |        84 |     3223 |     33 |   309 |
| Task    |        27 |      344 |    497 |   156 |
| NIL     |       116 |     1727 |    153 |     0 |

### Entity Counts per Label

| Label | Gold | GSAP | SCINLP |
|-------|------|----|------|
| Dataset | 842 | 998 | 835 |
| Method | 4905 | 3649 | 5352 |
| Task | 824 | 1024 | 692 |
| NIL | 0 | 1996 | 788 |

### Label Mappings (Top 15 per Label Pair)

| GSAP Label | GSAP Original | SCINLP Label | SCINLP Original | Mention Text | Count |
|----------|----------|----------|----------|--------------|-------|
| Dataset | Dataset | Dataset | dataset | CIFAR-10 | 34 |
| Dataset | Dataset | Dataset | dataset | ImageNet | 29 |
| Dataset | Dataset | Dataset | dataset | FSS - 1 0 0 0 | 22 |
| Dataset | Dataset | Dataset | dataset | COCO | 21 |
| Dataset | Dataset | Dataset | dataset | MNIST | 16 |
| Dataset | Dataset | Dataset | dataset | SQuAD | 14 |
| Dataset | Dataset | Dataset | dataset | OpenWebText2 | 10 |
| Dataset | Dataset | Dataset | dataset | PASCAL VOC | 9 |
| Dataset | Dataset | Dataset | dataset | the Pile | 9 |
| Dataset | Dataset | Dataset | dataset | Pile | 9 |
| Dataset | Dataset | Dataset | dataset | XFUND | 9 |
| Dataset | Dataset | Dataset | dataset | PASCAL VOC 2 0 1 2 | 8 |
| Dataset | DataSource, Dataset | Dataset | dataset | GitHub | 8 |
| Dataset | Dataset | Dataset | dataset | CIFAR-100 | 8 |
| Dataset | Dataset | Dataset | dataset | Protein | 8 |
| Dataset | Dataset | Method | method | Pile | 8 |
| Dataset | Dataset | Method | method | the Pile | 6 |
| Dataset | Dataset | Method | method | SNLI | 5 |
| Dataset | DataSource | Method | method | Common Crawl | 5 |
| Dataset | Dataset | Method | method | FSS - 1 0 0 0 | 4 |
| Dataset | Dataset | Method | method | MNLI | 4 |
| Dataset | Dataset | Method | method | Pile - CC | 4 |
| Dataset | Dataset | Method | method | ImageNet | 3 |
| Dataset | Dataset | Method | method | FSS | 3 |
| Dataset | Dataset | Method | method | MRPC | 2 |
| Dataset | Dataset | Method | method | FlowTrack | 2 |
| Dataset | Dataset | Method | method | CC-100 | 2 |
| Dataset | Dataset | Method | method | mC4 | 2 |
| Dataset | Dataset | Method | method | pycld2 | 2 |
| Dataset | Dataset | Method | method | XFUND | 2 |
| Dataset | Dataset | Task | task | CoLA | 7 |
| Dataset | Dataset | Task | task | MRPC | 4 |
| Dataset | Dataset | Task | task | GLUE | 2 |
| Dataset | Dataset | Task | task | MNLI | 2 |
| Dataset | Dataset | Task | task | QNLI | 2 |
| Dataset | Dataset | Task | task | SNLI | 2 |
| Dataset | Dataset | Task | task | QQP | 1 |
| Dataset | Dataset | Task | task | SST-5 | 1 |
| Dataset | Dataset | Task | task | CR | 1 |
| Dataset | Dataset | Task | task | MPQA | 1 |
| Dataset | Dataset | Task | task | Subj | 1 |
| Dataset | Dataset | Task | task | TREC | 1 |
| Dataset | DataSource | Task | task | Fanfiction | 1 |
| Dataset | DataSource | Task | task | Common Crawl | 1 |
| Dataset | Dataset | NIL |  | Pile | 9 |
| Dataset | Dataset | NIL |  | Amalgam | 6 |
| Dataset | Dataset | NIL |  | GLUE | 5 |
| Dataset | Dataset | NIL |  | Kinetics | 3 |
| Dataset | Dataset | NIL |  | FSS - 1 0 0 0 | 3 |
| Dataset | Dataset | NIL |  | ILSVRC | 2 |
| Dataset | Dataset | NIL |  | penguin | 2 |
| Dataset | Dataset | NIL |  | COCO | 2 |
| Dataset | DataSource, Dataset | NIL |  | Wikipedia | 2 |
| Dataset | Dataset | NIL |  | MR | 2 |
| Dataset | Dataset | NIL |  | SS1 | 2 |
| Dataset | Dataset | NIL |  | SS2 | 2 |
| Dataset | Dataset | NIL |  | WPA | 2 |
| Dataset | Dataset | NIL |  | TransType2 | 2 |
| Dataset | Dataset | NIL |  | AAE | 2 |
| Method | ModelArchitecture | Dataset | dataset | ResNet - 1 8 | 2 |
| Method | MLModel | Dataset | dataset | AlexNet | 2 |
| Method | MLModel, ModelArchitecture | Dataset | dataset | FSS - 1 0 0 0 | 2 |
| Method | MLModel | Dataset | dataset | Hourglass - 1 0 4 | 2 |
| Method | MLModel, ModelArchitecture | Dataset | dataset | ResNet - 5 0 | 2 |
| Method | MLModel, ModelArchitecture | Dataset | dataset | ResNet | 2 |
| Method | MLModel | Dataset | dataset | RoBERTa-large | 2 |
| Method | Method | Dataset | dataset | Hatebase | 2 |
| Method | Method | Dataset | dataset | Hacker News | 2 |
| Method | MLModel, ModelArchitecture | Dataset | dataset | Resnet101 | 2 |
| Method | MLModel, Method | Dataset | dataset | sim2sim | 2 |
| Method | MLModel | Dataset | dataset | fsCOCO | 1 |
| Method | Method | Dataset | dataset | COCO | 1 |
| Method | MLModel | Dataset | dataset | MobileNet - v 2 | 1 |
| Method | ModelArchitecture | Dataset | dataset | ResNet 1 8 | 1 |
| Method | MLModelGeneric, ModelArchitecture | Method | method | NPTs | 111 |
| Method | MLModel, MLModelGeneric, Method, ModelArchitecture | Method | method | NPT | 93 |
| Method | MLModel, ModelArchitecture | Method | method | BERT | 48 |
| Method | MLModel, MLModelGeneric, Method | Method | method | TinyBERT | 46 |
| Method | MLModel, MLModelGeneric, Method | Method | method | GloVe | 36 |
| Method | MLModel, MLModelGeneric, ModelArchitecture | Method | method | GPT-3 | 35 |
| Method | MLModelGeneric, ModelArchitecture | Method | method | RCN | 34 |
| Method | MLModelGeneric, ModelArchitecture | Method | method | I 3 D | 32 |
| Method | MLModel, MLModelGeneric | Method | method | LayoutXLM | 30 |
| Method | MLModelGeneric, ModelArchitecture | Method | method | CNN | 25 |
| Method | MLModel, ModelArchitecture | Method | method | CornerNet | 25 |
| Method | MLModelGeneric, ModelArchitecture | Method | method | GCN | 25 |
| Method | MLModel, Method | Method | method | CornerNet - Squeeze | 22 |
| Method | MLModel, MLModelGeneric, Method | Method | method | ViCo | 22 |
| Method | MLModel, ModelArchitecture | Method | method | ULMFit | 18 |
| Method | Method | Task | task | KD | 11 |
| Method | Method | Task | task | task - specific distillation | 10 |
| Method | Method | Task | task | denoising score matching | 10 |
| Method | MLModelGeneric, Method | Task | task | data augmentation | 8 |
| Method | Method | Task | task | language modeling | 6 |
| Method | MLModelGeneric, Method | Task | task | natural language processing | 5 |
| Method | MLModelGeneric, Method | Task | task | pose tracking | 5 |
| Method | Method | Task | task | unsupervised learning | 5 |
| Method | Method | Task | task | label noise | 5 |
| Method | Method | Task | task | semi - supervised learning | 5 |
| Method | Method | Task | task | domain adaptation | 5 |
| Method | Method | Task | task | intermediate layer distillation | 4 |
| Method | MLModelGeneric, Method | Task | task | pose estimation | 4 |
| Method | Method | Task | task | human performance | 4 |
| Method | Method | Task | task | score matching | 4 |
| Method | MLModelGeneric | NIL |  | the model | 84 |
| Method | MLModelGeneric | NIL |  | models | 23 |
| Method | MLModel, ModelArchitecture | NIL |  | BERT | 16 |
| Method | MLModelGeneric | NIL |  | our model | 12 |
| Method | MLModelGeneric | NIL |  | a model | 11 |
| Method | Method | NIL |  | the spin - glass phase | 11 |
| Method | MLModelGeneric | NIL |  | the models | 10 |
| Method | MLModelGeneric | NIL |  | the generator | 10 |
| Method | Method | NIL |  | the flow | 10 |
| Method | Method | NIL |  | spin - glass | 10 |
| Method | MLModelGeneric | NIL |  | classifiers | 9 |
| Method | MLModelGeneric | NIL |  | the network | 8 |
| Method | MLModelGeneric | NIL |  | language models | 8 |
| Method | Method | NIL |  | fine - tuning | 7 |
| Method | MLModelGeneric | NIL |  | this model | 7 |
| Task | Task | Dataset | dataset | Protein regression | 3 |
| Task | Task | Dataset | dataset | FiQA Task 1 sentiment scoring | 1 |
| Task | Task | Dataset | dataset | FiQA sentiment scoring | 1 |
| Task | Task | Dataset | dataset | Re - ID | 1 |
| Task | Task | Dataset | dataset | PASCAL VOC 2 0 1 2 segmentation | 1 |
| Task | Task | Dataset | dataset | cloze | 1 |
| Task | Task | Dataset | dataset | sim2real transfer | 1 |
| Task | Task | Method | method | few - shot segmentation | 3 |
| Task | Task | Method | method | HPSG | 3 |
| Task | Task | Method | method | Re - ID | 2 |
| Task | Task | Method | method | Causal inference | 1 |
| Task | Task | Method | method | bounding box regression | 1 |
| Task | Task | Method | method | binary segmentation | 1 |
| Task | Task | Method | method | per - pixel classification | 1 |
| Task | Task | Method | method | C - way - K - shot segmentation | 1 |
| Task | Task | Method | method | saliency detection | 1 |
| Task | Task | Method | method | single - activity recognition strategies | 1 |
| Task | Task | Method | method | classification | 1 |
| Task | Task | Method | method | regression | 1 |
| Task | Task | Method | method | MLM | 1 |
| Task | Task | Method | method | NSP | 1 |
| Task | Task | Method | method | object detector | 1 |
| Task | Task | Task | task | classification | 47 |
| Task | Task | Task | task | semantic segmentation | 14 |
| Task | Task | Task | task | pose estimation | 13 |
| Task | Task | Task | task | localization | 11 |
| Task | Task | Task | task | text classification | 10 |
| Task | Task | Task | task | segmentation | 8 |
| Task | Task | Task | task | question answering | 8 |
| Task | Task | Task | task | few - shot segmentation | 7 |
| Task | Task | Task | task | regression | 7 |
| Task | Task | Task | task | concurrent activity recognition | 7 |
| Task | Task | Task | task | sentiment analysis | 6 |
| Task | Task | Task | task | image classification | 6 |
| Task | Task | Task | task | human detection | 6 |
| Task | Task | Task | task | binary classification | 6 |
| Task | Task | Task | task | multi-class classification | 6 |
| Task | Task | NIL |  | classification | 19 |
| Task | Task | NIL |  | localization | 7 |
| Task | Task | NIL |  | language modeling | 4 |
| Task | Task | NIL |  | temporal reasoning | 3 |
| Task | Task | NIL |  | regression | 3 |
| Task | Task | NIL |  | classify | 3 |
| Task | Task | NIL |  | generalization | 3 |
| Task | Task | NIL |  | person Re - ID | 2 |
| Task | Task | NIL |  | Regression | 2 |
| Task | Task | NIL |  | prompt-based zero-shot prediction | 2 |
| Task | Task | NIL |  | suffix prediction | 2 |
| Task | Task | NIL |  | reasoning | 2 |
| Task | Task | NIL |  | video understanding | 1 |
| Task | Task | NIL |  | action recognition and detection | 1 |
| Task | Task | NIL |  | temporal action detection and recognition | 1 |
| NIL |  | Dataset | dataset | black - aligned tweets | 9 |
| NIL |  | Dataset | dataset | this dataset | 7 |
| NIL |  | Dataset | dataset | tweets | 7 |
| NIL |  | Dataset | dataset | tabular data | 7 |
| NIL |  | Dataset | dataset | the dataset | 6 |
| NIL |  | Dataset | dataset | the Pile | 6 |
| NIL |  | Dataset | dataset | 2020 | 5 |
| NIL |  | Dataset | dataset | datapoints | 5 |
| NIL |  | Dataset | dataset | constituent datasets | 4 |
| NIL |  | Dataset | dataset | each dataset | 4 |
| NIL |  | Dataset | dataset | USPTO Backgrounds | 4 |
| NIL |  | Dataset | dataset | real data | 4 |
| NIL |  | Dataset | dataset | Wikipedia | 3 |
| NIL |  | Dataset | dataset | The dataset | 3 |
| NIL |  | Dataset | dataset | data | 3 |
| NIL |  | Method | method | datapoints | 19 |
| NIL |  | Method | method | Pile | 6 |
| NIL |  | Method | method | I 3 D | 4 |
| NIL |  | Method | method | ABA | 4 |
| NIL |  | Method | method | wrongly labeled samples | 3 |
| NIL |  | Method | method | Saremi | 3 |
| NIL |  | Method | method | test set | 3 |
| NIL |  | Method | method | batch | 3 |
| NIL |  | Method | method | 3D convolution | 2 |
| NIL |  | Method | method | S 3 D | 2 |
| NIL |  | Method | method | 2D | 2 |
| NIL |  | Method | method | deep learning | 2 |
| NIL |  | Method | method | GloVe | 2 |
| NIL |  | Method | method | GloVe+ViCo(linear, | 2 |
| NIL |  | Method | method | HPSG | 2 |
| NIL |  | Task | task | NLP | 7 |
| NIL |  | Task | task | reading comprehension | 5 |
| NIL |  | Task | task | label noise | 5 |
| NIL |  | Task | task | natural language processing | 4 |
| NIL |  | Task | task | tabular data | 4 |
| NIL |  | Task | task | development set | 3 |
| NIL |  | Task | task | noisy labels | 3 |
| NIL |  | Task | task | datapoints | 3 |
| NIL |  | Task | task | pose estimation | 2 |
| NIL |  | Task | task | sentence realization | 2 |
| NIL |  | Task | task | the dataset | 2 |
| NIL |  | Task | task | other answer types | 2 |
| NIL |  | Task | task | duplication | 2 |
| NIL |  | Task | task | transfer learning | 1 |
| NIL |  | Task | task | few - shot segmentation | 1 |

## Notes

- **Unified Labels**: All predictions mapped to unified schema (Dataset, Method, Task)
- **Partial Matching**: Uses gsaphub's partial span matching to align entities
- **NIL Class**: Represents entities annotated by one model but not the other
- **Pipeline Applied**: Merge → Drop → Map for both models before comparison

---
*Generated by UnifiedSciERE Unified Confusion Analysis*
