# Unified Label Confusion Analysis

**Generated:** 2026-02-08 11:29:43

**Split:** dev

**Model 1 (Rows):** GSAP

**Model 2 (Columns):** SCINLP

## Overview

This report shows confusion matrices comparing entity labels between two models
after applying the complete unification pipeline:

1. Merge stacked mentions (prefer larger spans)
2. Drop unmapped labels (null mappings)
3. Map to unified schema (Dataset, Method, Task)

The confusion matrix uses partial span matching to align entities with overlapping spans.


## SCINLP Dataset

### Confusion Matrix

Rows: GSAP labels | Columns: SCINLP labels

|         |   Dataset |   Method |   Task |   NIL |
|:--------|----------:|---------:|-------:|------:|
| Dataset |        47 |        4 |      0 |    15 |
| Method  |        11 |      277 |      7 |     9 |
| Task    |         9 |       34 |     73 |    10 |
| NIL     |        26 |      340 |     37 |     0 |

### Statistics

**GSAP Total Entities per Label:**

- Dataset: 66
- Method: 304
- Task: 126
- NIL: 403

**SCINLP Total Entities per Label:**

- Dataset: 93
- Method: 655
- Task: 117
- NIL: 34

### Label Mappings (Top 15 per Label Pair)

| GSAP Label | GSAP Original | SCINLP Label | SCINLP Original | Mention Text | Count |
|----------|----------|----------|----------|--------------|-------|
| Dataset | Dataset | Dataset | dataset | SST-2 | 6 |
| Dataset | Dataset | Dataset | dataset | TREC | 5 |
| Dataset | Dataset | Dataset | dataset | SNLI | 5 |
| Dataset | Dataset | Dataset | dataset | SST-5 | 3 |
| Dataset | Dataset | Dataset | dataset | CoLA | 2 |
| Dataset | Dataset | Dataset | dataset | SocialDial | 2 |
| Dataset | Dataset | Dataset | dataset | NEGRA treebank | 2 |
| Dataset | Dataset | Dataset | dataset | GLUE benchmark | 1 |
| Dataset | Dataset | Dataset | dataset | MNLI | 1 |
| Dataset | Dataset | Dataset | dataset | RTE | 1 |
| Dataset | Dataset | Dataset | dataset | MR | 1 |
| Dataset | Dataset | Dataset | dataset | CR | 1 |
| Dataset | Dataset | Dataset | dataset | MPQA | 1 |
| Dataset | Dataset | Dataset | dataset | Subj | 1 |
| Dataset | Dataset | Dataset | dataset | Amazon Review Polarity | 1 |
| Dataset | Dataset | Method | method | SNLI | 5 |
| Dataset | Dataset | Method | method | PET | 1 |
| Dataset | Dataset | Method | method | MNLI | 1 |
| Dataset | Dataset | Method | method | QNLI | 1 |
| Dataset | Dataset | Method | method | RTE | 1 |
| Dataset | Dataset | Method | method | MRPC | 1 |
| Dataset | Dataset | Method | method | WPA | 1 |
| Dataset | Dataset | Task | task | SNLI | 2 |
| Dataset | Dataset | Task | task | SST-5 | 1 |
| Dataset | Dataset | Task | task | CR | 1 |
| Dataset | Dataset | Task | task | MPQA | 1 |
| Dataset | Dataset | Task | task | Subj | 1 |
| Dataset | Dataset | Task | task | TREC | 1 |
| Dataset | Dataset | Task | task | QNLI | 1 |
| Dataset | Dataset | Task | task | MRPC | 1 |
| Dataset | Dataset | NIL |  | Amalgam | 6 |
| Dataset | Dataset | NIL |  | MR | 2 |
| Dataset | Dataset | NIL |  | SS1 | 2 |
| Dataset | Dataset | NIL |  | SS2 | 2 |
| Dataset | Dataset | NIL |  | WPA | 2 |
| Dataset | Dataset | NIL |  | TransType2 | 2 |
| Dataset | Dataset | NIL |  | SST | 1 |
| Dataset | Dataset | NIL |  | CR | 1 |
| Dataset | Dataset | NIL |  | MPQA | 1 |
| Dataset | Dataset | NIL |  | LEXSYS | 1 |
| Dataset | Dataset | NIL |  | IMP_VNP | 1 |
| Dataset | Dataset | NIL |  | TransType | 1 |
| Dataset | Dataset | NIL |  | disamb + | 1 |
| Dataset | Dataset | NIL |  | RK-VFIN | 1 |
| Dataset | Dataset | NIL |  | MF | 1 |
| Method | MLModel | Dataset | dataset | RoBERTa-large | 2 |
| Method | MLModel | Dataset | dataset | ALPACA-7B | 1 |
| Method | MLModel | Dataset | dataset | ALPACA-7B-LoRA | 1 |
| Method | MLModel, MLModelGeneric, Method | Method | method | IMO | 15 |
| Method | MLModel | Method | method | BERT | 10 |
| Method | MLModel | Method | method | GPT-3 | 9 |
| Method | MLModel, MLModelGeneric, Method | Method | method | LM-BFF | 7 |
| Method | MLModelGeneric, Method | Method | method | phrase-based system | 7 |
| Method | MLModel | Method | method | RoBERTa | 6 |
| Method | Method | Method | method | standard fine-tuning | 6 |
| Method | MLModel, ModelArchitecture | Method | method | T5 | 5 |
| Method | MLModel, ModelArchitecture | Method | method | BART | 5 |
| Method | MLModelGeneric, Method | Method | method | phrase-based | 5 |
| Method | Method | Method | method | prompt-based fine-tuning | 4 |
| Method | Method | Method | method | beam search | 4 |
| Method | MLModel, Method | Method | method | Auto L | 4 |
| Method | MLModelGeneric, ModelArchitecture | Method | method | LLMs | 4 |
| Method | ModelArchitecture | Method | method | transformer | 4 |
| Method | Method | Task | task | few-shot learning | 2 |
| Method | MLModelGeneric, Method | Task | task | Fine-tuning of language models | 2 |
| Method | MLModelGeneric, Method | Task | task | fine-tuning language models | 2 |
| Method | MLModelGeneric, Method | Task | task | data augmentation | 2 |
| Method | MLModel | Task | task | PET | 1 |
| Method | Method | Task | task | fine-tuning | 1 |
| Method | Method | Task | task | Automatic prompt search | 1 |
| Method | Method | Task | task | prompt-based fine-tuning | 1 |
| Method | Method | Task | task | semi-supervised learning | 1 |
| Method | Method | Task | task | meta-learning | 1 |
| Method | Method | Task | task | intermediate training | 1 |
| Method | Method | Task | task | standard finetuning | 1 |
| Method | Method | Task | task | Automatic Prompt Generation | 1 |
| Method | Method | Task | task | automatic prompt search | 1 |
| Method | Method | Task | task | automatically template generation | 1 |
| Method | MLModelGeneric | NIL |  | the model | 25 |
| Method | MLModelGeneric | NIL |  | the generator | 10 |
| Method | Method | NIL |  | fine-tuning | 7 |
| Method | MLModel, MLModelGeneric, Method | NIL |  | Amalgam | 7 |
| Method | MLModelGeneric | NIL |  | this model | 6 |
| Method | MLModelGeneric, Method | NIL |  | NMT | 6 |
| Method | MLModelGeneric | NIL |  | language models | 5 |
| Method | MLModel, Method | NIL |  | WPA | 5 |
| Method | Method | NIL |  | tree entropy | 5 |
| Method | MLModelGeneric | NIL |  | the language model | 4 |
| Method | MLModelGeneric | NIL |  | our method | 4 |
| Method | MLModelGeneric | NIL |  | the model 's | 3 |
| Method | MLModelGeneric | NIL |  | L | 3 |
| Method | MLModel, Method | NIL |  | Auto T | 3 |
| Method | MLModelGeneric | NIL |  | models | 3 |
| Task | Task | Method | method | HPSG | 3 |
| Task | Task | Method | method | few-shot learning | 1 |
| Task | Task | Method | method | HPSG parsing | 1 |
| Task | Task | Method | method | deep syntactic analysis | 1 |
| Task | Task | Method | method | topological parsing | 1 |
| Task | Task | Task | task | multi-class classification | 6 |
| Task | Task | Task | task | text classification | 5 |
| Task | Task | Task | task | classification | 4 |
| Task | Task | Task | task | binary classification | 4 |
| Task | Task | Task | task | sentiment analysis | 3 |
| Task | Task | Task | task | domain generalization | 2 |
| Task | Task | Task | task | OOD text classification | 2 |
| Task | Task | Task | task | Binary Classification | 2 |
| Task | Task | Task | task | Multi-class Classification | 2 |
| Task | Task | Task | task | sentence realization | 2 |
| Task | Task | Task | task | HPSG parsing | 2 |
| Task | Task | Task | task | topological parsing | 2 |
| Task | Task | Task | task | automating prompt generation | 1 |
| Task | Task | Task | task | language understanding | 1 |
| Task | Task | Task | task | binary sentence classification | 1 |
| Task | Task | NIL |  | classification | 3 |
| Task | Task | NIL |  | regression | 2 |
| Task | Task | NIL |  | Regression | 2 |
| Task | Task | NIL |  | prompt-based zero-shot prediction | 2 |
| Task | Task | NIL |  | suffix prediction | 2 |
| Task | Task | NIL |  | prompt-based prediction | 1 |
| Task | Task | NIL |  | zero-shot prediction | 1 |
| Task | Task | NIL |  | Prompt-based prediction | 1 |
| Task | Task | NIL |  | sentence classification | 1 |
| Task | Task | NIL |  | Classification | 1 |
| Task | Task | NIL |  | Out-of-Distribution Text Classification | 1 |
| Task | Task | NIL |  | OOD generalization | 1 |
| Task | Task | NIL |  | DA | 1 |
| Task | Task | NIL |  | NLG | 1 |
| Task | Task | NIL |  | Prefix-Constrained Machine Translation | 1 |
| NIL |  | Dataset | dataset | PET | 1 |
| NIL |  | Dataset | dataset | MNLI | 1 |
| NIL |  | Dataset | dataset | SNLI | 1 |
| NIL |  | Dataset | dataset | GLUE | 1 |
| NIL |  | Dataset | dataset | QQP 12 | 1 |
| NIL |  | Dataset | dataset | STS-B | 1 |
| NIL |  | Dataset | dataset | SNLI datasets | 1 |
| NIL |  | Dataset | dataset | AG News | 1 |
| NIL |  | Dataset | dataset | Amazon review dataset | 1 |
| NIL |  | Dataset | dataset | SocialDial dataset | 1 |
| NIL |  | Dataset | dataset | Common Crawl | 1 |
| NIL |  | Dataset | dataset | Europarl | 1 |
| NIL |  | Dataset | dataset | Common Crawl corpus | 1 |
| NIL |  | Dataset | dataset | WMT 20165 shared task | 1 |
| NIL |  | Dataset | dataset | newstest2013 data set | 1 |
| NIL |  | Method | method | HPSG | 2 |
| NIL |  | Method | method | MRPC | 1 |
| NIL |  | Method | method | QQP | 1 |
| NIL |  | Method | method | Auto | 1 |
| NIL |  | Method | method | maximum confidence | 1 |
| NIL |  | Method | method | CY | 1 |
| NIL |  | Method | method | topological parse | 1 |
| NIL |  | Method | method | topological parses | 1 |
| NIL |  | Task | task | sentence realization | 2 |
| NIL |  | Task | task | single-sentence | 1 |
| NIL |  | Task | task | domain generalization | 1 |
| NIL |  | Task | task | sentiment analysis | 1 |
| NIL |  | Task | task | multi-class classification | 1 |
| NIL |  | Task | task | natural language generation ( NLG ) | 1 |
| NIL |  | Task | task | for | 1 |
| NIL |  | Task | task | suffix prediction | 1 |
| NIL |  | Task | task | phrasal integration | 1 |

## Notes

- **Unified Labels**: All predictions mapped to unified schema (Dataset, Method, Task)
- **Partial Matching**: Uses gsaphub's partial span matching to align entities
- **NIL Class**: Represents entities annotated by one model but not the other
- **Pipeline Applied**: Merge → Drop → Map for both models before comparison

---
*Generated by UnifiedSciERE Unified Confusion Analysis*
