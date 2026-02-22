# Unified Label Confusion Analysis

**Generated:** 2026-02-08 11:29:32

**Split:** dev

**Model 1 (Rows):** SCINLP

**Model 2 (Columns):** SCIER

## Overview

This report shows confusion matrices comparing entity labels between two models
after applying the complete unification pipeline:

1. Merge stacked mentions (prefer larger spans)
2. Drop unmapped labels (null mappings)
3. Map to unified schema (Dataset, Method, Task)

The confusion matrix uses partial span matching to align entities with overlapping spans.


## SCIER Dataset

### Confusion Matrix

Rows: SCINLP labels | Columns: SCIER labels

|         |   Dataset |   Method |   Task |   NIL |
|:--------|----------:|---------:|-------:|------:|
| Dataset |       202 |       19 |     16 |    32 |
| Method  |        22 |     1282 |     62 |   171 |
| Task    |         3 |       32 |    316 |    85 |
| NIL     |         1 |       11 |     10 |     0 |

### Statistics

**SCINLP Total Entities per Label:**

- Dataset: 269
- Method: 1537
- Task: 436
- NIL: 22

**SCIER Total Entities per Label:**

- Dataset: 228
- Method: 1344
- Task: 404
- NIL: 288

### Label Mappings (Top 15 per Label Pair)

| SCINLP Label | SCINLP Original | SCIER Label | SCIER Original | Mention Text | Count |
|----------|----------|----------|----------|--------------|-------|
| Dataset | dataset | Dataset | Dataset | ImageNet | 26 |
| Dataset | dataset | Dataset | Dataset | FSS - 1 0 0 0 | 24 |
| Dataset | dataset | Dataset | Dataset | COCO | 22 |
| Dataset | dataset | Dataset | Dataset | PASCAL VOC | 9 |
| Dataset | dataset | Dataset | Dataset | Kinetics | 8 |
| Dataset | dataset | Dataset | Dataset | PASCAL VOC 2 0 1 2 | 8 |
| Dataset | dataset | Dataset | Dataset | PoseTrack | 7 |
| Dataset | dataset | Dataset | Dataset | WordNet | 6 |
| Dataset | dataset | Dataset | Dataset | Financial PhraseBank | 6 |
| Dataset | dataset | Dataset | Dataset | charades | 5 |
| Dataset | dataset | Dataset | Dataset | Cityscapes | 5 |
| Dataset | dataset | Dataset | Dataset | VisualGenome | 4 |
| Dataset | dataset | Dataset | Dataset | UCF 1 0 1 | 3 |
| Dataset | dataset | Dataset | Dataset | fsPASCAL | 3 |
| Dataset | dataset | Dataset | Dataset | hockey | 3 |
| Dataset | dataset | Method | Method | fsCOCO | 4 |
| Dataset | dataset | Method | Method | fsPASCAL | 3 |
| Dataset | dataset | Method | Method | Hourglass - 1 0 4 | 3 |
| Dataset | dataset | Method | Method | ResNet - 1 8 | 2 |
| Dataset | dataset | Method | Method | ResNet - 5 0 | 2 |
| Dataset | dataset | Method | Method | AlexNet | 1 |
| Dataset | dataset | Method | Method | FSS - 1 0 0 0 | 1 |
| Dataset | dataset | Method | Method | MobileNet - v 2 | 1 |
| Dataset | dataset | Method | Method | ResNet 1 8 | 1 |
| Dataset | dataset | Method | Method | PoseTrack | 1 |
| Dataset | dataset | Method | Method | ResNet 5 0 | 1 |
| Dataset | dataset | Method | Method | ResNet 5 0 - GCN | 1 |
| Dataset | dataset | Method | Method | WordNet | 1 |
| Dataset | dataset | Task | Task | person search | 1 |
| Dataset | dataset | Task | Task | Re - ID | 1 |
| Dataset | dataset | Task | Task | segmentation | 1 |
| Dataset | dataset | NIL |  | ImageNet/COCO dataset | 1 |
| Method | method | Dataset | Dataset | ImageNet | 4 |
| Method | method | Dataset | Dataset | MNLI | 3 |
| Method | method | Dataset | Dataset | FSS - 1 0 0 0 | 2 |
| Method | method | Dataset | Dataset | autonomous - driving cars | 1 |
| Method | method | Dataset | Dataset | few - shot segmentation | 1 |
| Method | method | Dataset | Dataset | FinBERT | 1 |
| Method | method | Dataset | Dataset | FinBERT - task | 1 |
| Method | method | Dataset | Dataset | FinBERT - domain | 1 |
| Method | method | Dataset | Dataset | MRPC | 1 |
| Method | method | Dataset | Dataset | SSM | 1 |
| Method | method | Dataset | Dataset | ViCo | 1 |
| Method | method | Dataset | Dataset | Vi - sualGenome | 1 |
| Method | method | Dataset | Dataset | coco | 1 |
| Method | method | Method | Method | TinyBERT | 45 |
| Method | method | Method | Method | GloVe | 39 |
| Method | method | Method | Method | I 3 D | 38 |
| Method | method | Method | Method | BERT | 37 |
| Method | method | Method | Method | RCN | 36 |
| Method | method | Method | Method | CornerNet | 25 |
| Method | method | Method | Method | GCN | 24 |
| Method | method | Method | Method | CornerNet - Squeeze | 22 |
| Method | method | Method | Method | ViCo | 22 |
| Method | method | Method | Method | MTN | 19 |
| Method | method | Method | Method | CNN | 18 |
| Method | method | Method | Method | ULMFit | 18 |
| Method | method | Method | Method | sparse convolution | 16 |
| Method | method | Method | Method | FinBERT | 16 |
| Method | method | Method | Method | CNNs | 14 |
| Method | method | Task | Task | few - shot segmentation | 3 |
| Method | method | Task | Task | few - shot learning | 2 |
| Method | method | Task | Task | Re - ID | 2 |
| Method | method | Task | Task | segmentation | 2 |
| Method | method | Task | Task | Causal inference | 1 |
| Method | method | Task | Task | bounding box regression | 1 |
| Method | method | Task | Task | transfer learning | 1 |
| Method | method | Task | Task | Few - Shot Learning | 1 |
| Method | method | Task | Task | binary segmentation | 1 |
| Method | method | Task | Task | per - pixel classification | 1 |
| Method | method | Task | Task | C - way - K - shot segmentation | 1 |
| Method | method | Task | Task | saliency detection | 1 |
| Method | method | Task | Task | Few - shot learning/segmentation | 1 |
| Method | method | Task | Task | NLP transfer learning | 1 |
| Method | method | Task | Task | natural language processing | 1 |
| Method | method | NIL |  | GloVe+ViCo(linear, | 2 |
| Method | method | NIL |  | 3D networks | 1 |
| Method | method | NIL |  | convolution | 1 |
| Method | method | NIL |  | VLAD | 1 |
| Method | method | NIL |  | KD | 1 |
| Method | method | NIL |  | human detector | 1 |
| Method | method | NIL |  | keypoints | 1 |
| Method | method | NIL |  | non - maximum suppression | 1 |
| Method | method | NIL |  | nonlinearities | 1 |
| Method | method | NIL |  | VRF ( C ) | 1 |
| Task | task | Dataset | Dataset | CoLA | 7 |
| Task | task | Dataset | Dataset | MRPC | 3 |
| Task | task | Dataset | Dataset | MNLI | 2 |
| Task | task | Dataset | Dataset | GLUE | 1 |
| Task | task | Dataset | Dataset | QQP | 1 |
| Task | task | Dataset | Dataset | QNLI | 1 |
| Task | task | Dataset | Dataset | ImageNet | 1 |
| Task | task | Method | Method | KD | 9 |
| Task | task | Method | Method | task - specific distillation | 7 |
| Task | task | Method | Method | data augmentation | 5 |
| Task | task | Method | Method | intermediate layer distillation | 4 |
| Task | task | Method | Method | feature extraction | 3 |
| Task | task | Method | Method | Transformer distillation | 2 |
| Task | task | Method | Method | BERT distillation | 2 |
| Task | task | Method | Method | distillation | 2 |
| Task | task | Method | Method | general distillation | 2 |
| Task | task | Method | Method | causality | 1 |
| Task | task | Method | Method | long - term dependencies | 1 |
| Task | task | Method | Method | temporal resolution | 1 |
| Task | task | Method | Method | spatial convolution | 1 |
| Task | task | Method | Method | Pixelwise Segmentation Annotation | 1 |
| Task | task | Method | Method | text simplification | 1 |
| Task | task | Task | Task | classification | 35 |
| Task | task | Task | Task | pose estimation | 16 |
| Task | task | Task | Task | semantic segmentation | 15 |
| Task | task | Task | Task | segmentation | 13 |
| Task | task | Task | Task | localization | 11 |
| Task | task | Task | Task | NLP | 10 |
| Task | task | Task | Task | pose tracking | 10 |
| Task | task | Task | Task | few - shot segmentation | 8 |
| Task | task | Task | Task | activity recognition | 7 |
| Task | task | Task | Task | computer vision | 6 |
| Task | task | Task | Task | question answering | 6 |
| Task | task | Task | Task | human detection | 6 |
| Task | task | Task | Task | person Re - ID | 6 |
| Task | task | Task | Task | image recognition | 5 |
| Task | task | Task | Task | natural language processing | 5 |
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
| NIL |  | Dataset | Dataset | GLUE | 4 |
| NIL |  | Dataset | Dataset | Kinetics | 3 |
| NIL |  | Dataset | Dataset | FSS - 1 0 0 0 | 3 |
| NIL |  | Dataset | Dataset | ILSVRC | 2 |
| NIL |  | Dataset | Dataset | WSI | 2 |
| NIL |  | Dataset | Dataset | VisualGenome | 2 |
| NIL |  | Dataset | Dataset | Open Image dataset | 1 |
| NIL |  | Dataset | Dataset | Photoshop | 1 |
| NIL |  | Dataset | Dataset | MS COCO | 1 |
| NIL |  | Dataset | Dataset | UC Merced Land Use | 1 |
| NIL |  | Dataset | Dataset | sunflower | 1 |
| NIL |  | Dataset | Dataset | CLS | 1 |
| NIL |  | Dataset | Dataset | NIST | 1 |
| NIL |  | Dataset | Dataset | charades | 1 |
| NIL |  | Dataset | Dataset | General Language Understanding Evaluation | 1 |
| NIL |  | Method | Method | BERT | 18 |
| NIL |  | Method | Method | ( 2 + 1 )D | 15 |
| NIL |  | Method | Method | convolution | 6 |
| NIL |  | Method | Method | 2D CNNs | 4 |
| NIL |  | Method | Method | word embeddings | 4 |
| NIL |  | Method | Method | convolution layers | 2 |
| NIL |  | Method | Method | ResNet - 1 0 1 | 2 |
| NIL |  | Method | Method | feature extraction | 2 |
| NIL |  | Method | Method | multi - task network | 2 |
| NIL |  | Method | Method | FastPose - 1 0 1 | 2 |
| NIL |  | Method | Method | boundary refinement block | 2 |
| NIL |  | Method | Method | global pooling layer | 2 |
| NIL |  | Method | Method | temporal convolution kernel | 1 |
| NIL |  | Method | Method | 1D ( temporal ) convolutions | 1 |
| NIL |  | Method | Method | S 3 D | 1 |
| NIL |  | Task | Task | classification | 17 |
| NIL |  | Task | Task | localization | 7 |
| NIL |  | Task | Task | segmentation | 4 |
| NIL |  | Task | Task | unsupervised clustering | 3 |
| NIL |  | Task | Task | action recognition | 2 |
| NIL |  | Task | Task | detection | 2 |
| NIL |  | Task | Task | financial sentiment analysis | 2 |
| NIL |  | Task | Task | tracking | 2 |
| NIL |  | Task | Task | person Re - ID | 2 |
| NIL |  | Task | Task | semantic segmentation | 2 |
| NIL |  | Task | Task | video understanding | 1 |
| NIL |  | Task | Task | temporal action detection | 1 |
| NIL |  | Task | Task | recognition | 1 |
| NIL |  | Task | Task | spatial reasoning | 1 |
| NIL |  | Task | Task | spatial attention | 1 |

## Notes

- **Unified Labels**: All predictions mapped to unified schema (Dataset, Method, Task)
- **Partial Matching**: Uses gsaphub's partial span matching to align entities
- **NIL Class**: Represents entities annotated by one model but not the other
- **Pipeline Applied**: Merge → Drop → Map for both models before comparison

---
*Generated by UnifiedSciERE Unified Confusion Analysis*
