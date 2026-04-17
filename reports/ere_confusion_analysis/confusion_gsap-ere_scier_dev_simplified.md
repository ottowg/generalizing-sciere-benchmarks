# Entity Label Confusion Analysis

**Generated:** 2026-04-08 15:22:54

**Split:** dev

**Model 1:** GSAP-ERE

**Model 2:** SCIER

## Overview

This report shows confusion matrices comparing entity labels between two different
annotation schemes using partial span matching. The "NIL" class represents entities
that were not annotated by the other model.


## GSAP-ERE Dataset

### Confusion Matrix

Rows: GSAP-ERE labels | Columns: SCIER labels

|         |   DataSource |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   ReferenceLink |   Task |   URL |   NIL |
|:--------|-------------:|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|----------------:|-------:|------:|------:|
| Dataset |           79 |       348 |              349 |        12 |                6 |       41 |                   1 |               8 |     16 |     6 |    33 |
| Method  |           13 |        27 |              148 |       144 |              569 |      986 |                 335 |             185 |     22 |    19 |    63 |
| Task    |            5 |         1 |              248 |         0 |               20 |      204 |                   3 |               3 |    236 |     0 |    33 |
| NIL     |           13 |        13 |              875 |         1 |              418 |      504 |                  32 |             558 |     10 |     3 |     0 |

### Statistics

**GSAP-ERE Total Entities per Label:**

- Dataset: 899
- Method: 2511
- Task: 753
- NIL: 2427

**SCIER Total Entities per Label:**

- DataSource: 110
- Dataset: 389
- DatasetGeneric: 1620
- MLModel: 157
- MLModelGeneric: 1013
- Method: 1735
- ModelArchitecture: 371
- ReferenceLink: 754
- Task: 284
- URL: 28
- NIL: 129

### Label Mappings (Top 15 per Label Pair)

| GSAP-ERE Label | SCIER Label | Mention Text | Count |
|----------|----------|--------------|-------|
| DataSource | Dataset | Wikipedia | 7 |
| DataSource | Dataset | Common Crawl | 7 |
| DataSource | Dataset | Twitter | 4 |
| DataSource | Dataset | YouTube | 3 |
| DataSource | Dataset | PubMed Central | 3 |
| DataSource | Dataset | ArXiv | 3 |
| DataSource | Dataset | GitHub | 3 |
| DataSource | Dataset | PubMed | 3 |
| DataSource | Dataset | Reddit | 3 |
| DataSource | Dataset | arXiv | 3 |
| DataSource | Dataset | Amazon Web Services | 2 |
| DataSource | Dataset | Wikipedia articles | 2 |
| DataSource | Dataset | Facebook | 2 |
| DataSource | Dataset | PubMed Abstracts | 2 |
| DataSource | Dataset | PMC | 2 |
| DataSource | Method | Common Crawl | 5 |
| DataSource | Method | PMC | 2 |
| DataSource | Method | raw and filtered Common Crawl models | 1 |
| DataSource | Method | CourtListener | 1 |
| DataSource | Method | Stack Exchange | 1 |
| DataSource | Method | Hacker News | 1 |
| DataSource | Method | PubMed Abstracts | 1 |
| DataSource | Method | davinci | 1 |
| DataSource | Task | Stack Exchange | 1 |
| DataSource | Task | Center for Digital Philosophy | 1 |
| DataSource | Task | git cloning | 1 |
| DataSource | Task | Hacker News | 1 |
| DataSource | Task | internet | 1 |
| DataSource | NIL | internet | 2 |
| DataSource | NIL | Census | 1 |
| DataSource | NIL | FreeLaw Project | 1 |
| DataSource | NIL | Stack Exchange | 1 |
| DataSource | NIL | The Free Law Project | 1 |
| DataSource | NIL | Free Law | 1 |
| DataSource | NIL | Common Crawl | 1 |
| DataSource | NIL | GitHub | 1 |
| DataSource | NIL | TripAdvisor | 1 |
| DataSource | NIL | SimplyHired | 1 |
| DataSource | NIL | Facebook | 1 |
| DataSource | NIL | codebase | 1 |
| Dataset | Dataset | Pile | 34 |
| Dataset | Dataset | CIFAR-10 | 33 |
| Dataset | Dataset | MNIST | 16 |
| Dataset | Dataset | XFUND | 14 |
| Dataset | Dataset | SQuAD | 13 |
| Dataset | Dataset | Protein | 11 |
| Dataset | Dataset | OpenWebText2 | 10 |
| Dataset | Dataset | BookCorpus | 9 |
| Dataset | Dataset | CIFAR-100 | 8 |
| Dataset | Dataset | PhilPapers | 6 |
| Dataset | Dataset | Boston | 6 |
| Dataset | Dataset | Higgs | 6 |
| Dataset | Dataset | Books3 | 5 |
| Dataset | Dataset | Pile - CC | 5 |
| Dataset | Dataset | Literotica | 5 |
| Dataset | Method | Pile | 2 |
| Dataset | Method | OWT2 | 2 |
| Dataset | Method | AAE | 1 |
| Dataset | Method | PMC | 1 |
| Dataset | Method | Hacker News 9 | 1 |
| Dataset | Method | CC | 1 |
| Dataset | Method | Pile - CC | 1 |
| Dataset | Method | C4 | 1 |
| Dataset | Method | mC4 | 1 |
| Dataset | Method | CC-100 | 1 |
| Dataset | Method | Stack Exchange | 1 |
| Dataset | Method | GitHub | 1 |
| Dataset | Method | Fanfiction | 1 |
| Dataset | Method | Goose3 | 1 |
| Dataset | Method | DragNet | 1 |
| Dataset | Task | XFUND | 1 |
| Dataset | NIL | Pile | 7 |
| Dataset | NIL | Founta et al . ( 2018 ) | 1 |
| Dataset | NIL | white - aligned corpus | 1 |
| Dataset | NIL | GitHub | 1 |
| Dataset | NIL | the Pile | 1 |
| Dataset | NIL | CRISP | 1 |
| Dataset | NIL | Protein | 1 |
| DatasetGeneric | Dataset | Pile | 14 |
| DatasetGeneric | Dataset | black - aligned tweets | 12 |
| DatasetGeneric | Dataset | white - aligned tweets | 9 |
| DatasetGeneric | Dataset | tabular data | 9 |
| DatasetGeneric | Dataset | tweets | 5 |
| DatasetGeneric | Dataset | dataset | 5 |
| DatasetGeneric | Dataset | training data | 5 |
| DatasetGeneric | Dataset | datasets | 5 |
| DatasetGeneric | Dataset | a dataset | 4 |
| DatasetGeneric | Dataset | blackaligned tweets | 3 |
| DatasetGeneric | Dataset | USPTO Backgrounds | 3 |
| DatasetGeneric | Dataset | data | 3 |
| DatasetGeneric | Dataset | BookCorpus | 3 |
| DatasetGeneric | Dataset | Wikipedia articles | 2 |
| DatasetGeneric | Dataset | 536 articles | 2 |
| DatasetGeneric | Method | datapoints | 18 |
| DatasetGeneric | Method | Pile | 3 |
| DatasetGeneric | Method | noisy samples | 3 |
| DatasetGeneric | Method | Attention Between Datapoints | 3 |
| DatasetGeneric | Method | training data | 3 |
| DatasetGeneric | Method | SAE | 2 |
| DatasetGeneric | Method | raw web pages , metadata and text extractions | 2 |
| DatasetGeneric | Method | GPT-3 | 2 |
| DatasetGeneric | Method | raw ( pixel ) images | 2 |
| DatasetGeneric | Method | data samples | 2 |
| DatasetGeneric | Method | 100 , 000 samples | 2 |
| DatasetGeneric | Method | tabular data | 2 |
| DatasetGeneric | Method | two datapoints | 2 |
| DatasetGeneric | Method | datapoints on training data | 2 |
| DatasetGeneric | Method | data | 2 |
| DatasetGeneric | Task | noisy labels | 8 |
| DatasetGeneric | Task | missing values | 6 |
| DatasetGeneric | Task | multilingual form understanding | 4 |
| DatasetGeneric | Task | a corpus of cloze style questions | 3 |
| DatasetGeneric | Task | wrongly labeled samples | 3 |
| DatasetGeneric | Task | potentially noisy labels | 3 |
| DatasetGeneric | Task | real data | 3 |
| DatasetGeneric | Task | datapoints | 3 |
| DatasetGeneric | Task | reading comprehension | 2 |
| DatasetGeneric | Task | answer choices | 2 |
| DatasetGeneric | Task | span - based answers | 2 |
| DatasetGeneric | Task | questions and answer types | 2 |
| DatasetGeneric | Task | questions whose answers | 2 |
| DatasetGeneric | Task | proportion of tweets | 2 |
| DatasetGeneric | Task | black - aligned tweets | 2 |
| DatasetGeneric | NIL | the data | 49 |
| DatasetGeneric | NIL | the dataset | 41 |
| DatasetGeneric | NIL | datapoints | 31 |
| DatasetGeneric | NIL | each dataset | 20 |
| DatasetGeneric | NIL | these datasets | 16 |
| DatasetGeneric | NIL | data | 15 |
| DatasetGeneric | NIL | the training set | 15 |
| DatasetGeneric | NIL | the training data | 14 |
| DatasetGeneric | NIL | tweets | 14 |
| DatasetGeneric | NIL | the Pile | 13 |
| DatasetGeneric | NIL | other datapoints | 13 |
| DatasetGeneric | NIL | datasets | 11 |
| DatasetGeneric | NIL | the entire dataset | 10 |
| DatasetGeneric | NIL | this dataset | 9 |
| DatasetGeneric | NIL | all samples | 9 |
| MLModel | Dataset | Pile | 6 |
| MLModel | Dataset | Pile - CC | 3 |
| MLModel | Dataset | robocar | 2 |
| MLModel | Dataset | Pile codebase | 1 |
| MLModel | Method | LayoutXLM | 27 |
| MLModel | Method | GPT-3 | 20 |
| MLModel | Method | TabNet | 7 |
| MLModel | Method | jusText | 6 |
| MLModel | Method | GPT-2 | 5 |
| MLModel | Method | f att | 5 |
| MLModel | Method | NPT - Base | 5 |
| MLModel | Method | CC-100 | 4 |
| MLModel | Method | InfoXLM | 4 |
| MLModel | Method | LayoutLMv2 | 4 |
| MLModel | Method | DARLA | 4 |
| MLModel | Method | Lay - outXLM | 2 |
| MLModel | Method | LayoutXLM LARGE | 2 |
| MLModel | Method | XLM - R | 2 |
| MLModel | Method | Resnet26 | 2 |
| MLModel | NIL | MHSelfAtt | 1 |
| MLModelGeneric | Dataset | NPTs | 2 |
| MLModelGeneric | Dataset | Waseem and Hovy ( 2016 ) | 1 |
| MLModelGeneric | Dataset | Common Crawl - derived | 1 |
| MLModelGeneric | Dataset | Pile - CC | 1 |
| MLModelGeneric | Dataset | CIFAR-10 model | 1 |
| MLModelGeneric | Method | NPTs | 107 |
| MLModelGeneric | Method | NPT | 16 |
| MLModelGeneric | Method | non - parametric models | 13 |
| MLModelGeneric | Method | SK | 10 |
| MLModelGeneric | Method | models | 9 |
| MLModelGeneric | Method | language models | 9 |
| MLModelGeneric | Method | logistic regression | 7 |
| MLModelGeneric | Method | classifiers | 7 |
| MLModelGeneric | Method | LayoutXLM | 7 |
| MLModelGeneric | Method | attention | 7 |
| MLModelGeneric | Method | model | 6 |
| MLModelGeneric | Method | a model | 6 |
| MLModelGeneric | Method | neural networks | 6 |
| MLModelGeneric | Method | EBMs | 6 |
| MLModelGeneric | Method | large - scale language models | 5 |
| MLModelGeneric | Task | classification | 2 |
| MLModelGeneric | Task | ML architectures | 1 |
| MLModelGeneric | Task | deploying them | 1 |
| MLModelGeneric | Task | various ML architecture | 1 |
| MLModelGeneric | Task | captioning | 1 |
| MLModelGeneric | Task | gender and racial biases exist in sentiment classification | 1 |
| MLModelGeneric | Task | occupational classification | 1 |
| MLModelGeneric | Task | classifiers to disproportionately predict that tweets | 1 |
| MLModelGeneric | Task | classifiers | 1 |
| MLModelGeneric | Task | large - scale language models | 1 |
| MLModelGeneric | Task | autonomous control agents | 1 |
| MLModelGeneric | Task | two baselines | 1 |
| MLModelGeneric | Task | implementation | 1 |
| MLModelGeneric | Task | sets a new baseline | 1 |
| MLModelGeneric | Task | inference in graphical models | 1 |
| MLModelGeneric | NIL | the model | 70 |
| MLModelGeneric | NIL | our model | 21 |
| MLModelGeneric | NIL | these models | 13 |
| MLModelGeneric | NIL | the baselines | 11 |
| MLModelGeneric | NIL | they | 10 |
| MLModelGeneric | NIL | models | 7 |
| MLModelGeneric | NIL | our approach | 7 |
| MLModelGeneric | NIL | the models | 6 |
| MLModelGeneric | NIL | The model | 6 |
| MLModelGeneric | NIL | such models | 6 |
| MLModelGeneric | NIL | the classifiers | 5 |
| MLModelGeneric | NIL | our models | 4 |
| MLModelGeneric | NIL | each classifier | 4 |
| MLModelGeneric | NIL | the classifier | 4 |
| MLModelGeneric | NIL | the model 's | 4 |
| Method | Dataset | OpenAI API | 5 |
| Method | Dataset | Hatebase | 2 |
| Method | Dataset | Pile | 2 |
| Method | Dataset | Mongo | 2 |
| Method | Dataset | NPT | 2 |
| Method | Dataset | IBM Watson | 1 |
| Method | Dataset | Project Nayuki | 1 |
| Method | Dataset | Question - answer collection | 1 |
| Method | Dataset | Turkopticon | 1 |
| Method | Dataset | Stanford CoreNLP | 1 |
| Method | Dataset | Gensim | 1 |
| Method | Dataset | profanity - checker | 1 |
| Method | Dataset | average sentiment | 1 |
| Method | Dataset | py - cld2 | 1 |
| Method | Dataset | pycld2 | 1 |
| Method | Method | NPT | 75 |
| Method | Method | normalizing flows | 25 |
| Method | Method | normalizing flow | 14 |
| Method | Method | denoising score matching | 12 |
| Method | Method | DKL | 11 |
| Method | Method | ABA | 10 |
| Method | Method | semi - supervised learning | 9 |
| Method | Method | IF - SSL | 8 |
| Method | Method | spin - glasses | 8 |
| Method | Method | k - NN | 8 |
| Method | Method | domain adaptation | 7 |
| Method | Method | linear patching | 7 |
| Method | Method | spin - glass | 6 |
| Method | Method | iterative filtering | 5 |
| Method | Method | annotation vectors | 5 |
| Method | Task | denoising score matching | 5 |
| Method | Task | natural language processing | 4 |
| Method | Task | language modeling | 4 |
| Method | Task | pre - training | 4 |
| Method | Task | against label noise | 4 |
| Method | Task | unsupervised learning | 4 |
| Method | Task | ML | 3 |
| Method | Task | iterative filtering | 3 |
| Method | Task | filtering | 3 |
| Method | Task | spin - glass phase transition | 3 |
| Method | Task | answer extraction | 2 |
| Method | Task | Metadata Harvesting | 2 |
| Method | Task | Text - Image Matching | 2 |
| Method | Task | pre - processing | 2 |
| Method | Task | transfer knowledge | 2 |
| Method | NIL | the flow | 19 |
| Method | NIL | the spin - glass phase | 14 |
| Method | NIL | the Pile | 8 |
| Method | NIL | human performance | 7 |
| Method | NIL | the reverse KL divergence | 7 |
| Method | NIL | the annotation vectors | 6 |
| Method | NIL | the KL divergence | 5 |
| Method | NIL | the filtering step | 4 |
| Method | NIL | an unsupervised fashion | 4 |
| Method | NIL | the forward KL divergence | 4 |
| Method | NIL | stochastic feature masking | 4 |
| Method | NIL | filtering | 3 |
| Method | NIL | the input embedding | 3 |
| Method | NIL | the continuous formulation | 3 |
| Method | NIL | the Boltzmann distribution | 3 |
| ModelArchitecture | Dataset | Hatebase | 1 |
| ModelArchitecture | Method | attention | 15 |
| ModelArchitecture | Method | self - attention | 10 |
| ModelArchitecture | Method | DACNN | 9 |
| ModelArchitecture | Method | logistic regression | 7 |
| ModelArchitecture | Method | Transformer | 7 |
| ModelArchitecture | Method | attention network | 7 |
| ModelArchitecture | Method | GPT-3 | 5 |
| ModelArchitecture | Method | CNN layers | 5 |
| ModelArchitecture | Method | Transformers | 5 |
| ModelArchitecture | Method | MLP | 5 |
| ModelArchitecture | Method | logistic regression model | 4 |
| ModelArchitecture | Method | GPT-2 | 4 |
| ModelArchitecture | Method | attention mechanism | 4 |
| ModelArchitecture | Method | attention model | 4 |
| ModelArchitecture | Method | Non - Parametric Transformers | 4 |
| ModelArchitecture | Task | causal attention masking | 1 |
| ModelArchitecture | Task | serial - link robotic manipulators | 1 |
| ModelArchitecture | Task | robotic manipulators | 1 |
| ModelArchitecture | NIL | attention | 20 |
| ModelArchitecture | NIL | attention between datapoints | 6 |
| ModelArchitecture | NIL | heads | 2 |
| ModelArchitecture | NIL | GPT-2 | 1 |
| ModelArchitecture | NIL | attention maps | 1 |
| ModelArchitecture | NIL | NPT input embedding layer | 1 |
| ModelArchitecture | NIL | Attention | 1 |
| ReferenceLink | Dataset | Waseem | 2 |
| ReferenceLink | Dataset | Waseem and Hovy ( 2016 ) | 1 |
| ReferenceLink | Dataset | Obar | 1 |
| ReferenceLink | Dataset | Kobayashi ( 2018 ) | 1 |
| ReferenceLink | Dataset | 2019 | 1 |
| ReferenceLink | Dataset | 30 | 1 |
| ReferenceLink | Dataset | CIFAR-10 [ 55 | 1 |
| ReferenceLink | Method | Song and Ermon ( 2019 ) | 10 |
| ReferenceLink | Method | Waseem , 2016 | 4 |
| ReferenceLink | Method | Waseem and Hovy ( 2016 ) | 4 |
| ReferenceLink | Method | 90 | 4 |
| ReferenceLink | Method | Waseem and Hovy , 2016 | 3 |
| ReferenceLink | Method | Waseem | 3 |
| ReferenceLink | Method | Bostrom | 3 |
| ReferenceLink | Method | Du and Mordatch , 2019 | 3 |
| ReferenceLink | Method | Saremi and Hyvarinen ( 2019 ) | 3 |
| ReferenceLink | Method | 25 | 3 |
| ReferenceLink | Method | 24 | 3 |
| ReferenceLink | Method | Efron and Tibshirani , 1986 | 2 |
| ReferenceLink | Method | Kwok and Wang , 2013 | 2 |
| ReferenceLink | Method | Blodgett and O'Connor ( 2017 ) | 2 |
| ReferenceLink | Method | Rosset , 2019 | 2 |
| ReferenceLink | Task | 18 | 1 |
| ReferenceLink | Task | 90 | 1 |
| ReferenceLink | Task | 64 | 1 |
| ReferenceLink | NIL | 24 | 13 |
| ReferenceLink | NIL | 2 | 12 |
| ReferenceLink | NIL | Brown et al . , 2020 | 11 |
| ReferenceLink | NIL | 4 | 10 |
| ReferenceLink | NIL | 15 | 10 |
| ReferenceLink | NIL | 14 | 9 |
| ReferenceLink | NIL | 25 | 9 |
| ReferenceLink | NIL | 5 | 8 |
| ReferenceLink | NIL | 12 | 8 |
| ReferenceLink | NIL | 3 | 7 |
| ReferenceLink | NIL | 6 | 7 |
| ReferenceLink | NIL | Davidson et al . ( 2017 ) | 7 |
| ReferenceLink | NIL | Brown et al . ( 2020 ) | 7 |
| ReferenceLink | NIL | Ren et al . , 2018 | 7 |
| ReferenceLink | NIL | Davidson et al . , 2017 | 6 |
| Task | Dataset | CC | 2 |
| Task | Dataset | Protein regression | 2 |
| Task | Dataset | classification / regression dataset | 2 |
| Task | Dataset | previous manually labeled RC datasets | 1 |
| Task | Dataset | a large reading comprehension dataset | 1 |
| Task | Dataset | Hatebase | 1 |
| Task | Dataset | AAE | 1 |
| Task | Dataset | labeling datasets | 1 |
| Task | Dataset | perplexity evaluation | 1 |
| Task | Dataset | Wikidetox Toxic Comment | 1 |
| Task | Dataset | sim2sim | 1 |
| Task | Dataset | Protein | 1 |
| Task | Dataset | UCI classification | 1 |
| Task | Method | open - domain QA | 3 |
| Task | Method | generalization | 3 |
| Task | Method | domain adaptation | 2 |
| Task | Method | NRI | 2 |
| Task | Method | cross - domain knowledge | 1 |
| Task | Method | cross - domain generalization | 1 |
| Task | Method | generalize | 1 |
| Task | Method | image - based visual servo control | 1 |
| Task | Method | model complex spin - glass distributions | 1 |
| Task | Method | spin - glasses | 1 |
| Task | Method | inference in graphical models | 1 |
| Task | Method | self - supervised reconstruction | 1 |
| Task | Method | semi - synthetic settings | 1 |
| Task | Method | machine learning | 1 |
| Task | Method | Neural Relational Inference | 1 |
| Task | Task | classification | 11 |
| Task | Task | regression | 10 |
| Task | Task | reasoning | 7 |
| Task | Task | reading comprehension | 6 |
| Task | Task | image classification | 6 |
| Task | Task | language modeling | 5 |
| Task | Task | document understanding | 5 |
| Task | Task | multilingual document understanding | 4 |
| Task | Task | multilingual form understanding | 3 |
| Task | Task | VrDU | 3 |
| Task | Task | form understanding | 3 |
| Task | Task | autonomous driving | 3 |
| Task | Task | sample synthesis | 3 |
| Task | Task | denoising | 3 |
| Task | Task | binary classification | 3 |
| Task | NIL | predict | 3 |
| Task | NIL | de - duplication | 1 |
| Task | NIL | the multilingual VrDU | 1 |
| Task | NIL | sequence labeling | 1 |
| Task | NIL | cross - lingual zero - shot transfer | 1 |
| Task | NIL | multitask learning | 1 |
| Task | NIL | autonomous - driving | 1 |
| Task | NIL | regression | 1 |
| URL | Dataset | https :/ / stanford - qa.com | 1 |
| URL | Dataset | wikipedia / 20200301.en | 1 |
| URL | Dataset | http :/ / data.statmt . org / cc-100 / | 1 |
| URL | Dataset | https :/ / github.com / jdepoix / youtube - transcript - api | 1 |
| URL | Dataset | https :/ / github.com / vphill / pyoaiharvester / | 1 |
| URL | Dataset | https :/ / driving - olympics.ai / | 1 |
| URL | Method | https :/ / www.perspectiveapi.com | 1 |
| URL | Method | https :/ / hatebase.org / | 1 |
| URL | Method | https :/ / github.com / EleutherAI / the - pile | 1 |
| URL | Method | https :/ / archive.org / details / stackexchange | 1 |
| URL | Method | https :/ / bulkdata.uspto.gov / | 1 |
| URL | Method | https :/ / irclogs.ubuntu.com / | 1 |
| URL | Method | https :/ / philpapers.org / | 1 |
| URL | Method | https :/ / exporter.nih.gov / | 1 |
| URL | Method | https :/ / news.ycombinator.com | 1 |
| URL | Method | https :/ / arxiv.org / help / bulk_data_s3 | 1 |
| URL | Method | https :/ / www.courtlistener.com / api / bulk - info / | 1 |
| URL | Method | http :/ / www.statmt.org / europarl / | 1 |
| URL | Method | https :/ / github.com / sdtblck / PDFextract | 1 |
| URL | Method | https :/ / aka.ms / layoutxlm | 1 |
| URL | Method | https :/ / commoncrawl.org | 1 |
| URL | NIL | https :/ / stanford - qa.com | 1 |
| URL | NIL | https :/ / www.courtlistener.com / | 1 |
| URL | NIL | https :/ / www.tensorflow.org / datasets / catalog / c4 | 1 |
| NIL | Dataset | NIH | 3 |
| NIL | Dataset | Microsoft Azure | 1 |
| NIL | Dataset | Quebec | 1 |
| NIL | Dataset | African - American English | 1 |
| NIL | Dataset | sexist | 1 |
| NIL | Dataset | large crowdsourced dictionaries of keywords | 1 |
| NIL | Dataset | Venezuela | 1 |
| NIL | Dataset | subtitles | 1 |
| NIL | Dataset | prose | 1 |
| NIL | Dataset | bulk - data repository | 1 |
| NIL | Dataset | Pile | 1 |
| NIL | Dataset | ACF | 1 |
| NIL | Dataset | AHRQ | 1 |
| NIL | Dataset | CDC | 1 |
| NIL | Dataset | HRSA | 1 |
| NIL | Method | AAE | 5 |
| NIL | Method | RECs | 2 |
| NIL | Method | BPB | 2 |
| NIL | Method | vesicular GABA transporter | 2 |
| NIL | Method | PUE | 1 |
| NIL | Method | crowdworkers | 1 |
| NIL | Method | supervised learning | 1 |
| NIL | Method | net upvotes | 1 |
| NIL | Method | 1 GiB | 1 |
| NIL | Method | datasheet | 1 |
| NIL | Method | Sid Black | 1 |
| NIL | Method | DeepMind Mathematics | 1 |
| NIL | Method | nbsp | 1 |
| NIL | Method | Total knee arthroplasty | 1 |
| NIL | Method | Morningstar | 1 |
| NIL | Task | NLP | 4 |
| NIL | Task | natural language processing | 2 |
| NIL | Task | ML | 1 |
| NIL | Task | much longer phrases | 1 |
| NIL | Task | location | 1 |
| NIL | Task | demographic information | 1 |
| NIL | Task | harassment | 1 |
| NIL | Task | computer science | 1 |
| NIL | Task | technical writing | 1 |
| NIL | Task | television shows | 1 |
| NIL | Task | text | 1 |
| NIL | Task | text gathered | 1 |
| NIL | Task | profanity analysis | 1 |
| NIL | Task | Stack Exchange database dump | 1 |
| NIL | Task | TKA | 1 |

## Notes

- **Partial Matching**: Uses gsaphub's partial span matching to align entities with overlapping spans
- **NIL Class**: Represents entities annotated by one model but not the other
- Confusion matrix shows counts of entity pairs with overlapping spans
- Table shows top mentions for each label pair combination

---
*Generated by UnifiedSciERE Label Confusion Analysis*
