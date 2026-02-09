# Entity Label Confusion Analysis

**Generated:** 2026-02-06 16:40:26

**Split:** dev

**Model 1:** GSAP

**Model 2:** SCINLP

**Datasets Combined:** SCIER, SCINLP, GSAP

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.


## Combined Datasets

### Confusion Matrix

Rows: GSAP labels | Columns: SCINLP labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |   URL |   NIL |
|:--------|-------------:|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|------:|------:|
| dataset |           67 |       385 |              232 |         9 |                5 |       24 |                   3 |              45 |      9 |     3 |    27 |
| method  |           14 |        53 |              172 |       204 |              708 |      865 |                 381 |              40 |     16 |     5 |    65 |
| metric  |            0 |         8 |                8 |         6 |                1 |       67 |                   0 |              15 |      2 |     0 |   122 |
| task    |            2 |         9 |               93 |         1 |               24 |      222 |                   1 |               2 |    250 |     0 |    35 |
| NIL     |           30 |        53 |             1215 |        33 |              565 |      717 |                  50 |             864 |     86 |    27 |     0 |

### Statistics

**GSAP Total Entities per Label:**

- dataset: 809
- method: 2523
- metric: 229
- task: 639
- NIL: 3640

**SCINLP Total Entities per Label:**

- DataSource: 113
- Dataset: 508
- DatasetGeneric: 1720
- MLModel: 253
- MLModelGeneric: 1303
- Method: 1895
- ModelArchitecture: 435
- ReferenceLink: 966
- Task: 363
- URL: 35
- NIL: 249

### Label Mappings (Top 15 per Label Pair)

| GSAP Label | SCINLP Label | Mention Text | Count |
|----------|----------|--------------|-------|
| DataSource | dataset | Common Crawl | 7 |
| DataSource | dataset | Wikipedia | 6 |
| DataSource | dataset | ArXiv | 4 |
| DataSource | dataset | YouTube | 3 |
| DataSource | dataset | GitHub | 3 |
| DataSource | dataset | Reddit | 3 |
| DataSource | dataset | arXiv | 3 |
| DataSource | dataset | English Wikipedia | 2 |
| DataSource | dataset | Twitter | 2 |
| DataSource | dataset | Hatebase | 2 |
| DataSource | dataset | PubMed Central | 2 |
| DataSource | dataset | Stack Exchange | 2 |
| DataSource | dataset | Ubuntu IRC | 2 |
| DataSource | dataset | PubMed | 2 |
| DataSource | dataset | YouTube Subtitles | 2 |
| DataSource | method | Common Crawl | 5 |
| DataSource | method | Google Perspective API | 1 |
| DataSource | method | SAE | 1 |
| DataSource | method | Crawl | 1 |
| DataSource | method | PMC | 1 |
| DataSource | method | Stack Exchange | 1 |
| DataSource | method | Freenode IRC chat server | 1 |
| DataSource | method | repository | 1 |
| DataSource | method | StackOverflow | 1 |
| DataSource | method | OAI - MPH | 1 |
| DataSource | task | Fanfiction | 1 |
| DataSource | task | Common Crawl | 1 |
| DataSource | NIL | Wikipedia | 3 |
| DataSource | NIL | PubMed | 3 |
| DataSource | NIL | Twitter | 2 |
| DataSource | NIL | Common Crawl | 2 |
| DataSource | NIL | NIH | 2 |
| DataSource | NIL | Facebook | 2 |
| DataSource | NIL | Wikipedia 's | 1 |
| DataSource | NIL | the FreeLaw Project | 1 |
| DataSource | NIL | the US Patent and Trademark Office | 1 |
| DataSource | NIL | NCBI | 1 |
| DataSource | NIL | Bibliotik | 1 |
| DataSource | NIL | open - source code repositories | 1 |
| DataSource | NIL | Center for Digital Philosophy | 1 |
| DataSource | NIL | Common Crawl - derived | 1 |
| DataSource | NIL | PMC | 1 |
| Dataset | dataset | CIFAR-10 | 35 |
| Dataset | dataset | MNIST | 16 |
| Dataset | dataset | SQuAD | 13 |
| Dataset | dataset | Pile | 11 |
| Dataset | dataset | the Pile | 10 |
| Dataset | dataset | OpenWebText2 | 10 |
| Dataset | dataset | BookCorpus | 9 |
| Dataset | dataset | XFUND | 9 |
| Dataset | dataset | CIFAR-100 | 8 |
| Dataset | dataset | Protein | 8 |
| Dataset | dataset | Higgs | 7 |
| Dataset | dataset | SST-2 | 6 |
| Dataset | dataset | AAE | 6 |
| Dataset | dataset | Boston | 6 |
| Dataset | dataset | TREC | 5 |
| Dataset | method | Pile | 8 |
| Dataset | method | the Pile | 7 |
| Dataset | method | SNLI | 5 |
| Dataset | method | Pile - CC | 4 |
| Dataset | method | C4 | 3 |
| Dataset | method | CC-100 | 2 |
| Dataset | method | pycld2 | 2 |
| Dataset | method | XFUND | 2 |
| Dataset | method | Protein | 2 |
| Dataset | method | PET | 1 |
| Dataset | method | MNLI | 1 |
| Dataset | method | QNLI | 1 |
| Dataset | method | RTE | 1 |
| Dataset | method | MRPC | 1 |
| Dataset | method | WPA | 1 |
| Dataset | metric | WPA | 2 |
| Dataset | metric | v1.0 | 2 |
| Dataset | metric | MR | 1 |
| Dataset | metric | CR | 1 |
| Dataset | metric | MPQA | 1 |
| Dataset | metric | SS2 | 1 |
| Dataset | task | SNLI | 2 |
| Dataset | task | SST-5 | 1 |
| Dataset | task | CR | 1 |
| Dataset | task | MPQA | 1 |
| Dataset | task | Subj | 1 |
| Dataset | task | TREC | 1 |
| Dataset | task | QNLI | 1 |
| Dataset | task | MRPC | 1 |
| Dataset | NIL | Pile | 11 |
| Dataset | NIL | Amalgam | 6 |
| Dataset | NIL | SS1 | 2 |
| Dataset | NIL | TransType2 | 2 |
| Dataset | NIL | AAE | 2 |
| Dataset | NIL | PubMed Central | 2 |
| Dataset | NIL | BigQuery | 2 |
| Dataset | NIL | MR | 1 |
| Dataset | NIL | SST | 1 |
| Dataset | NIL | LEXSYS | 1 |
| Dataset | NIL | IMP_VNP | 1 |
| Dataset | NIL | SS2 | 1 |
| Dataset | NIL | TransType | 1 |
| Dataset | NIL | disamb + | 1 |
| Dataset | NIL | RK-VFIN | 1 |
| DatasetGeneric | dataset | black - aligned tweets | 9 |
| DatasetGeneric | dataset | tweets | 8 |
| DatasetGeneric | dataset | this dataset | 7 |
| DatasetGeneric | dataset | tabular data | 7 |
| DatasetGeneric | dataset | the dataset | 6 |
| DatasetGeneric | dataset | the Pile | 5 |
| DatasetGeneric | dataset | datapoints | 5 |
| DatasetGeneric | dataset | black - aligned | 4 |
| DatasetGeneric | dataset | constituent datasets | 4 |
| DatasetGeneric | dataset | each dataset | 4 |
| DatasetGeneric | dataset | real data | 4 |
| DatasetGeneric | dataset | The dataset | 3 |
| DatasetGeneric | dataset | white - aligned tweets | 3 |
| DatasetGeneric | dataset | USPTO Backgrounds | 3 |
| DatasetGeneric | dataset | datasets | 3 |
| DatasetGeneric | method | datapoints | 19 |
| DatasetGeneric | method | attention between datapoints | 13 |
| DatasetGeneric | method | Pile | 6 |
| DatasetGeneric | method | GPT-3 | 3 |
| DatasetGeneric | method | wrongly labeled samples | 3 |
| DatasetGeneric | method | test set | 3 |
| DatasetGeneric | method | span - based answers | 2 |
| DatasetGeneric | method | white - aligned tweets | 2 |
| DatasetGeneric | method | data | 2 |
| DatasetGeneric | method | datasets | 2 |
| DatasetGeneric | method | overall Pile | 2 |
| DatasetGeneric | method | training set | 2 |
| DatasetGeneric | method | form templates | 2 |
| DatasetGeneric | method | unlabeled samples | 2 |
| DatasetGeneric | method | all samples | 2 |
| DatasetGeneric | metric | pause duration | 1 |
| DatasetGeneric | metric | 80 % | 1 |
| DatasetGeneric | metric | 10 % | 1 |
| DatasetGeneric | metric | v1.0 | 1 |
| DatasetGeneric | metric | Raw CC | 1 |
| DatasetGeneric | metric | data | 1 |
| DatasetGeneric | metric | input - output | 1 |
| DatasetGeneric | metric | missing | 1 |
| DatasetGeneric | task | reading comprehension | 5 |
| DatasetGeneric | task | tabular data | 4 |
| DatasetGeneric | task | development set | 3 |
| DatasetGeneric | task | the dataset | 2 |
| DatasetGeneric | task | cloze style questions | 2 |
| DatasetGeneric | task | other answer types | 2 |
| DatasetGeneric | task | noisy labels | 2 |
| DatasetGeneric | task | datapoints | 2 |
| DatasetGeneric | task | duplication | 2 |
| DatasetGeneric | task | single-sentence | 1 |
| DatasetGeneric | task | sentiment analysis | 1 |
| DatasetGeneric | task | multi-class classification | 1 |
| DatasetGeneric | task | updating data | 1 |
| DatasetGeneric | task | answer questions | 1 |
| DatasetGeneric | task | answer types | 1 |
| DatasetGeneric | NIL | the data | 42 |
| DatasetGeneric | NIL | the dataset | 33 |
| DatasetGeneric | NIL | tweets | 24 |
| DatasetGeneric | NIL | datapoints | 24 |
| DatasetGeneric | NIL | data | 22 |
| DatasetGeneric | NIL | the training set | 19 |
| DatasetGeneric | NIL | datasets | 19 |
| DatasetGeneric | NIL | each dataset | 18 |
| DatasetGeneric | NIL | a dataset | 13 |
| DatasetGeneric | NIL | the training data | 13 |
| DatasetGeneric | NIL | training data | 12 |
| DatasetGeneric | NIL | these datasets | 12 |
| DatasetGeneric | NIL | the entire dataset | 11 |
| DatasetGeneric | NIL | the Pile | 10 |
| DatasetGeneric | NIL | other datapoints | 9 |
| MLModel | dataset | RoBERTa-large | 2 |
| MLModel | dataset | ALPACA-7B | 1 |
| MLModel | dataset | ALPACA-7B-LoRA | 1 |
| MLModel | dataset | OWT2 | 1 |
| MLModel | dataset | Resnet101 | 1 |
| MLModel | dataset | Resnet26 | 1 |
| MLModel | dataset | Resnet18 | 1 |
| MLModel | dataset | sim2sim | 1 |
| MLModel | method | GPT-3 | 24 |
| MLModel | method | LayoutXLM | 24 |
| MLModel | method | BERT | 12 |
| MLModel | method | TabNet | 7 |
| MLModel | method | RoBERTa | 6 |
| MLModel | method | IMO | 5 |
| MLModel | method | GPT-2 | 5 |
| MLModel | method | DARLA | 5 |
| MLModel | method | T5 | 4 |
| MLModel | method | InfoXLM | 4 |
| MLModel | method | LayoutLMv2 | 4 |
| MLModel | method | NPT - Base | 4 |
| MLModel | method | SBERT | 3 |
| MLModel | method | RoBERTa-large | 3 |
| MLModel | method | Auto L | 3 |
| MLModel | metric | pxBleu | 2 |
| MLModel | metric | WPA | 2 |
| MLModel | metric | KSR | 1 |
| MLModel | metric | Inception | 1 |
| MLModel | task | PET | 1 |
| MLModel | NIL | Amalgam | 4 |
| MLModel | NIL | Pile | 3 |
| MLModel | NIL | PAS_VNPP | 2 |
| MLModel | NIL | SPLITNET | 2 |
| MLModel | NIL | robocar | 2 |
| MLModel | NIL | T5 | 1 |
| MLModel | NIL | PET 's | 1 |
| MLModel | NIL | Auto L | 1 |
| MLModel | NIL | Auto T | 1 |
| MLModel | NIL | roberta-large-nli-stsb | 1 |
| MLModel | NIL | IMO | 1 |
| MLModel | NIL | BERT | 1 |
| MLModel | NIL | IMO-BART | 1 |
| MLModel | NIL | Biber | 1 |
| MLModel | NIL | BYPAS_VN | 1 |
| MLModelGeneric | dataset | YouTube | 1 |
| MLModelGeneric | dataset | Waseem | 1 |
| MLModelGeneric | dataset | CC | 1 |
| MLModelGeneric | dataset | CIFAR-10 | 1 |
| MLModelGeneric | dataset | NPTs | 1 |
| MLModelGeneric | method | NPTs | 102 |
| MLModelGeneric | method | NPT | 63 |
| MLModelGeneric | method | the model | 15 |
| MLModelGeneric | method | SK model | 14 |
| MLModelGeneric | method | our model | 12 |
| MLModelGeneric | method | baselines | 9 |
| MLModelGeneric | method | these models | 9 |
| MLModelGeneric | method | models | 9 |
| MLModelGeneric | method | GPT-3 | 9 |
| MLModelGeneric | method | attention model | 9 |
| MLModelGeneric | method | language models | 8 |
| MLModelGeneric | method | logistic regression model | 7 |
| MLModelGeneric | method | LayoutXLM | 7 |
| MLModelGeneric | method | DACNN | 7 |
| MLModelGeneric | method | a model | 6 |
| MLModelGeneric | metric | WPA | 1 |
| MLModelGeneric | task | robotic manipulators | 2 |
| MLModelGeneric | task | Fine-tuning of language models | 1 |
| MLModelGeneric | task | fine-tuning language models | 1 |
| MLModelGeneric | task | data augmentation | 1 |
| MLModelGeneric | task | text classification | 1 |
| MLModelGeneric | task | sentence realization | 1 |
| MLModelGeneric | task | pattern matching baseline | 1 |
| MLModelGeneric | task | Natural language processing | 1 |
| MLModelGeneric | task | sentiment classification | 1 |
| MLModelGeneric | task | co - reference resolution | 1 |
| MLModelGeneric | task | occupational classification | 1 |
| MLModelGeneric | task | within classifier | 1 |
| MLModelGeneric | task | training language models | 1 |
| MLModelGeneric | task | Benchmarking Language Models | 1 |
| MLModelGeneric | task | large - scale language models | 1 |
| MLModelGeneric | NIL | the model | 81 |
| MLModelGeneric | NIL | models | 16 |
| MLModelGeneric | NIL | the generator | 10 |
| MLModelGeneric | NIL | a model | 9 |
| MLModelGeneric | NIL | our model | 9 |
| MLModelGeneric | NIL | the models | 8 |
| MLModelGeneric | NIL | the model 's | 7 |
| MLModelGeneric | NIL | language models | 6 |
| MLModelGeneric | NIL | classifiers | 6 |
| MLModelGeneric | NIL | this model | 6 |
| MLModelGeneric | NIL | our approach | 6 |
| MLModelGeneric | NIL | such models | 5 |
| MLModelGeneric | NIL | the best model | 5 |
| MLModelGeneric | NIL | the language model | 4 |
| MLModelGeneric | NIL | our method | 4 |
| Method | dataset | Google Cloud | 2 |
| Method | dataset | Hatebase | 2 |
| Method | dataset | Hacker News | 2 |
| Method | dataset | Google Cloud Services | 1 |
| Method | dataset | Question - answer collection | 1 |
| Method | dataset | the CodaLab platform | 1 |
| Method | dataset | the Pile | 1 |
| Method | dataset | trafilatura | 1 |
| Method | dataset | Newspaper | 1 |
| Method | dataset | jusText | 1 |
| Method | dataset | Github 's API | 1 |
| Method | dataset | APS | 1 |
| Method | dataset | OAI - MPH XML | 1 |
| Method | dataset | OpenAI | 1 |
| Method | dataset | BlingFire 3 | 1 |
| Method | method | normalizing flows | 21 |
| Method | method | NPT | 15 |
| Method | method | spin - glasses | 11 |
| Method | method | DKL | 11 |
| Method | method | IMO | 9 |
| Method | method | spin - glass | 9 |
| Method | method | normalizing flow | 9 |
| Method | method | iterative filtering | 8 |
| Method | method | IF - SSL | 7 |
| Method | method | denoising score matching | 7 |
| Method | method | flow | 7 |
| Method | method | linear patching | 7 |
| Method | method | k - NN | 7 |
| Method | method | standard fine-tuning | 6 |
| Method | method | OpenAI API | 6 |
| Method | metric | tree entropy | 6 |
| Method | metric | KL divergence | 4 |
| Method | metric | entropy | 3 |
| Method | metric | coverage | 3 |
| Method | metric | human performance | 3 |
| Method | metric | macro F1 | 2 |
| Method | metric | KSR | 2 |
| Method | metric | recall | 2 |
| Method | metric | F-measure | 2 |
| Method | metric | precision | 2 |
| Method | metric | perplexity | 2 |
| Method | metric | KL-divergence | 1 |
| Method | metric | macro-F1 | 1 |
| Method | metric | Cosine | 1 |
| Method | metric | F test | 1 |
| Method | task | denoising score matching | 10 |
| Method | task | language modeling | 6 |
| Method | task | unsupervised learning | 5 |
| Method | task | label noise | 5 |
| Method | task | semi - supervised learning | 5 |
| Method | task | domain adaptation | 5 |
| Method | task | human performance | 4 |
| Method | task | score matching | 4 |
| Method | task | natural language processing | 3 |
| Method | task | robust learning | 3 |
| Method | task | Semi - supervised learning | 3 |
| Method | task | machine learning | 3 |
| Method | task | self - supervised learning | 3 |
| Method | task | few-shot learning | 2 |
| Method | task | data augmentation | 2 |
| Method | NIL | spin - glass | 13 |
| Method | NIL | the spin - glass phase | 11 |
| Method | NIL | the flow | 10 |
| Method | NIL | fine-tuning | 7 |
| Method | NIL | NMT | 5 |
| Method | NIL | crowdworkers | 5 |
| Method | NIL | pre - training | 5 |
| Method | NIL | the reverse KL divergence | 5 |
| Method | NIL | an unsupervised fashion | 4 |
| Method | NIL | sampling | 4 |
| Method | NIL | prefix tuning | 3 |
| Method | NIL | deep processing | 3 |
| Method | NIL | filtering | 3 |
| Method | NIL | regularization | 3 |
| Method | NIL | the annotation vectors | 3 |
| ModelArchitecture | dataset | ResNext18 | 1 |
| ModelArchitecture | dataset | Resnext50 | 1 |
| ModelArchitecture | dataset | Resnet101 | 1 |
| ModelArchitecture | method | NPT | 27 |
| ModelArchitecture | method | GPT-3 | 14 |
| ModelArchitecture | method | attention | 13 |
| ModelArchitecture | method | attention between datapoints | 11 |
| ModelArchitecture | method | NPTs | 11 |
| ModelArchitecture | method | attention model | 10 |
| ModelArchitecture | method | self - attention | 10 |
| ModelArchitecture | method | attention network | 8 |
| ModelArchitecture | method | DACNN | 8 |
| ModelArchitecture | method | logistic regression model | 7 |
| ModelArchitecture | method | CNN | 7 |
| ModelArchitecture | method | LayoutXLM | 6 |
| ModelArchitecture | method | XGBoost | 6 |
| ModelArchitecture | method | attention mechanism | 5 |
| ModelArchitecture | method | GPT-2 | 5 |
| ModelArchitecture | task | Forest Cover | 1 |
| ModelArchitecture | NIL | attention | 5 |
| ModelArchitecture | NIL | Transformer | 4 |
| ModelArchitecture | NIL | decision trees | 3 |
| ModelArchitecture | NIL | IBVS | 2 |
| ModelArchitecture | NIL | neural network | 2 |
| ModelArchitecture | NIL | attention mechanisms | 2 |
| ModelArchitecture | NIL | attention weights | 2 |
| ModelArchitecture | NIL | CNN layers | 2 |
| ModelArchitecture | NIL | rFF | 2 |
| ModelArchitecture | NIL | heads | 2 |
| ModelArchitecture | NIL | generator | 1 |
| ModelArchitecture | NIL | propnets | 1 |
| ModelArchitecture | NIL | SPLIT-NET | 1 |
| ModelArchitecture | NIL | decoder | 1 |
| ModelArchitecture | NIL | dependency trees | 1 |
| ReferenceLink | dataset | 2020 | 5 |
| ReferenceLink | dataset | Waseem | 4 |
| ReferenceLink | dataset | Waseem ( 2016 ) | 2 |
| ReferenceLink | dataset | Blodgett et al . ( 2016 ) | 2 |
| ReferenceLink | dataset | Azadi | 2 |
| ReferenceLink | dataset | 28 | 2 |
| ReferenceLink | dataset | 69 | 2 |
| ReferenceLink | dataset | Narasimhan | 1 |
| ReferenceLink | dataset | Weston et al . , 2015 | 1 |
| ReferenceLink | dataset | Waseem et al . , 2018 | 1 |
| ReferenceLink | dataset | Founta et al . ( 2018 ) | 1 |
| ReferenceLink | dataset | Rosset | 1 |
| ReferenceLink | dataset | Gokaslan | 1 |
| ReferenceLink | dataset | Kobayashi , 2018 | 1 |
| ReferenceLink | dataset | Suárez | 1 |
| ReferenceLink | method | Saremi | 3 |
| ReferenceLink | method | Ermon | 3 |
| ReferenceLink | method | Efron | 2 |
| ReferenceLink | method | 4 | 2 |
| ReferenceLink | method | Hinton | 2 |
| ReferenceLink | method | 24 | 2 |
| ReferenceLink | method | Tatman | 1 |
| ReferenceLink | method | ounta | 1 |
| ReferenceLink | method | Waseem | 1 |
| ReferenceLink | method | Golbeck et al . ( 2017 ) | 1 |
| ReferenceLink | method | Founta et al . ( 2018 ) | 1 |
| ReferenceLink | method | Blodgett et al . ( 2016 ) | 1 |
| ReferenceLink | method | Shoeybi | 1 |
| ReferenceLink | method | Seck et al . , 2018 | 1 |
| ReferenceLink | method | Biderman | 1 |
| ReferenceLink | metric | Waseem | 4 |
| ReferenceLink | metric | Athey | 1 |
| ReferenceLink | metric | Gonen | 1 |
| ReferenceLink | metric | Devlin | 1 |
| ReferenceLink | metric | Blei | 1 |
| ReferenceLink | metric | Rae | 1 |
| ReferenceLink | metric | Yudkowsky | 1 |
| ReferenceLink | metric | Bostrom | 1 |
| ReferenceLink | metric | Springenberg | 1 |
| ReferenceLink | metric | Lawrence | 1 |
| ReferenceLink | metric | 46 | 1 |
| ReferenceLink | metric | 90 | 1 |
| ReferenceLink | task | 59 | 1 |
| ReferenceLink | task | 35 | 1 |
| ReferenceLink | NIL | 24 | 15 |
| ReferenceLink | NIL | 2 | 13 |
| ReferenceLink | NIL | 25 | 12 |
| ReferenceLink | NIL | 14 | 11 |
| ReferenceLink | NIL | 15 | 11 |
| ReferenceLink | NIL | Brown et al . , 2020 | 11 |
| ReferenceLink | NIL | 90 | 9 |
| ReferenceLink | NIL | 4 | 8 |
| ReferenceLink | NIL | 5 | 8 |
| ReferenceLink | NIL | 12 | 8 |
| ReferenceLink | NIL | 6 | 7 |
| ReferenceLink | NIL | Davidson et al . ( 2017 ) | 7 |
| ReferenceLink | NIL | Ren et al . , 2018 | 7 |
| ReferenceLink | NIL | Song and Ermon ( 2019 ) | 7 |
| ReferenceLink | NIL | 16 | 6 |
| Task | dataset | Protein regression | 3 |
| Task | dataset | RC | 2 |
| Task | dataset | cloze | 1 |
| Task | dataset | traditional language modeling benchmarks | 1 |
| Task | dataset | OCR | 1 |
| Task | dataset | sim2real transfer | 1 |
| Task | method | HPSG | 3 |
| Task | method | few-shot learning | 1 |
| Task | method | HPSG parsing | 1 |
| Task | method | deep syntactic analysis | 1 |
| Task | method | topological parsing | 1 |
| Task | method | RC | 1 |
| Task | method | reasoning | 1 |
| Task | method | classification models | 1 |
| Task | method | DeepMind Mathematics | 1 |
| Task | method | OCR | 1 |
| Task | method | RL | 1 |
| Task | method | NRI | 1 |
| Task | method | regression | 1 |
| Task | method | Add One | 1 |
| Task | metric | cross - domain generalization | 1 |
| Task | metric | generalization | 1 |
| Task | task | classification | 13 |
| Task | task | reading comprehension | 9 |
| Task | task | binary classification | 7 |
| Task | task | regression | 7 |
| Task | task | multi-class classification | 6 |
| Task | task | text classification | 5 |
| Task | task | image classification | 5 |
| Task | task | multilingual document understanding | 4 |
| Task | task | document understanding | 4 |
| Task | task | sentiment analysis | 3 |
| Task | task | question answering | 3 |
| Task | task | machine translation | 3 |
| Task | task | VrDU | 3 |
| Task | task | form understanding | 3 |
| Task | task | autonomous driving | 3 |
| Task | NIL | classification | 4 |
| Task | NIL | regression | 3 |
| Task | NIL | classify | 3 |
| Task | NIL | Regression | 2 |
| Task | NIL | prompt-based zero-shot prediction | 2 |
| Task | NIL | suffix prediction | 2 |
| Task | NIL | reasoning | 2 |
| Task | NIL | language modeling | 2 |
| Task | NIL | generalization | 2 |
| Task | NIL | prompt-based prediction | 1 |
| Task | NIL | zero-shot prediction | 1 |
| Task | NIL | Prompt-based prediction | 1 |
| Task | NIL | sentence classification | 1 |
| Task | NIL | Classification | 1 |
| Task | NIL | Out-of-Distribution Text Classification | 1 |
| URL | dataset | stanford - qa.com | 1 |
| URL | dataset | wikipedia / 20200301.en | 1 |
| URL | dataset | data.statmt | 1 |
| URL | method | stackexchange | 1 |
| URL | method | PDFextract | 1 |
| URL | method | PyMuPDF | 1 |
| URL | method | BlingFire | 1 |
| URL | method | Parametric - Transformers | 1 |
| URL | NIL | https : // github.com/princeton-nlp/LM-BFF | 1 |
| URL | NIL | https : //github.com/UKPLab/ sentence-transformers | 1 |
| URL | NIL | https :/ / stanford - qa.com | 1 |
| URL | NIL | https :/ / www.perspectiveapi.com | 1 |
| URL | NIL | https :/ / hatebase.org / | 1 |
| URL | NIL | https :/ / www.courtlistener.com / | 1 |
| URL | NIL | www.fanfiction.net | 1 |
| URL | NIL | https | 1 |
| URL | NIL | https :/ / github.com / SpamScope / | 1 |
| URL | NIL | https :/ / github.com / EleutherAI / the - pile | 1 |
| URL | NIL | https :/ / bulkdata.uspto.gov / | 1 |
| URL | NIL | https :/ / irclogs.ubuntu.com / | 1 |
| URL | NIL | https :/ / philpapers.org / | 1 |
| URL | NIL | https :/ / exporter.nih.gov / | 1 |
| URL | NIL | https :/ / news.ycombinator.com | 1 |
| NIL | dataset | Microsoft Azure | 2 |
| NIL | dataset | humans | 2 |
| NIL | dataset | PET | 1 |
| NIL | dataset | SNLI | 1 |
| NIL | dataset | GLUE | 1 |
| NIL | dataset | QQP 12 | 1 |
| NIL | dataset | STS-B | 1 |
| NIL | dataset | Amazon Web Services | 1 |
| NIL | dataset | crowdworkers | 1 |
| NIL | dataset | IBM Watson | 1 |
| NIL | dataset | Amazon Mechanical Turk | 1 |
| NIL | dataset | Turkopticon | 1 |
| NIL | dataset | data | 1 |
| NIL | dataset | the code | 1 |
| NIL | dataset | MED - LINE | 1 |
| NIL | method | ABA | 4 |
| NIL | method | batch | 3 |
| NIL | method | HPSG | 2 |
| NIL | method | attention | 2 |
| NIL | method | G | 2 |
| NIL | method | MRPC | 1 |
| NIL | method | QQP | 1 |
| NIL | method | Auto | 1 |
| NIL | method | maximum confidence | 1 |
| NIL | method | CY | 1 |
| NIL | method | topological parse | 1 |
| NIL | method | topological parses | 1 |
| NIL | method | freeform answers | 1 |
| NIL | method | Length features | 1 |
| NIL | method | L 2 regularization | 1 |
| NIL | metric | accuracy | 35 |
| NIL | metric | precision | 19 |
| NIL | metric | perplexity | 10 |
| NIL | metric | recall | 9 |
| NIL | metric | confidence | 9 |
| NIL | metric | F1 | 6 |
| NIL | metric | R2 | 4 |
| NIL | metric | coverage | 4 |
| NIL | metric | Coverage | 3 |
| NIL | metric | F1 score | 3 |
| NIL | metric | f-measure | 2 |
| NIL | metric | mean - squared - error | 2 |
| NIL | metric | cosine | 1 |
| NIL | metric | macro-F1 | 1 |
| NIL | metric | keystroke ratio ( KSR ) | 1 |
| NIL | task | label noise | 5 |
| NIL | task | sentence realization | 2 |
| NIL | task | natural language processing | 2 |
| NIL | task | domain generalization | 1 |
| NIL | task | natural language generation ( NLG ) | 1 |
| NIL | task | for | 1 |
| NIL | task | suffix prediction | 1 |
| NIL | task | phrasal integration | 1 |
| NIL | task | embedded applications | 1 |
| NIL | task | answer extraction | 1 |
| NIL | task | our analysis | 1 |
| NIL | task | analysis | 1 |
| NIL | task | mathematical problems | 1 |
| NIL | task | fanfiction | 1 |
| NIL | task | key - value extraction | 1 |

## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
