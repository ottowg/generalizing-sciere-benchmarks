# Cross-Model Mention Detection Report

**Generated:** 2026-02-08 21:02:56
**Split:** dev (all three datasets combined: GSAP, SciER, SciNLP)
**Matching:** gsaphub partial span matching
**Unification:** apply_unification_pipeline (merge stacked, drop unmapped, map labels, normalize spans)

## Overview

This report analyzes which mentions are detected by which subset of the three
models (GSAP, SciER, SciNLP). All predictions are unified via the standard
unification pipeline (using each model's label scheme) before comparison.
Mentions are matched across models using partial span overlap within each
dataset's dev set, then combined across all three datasets.

### Mention Counts by Group and Entity Type

| Group | Dataset (total / unique) | Method (total / unique) | Task (total / unique) | Total (total / unique) |
| ----- | ---: | ---: | ---: | ---: |
| GSAP only | 23 / 19 | 1,135 / 678 | 40 / 33 | 1,198 / 730 |
| SciER only | 208 / 147 | 307 / 229 | 232 / 160 | 747 / 536 |
| SciNLP only | 133 / 90 | 154 / 99 | 39 / 32 | 326 / 221 |
| GSAP + SciER | 93 / 65 | 631 / 473 | 113 / 86 | 837 / 624 |
| GSAP + SciNLP | 8 / 8 | 250 / 177 | 9 / 9 | 267 / 194 |
| SciER + SciNLP | 199 / 143 | 118 / 98 | 172 / 137 | 489 / 378 |
| All three | 711 / 226 | 3,336 / 1,514 | 530 / 276 | 4,577 / 2,016 |
| **Total** | **1,375 / 592** | **5,931 / 2,853** | **1,135 / 628** | **8,441 / 4,073** |

---

## Dataset

### GSAP only

**23** mentions, **19** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | Amalgam | 3 |
| 2 | Pile | 2 |
| 3 | penguin | 2 |
| 4 | Twitter | 1 |
| 5 | open - source code repositories | 1 |
| 6 | stories | 1 |
| 7 | Open Archives Initiative | 1 |
| 8 | PubMed | 1 |
| 9 | Q4 | 1 |
| 10 | wild goose | 1 |
| 11 | GLUE | 1 |
| 12 | minival | 1 |
| 13 | MOTA | 1 |
| 14 | COCO | 1 |
| 15 | OASeg | 1 |
| 16 | VOC | 1 |
| 17 | disamb + | 1 |
| 18 | RK-VFIN | 1 |
| 19 | NEGRA | 1 |

### SciER only

**208** mentions, **147** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | datasets | 11 |
| 2 | black - aligned | 8 |
| 3 | Pile | 8 |
| 4 | dataset | 7 |
| 5 | German | 5 |
| 6 | Waseem | 4 |
| 7 | white - aligned | 4 |
| 8 | English-German | 4 |
| 9 | Davidson et al . ( 2017 ) | 3 |
| 10 | Wikipedia articles | 2 |
| 11 | tweets | 2 |
| 12 | blackaligned tweets | 2 |
| 13 | whitealigned tweets | 2 |
| 14 | training data | 2 |
| 15 | LaTeX | 2 |
| 16 | datasheet | 2 |
| 17 | PhilPapers | 2 |
| 18 | fanfiction | 2 |
| 19 | the semi - synthetic dataset | 2 |
| 20 | CLS | 2 |
| 21 | SS1 | 2 |
| 22 | bitext | 2 |
| 23 | English-German newstest2015 | 2 |
| 24 | Minnesota | 2 |
| 25 | DNLP | 2 |
| 26 | curated datasets | 1 |
| 27 | Text REtreival Conference | 1 |
| 28 | this dataset | 1 |
| 29 | Richardson et al . , 2013 | 1 |
| 30 | v1.0 | 1 |

*... and 117 more unique mentions.*

### SciNLP only

**133** mentions, **90** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | dataset | 9 |
| 2 | this | 7 |
| 3 | each | 5 |
| 4 | datapoints | 5 |
| 5 | constituent | 4 |
| 6 | data | 3 |
| 7 | tweets | 3 |
| 8 | training | 3 |
| 9 | 2020 | 3 |
| 10 | these | 2 |
| 11 | Waseem | 2 |
| 12 | Blodgett et al . ( 2016 ) | 2 |
| 13 | datasets | 2 |
| 14 | 2019 | 2 |
| 15 | benchmarks | 2 |
| 16 | filtered data | 2 |
| 17 | Azadi | 2 |
| 18 | 28 | 2 |
| 19 | 69 | 2 |
| 20 | stanford - qa.com | 1 |
| 21 | large , realistic | 1 |
| 22 | 536 articles | 1 |
| 23 | prior | 1 |
| 24 | humans | 1 |
| 25 | Narasimhan | 1 |
| 26 | Weston et al . , 2015 | 1 |
| 27 | our | 1 |
| 28 | other numbers | 1 |
| 29 | numbers | 1 |
| 30 | these data | 1 |

*... and 60 more unique mentions.*

### GSAP + SciER

**93** mentions, **65** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | Pile | 7 |
| 2 | GLUE | 4 |
| 3 | Kinetics | 3 |
| 4 | FSS - 1 0 0 0 | 3 |
| 5 | Amalgam | 3 |
| 6 | AAE | 2 |
| 7 | PubMed Central | 2 |
| 8 | Wikipedia | 2 |
| 9 | BigQuery | 2 |
| 10 | NIH | 2 |
| 11 | Facebook | 2 |
| 12 | ILSVRC | 2 |
| 13 | VisualGenome | 2 |
| 14 | MR | 2 |
| 15 | SS1 | 2 |
| 16 | SS2 | 2 |
| 17 | WPA | 2 |
| 18 | TransType2 | 2 |
| 19 | v1.0 | 1 |
| 20 | TREC | 1 |
| 21 | Children 's Book Test | 1 |
| 22 | SAE | 1 |
| 23 | the FreeLaw Project | 1 |
| 24 | the US Patent and Trademark Office | 1 |
| 25 | PubMed | 1 |
| 26 | NCBI | 1 |
| 27 | Bibliotik | 1 |
| 28 | OpenWebTextCorpus | 1 |
| 29 | Center for Digital Philosophy | 1 |
| 30 | ArXiv | 1 |

*... and 35 more unique mentions.*

### GSAP + SciNLP

**8** mentions, **8** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | Twitter | 1 |
| 2 | YouTube | 1 |
| 3 | Reddit | 1 |
| 4 | each repository | 1 |
| 5 | sim2real | 1 |
| 6 | codebase | 1 |
| 7 | ImageNet/COCO | 1 |
| 8 | GLUE | 1 |

### SciER + SciNLP

**199** mentions, **143** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | black - aligned tweets | 14 |
| 2 | Pile | 10 |
| 3 | tabular data | 8 |
| 4 | white - aligned tweets | 6 |
| 5 | Waseem | 3 |
| 6 | USPTO | 3 |
| 7 | CC | 3 |
| 8 | BookCorpus | 3 |
| 9 | Microsoft Azure | 2 |
| 10 | SQuAD | 2 |
| 11 | dates | 2 |
| 12 | SAE | 2 |
| 13 | training data | 2 |
| 14 | Common Crawl | 2 |
| 15 | unsupervised samples | 2 |
| 16 | labeled data | 2 |
| 17 | Protein | 2 |
| 18 | real data | 2 |
| 19 | Higgs Boson | 2 |
| 20 | English Wikipedia | 2 |
| 21 | SNLI | 2 |
| 22 | HPSG | 2 |
| 23 | Amazon Web Services | 1 |
| 24 | IBM Watson | 1 |
| 25 | Wikipedia passages | 1 |
| 26 | Cloze datasets | 1 |
| 27 | cloze datasets | 1 |
| 28 | CNN / Daily News articles | 1 |
| 29 | cloze - style queries | 1 |
| 30 | development set | 1 |

*... and 113 more unique mentions.*

### All three

**711** mentions, **226** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | CIFAR-10 | 34 |
| 2 | Pile | 32 |
| 3 | ImageNet | 32 |
| 4 | FSS - 1 0 0 0 | 30 |
| 5 | COCO | 21 |
| 6 | MNIST | 17 |
| 7 | XFUND | 15 |
| 8 | SQuAD | 13 |
| 9 | Common Crawl | 13 |
| 10 | SNLI | 12 |
| 11 | Protein | 11 |
| 12 | OpenWebText2 | 10 |
| 13 | CoLA | 10 |
| 14 | PASCAL VOC 2 0 1 2 | 9 |
| 15 | GitHub | 8 |
| 16 | CIFAR-100 | 8 |
| 17 | PASCAL VOC | 8 |
| 18 | MNLI | 8 |
| 19 | PoseTrack | 8 |
| 20 | CC-100 | 7 |
| 21 | BookCorpus | 7 |
| 22 | Pile - CC | 7 |
| 23 | Higgs | 7 |
| 24 | Kinetics | 7 |
| 25 | WordNet | 7 |
| 26 | Literotica | 6 |
| 27 | Boston | 6 |
| 28 | fsPASCAL | 6 |
| 29 | Financial PhraseBank | 6 |
| 30 | MRPC | 6 |

*... and 196 more unique mentions.*

---

## Method

### GSAP only

**1,135** mentions, **678** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | model | 147 |
| 2 | models | 56 |
| 3 | language | 14 |
| 4 | network | 13 |
| 5 | classifiers | 11 |
| 6 | approach | 9 |
| 7 | spin - glass phase | 9 |
| 8 | flow | 9 |
| 9 | fine - tuning | 7 |
| 10 | spin - glass | 7 |
| 11 | classifier | 6 |
| 12 | base | 6 |
| 13 | best | 6 |
| 14 | student | 6 |
| 15 | baselines | 6 |
| 16 | method | 6 |
| 17 | fine-tuning | 6 |
| 18 | pre - training | 5 |
| 19 | baseline | 5 |
| 20 | new | 4 |
| 21 | proposed | 4 |
| 22 | unsupervised fashion | 4 |
| 23 | teacher | 4 |
| 24 | other | 4 |
| 25 | reverse KL loss | 4 |
| 26 | attention | 4 |
| 27 | Wilcoxon signed - rank test | 4 |
| 28 | pre - trained language | 4 |
| 29 | generator | 4 |
| 30 | decision tree | 4 |

*... and 648 more unique mentions.*

### SciER only

**307** mentions, **229** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | generator | 17 |
| 2 | NMT | 7 |
| 3 | Pile | 5 |
| 4 | models | 4 |
| 5 | machine learning | 4 |
| 6 | convolution | 4 |
| 7 | R2 | 4 |
| 8 | AAE | 3 |
| 9 | n*gga | 3 |
| 10 | b*tch | 3 |
| 11 | PT | 3 |
| 12 | RMSE | 3 |
| 13 | DG | 3 |
| 14 | SS2 | 3 |
| 15 | WPA | 3 |
| 16 | feature extraction | 3 |
| 17 | confidence measures | 3 |
| 18 | HPSG | 3 |
| 19 | confidence weights | 3 |
| 20 | RECs | 2 |
| 21 | Stablecoins | 2 |
| 22 | sub | 2 |
| 23 | mean - squared - error | 2 |
| 24 | softmax | 2 |
| 25 | CLS | 2 |
| 26 | MASK | 2 |
| 27 | Auto L T ( x in ) | 2 |
| 28 | fully-connected layer | 2 |
| 29 | propnets | 2 |
| 30 | Generator | 2 |

*... and 199 more unique mentions.*

### SciNLP only

**154** mentions, **99** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | datapoints | 19 |
| 2 | our | 12 |
| 3 | these | 7 |
| 4 | a | 6 |
| 5 | their | 2 |
| 6 | Efron | 2 |
| 7 | data | 2 |
| 8 | datasets | 2 |
| 9 | Pile | 2 |
| 10 | training set | 2 |
| 11 | all samples | 2 |
| 12 | 4 | 2 |
| 13 | Saremi | 2 |
| 14 | Hinton | 2 |
| 15 | 24 | 2 |
| 16 | test set | 2 |
| 17 | original and duplicate datapoints | 2 |
| 18 | missing values | 2 |
| 19 | GloVe+ViCo(linear, | 2 |
| 20 | 10 % | 1 |
| 21 | all questions | 1 |
| 22 | sets | 1 |
| 23 | building | 1 |
| 24 | no | 1 |
| 25 | ounta | 1 |
| 26 | train | 1 |
| 27 | This | 1 |
| 28 | bootstrap samples | 1 |
| 29 | tweets | 1 |
| 30 | Golbeck et al . ( 2017 ) | 1 |

*... and 69 more unique mentions.*

### GSAP + SciER

**631** mentions, **473** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | BERT | 18 |
| 2 | ( 2 + 1 )D | 8 |
| 3 | generator | 8 |
| 4 | model | 7 |
| 5 | NMT | 7 |
| 6 | Amalgam | 7 |
| 7 | Pile | 6 |
| 8 | Transformer | 6 |
| 9 | neural network | 5 |
| 10 | word | 5 |
| 11 | WPA | 5 |
| 12 | tree entropy | 5 |
| 13 | models | 4 |
| 14 | spin - glass | 4 |
| 15 | SK | 4 |
| 16 | convolution | 4 |
| 17 | ML | 3 |
| 18 | human performance | 3 |
| 19 | such | 3 |
| 20 | language | 3 |
| 21 | CNN | 3 |
| 22 | spin - glass phase | 3 |
| 23 | KL divergence | 3 |
| 24 | NPT | 3 |
| 25 | RMSE | 3 |
| 26 | 2D CNNs | 3 |
| 27 | Auto T | 3 |
| 28 | factor analysis | 3 |
| 29 | pxBleu | 3 |
| 30 | KSR | 3 |

*... and 443 more unique mentions.*

### GSAP + SciNLP

**250** mentions, **177** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | model | 21 |
| 2 | attention | 9 |
| 3 | baselines | 7 |
| 4 | models | 7 |
| 5 | flow | 7 |
| 6 | classifiers | 5 |
| 7 | network | 4 |
| 8 | fine - tuning | 3 |
| 9 | framework | 3 |
| 10 | annotation vectors | 3 |
| 11 | fine-tuning | 3 |
| 12 | all | 2 |
| 13 | Waseem and Hovy ( 2016 ) | 2 |
| 14 | classifier | 2 |
| 15 | pre - training | 2 |
| 16 | filtering step | 2 |
| 17 | Mean Teacher | 2 |
| 18 | approach | 2 |
| 19 | networks | 2 |
| 20 | proposed approach | 2 |
| 21 | Attention | 2 |
| 22 | baseline | 2 |
| 23 | diffeomorphisms | 2 |
| 24 | new | 1 |
| 25 | training from scratch | 1 |
| 26 | ML emissions calculator | 1 |
| 27 | ML Emissions Calculator | 1 |
| 28 | them | 1 |
| 29 | simple baseline | 1 |
| 30 | best | 1 |

*... and 147 more unique mentions.*

### SciER + SciNLP

**118** mentions, **98** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | ABA | 4 |
| 2 | I 3 D | 4 |
| 3 | white - aligned tweets | 3 |
| 4 | Pile | 3 |
| 5 | GPT-3 | 3 |
| 6 | form templates | 2 |
| 7 | deep learning | 2 |
| 8 | G | 2 |
| 9 | batch size 512 | 2 |
| 10 | 3D convolution | 2 |
| 11 | S 3 D | 2 |
| 12 | 2D features | 2 |
| 13 | GloVe | 2 |
| 14 | data | 1 |
| 15 | span - based answers | 1 |
| 16 | freeform answers | 1 |
| 17 | crowdworkers | 1 |
| 18 | Amazon Mechanical Turk | 1 |
| 19 | Length features | 1 |
| 20 | L 2 regularization | 1 |
| 21 | Tatman | 1 |
| 22 | classifiers | 1 |
| 23 | n random samples | 1 |
| 24 | blackaligned tweets | 1 |
| 25 | black - aligned tweets | 1 |
| 26 | feature sets | 1 |
| 27 | Rosset | 1 |
| 28 | multilingual data | 1 |
| 29 | Terms of Service | 1 |
| 30 | ToS | 1 |

*... and 68 more unique mentions.*

### All three

**3,336** mentions, **1,514** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | NPTs | 112 |
| 2 | NPT | 84 |
| 3 | BERT | 48 |
| 4 | TinyBERT | 44 |
| 5 | GloVe | 35 |
| 6 | GPT-3 | 32 |
| 7 | attention | 30 |
| 8 | RCN | 30 |
| 9 | CornerNet | 25 |
| 10 | GCN | 25 |
| 11 | LayoutXLM | 23 |
| 12 | CNN | 22 |
| 13 | CornerNet - Squeeze | 22 |
| 14 | MTN | 20 |
| 15 | ViCo | 20 |
| 16 | ULMFit | 18 |
| 17 | FinBERT | 17 |
| 18 | normalizing flows | 16 |
| 19 | I 3 D | 16 |
| 20 | denoising score matching | 15 |
| 21 | SK | 15 |
| 22 | IMO | 15 |
| 23 | CNNs | 14 |
| 24 | LSTM | 14 |
| 25 | fully connected | 14 |
| 26 | sparse convolution | 14 |
| 27 | CornerNet - Saccade | 14 |
| 28 | language | 13 |
| 29 | Pile | 13 |
| 30 | Transformer | 13 |

*... and 1,484 more unique mentions.*

---

## Task

### GSAP only

**40** mentions, **33** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | language modeling | 3 |
| 2 | temporal reasoning | 3 |
| 3 | classify | 2 |
| 4 | regression | 2 |
| 5 | Regression | 2 |
| 6 | predict the class membership | 1 |
| 7 | classifying | 1 |
| 8 | predict | 1 |
| 9 | interactive storytelling | 1 |
| 10 | generalize | 1 |
| 11 | image inpainting | 1 |
| 12 | identify phases and phase transitions | 1 |
| 13 | supervised machine learning | 1 |
| 14 | spatial and temporal reasoning | 1 |
| 15 | precipitation forecasting | 1 |
| 16 | dense prediction | 1 |
| 17 | linguistic generalization | 1 |
| 18 | feature extraction | 1 |
| 19 | localization | 1 |
| 20 | -classification | 1 |
| 21 | prompt-based prediction | 1 |
| 22 | zero-shot prediction | 1 |
| 23 | prompt-based zero-shot prediction | 1 |
| 24 | Out-of-Distribution Text Classification | 1 |
| 25 | Prefix-Constrained Machine Translation | 1 |
| 26 | phrase-based translation | 1 |
| 27 | suffix prediction | 1 |
| 28 | Neural machine translation | 1 |
| 29 | English-German | 1 |
| 30 | interactive MT | 1 |

*... and 3 more unique mentions.*

### SciER only

**232** mentions, **160** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | tweets | 22 |
| 2 | ML | 10 |
| 3 | recall | 5 |
| 4 | precision | 5 |
| 5 | natural language processing | 4 |
| 6 | segmentation | 4 |
| 7 | classification | 4 |
| 8 | EMT | 3 |
| 9 | targets | 3 |
| 10 | training datapoints | 3 |
| 11 | OOD | 3 |
| 12 | translation | 3 |
| 13 | case assignment | 3 |
| 14 | questions | 2 |
| 15 | answer types | 2 |
| 16 | paragraphs | 2 |
| 17 | computer science | 2 |
| 18 | NLP | 2 |
| 19 | denoising | 2 |
| 20 | machine learning | 2 |
| 21 | datapoints | 2 |
| 22 | accuracy | 2 |
| 23 | sentence completion | 2 |
| 24 | alignment | 2 |
| 25 | prefix alignment | 2 |
| 26 | coverage | 2 |
| 27 | public data sources | 1 |
| 28 | standardized tests | 1 |
| 29 | solving 4th grade science exams | 1 |
| 30 | Jeopardy ! | 1 |

*... and 130 more unique mentions.*

### SciNLP only

**39** mentions, **32** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | development set | 3 |
| 2 | noisy labels | 3 |
| 3 | datapoints | 3 |
| 4 | the dataset | 2 |
| 5 | questions | 1 |
| 6 | answers | 1 |
| 7 | named entities | 1 |
| 8 | our analysis | 1 |
| 9 | the English sentences | 1 |
| 10 | Splitting datasets | 1 |
| 11 | fanfiction | 1 |
| 12 | classification information | 1 |
| 13 | the data | 1 |
| 14 | curriculum | 1 |
| 15 | comment data | 1 |
| 16 | preparing the | 1 |
| 17 | natural images | 1 |
| 18 | completed forms | 1 |
| 19 | more languages | 1 |
| 20 | parallel documents | 1 |
| 21 | all samples | 1 |
| 22 | data | 1 |
| 23 | test datapoints | 1 |
| 24 | training and test data | 1 |
| 25 | 59 | 1 |
| 26 | tabular data | 1 |
| 27 | 35 | 1 |
| 28 | prompting | 1 |
| 29 | modified tasks | 1 |
| 30 | missing data | 1 |

*... and 2 more unique mentions.*

### GSAP + SciER

**113** mentions, **86** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | classification | 19 |
| 2 | localization | 6 |
| 3 | generalization | 3 |
| 4 | reasoning | 2 |
| 5 | person Re - ID | 2 |
| 6 | understanding of natural language | 1 |
| 7 | reasoning across multiple sentences | 1 |
| 8 | detect hate speech and abusive language | 1 |
| 9 | identify abusive language | 1 |
| 10 | classify | 1 |
| 11 | detecting abusive language | 1 |
| 12 | screenwriting | 1 |
| 13 | speechwriting | 1 |
| 14 | language modeling | 1 |
| 15 | cross - domain generalization | 1 |
| 16 | code generation | 1 |
| 17 | TKA | 1 |
| 18 | cross - lingual natural language understanding | 1 |
| 19 | multilingual VrDU | 1 |
| 20 | OCR | 1 |
| 21 | cross - lingual zero - shot transfer | 1 |
| 22 | document understanding | 1 |
| 23 | n - way - classification | 1 |
| 24 | open - set problems | 1 |
| 25 | joint perception | 1 |
| 26 | autonomous - driving | 1 |
| 27 | visual - servoing | 1 |
| 28 | Bayesian reasoning | 1 |
| 29 | inpainting | 1 |
| 30 | NP - hard combinatorial optimization problems | 1 |

*... and 56 more unique mentions.*

### GSAP + SciNLP

**9** mentions, **9** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | transfer | 1 |
| 2 | Add One | 1 |
| 3 | regression | 1 |
| 4 | Video - level action recognition | 1 |
| 5 | keypointbased object detection | 1 |
| 6 | instance identification | 1 |
| 7 | multiperson pose tracking | 1 |
| 8 | tracking | 1 |
| 9 | clas - sification | 1 |

### SciER + SciNLP

**172** mentions, **137** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | NLP | 7 |
| 2 | natural language processing | 6 |
| 3 | tweets | 5 |
| 4 | reading comprehension | 4 |
| 5 | answer types | 3 |
| 6 | data | 3 |
| 7 | against label noise | 3 |
| 8 | wrongly labeled samples | 3 |
| 9 | RC | 2 |
| 10 | samples | 2 |
| 11 | unlabeled data | 2 |
| 12 | datapoints | 2 |
| 13 | attention between datapoints | 2 |
| 14 | tabular data | 2 |
| 15 | few - shot segmentation | 2 |
| 16 | segmentation | 2 |
| 17 | sentence realization | 2 |
| 18 | datasets | 1 |
| 19 | embedded applications | 1 |
| 20 | answer questions | 1 |
| 21 | explicit reading comprehension questions | 1 |
| 22 | span - based answers | 1 |
| 23 | question answering | 1 |
| 24 | QA | 1 |
| 25 | 600 real 3rd-6th grade reading comprehension questions | 1 |
| 26 | stories | 1 |
| 27 | answer extraction | 1 |
| 28 | naturally occurring data | 1 |
| 29 | cloze style questions | 1 |
| 30 | obtaining additional answers | 1 |

*... and 107 more unique mentions.*

### All three

**530** mentions, **276** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | classification | 49 |
| 2 | semantic segmentation | 14 |
| 3 | pose estimation | 13 |
| 4 | localization | 11 |
| 5 | few - shot segmentation | 10 |
| 6 | text classification | 10 |
| 7 | segmentation | 9 |
| 8 | question answering | 7 |
| 9 | concurrent activity recognition | 7 |
| 10 | Re - ID | 7 |
| 11 | image classification | 6 |
| 12 | binary classification | 6 |
| 13 | regression | 6 |
| 14 | human detection | 6 |
| 15 | image recognition | 5 |
| 16 | computer vision | 5 |
| 17 | sentiment analysis | 5 |
| 18 | pose tracking | 5 |
| 19 | person Re - ID | 5 |
| 20 | multi-class classification | 5 |
| 21 | multilingual document understanding | 4 |
| 22 | document understanding | 4 |
| 23 | autonomous driving | 4 |
| 24 | Protein regression | 4 |
| 25 | action recognition | 4 |
| 26 | activity recognition | 4 |
| 27 | RC | 3 |
| 28 | reading comprehension | 3 |
| 29 | reasoning | 3 |
| 30 | machine translation | 3 |

*... and 246 more unique mentions.*

---

## Notes

- **Matching method:** gsaphub `partial()` span matching — two mentions match if their
  character spans overlap within the same document and sentence.
- **Unification pipeline:** Predictions are processed through the standard pipeline
  (merge stacked mentions, drop unmapped labels, map to unified schema, normalize spans).
  Label mapping uses the **model's** label scheme (not the dataset's), since predictions
  carry the vocabulary of the model that produced them.
- **Deduplication:** Each physical mention span is counted once. When multiple models
  detect overlapping spans, the mention is attributed to all detecting models but counted
  only once in the group totals.
- **"Total"** counts mention occurrences; **"Unique"** counts distinct mention texts.

---
*Generated by UnifiedSciERE Cross-Model Mention Report*
