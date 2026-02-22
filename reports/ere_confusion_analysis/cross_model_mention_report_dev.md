# Cross-Model Mention Detection Report

**Generated:** 2026-02-09 16:49:58
**Split:** dev (all three datasets combined: GSAP, SciER, SciNLP)
**Matching:** gsaphub partial span matching
**Unification:** apply_unification_pipeline (merge stacked, drop unmapped, map labels, dataset-specific corrections, normalize spans)

## Overview

This report analyzes which mentions are detected by which subset of the three
models (GSAP, SciER, SciNLP). All predictions are unified via the standard
unification pipeline (using each model's label scheme) before comparison.
Mentions are matched across models using partial span overlap within each
dataset's dev set, then combined across all three datasets.

### Mention Counts by Group and Entity Type

| Group | Dataset (total / unique) | Method (total / unique) | Task (total / unique) | Total (total / unique) |
| ----- | ---: | ---: | ---: | ---: |
| GSAP only | 23 / 19 | 790 / 644 | 40 / 33 | 853 / 696 |
| SciER only | 208 / 147 | 328 / 236 | 232 / 160 | 768 / 543 |
| SciNLP only | 133 / 90 | 207 / 113 | 39 / 32 | 379 / 235 |
| GSAP + SciER | 93 / 65 | 604 / 471 | 113 / 86 | 810 / 622 |
| GSAP + SciNLP | 8 / 8 | 197 / 165 | 9 / 9 | 214 / 182 |
| SciER + SciNLP | 199 / 143 | 144 / 109 | 172 / 137 | 515 / 389 |
| All three | 711 / 226 | 3,312 / 1,507 | 530 / 276 | 4,553 / 2,009 |
| **Total** | **1,375 / 592** | **5,582 / 2,844** | **1,135 / 628** | **8,092 / 4,064** |

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

**790** mentions, **644** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | spin - glass phase | 9 |
| 2 | flow | 9 |
| 3 | model | 8 |
| 4 | fine - tuning | 7 |
| 5 | spin - glass | 7 |
| 6 | fine-tuning | 6 |
| 7 | pre - training | 5 |
| 8 | new | 4 |
| 9 | unsupervised fashion | 4 |
| 10 | reverse KL loss | 4 |
| 11 | attention | 4 |
| 12 | Wilcoxon signed - rank test | 4 |
| 13 | base | 4 |
| 14 | pre - trained language | 4 |
| 15 | decision tree | 4 |
| 16 | models | 3 |
| 17 | crowdworkers | 3 |
| 18 | input | 3 |
| 19 | previous | 3 |
| 20 | framework | 3 |
| 21 | baseline | 3 |
| 22 | annotation vectors | 3 |
| 23 | sampling | 3 |
| 24 | Boltzmann distribution | 3 |
| 25 | forward KL divergence | 3 |
| 26 | reverse KL divergence | 3 |
| 27 | random initialisation | 3 |
| 28 | finetuning | 3 |
| 29 | training | 2 |
| 30 | systems | 2 |

*... and 614 more unique mentions.*

### SciER only

**328** mentions, **236** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | generator | 24 |
| 2 | NMT | 7 |
| 3 | Pile | 5 |
| 4 | ( 2 + 1 )D | 5 |
| 5 | models | 4 |
| 6 | machine learning | 4 |
| 7 | convolution | 4 |
| 8 | R2 | 4 |
| 9 | AAE | 3 |
| 10 | n*gga | 3 |
| 11 | b*tch | 3 |
| 12 | the model | 3 |
| 13 | PT | 3 |
| 14 | RMSE | 3 |
| 15 | DG | 3 |
| 16 | SS2 | 3 |
| 17 | WPA | 3 |
| 18 | feature extraction | 3 |
| 19 | confidence measures | 3 |
| 20 | HPSG | 3 |
| 21 | confidence weights | 3 |
| 22 | RECs | 2 |
| 23 | such models | 2 |
| 24 | Stablecoins | 2 |
| 25 | sub | 2 |
| 26 | mean - squared - error | 2 |
| 27 | softmax | 2 |
| 28 | CLS | 2 |
| 29 | MASK | 2 |
| 30 | Auto L T ( x in ) | 2 |

*... and 206 more unique mentions.*

### SciNLP only

**207** mentions, **113** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | model | 21 |
| 2 | datapoints | 19 |
| 3 | our | 12 |
| 4 | baselines | 8 |
| 5 | these | 7 |
| 6 | models | 7 |
| 7 | a | 6 |
| 8 | classifiers | 5 |
| 9 | their | 2 |
| 10 | Efron | 2 |
| 11 | data | 2 |
| 12 | datasets | 2 |
| 13 | Pile | 2 |
| 14 | training set | 2 |
| 15 | all samples | 2 |
| 16 | our approach | 2 |
| 17 | 4 | 2 |
| 18 | our network | 2 |
| 19 | Saremi | 2 |
| 20 | Hinton | 2 |
| 21 | 24 | 2 |
| 22 | test set | 2 |
| 23 | original and duplicate datapoints | 2 |
| 24 | missing values | 2 |
| 25 | GloVe+ViCo(linear, | 2 |
| 26 | 10 % | 1 |
| 27 | all questions | 1 |
| 28 | sets | 1 |
| 29 | building | 1 |
| 30 | no | 1 |

*... and 83 more unique mentions.*

### GSAP + SciER

**604** mentions, **471** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | BERT | 18 |
| 2 | NMT | 7 |
| 3 | Amalgam | 7 |
| 4 | Pile | 6 |
| 5 | Transformer | 6 |
| 6 | neural network | 5 |
| 7 | word | 5 |
| 8 | WPA | 5 |
| 9 | tree entropy | 5 |
| 10 | spin - glass | 4 |
| 11 | SK | 4 |
| 12 | ( 2 + 1 )D | 4 |
| 13 | convolution | 4 |
| 14 | ML | 3 |
| 15 | human performance | 3 |
| 16 | CNN | 3 |
| 17 | spin - glass phase | 3 |
| 18 | KL divergence | 3 |
| 19 | NPT | 3 |
| 20 | RMSE | 3 |
| 21 | 2D CNNs | 3 |
| 22 | Auto T | 3 |
| 23 | factor analysis | 3 |
| 24 | pxBleu | 3 |
| 25 | KSR | 3 |
| 26 | crowdworkers | 2 |
| 27 | machine learning | 2 |
| 28 | AAE | 2 |
| 29 | BPB | 2 |
| 30 | profanity - checker | 2 |

*... and 441 more unique mentions.*

### GSAP + SciNLP

**197** mentions, **165** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | attention | 9 |
| 2 | flow | 7 |
| 3 | fine - tuning | 3 |
| 4 | framework | 3 |
| 5 | annotation vectors | 3 |
| 6 | fine-tuning | 3 |
| 7 | all | 2 |
| 8 | Waseem and Hovy ( 2016 ) | 2 |
| 9 | pre - training | 2 |
| 10 | filtering step | 2 |
| 11 | Mean Teacher | 2 |
| 12 | networks | 2 |
| 13 | proposed approach | 2 |
| 14 | Attention | 2 |
| 15 | baseline | 2 |
| 16 | diffeomorphisms | 2 |
| 17 | new | 1 |
| 18 | training from scratch | 1 |
| 19 | ML emissions calculator | 1 |
| 20 | ML Emissions Calculator | 1 |
| 21 | them | 1 |
| 22 | simple baseline | 1 |
| 23 | best | 1 |
| 24 | sliding window baseline | 1 |
| 25 | Their pattern matching baseline | 1 |
| 26 | Daemo | 1 |
| 27 | Stratification by syntactic divergence | 1 |
| 28 | constituency parse | 1 |
| 29 | Humans | 1 |
| 30 | systems | 1 |

*... and 135 more unique mentions.*

### SciER + SciNLP

**144** mentions, **109** unique

| Rank | Mention Text | Count |
|-----:|:-------------|------:|
| 1 | language models | 9 |
| 2 | classifiers | 5 |
| 3 | ABA | 4 |
| 4 | I 3 D | 4 |
| 5 | white - aligned tweets | 3 |
| 6 | Pile | 3 |
| 7 | GPT-3 | 3 |
| 8 | these models | 2 |
| 9 | such models | 2 |
| 10 | form templates | 2 |
| 11 | our model | 2 |
| 12 | deep learning | 2 |
| 13 | G | 2 |
| 14 | batch size 512 | 2 |
| 15 | 3D convolution | 2 |
| 16 | S 3 D | 2 |
| 17 | 2D features | 2 |
| 18 | GloVe | 2 |
| 19 | data | 1 |
| 20 | span - based answers | 1 |
| 21 | freeform answers | 1 |
| 22 | crowdworkers | 1 |
| 23 | Amazon Mechanical Turk | 1 |
| 24 | Length features | 1 |
| 25 | L 2 regularization | 1 |
| 26 | Tatman | 1 |
| 27 | n random samples | 1 |
| 28 | blackaligned tweets | 1 |
| 29 | black - aligned tweets | 1 |
| 30 | feature sets | 1 |

*... and 79 more unique mentions.*

### All three

**3,312** mentions, **1,507** unique

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
| 28 | Pile | 13 |
| 29 | Transformer | 13 |
| 30 | ResNet | 13 |

*... and 1,477 more unique mentions.*

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
- **Unification pipeline:** Predictions are processed through the full pipeline
  (merge stacked mentions, drop unmapped labels, map to unified schema, dataset-specific
  corrections, normalize spans). Label mapping uses the **model's** label scheme (not the
  dataset's), since predictions carry the vocabulary of the model that produced them.
- **Deduplication:** Each physical mention span is counted once. When multiple models
  detect overlapping spans, the mention is attributed to all detecting models but counted
  only once in the group totals.
- **"Total"** counts mention occurrences; **"Unique"** counts distinct mention texts.

---
*Generated by UnifiedSciERE Cross-Model Mention Report*
