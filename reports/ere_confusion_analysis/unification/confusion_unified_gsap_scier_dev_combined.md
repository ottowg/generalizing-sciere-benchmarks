# Unified Label Confusion Analysis

**Generated:** 2026-02-08 11:36:06

**Split:** dev

**Model 1 (Rows):** GSAP

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

Rows: GSAP labels | Columns: SCIER labels

|         |   Dataset |   Method |   Task |   NIL |
|:--------|----------:|---------:|-------:|------:|
| Dataset |       735 |       97 |      9 |   407 |
| Method  |        64 |     3549 |     32 |   419 |
| Task    |         5 |      326 |    602 |   404 |
| NIL     |        31 |     1380 |     49 |     0 |

### Entity Counts per Label

| Label | Gold | GSAP | SCIER |
|-------|------|----|-----|
| Dataset | 842 | 1248 | 835 |
| Method | 4905 | 4064 | 5352 |
| Task | 824 | 1337 | 692 |
| NIL | 0 | 1460 | 1230 |

### Label Mappings (Top 15 per Label Pair)

| GSAP Label | GSAP Original | SCIER Label | SCIER Original | Mention Text | Count |
|----------|----------|----------|----------|--------------|-------|
| Dataset | Dataset | Dataset | Dataset | Pile | 36 |
| Dataset | Dataset | Dataset | Dataset | CIFAR-10 | 34 |
| Dataset | Dataset | Dataset | Dataset | ImageNet | 33 |
| Dataset | Dataset | Dataset | Dataset | FSS - 1 0 0 0 | 27 |
| Dataset | Dataset | Dataset | Dataset | COCO | 21 |
| Dataset | Dataset | Dataset | Dataset | MNIST | 17 |
| Dataset | Dataset | Dataset | Dataset | XFUND | 15 |
| Dataset | Dataset | Dataset | Dataset | SQuAD | 13 |
| Dataset | Dataset | Dataset | Dataset | SNLI | 12 |
| Dataset | Dataset | Dataset | Dataset | Kinetics | 10 |
| Dataset | Dataset | Dataset | Dataset | CoLA | 10 |
| Dataset | Dataset | Dataset | Dataset | OpenWebText2 | 10 |
| Dataset | Dataset | Dataset | Dataset | PASCAL VOC | 9 |
| Dataset | Dataset | Dataset | Dataset | Protein | 9 |
| Dataset | Dataset | Dataset | Dataset | PASCAL VOC 2 0 1 2 | 8 |
| Dataset | Dataset | Method | Method | FSS - 1 0 0 0 | 6 |
| Dataset | Dataset | Method | Method | Pile | 6 |
| Dataset | Dataset | Method | Method | fsCOCO | 4 |
| Dataset | DataSource | Method | Method | Common Crawl | 4 |
| Dataset | Dataset | Method | Method | fsPASCAL | 3 |
| Dataset | Dataset | Method | Method | WPA | 3 |
| Dataset | Dataset | Method | Method | Pile - CC | 3 |
| Dataset | Dataset | Method | Method | FlowTrack - 1 5 2 | 2 |
| Dataset | Dataset | Method | Method | Amalgam | 2 |
| Dataset | Dataset | Method | Method | CC-100 | 2 |
| Dataset | Dataset | Method | Method | pycld2 | 2 |
| Dataset | Dataset | Method | Method | Guided Network - 1 shot | 1 |
| Dataset | Dataset | Method | Method | VGG - 1 6 | 1 |
| Dataset | Dataset | Method | Method | Hourglass - 1 0 4 | 1 |
| Dataset | Dataset | Method | Method | PoseTrack | 1 |
| Dataset | DataSource | Task | Task | Common Crawl | 2 |
| Dataset | Dataset | Task | Task | person search | 1 |
| Dataset | DataSource | Task | Task | Center for Digital Philosophy | 1 |
| Dataset | Dataset | Task | Task | Protein | 1 |
| Dataset | Dataset | NIL |  | Amalgam | 3 |
| Dataset | Dataset | NIL |  | penguin | 2 |
| Dataset | Dataset | NIL |  | GLUE | 2 |
| Dataset | DataSource | NIL |  | Twitter | 2 |
| Dataset | Dataset | NIL |  | Pile | 2 |
| Dataset | Dataset | NIL |  | ImageNet/COCO | 1 |
| Dataset | Dataset | NIL |  | wild goose | 1 |
| Dataset | Dataset | NIL |  | minival | 1 |
| Dataset | Dataset | NIL |  | MOTA | 1 |
| Dataset | Dataset | NIL |  | COCO | 1 |
| Dataset | Dataset | NIL |  | OASeg | 1 |
| Dataset | Dataset | NIL |  | VOC | 1 |
| Dataset | Dataset | NIL |  | disamb + | 1 |
| Dataset | Dataset | NIL |  | RK-VFIN | 1 |
| Dataset | Dataset | NIL |  | NEGRA | 1 |
| Method | MLModel, MLModelGeneric, Method | Dataset | Dataset | Pile | 8 |
| Method | Method | Dataset | Dataset | OpenAI API | 3 |
| Method | MLModelGeneric | Dataset | Dataset | NPTs | 3 |
| Method | MLModel, MLModelGeneric | Dataset | Dataset | NPT - Base | 3 |
| Method | MLModelGeneric, Method | Dataset | Dataset | ImageNet | 2 |
| Method | MLModel, ModelArchitecture | Dataset | Dataset | FSS - 1 0 0 0 | 2 |
| Method | MLModel, MLModelGeneric | Dataset | Dataset | PET | 2 |
| Method | Method | Dataset | Dataset | HPSG | 2 |
| Method | Method | Dataset | Dataset | Google Cloud Platform | 2 |
| Method | MLModelGeneric | Dataset | Dataset | Founta et al . ( 2018 ) | 2 |
| Method | Method | Dataset | Dataset | pandoc | 2 |
| Method | Method | Dataset | Dataset | Hacker News | 2 |
| Method | MLModel, Method | Dataset | Dataset | sim2sim | 2 |
| Method | MLModelGeneric, Method | Dataset | Dataset | scikit - learn | 2 |
| Method | MLModelGeneric | Dataset | Dataset | NPT | 2 |
| Method | MLModelGeneric, ModelArchitecture | Method | Method | NPTs | 110 |
| Method | MLModel, MLModelGeneric, Method, ModelArchitecture | Method | Method | NPT | 90 |
| Method | MLModel, MLModelGeneric, ModelArchitecture | Method | Method | BERT | 69 |
| Method | MLModel, Method | Method | Method | TinyBERT | 45 |
| Method | MLModel, MLModelGeneric, ModelArchitecture | Method | Method | GPT-3 | 38 |
| Method | MLModel, MLModelGeneric, Method | Method | Method | GloVe | 37 |
| Method | MLModelGeneric, ModelArchitecture | Method | Method | RCN | 34 |
| Method | MLModel, MLModelGeneric | Method | Method | LayoutXLM | 31 |
| Method | MLModelGeneric, ModelArchitecture | Method | Method | I 3 D | 29 |
| Method | MLModelGeneric, Method, ModelArchitecture | Method | Method | CNN | 25 |
| Method | MLModel, ModelArchitecture | Method | Method | CornerNet | 25 |
| Method | MLModelGeneric, ModelArchitecture | Method | Method | GCN | 24 |
| Method | MLModel, Method | Method | Method | CornerNet - Squeeze | 22 |
| Method | MLModel, MLModelGeneric, Method | Method | Method | ViCo | 21 |
| Method | MLModelGeneric, ModelArchitecture | Method | Method | MTN | 20 |
| Method | MLModelGeneric, Method | Task | Task | ML | 10 |
| Method | MLModelGeneric, Method | Task | Task | pose tracking | 6 |
| Method | Method | Task | Task | language modeling | 6 |
| Method | MLModelGeneric, Method | Task | Task | segmentation | 5 |
| Method | MLModelGeneric, Method | Task | Task | natural language processing | 5 |
| Method | Method | Task | Task | word embeddings | 5 |
| Method | MLModelGeneric, Method | Task | Task | few-shot learning | 5 |
| Method | Method | Task | Task | human | 5 |
| Method | Method | Task | Task | filtering | 5 |
| Method | Method | Task | Task | target masking | 5 |
| Method | MLModelGeneric, Method | Task | Task | NLP | 4 |
| Method | MLModelGeneric, Method, ModelArchitecture | Task | Task | NPT | 4 |
| Method | Method | Task | Task | Few - Shot Learning | 3 |
| Method | MLModelGeneric | Task | Task | language models | 3 |
| Method | Method | Task | Task | MLM | 3 |
| Method | MLModelGeneric | NIL |  | the model | 97 |
| Method | MLModelGeneric | NIL |  | models | 30 |
| Method | MLModelGeneric | NIL |  | our model | 22 |
| Method | MLModelGeneric | NIL |  | a model | 17 |
| Method | ModelArchitecture | NIL |  | attention | 13 |
| Method | Method | NIL |  | the flow | 13 |
| Method | MLModelGeneric | NIL |  | the models | 11 |
| Method | MLModelGeneric | NIL |  | these models | 11 |
| Method | Method | NIL |  | fine - tuning | 10 |
| Method | MLModelGeneric | NIL |  | classifiers | 10 |
| Method | MLModelGeneric | NIL |  | the baselines | 10 |
| Method | MLModelGeneric | NIL |  | the network | 9 |
| Method | Method | NIL |  | fine-tuning | 9 |
| Method | MLModelGeneric | NIL |  | The model | 8 |
| Method | MLModelGeneric | NIL |  | our approach | 8 |
| Task | Task | Dataset | Dataset | HPSG | 2 |
| Task | Task | Dataset | Dataset | few - shot segmentation | 1 |
| Task | Task | Dataset | Dataset | FiQA Task 1 sentiment scoring dataset | 1 |
| Task | Task | Dataset | Dataset | FiQA sentiment scoring | 1 |
| Task | Task | Dataset | Dataset | PASCAL VOC 2 0 1 2 segmentation | 1 |
| Task | Task | Dataset | Dataset | English-French | 1 |
| Task | Task | Dataset | Dataset | cloze queries | 1 |
| Task | Task | Dataset | Dataset | DeepMind Mathematics | 1 |
| Task | Task | Method | Method | feature extraction | 2 |
| Task | Task | Method | Method | HPSG parsing | 2 |
| Task | Task | Method | Method | deep syntactic analysis | 2 |
| Task | Task | Method | Method | domain adaptation | 2 |
| Task | Task | Method | Method | OSLSM - 1 shot | 1 |
| Task | Task | Method | Method | few - shot segmentation | 1 |
| Task | Task | Method | Method | object detector | 1 |
| Task | Task | Method | Method | Re - ID head | 1 |
| Task | Task | Method | Method | FastPose | 1 |
| Task | Task | Method | Method | zero - shot - like generalization analysis | 1 |
| Task | Task | Method | Method | Prompt-based prediction | 1 |
| Task | Task | Method | Method | prompt generation | 1 |
| Task | Task | Method | Method | prompt-based zero-shot prediction | 1 |
| Task | Task | Method | Method | zero-shot prediction | 1 |
| Task | Task | Method | Method | DA | 1 |
| Task | Task | Task | Task | classification | 68 |
| Task | Task | Task | Task | localization | 17 |
| Task | Task | Task | Task | semantic segmentation | 15 |
| Task | Task | Task | Task | pose estimation | 13 |
| Task | Task | Task | Task | text classification | 10 |
| Task | Task | Task | Task | segmentation | 9 |
| Task | Task | Task | Task | few - shot segmentation | 9 |
| Task | Task | Task | Task | question answering | 9 |
| Task | Task | Task | Task | regression | 7 |
| Task | Task | Task | Task | activity recognition | 7 |
| Task | Task | Task | Task | image classification | 7 |
| Task | Task | Task | Task | Re - ID | 7 |
| Task | Task | Task | Task | person Re - ID | 7 |
| Task | Task | Task | Task | reasoning | 7 |
| Task | Task | Task | Task | computer vision | 6 |
| Task | Task | NIL |  | temporal reasoning | 3 |
| Task | Task | NIL |  | language modeling | 3 |
| Task | Task | NIL |  | regression | 3 |
| Task | Task | NIL |  | Regression | 2 |
| Task | Task | NIL |  | classify | 2 |
| Task | Task | NIL |  | spatial and temporal reasoning | 1 |
| Task | Task | NIL |  | precipitation forecasting | 1 |
| Task | Task | NIL |  | Video - level action recognition | 1 |
| Task | Task | NIL |  | dense prediction | 1 |
| Task | Task | NIL |  | keypointbased object detection | 1 |
| Task | Task | NIL |  | linguistic generalization | 1 |
| Task | Task | NIL |  | instance identification | 1 |
| Task | Task | NIL |  | multiperson pose tracking | 1 |
| Task | Task | NIL |  | feature extraction | 1 |
| Task | Task | NIL |  | tracking | 1 |
| NIL |  | Dataset | Dataset | Pile | 18 |
| NIL |  | Dataset | Dataset | black - aligned tweets | 15 |
| NIL |  | Dataset | Dataset | datasets | 12 |
| NIL |  | Dataset | Dataset | dataset | 8 |
| NIL |  | Dataset | Dataset | tabular data | 8 |
| NIL |  | Dataset | Dataset | Waseem | 7 |
| NIL |  | Dataset | Dataset | white - aligned tweets | 7 |
| NIL |  | Dataset | Dataset | black - aligned corpus | 7 |
| NIL |  | Dataset | Dataset | German | 5 |
| NIL |  | Dataset | Dataset | English-German | 4 |
| NIL |  | Dataset | Dataset | white - aligned corpus | 4 |
| NIL |  | Dataset | Dataset | training data | 4 |
| NIL |  | Dataset | Dataset | USPTO | 4 |
| NIL |  | Dataset | Dataset | Davidson et al . ( 2017 ) | 3 |
| NIL |  | Dataset | Dataset | CC | 3 |
| NIL |  | Method | Method | generator | 17 |
| NIL |  | Method | Method | Pile | 8 |
| NIL |  | Method | Method | NMT | 7 |
| NIL |  | Method | Method | convolution | 5 |
| NIL |  | Method | Method | I 3 D | 4 |
| NIL |  | Method | Method | R2 | 4 |
| NIL |  | Method | Method | machine learning | 4 |
| NIL |  | Method | Method | white - aligned tweets | 4 |
| NIL |  | Method | Method | ABA | 4 |
| NIL |  | Method | Method | DG | 3 |
| NIL |  | Method | Method | SS2 | 3 |
| NIL |  | Method | Method | WPA | 3 |
| NIL |  | Method | Method | feature extraction | 3 |
| NIL |  | Method | Method | confidence measures | 3 |
| NIL |  | Method | Method | HPSG | 3 |
| NIL |  | Task | Task | tweets | 27 |
| NIL |  | Task | Task | natural language processing | 10 |
| NIL |  | Task | Task | ML | 10 |
| NIL |  | Task | Task | NLP | 9 |
| NIL |  | Task | Task | segmentation | 6 |
| NIL |  | Task | Task | recall | 5 |
| NIL |  | Task | Task | precision | 5 |
| NIL |  | Task | Task | answer types | 5 |
| NIL |  | Task | Task | classification | 4 |
| NIL |  | Task | Task | reading comprehension | 4 |
| NIL |  | Task | Task | wrongly labeled samples | 4 |
| NIL |  | Task | Task | datapoints | 4 |
| NIL |  | Task | Task | OOD | 3 |
| NIL |  | Task | Task | translation | 3 |
| NIL |  | Task | Task | sentence realization | 3 |

## Notes

- **Unified Labels**: All predictions mapped to unified schema (Dataset, Method, Task)
- **Partial Matching**: Uses gsaphub's partial span matching to align entities
- **NIL Class**: Represents entities annotated by one model but not the other
- **Pipeline Applied**: Merge → Drop → Map for both models before comparison

---
*Generated by UnifiedSciERE Unified Confusion Analysis*
