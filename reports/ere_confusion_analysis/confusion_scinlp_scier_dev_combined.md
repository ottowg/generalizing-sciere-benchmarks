# Entity Label Confusion Analysis

**Generated:** 2026-04-09 14:33:58

**Split:** dev

**Model 1:** SCINLP

**Model 2:** SCIER

**Datasets Combined:** SCIER, SCINLP, GSAP-ERE

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.


## Combined Datasets

### Confusion Matrix

Rows: SCINLP labels | Columns: SCIER labels

|         |   dataset |   method |   metric |   task |   NIL |
|:--------|----------:|---------:|---------:|-------:|------:|
| Dataset |       623 |      240 |        5 |     58 |   335 |
| Method  |        48 |     2962 |      101 |    183 |  1009 |
| Task    |        32 |      205 |       23 |    745 |   291 |
| NIL     |        31 |      159 |      167 |     15 |     0 |

### Statistics

**SCINLP Total Entities per Label:**

- Dataset: 1261
- Method: 4303
- Task: 1296
- NIL: 372

**SCIER Total Entities per Label:**

- dataset: 734
- method: 3566
- metric: 296
- task: 1001
- NIL: 1635

### Label Mappings (Top 15 per Label Pair)

| SCINLP Label | SCIER Label | Mention Text | Count |
|----------|----------|--------------|-------|
| dataset | Dataset | CIFAR-10 | 32 |
| dataset | Dataset | ImageNet | 22 |
| dataset | Dataset | COCO | 16 |
| dataset | Dataset | XFUND | 14 |
| dataset | Dataset | MNIST | 12 |
| dataset | Dataset | Wikipedia | 11 |
| dataset | Dataset | Protein | 11 |
| dataset | Dataset | SQuAD | 9 |
| dataset | Dataset | Pile | 9 |
| dataset | Dataset | BookCorpus | 9 |
| dataset | Dataset | PASCAL VOC | 8 |
| dataset | Dataset | SNLI | 8 |
| dataset | Dataset | Boston | 8 |
| dataset | Dataset | Kinetics | 7 |
| dataset | Dataset | WordNet | 7 |
| dataset | Method | CC-100 | 4 |
| dataset | Method | AlexNet | 2 |
| dataset | Method | ResNet 1 5 2 | 2 |
| dataset | Method | Stack Exchange | 2 |
| dataset | Method | PubMed Abstracts | 2 |
| dataset | Method | Resnet101 | 2 |
| dataset | Method | AlexNet classification | 1 |
| dataset | Method | Inception | 1 |
| dataset | Method | Hourglass - 5 4 | 1 |
| dataset | Method | BERTBASE | 1 |
| dataset | Method | WordNet | 1 |
| dataset | Method | GPT series | 1 |
| dataset | Method | HPSG structures | 1 |
| dataset | Method | Google Cloud Platform | 1 |
| dataset | Method | Microsoft Azure | 1 |
| dataset | Task | Hacker News | 2 |
| dataset | Task | datasets for RC | 1 |
| dataset | Task | question answering | 1 |
| dataset | Task | 660 stories | 1 |
| dataset | Task | RC | 1 |
| dataset | Task | predict that tweets | 1 |
| dataset | Task | tweets written | 1 |
| dataset | Task | presence of tweets | 1 |
| dataset | Task | unseen tweets | 1 |
| dataset | Task | geolocated tweets | 1 |
| dataset | Task | analysis to tweets | 1 |
| dataset | Task | classify tweets | 1 |
| dataset | Task | classify black - aligned tweets | 1 |
| dataset | Task | comparing tweets | 1 |
| dataset | Task | large text corpora | 1 |
| dataset | NIL | tweets | 5 |
| dataset | NIL | dataset | 3 |
| dataset | NIL | datasets | 2 |
| dataset | NIL | GitHub | 2 |
| dataset | NIL | MRPC-but | 1 |
| dataset | NIL | Medical Journal | 1 |
| dataset | NIL | stanford - qa.com | 1 |
| dataset | NIL | tweet | 1 |
| dataset | NIL | corpus | 1 |
| dataset | NIL | negative classes | 1 |
| dataset | NIL | an 825 GiB English text corpus | 1 |
| dataset | NIL | Stack Exchange | 1 |
| dataset | NIL | https :/ / www.courtlistener.com / | 1 |
| dataset | NIL | English language dataset | 1 |
| dataset | NIL | international database | 1 |
| method | Dataset | Pile | 13 |
| method | Dataset | ImageNet | 9 |
| method | Dataset | Common Crawl | 8 |
| method | Dataset | fsCOCO | 6 |
| method | Dataset | black - aligned tweets | 6 |
| method | Dataset | Pile - CC | 6 |
| method | Dataset | IMO | 5 |
| method | Dataset | white - aligned tweets | 5 |
| method | Dataset | OpenAI API | 5 |
| method | Dataset | fsPASCAL | 4 |
| method | Dataset | COCO | 4 |
| method | Dataset | sim2sim | 4 |
| method | Dataset | MNIST | 4 |
| method | Dataset | Kinetics | 3 |
| method | Dataset | GLUE | 3 |
| method | Method | NPTs | 89 |
| method | Method | NPT | 77 |
| method | Method | BERT | 68 |
| method | Method | TinyBERT | 42 |
| method | Method | GloVe | 38 |
| method | Method | GPT-3 | 31 |
| method | Method | LayoutXLM | 28 |
| method | Method | RCN | 27 |
| method | Method | CornerNet | 25 |
| method | Method | CNN | 22 |
| method | Method | CornerNet - Squeeze | 22 |
| method | Method | ViCo | 21 |
| method | Method | GCN | 20 |
| method | Method | normalizing flows | 20 |
| method | Method | FinBERT | 18 |
| method | Task | Re - ID | 5 |
| method | Task | MLM | 4 |
| method | Task | pre - training | 4 |
| method | Task | transfer learning | 3 |
| method | Task | classification | 3 |
| method | Task | ML | 3 |
| method | Task | OCR | 3 |
| method | Task | person Re - ID | 2 |
| method | Task | few-shot learning | 2 |
| method | Task | span - based answers | 2 |
| method | Task | black - aligned tweets | 2 |
| method | Task | pre - processing | 2 |
| method | Task | contrastive learning of parallel documents | 2 |
| method | Task | iterative filtering | 2 |
| method | Task | filtering | 2 |
| method | NIL | attention | 14 |
| method | NIL | datapoints | 11 |
| method | NIL | attention between datapoints | 6 |
| method | NIL | Boltzmann | 5 |
| method | NIL | classifier | 4 |
| method | NIL | unsupervised fashion | 4 |
| method | NIL | dataset | 3 |
| method | NIL | datasets | 3 |
| method | NIL | training | 3 |
| method | NIL | baseline | 3 |
| method | NIL | hourglass backbone | 2 |
| method | NIL | ML model | 2 |
| method | NIL | models | 2 |
| method | NIL | isotropic Gaussian | 2 |
| method | NIL | test data | 2 |
| metric | Dataset | MOTA | 1 |
| metric | Dataset | pxBleu | 1 |
| metric | Dataset | average sentiment | 1 |
| metric | Dataset | huge datasets | 1 |
| metric | Dataset | large data | 1 |
| metric | Method | WPA | 10 |
| metric | Method | precision | 7 |
| metric | Method | KSR | 5 |
| metric | Method | tree entropy | 5 |
| metric | Method | R2 | 3 |
| metric | Method | Precision | 3 |
| metric | Method | confidence measures | 3 |
| metric | Method | confidence | 3 |
| metric | Method | entropy | 3 |
| metric | Method | RMSE | 3 |
| metric | Method | macro F1 | 2 |
| metric | Method | F test | 2 |
| metric | Method | pxBleu | 2 |
| metric | Method | pxB | 2 |
| metric | Method | precision / recall numbers | 2 |
| metric | Task | pause duration and frequency | 2 |
| metric | Task | precision | 2 |
| metric | Task | mode coverage | 2 |
| metric | Task | real - time speed | 1 |
| metric | Task | Word Prediction Accuracy | 1 |
| metric | Task | pupil dilation | 1 |
| metric | Task | mouse-action ratio | 1 |
| metric | Task | source difficulty | 1 |
| metric | Task | improve recall | 1 |
| metric | Task | Labelled precision | 1 |
| metric | Task | recall of topological parsing | 1 |
| metric | Task | coverage | 1 |
| metric | Task | recall | 1 |
| metric | Task | quantify the syntactic divergence | 1 |
| metric | Task | cross - domain knowledge | 1 |
| metric | NIL | accuracy | 86 |
| metric | NIL | perplexity | 11 |
| metric | NIL | precision | 9 |
| metric | NIL | AP | 8 |
| metric | NIL | recall | 7 |
| metric | NIL | F1 | 6 |
| metric | NIL | coverage | 5 |
| metric | NIL | mAP | 3 |
| metric | NIL | F-measure | 3 |
| metric | NIL | Coverage | 2 |
| metric | NIL | f-measure | 2 |
| metric | NIL | perplexities | 2 |
| metric | NIL | MSE | 2 |
| metric | NIL | speed | 1 |
| metric | NIL | F 1 - score | 1 |
| task | Dataset | CoLA | 7 |
| task | Dataset | GLUE | 4 |
| task | Dataset | MRPC | 4 |
| task | Dataset | MNLI | 3 |
| task | Dataset | TREC | 3 |
| task | Dataset | SQuAD | 3 |
| task | Dataset | QNLI | 2 |
| task | Dataset | SNLI | 2 |
| task | Dataset | CR | 2 |
| task | Dataset | hate speech and abusive language detection datasets | 2 |
| task | Dataset | FiQA Task 1 sentiment scoring | 1 |
| task | Dataset | SST - 5 | 1 |
| task | Dataset | SST-5 | 1 |
| task | Dataset | MR | 1 |
| task | Dataset | MPQA | 1 |
| task | Method | KD | 8 |
| task | Method | word embeddings | 8 |
| task | Method | deep learning | 7 |
| task | Method | domain adaptation | 7 |
| task | Method | task - specific distillation | 6 |
| task | Method | data augmentation | 5 |
| task | Method | semi - supervised learning | 5 |
| task | Method | hyperparameter optimization | 4 |
| task | Method | Transformer distillation | 3 |
| task | Method | DA | 3 |
| task | Method | machine learning | 3 |
| task | Method | self - supervised learning | 3 |
| task | Method | knowledge distillation | 2 |
| task | Method | general distillation | 2 |
| task | Method | unsupervised clustering | 2 |
| task | Task | classification | 47 |
| task | Task | pose estimation | 17 |
| task | Task | semantic segmentation | 16 |
| task | Task | localization | 15 |
| task | Task | natural language processing | 13 |
| task | Task | segmentation | 11 |
| task | Task | NLP | 11 |
| task | Task | text classification | 11 |
| task | Task | few - shot segmentation | 9 |
| task | Task | sentiment analysis | 9 |
| task | Task | question answering | 9 |
| task | Task | pose tracking | 9 |
| task | Task | language modeling | 9 |
| task | Task | computer vision | 8 |
| task | Task | regression | 7 |
| task | NIL | classification | 1 |
| task | NIL | text simplification | 1 |
| task | NIL | detection | 1 |
| task | NIL | instance identification | 1 |
| task | NIL | multiple documents | 1 |
| task | NIL | Diversity in answers | 1 |
| task | NIL | fanfiction | 1 |
| task | NIL | an extraction benchmark | 1 |
| task | NIL | filtering | 1 |
| task | NIL | traditional network training | 1 |
| task | NIL | sampling and inference | 1 |
| task | NIL | each gradient descent update | 1 |
| task | NIL | datapoints | 1 |
| task | NIL | prompting | 1 |
| task | NIL | input datapoints | 1 |
| NIL | Dataset | FSS - 1 0 0 0 | 31 |
| NIL | Dataset | Pile | 31 |
| NIL | Dataset | PASCAL VOC 2 0 1 2 | 8 |
| NIL | Dataset | training data | 6 |
| NIL | Dataset | a dataset | 4 |
| NIL | Dataset | dataset | 4 |
| NIL | Dataset | ImageNet | 3 |
| NIL | Dataset | UCF 1 0 1 | 3 |
| NIL | Dataset | COCO | 3 |
| NIL | Dataset | IMO | 3 |
| NIL | Dataset | SS1 | 3 |
| NIL | Dataset | tweets | 3 |
| NIL | Dataset | data | 3 |
| NIL | Dataset | datasets | 3 |
| NIL | Dataset | NIH | 3 |
| NIL | Method | I 3 D | 36 |
| NIL | Method | NPTs | 20 |
| NIL | Method | generator | 15 |
| NIL | Method | NPT | 12 |
| NIL | Method | Song and Ermon ( 2019 ) | 10 |
| NIL | Method | SK | 10 |
| NIL | Method | datapoints | 9 |
| NIL | Method | NMT | 7 |
| NIL | Method | a model | 7 |
| NIL | Method | S 3 D | 6 |
| NIL | Method | RCN | 6 |
| NIL | Method | Amalgam | 6 |
| NIL | Method | k - NN | 6 |
| NIL | Method | C 3 D | 5 |
| NIL | Method | FSS - 1 0 0 0 | 5 |
| NIL | Task | classification | 16 |
| NIL | Task | noisy labels | 8 |
| NIL | Task | NLP | 7 |
| NIL | Task | human detection | 6 |
| NIL | Task | segmentation | 5 |
| NIL | Task | multilingual form understanding | 4 |
| NIL | Task | form understanding | 4 |
| NIL | Task | regression | 4 |
| NIL | Task | feature extraction | 3 |
| NIL | Task | localization | 3 |
| NIL | Task | potentially noisy labels | 3 |
| NIL | Task | single - activity recognition | 2 |
| NIL | Task | Re - ID | 2 |
| NIL | Task | vis - w 2 v | 2 |
| NIL | Task | OOD | 2 |

## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
