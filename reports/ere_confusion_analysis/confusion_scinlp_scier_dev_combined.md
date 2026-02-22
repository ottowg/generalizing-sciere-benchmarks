# Entity Label Confusion Analysis

**Generated:** 2026-02-06 16:40:35

**Split:** dev

**Model 1:** SCINLP

**Model 2:** SCIER

**Datasets Combined:** SCIER, SCINLP, GSAP

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.


## Combined Datasets

### Confusion Matrix

Rows: SCINLP labels | Columns: SCIER labels

|         |   dataset |   method |   metric |   task |   NIL |
|:--------|----------:|---------:|---------:|-------:|------:|
| Dataset |       574 |      113 |        7 |     30 |   269 |
| Method  |        26 |     1758 |       72 |    123 |   634 |
| Task    |        39 |      142 |       36 |    413 |   307 |
| NIL     |       134 |      390 |      123 |     61 |     0 |

### Statistics

**SCINLP Total Entities per Label:**

- Dataset: 993
- Method: 2613
- Task: 937
- NIL: 708

**SCIER Total Entities per Label:**

- dataset: 773
- method: 2403
- metric: 238
- task: 627
- NIL: 1210

### Label Mappings (Top 15 per Label Pair)

| SCINLP Label | SCIER Label | Mention Text | Count |
|----------|----------|--------------|-------|
| dataset | Dataset | CIFAR-10 | 35 |
| dataset | Dataset | Pile | 29 |
| dataset | Dataset | SQuAD | 16 |
| dataset | Dataset | MNIST | 16 |
| dataset | Dataset | XFUND | 14 |
| dataset | Dataset | black - aligned tweets | 12 |
| dataset | Dataset | OpenWebText2 | 10 |
| dataset | Dataset | Protein | 10 |
| dataset | Dataset | BookCorpus | 9 |
| dataset | Dataset | GitHub | 8 |
| dataset | Dataset | CIFAR-100 | 8 |
| dataset | Dataset | SNLI | 7 |
| dataset | Dataset | Common Crawl | 7 |
| dataset | Dataset | Project Gutenberg | 7 |
| dataset | Dataset | Higgs | 7 |
| dataset | Method | Critch and Krueger , 2020 | 2 |
| dataset | Method | Resnet101 | 2 |
| dataset | Method | RoBERTa-large | 1 |
| dataset | Method | Google Cloud Services | 1 |
| dataset | Method | crowdworkers | 1 |
| dataset | Method | Amazon Mechanical Turk | 1 |
| dataset | Method | AAE | 1 |
| dataset | Method | Rosset | 1 |
| dataset | Method | Reddit submissions | 1 |
| dataset | Method | multilingual data | 1 |
| dataset | Method | Pile | 1 |
| dataset | Method | Raw CC | 1 |
| dataset | Method | Common Crawl | 1 |
| dataset | Method | trafilatura | 1 |
| dataset | Method | jusText | 1 |
| dataset | Task | tweets | 6 |
| dataset | Task | Protein regression | 3 |
| dataset | Task | RC | 2 |
| dataset | Task | stories | 1 |
| dataset | Task | Wikipedia | 1 |
| dataset | Task | naturally occurring data | 1 |
| dataset | Task | Question - answer collection | 1 |
| dataset | Task | person | 1 |
| dataset | Task | all named entities | 1 |
| dataset | Task | demographic information | 1 |
| dataset | Task | tweets written | 1 |
| dataset | Task | classify tweets | 1 |
| dataset | Task | hate speech | 1 |
| dataset | Task | natural language processing | 1 |
| dataset | Task | traditional language modeling benchmarks | 1 |
| dataset | NIL | this dataset | 7 |
| dataset | NIL | the dataset | 6 |
| dataset | NIL | datapoints | 5 |
| dataset | NIL | constituent datasets | 4 |
| dataset | NIL | The dataset | 3 |
| dataset | NIL | Waseem | 3 |
| dataset | NIL | tweets | 3 |
| dataset | NIL | each dataset | 3 |
| dataset | NIL | 2020 | 3 |
| dataset | NIL | data | 2 |
| dataset | NIL | these datasets | 2 |
| dataset | NIL | Blodgett et al . ( 2016 ) | 2 |
| dataset | NIL | datasets | 2 |
| dataset | NIL | 2019 | 2 |
| dataset | NIL | benchmarks | 2 |
| method | Dataset | Pile | 16 |
| method | Dataset | SNLI | 5 |
| method | Dataset | HPSG | 4 |
| method | Dataset | MNIST | 3 |
| method | Dataset | NPTs | 3 |
| method | Dataset | NPT - Base | 3 |
| method | Dataset | Common Crawl | 2 |
| method | Dataset | PMC | 2 |
| method | Dataset | OpenAI API | 2 |
| method | Dataset | C4 | 2 |
| method | Dataset | mC4 | 2 |
| method | Dataset | Background sections | 2 |
| method | Dataset | XFUND | 2 |
| method | Dataset | unsupervised samples | 2 |
| method | Dataset | Song and Ermon ( 2019 ) | 2 |
| method | Method | NPTs | 106 |
| method | Method | NPT | 87 |
| method | Method | GPT-3 | 43 |
| method | Method | LayoutXLM | 31 |
| method | Method | normalizing flows | 20 |
| method | Method | IMO | 15 |
| method | Method | logistic regression | 15 |
| method | Method | Pile | 15 |
| method | Method | SK | 14 |
| method | Method | ABA | 14 |
| method | Method | BERT | 13 |
| method | Method | DACNN | 13 |
| method | Method | language models | 12 |
| method | Method | attention model | 12 |
| method | Method | attention | 11 |
| method | Task | ML | 8 |
| method | Task | few-shot learning | 4 |
| method | Task | NPT | 4 |
| method | Task | target masking | 4 |
| method | Task | language models | 3 |
| method | Task | MLM | 3 |
| method | Task | samples | 3 |
| method | Task | zero - shot reinforcement learning | 3 |
| method | Task | datapoints | 3 |
| method | Task | masked language modeling | 2 |
| method | Task | in-context learning | 2 |
| method | Task | topological parse | 2 |
| method | Task | train , validation , and testing splits | 2 |
| method | Task | iterative filtering | 2 |
| method | Task | wrongly labeled samples | 2 |
| method | NIL | datapoints | 19 |
| method | NIL | the model | 15 |
| method | NIL | baselines | 11 |
| method | NIL | our model | 10 |
| method | NIL | models | 8 |
| method | NIL | these models | 7 |
| method | NIL | a model | 6 |
| method | NIL | model | 6 |
| method | NIL | attention between datapoints | 6 |
| method | NIL | flow | 5 |
| method | NIL | Pile | 4 |
| method | NIL | phrase-based | 3 |
| method | NIL | The model | 3 |
| method | NIL | the classifiers | 3 |
| method | NIL | attention | 3 |
| metric | Dataset | v1.0 | 2 |
| metric | Dataset | MR | 1 |
| metric | Dataset | CR | 1 |
| metric | Dataset | MPQA | 1 |
| metric | Dataset | SS2 | 1 |
| metric | Dataset | Chi et al . , 2020 | 1 |
| metric | Method | WPA | 7 |
| metric | Method | tree entropy | 6 |
| metric | Method | R2 | 4 |
| metric | Method | pxBleu | 3 |
| metric | Method | KSR | 3 |
| metric | Method | confidence measures | 3 |
| metric | Method | entropy | 3 |
| metric | Method | macro F1 | 2 |
| metric | Method | thresholded precision | 2 |
| metric | Method | mean - squared - error | 2 |
| metric | Method | KL divergence | 2 |
| metric | Method | RMSE | 2 |
| metric | Method | training or validation log loss | 2 |
| metric | Method | cosine similarities | 1 |
| metric | Method | macro-F1 | 1 |
| metric | Task | recall | 7 |
| metric | Task | precision | 5 |
| metric | Task | coverage | 3 |
| metric | Task | human | 3 |
| metric | Task | accuracy | 2 |
| metric | Task | Precision | 2 |
| metric | Task | F1 | 1 |
| metric | Task | precision calculations | 1 |
| metric | Task | pause duration | 1 |
| metric | Task | mouse-action ratio | 1 |
| metric | Task | Coverage | 1 |
| metric | Task | humans | 1 |
| metric | Task | perplexity evaluation | 1 |
| metric | Task | GPT-2 / 3 perplexity analysis | 1 |
| metric | Task | label noise | 1 |
| metric | NIL | accuracy | 33 |
| metric | NIL | precision | 14 |
| metric | NIL | perplexity | 10 |
| metric | NIL | recall | 7 |
| metric | NIL | F1 | 5 |
| metric | NIL | Waseem | 4 |
| metric | NIL | coverage | 3 |
| metric | NIL | F-measure | 3 |
| metric | NIL | F1 score | 3 |
| metric | NIL | Coverage | 2 |
| metric | NIL | f-measure | 2 |
| metric | NIL | 80 % | 2 |
| metric | NIL | KL divergence | 2 |
| metric | NIL | KL-divergence | 1 |
| metric | NIL | macro-F1 | 1 |
| task | Dataset | SNLI | 2 |
| task | Dataset | HPSG | 2 |
| task | Dataset | white - aligned tweets | 2 |
| task | Dataset | black - aligned tweets | 2 |
| task | Dataset | tabular data | 2 |
| task | Dataset | SST-5 | 1 |
| task | Dataset | CR | 1 |
| task | Dataset | MPQA | 1 |
| task | Dataset | Subj | 1 |
| task | Dataset | TREC | 1 |
| task | Dataset | QNLI | 1 |
| task | Dataset | MRPC | 1 |
| task | Dataset | cloze - style queries | 1 |
| task | Dataset | hate speech and abusive language detection datasets | 1 |
| task | Dataset | training data | 1 |
| task | Method | denoising score matching | 9 |
| task | Method | domain adaptation | 6 |
| task | Method | semi - supervised learning | 5 |
| task | Method | unsupervised learning | 4 |
| task | Method | data augmentation | 3 |
| task | Method | Semi - supervised learning | 3 |
| task | Method | score matching | 3 |
| task | Method | self - supervised learning | 3 |
| task | Method | Multimodal pre - training | 2 |
| task | Method | pre - processing | 2 |
| task | Method | supervised learning | 2 |
| task | Method | supervised deep learning | 2 |
| task | Method | Fine-tuning of language models | 1 |
| task | Method | fine-tuning language models | 1 |
| task | Method | prompt-based fine-tuning | 1 |
| task | Task | classification | 15 |
| task | Task | language modeling | 9 |
| task | Task | reading comprehension | 8 |
| task | Task | binary classification | 7 |
| task | Task | multi-class classification | 7 |
| task | Task | natural language processing | 7 |
| task | Task | regression | 6 |
| task | Task | sentiment analysis | 6 |
| task | Task | text classification | 6 |
| task | Task | sentence realization | 5 |
| task | Task | image classification | 5 |
| task | Task | human | 4 |
| task | Task | multilingual document understanding | 4 |
| task | Task | form understanding | 4 |
| task | Task | document understanding | 4 |
| task | NIL | development set | 3 |
| task | NIL | noisy labels | 3 |
| task | NIL | datapoints | 3 |
| task | NIL | the dataset | 2 |
| task | NIL | regression | 2 |
| task | NIL | fine-tuning | 1 |
| task | NIL | for | 1 |
| task | NIL | pattern matching baseline | 1 |
| task | NIL | questions | 1 |
| task | NIL | answers | 1 |
| task | NIL | Stratification | 1 |
| task | NIL | constituency parse | 1 |
| task | NIL | named entities | 1 |
| task | NIL | our analysis | 1 |
| task | NIL | analysis | 1 |
| NIL | Dataset | Pile | 17 |
| NIL | Dataset | black - aligned corpus | 7 |
| NIL | Dataset | datasets | 6 |
| NIL | Dataset | dataset | 6 |
| NIL | Dataset | German | 5 |
| NIL | Dataset | SS1 | 4 |
| NIL | Dataset | English-German | 4 |
| NIL | Dataset | Waseem | 4 |
| NIL | Dataset | white - aligned corpus | 4 |
| NIL | Dataset | semi - synthetic | 4 |
| NIL | Dataset | Davidson et al . ( 2017 ) | 3 |
| NIL | Dataset | AAE | 3 |
| NIL | Dataset | PhilPapers | 3 |
| NIL | Dataset | NIH | 3 |
| NIL | Dataset | SS2 | 2 |
| NIL | Method | generator | 25 |
| NIL | Method | NMT | 15 |
| NIL | Method | Amalgam | 9 |
| NIL | Method | Pile | 9 |
| NIL | Method | machine learning | 7 |
| NIL | Method | spin - glass | 6 |
| NIL | Method | SK | 6 |
| NIL | Method | neural network | 5 |
| NIL | Method | AAE | 5 |
| NIL | Method | deep learning | 5 |
| NIL | Method | NPT | 5 |
| NIL | Method | propnets | 4 |
| NIL | Method | WPA | 4 |
| NIL | Method | HPSG | 4 |
| NIL | Method | PT | 4 |
| NIL | Task | tweets | 24 |
| NIL | Task | ML | 12 |
| NIL | Task | classification | 6 |
| NIL | Task | reasoning | 5 |
| NIL | Task | NLP | 4 |
| NIL | Task | natural language processing | 4 |
| NIL | Task | OOD | 3 |
| NIL | Task | translation | 3 |
| NIL | Task | case assignment | 3 |
| NIL | Task | questions | 3 |
| NIL | Task | language modeling | 3 |
| NIL | Task | EMT | 3 |
| NIL | Task | the spin - glass phase | 3 |
| NIL | Task | datapoints | 3 |
| NIL | Task | targets | 3 |

## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
