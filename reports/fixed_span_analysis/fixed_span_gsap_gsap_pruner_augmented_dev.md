# Fixed-Span NER + RE — GSAP on GSAP (pruner_augmented_dev)

**Generated:** 2026-03-16 09:30:09

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_gsap_pruner_augmented_dev.json`  
**Gold NER spans:** 6717  
**NER overall accuracy:** 0.572

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|                   |   DataSource |   Dataset |   DatasetGeneric |   MISSING |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   NIL |   ReferenceLink |   Task |   URL |
|:------------------|-------------:|----------:|-----------------:|----------:|----------:|-----------------:|---------:|--------------------:|------:|----------------:|-------:|------:|
| DataSource        |           38 |        12 |               21 |         0 |         0 |                0 |        5 |                   0 |    27 |               0 |      0 |     0 |
| Dataset           |            9 |       175 |               83 |         0 |         4 |                1 |       38 |                   0 |   142 |               0 |      0 |     0 |
| DatasetGeneric    |            1 |         4 |             1215 |         0 |         0 |                2 |       78 |                   1 |   267 |               0 |      3 |     0 |
| MLModel           |            0 |         1 |                0 |         1 |        53 |                8 |       11 |                  16 |    35 |               0 |      0 |     0 |
| MLModelGeneric    |            0 |         1 |              135 |         0 |         9 |              568 |      209 |                  19 |   237 |               0 |      0 |     0 |
| Method            |            3 |         7 |               89 |         0 |         3 |               16 |      940 |                   4 |   347 |               0 |      9 |     0 |
| ModelArchitecture |            0 |         1 |               60 |         0 |        26 |              129 |      176 |                 168 |   208 |               0 |      1 |     0 |
| ReferenceLink     |            0 |         0 |               11 |         3 |         0 |                0 |       30 |                   0 |   152 |             558 |      0 |     0 |
| Task              |            0 |         2 |               29 |         0 |         0 |                1 |       57 |                   0 |   100 |               0 |    124 |     0 |
| URL               |            0 |         0 |                9 |         0 |         0 |                0 |        8 |                   0 |    14 |               0 |      0 |     3 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|                   | DataSource    | Dataset       | DatasetGeneric   | MISSING   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | NIL           | ReferenceLink   | Task          | URL           |
|:------------------|:--------------|:--------------|:-----------------|:----------|:--------------|:-----------------|:--------------|:--------------------|:--------------|:----------------|:--------------|:--------------|
| DataSource        | 0.025 / 0.903 | 0.006 / 0.915 | 0.216 / 0.611    | —         | —             | —                | 0.092 / 0.750 | —                   | 0.601 / 0.601 | —               | —             | —             |
| Dataset           | 0.012 / 0.842 | 0.010 / 0.959 | 0.160 / 0.654    | —         | 0.002 / 0.824 | 0.004 / 0.945    | 0.175 / 0.607 | —                   | 0.679 / 0.679 | —               | —             | —             |
| DatasetGeneric    | 0.424 / 0.568 | 0.000 / 0.984 | 0.106 / 0.862    | —         | —             | 0.049 / 0.664    | 0.164 / 0.663 | 0.039 / 0.603       | 0.769 / 0.769 | —               | 0.012 / 0.902 | —             |
| MLModel           | —             | 0.000 / 0.743 | —                | —         | 0.001 / 0.948 | 0.000 / 0.584    | 0.242 / 0.495 | 0.021 / 0.830       | 0.686 / 0.686 | —               | —             | —             |
| MLModelGeneric    | —             | 0.003 / 0.957 | 0.231 / 0.599    | —         | 0.136 / 0.713 | 0.036 / 0.904    | 0.133 / 0.717 | 0.009 / 0.700       | 0.642 / 0.642 | —               | —             | —             |
| Method            | 0.001 / 0.852 | 0.000 / 0.968 | 0.188 / 0.652    | —         | 0.004 / 0.772 | 0.065 / 0.831    | 0.105 / 0.840 | 0.073 / 0.670       | 0.742 / 0.742 | —               | 0.102 / 0.753 | —             |
| ModelArchitecture | —             | 0.000 / 0.608 | 0.266 / 0.602    | —         | 0.066 / 0.759 | 0.011 / 0.866    | 0.125 / 0.761 | 0.033 / 0.902       | 0.622 / 0.622 | —               | 0.187 / 0.208 | —             |
| ReferenceLink     | —             | —             | 0.268 / 0.466    | —         | —             | —                | 0.254 / 0.579 | —                   | 0.836 / 0.836 | 0.002 / 0.996   | —             | —             |
| Task              | —             | 0.000 / 1.000 | 0.170 / 0.560    | —         | —             | 0.256 / 0.732    | 0.153 / 0.692 | —                   | 0.703 / 0.703 | —               | 0.021 / 0.944 | —             |
| URL               | —             | —             | 0.078 / 0.584    | —         | —             | —                | 0.152 / 0.570 | —                   | 0.604 / 0.604 | —               | —             | 0.000 / 0.993 |

## NER — Per-Label Accuracy

| Gold Label        |   Total |   Correct |   Accuracy |
|:------------------|--------:|----------:|-----------:|
| DatasetGeneric    |    1571 |      1215 |      0.773 |
| Method            |    1418 |       940 |      0.663 |
| MLModelGeneric    |    1178 |       568 |      0.482 |
| ModelArchitecture |     769 |       168 |      0.218 |
| ReferenceLink     |     754 |       558 |      0.74  |
| Dataset           |     452 |       175 |      0.387 |
| Task              |     313 |       124 |      0.396 |
| MLModel           |     125 |        53 |      0.424 |
| DataSource        |     103 |        38 |      0.369 |
| URL               |      34 |         3 |      0.088 |

## NER — Examples (top 5 per cell)

| Gold Label        | Pred Label        | Mention Text                                                  |   Freq |
|:------------------|:------------------|:--------------------------------------------------------------|-------:|
| DataSource        | DataSource        | Wikipedia                                                     |      6 |
| DataSource        | DataSource        | Twitter                                                       |      2 |
| DataSource        | DataSource        | Hatebase                                                      |      2 |
| DataSource        | DataSource        | ArXiv                                                         |      2 |
| DataSource        | DataSource        | GitHub                                                        |      2 |
| DataSource        | Dataset           | Bibliotik                                                     |      3 |
| DataSource        | Dataset           | Hatebase                                                      |      1 |
| DataSource        | Dataset           | Wikipedia                                                     |      1 |
| DataSource        | Dataset           | PubMed Central                                                |      1 |
| DataSource        | Dataset           | ArXiv                                                         |      1 |
| DataSource        | DatasetGeneric    | Literotica                                                    |      3 |
| DataSource        | DatasetGeneric    | Wikipedia                                                     |      2 |
| DataSource        | DatasetGeneric    | arXiv                                                         |      2 |
| DataSource        | DatasetGeneric    | Stack Exchange                                                |      2 |
| DataSource        | DatasetGeneric    | English Wikipedia                                             |      1 |
| DataSource        | Method            | Stack Exchange                                                |      2 |
| DataSource        | Method            | StackOverflow                                                 |      1 |
| DataSource        | Method            | Common Crawl                                                  |      1 |
| DataSource        | Method            | Kaggle                                                        |      1 |
| DataSource        | NIL               | GitHub                                                        |      4 |
| DataSource        | NIL               | UCI                                                           |      4 |
| DataSource        | NIL               | Reddit                                                        |      3 |
| DataSource        | NIL               | Literotica                                                    |      3 |
| DataSource        | NIL               | PubMed                                                        |      2 |
| Dataset           | DataSource        | Common Crawl                                                  |      5 |
| Dataset           | DataSource        | English Wikipedia                                             |      1 |
| Dataset           | DataSource        | Wikipedia                                                     |      1 |
| Dataset           | DataSource        | PubMed Central                                                |      1 |
| Dataset           | DataSource        | Ubuntu IRC                                                    |      1 |
| Dataset           | Dataset           | CIFAR-10                                                      |     18 |
| Dataset           | Dataset           | MNIST                                                         |     16 |
| Dataset           | Dataset           | SQuAD                                                         |      9 |
| Dataset           | Dataset           | BookCorpus                                                    |      7 |
| Dataset           | Dataset           | XFUND                                                         |      7 |
| Dataset           | DatasetGeneric    | the Pile                                                      |     40 |
| Dataset           | DatasetGeneric    | Pile                                                          |      5 |
| Dataset           | DatasetGeneric    | Common Crawl                                                  |      4 |
| Dataset           | DatasetGeneric    | Enron Emails                                                  |      3 |
| Dataset           | DatasetGeneric    | USPTO Backgrounds                                             |      2 |
| Dataset           | MLModel           | OWT2                                                          |      1 |
| Dataset           | MLModel           | CC-100                                                        |      1 |
| Dataset           | MLModel           | Pile - CC                                                     |      1 |
| Dataset           | MLModel           | Pile                                                          |      1 |
| Dataset           | MLModelGeneric    | the Pile                                                      |      1 |
| Dataset           | Method            | the Pile                                                      |      7 |
| Dataset           | Method            | CIFAR-10                                                      |      6 |
| Dataset           | Method            | CIFAR-100                                                     |      3 |
| Dataset           | Method            | Common Crawl                                                  |      2 |
| Dataset           | Method            | SQuAD                                                         |      1 |
| Dataset           | NIL               | the Pile                                                      |     21 |
| Dataset           | NIL               | CIFAR-10                                                      |     11 |
| Dataset           | NIL               | Protein                                                       |     11 |
| Dataset           | NIL               | XFUND                                                         |      8 |
| Dataset           | NIL               | Pile                                                          |      7 |
| DatasetGeneric    | DataSource        | Wikipedia                                                     |      1 |
| DatasetGeneric    | Dataset           | AAE                                                           |      3 |
| DatasetGeneric    | Dataset           | Pile 's                                                       |      1 |
| DatasetGeneric    | DatasetGeneric    | the dataset                                                   |     38 |
| DatasetGeneric    | DatasetGeneric    | datapoints                                                    |     36 |
| DatasetGeneric    | DatasetGeneric    | the data                                                      |     32 |
| DatasetGeneric    | DatasetGeneric    | tweets                                                        |     24 |
| DatasetGeneric    | DatasetGeneric    | each dataset                                                  |     19 |
| DatasetGeneric    | MLModelGeneric    | the baselines                                                 |      1 |
| DatasetGeneric    | MLModelGeneric    | the development set                                           |      1 |
| DatasetGeneric    | Method            | label noise                                                   |      7 |
| DatasetGeneric    | Method            | the training set                                              |      4 |
| DatasetGeneric    | Method            | the Hatebase lexicon                                          |      2 |
| DatasetGeneric    | Method            | high noise ratios                                             |      2 |
| DatasetGeneric    | Method            | all samples                                                   |      2 |
| DatasetGeneric    | ModelArchitecture | matrix - shaped input                                         |      1 |
| DatasetGeneric    | NIL               | tweets                                                        |      6 |
| DatasetGeneric    | NIL               | datasets                                                      |      6 |
| DatasetGeneric    | NIL               | data                                                          |      5 |
| DatasetGeneric    | NIL               | targets                                                       |      5 |
| DatasetGeneric    | NIL               | potentially noisy labels                                      |      4 |
| DatasetGeneric    | Task              | Algebra word problems                                         |      1 |
| DatasetGeneric    | Task              | cloze queries                                                 |      1 |
| DatasetGeneric    | Task              | cloze - style queries                                         |      1 |
| MLModel           | Dataset           | TabNet                                                        |      1 |
| MLModel           | MISSING           | TabNet                                                        |      1 |
| MLModel           | MLModel           | GPT-3                                                         |      9 |
| MLModel           | MLModel           | LayoutXLM                                                     |      8 |
| MLModel           | MLModel           | TabNet                                                        |      5 |
| MLModel           | MLModel           | GPT-2                                                         |      4 |
| MLModel           | MLModel           | XLM                                                           |      2 |
| MLModel           | MLModelGeneric    | CatBoost                                                      |      3 |
| MLModel           | MLModelGeneric    | GPT-2 Pile                                                    |      1 |
| MLModel           | MLModelGeneric    | S - Model                                                     |      1 |
| MLModel           | MLModelGeneric    | XGBoost                                                       |      1 |
| MLModel           | MLModelGeneric    | LightGBM                                                      |      1 |
| MLModel           | Method            | LayoutXLM                                                     |      5 |
| MLModel           | Method            | GPT-3                                                         |      1 |
| MLModel           | Method            | GPT-2                                                         |      1 |
| MLModel           | Method            | LayoutLM                                                      |      1 |
| MLModel           | Method            | LayoutXLM 's                                                  |      1 |
| MLModel           | ModelArchitecture | GPT-3                                                         |      5 |
| MLModel           | ModelArchitecture | XGBoost                                                       |      4 |
| MLModel           | ModelArchitecture | GPT-2                                                         |      3 |
| MLModel           | ModelArchitecture | CatBoost                                                      |      2 |
| MLModel           | ModelArchitecture | LayoutXLM                                                     |      1 |
| MLModel           | NIL               | GPT-3                                                         |     10 |
| MLModel           | NIL               | LayoutXLM                                                     |      8 |
| MLModel           | NIL               | LayoutLMv2                                                    |      5 |
| MLModel           | NIL               | GPT-2                                                         |      2 |
| MLModel           | NIL               | IBM Watson                                                    |      1 |
| MLModelGeneric    | Dataset           | Protein                                                       |      1 |
| MLModelGeneric    | DatasetGeneric    | NPTs                                                          |     19 |
| MLModelGeneric    | DatasetGeneric    | NPT                                                           |     16 |
| MLModelGeneric    | DatasetGeneric    | the model                                                     |      3 |
| MLModelGeneric    | DatasetGeneric    | the classifiers                                               |      3 |
| MLModelGeneric    | DatasetGeneric    | language models                                               |      3 |
| MLModelGeneric    | MLModel           | Resnet26                                                      |      2 |
| MLModelGeneric    | MLModel           | Resnet18                                                      |      2 |
| MLModelGeneric    | MLModel           | Set Transformer                                               |      2 |
| MLModelGeneric    | MLModel           | Resnext                                                       |      1 |
| MLModelGeneric    | MLModel           | NPT - Base                                                    |      1 |
| MLModelGeneric    | MLModelGeneric    | NPTs                                                          |     57 |
| MLModelGeneric    | MLModelGeneric    | the model                                                     |     42 |
| MLModelGeneric    | MLModelGeneric    | NPT                                                           |     22 |
| MLModelGeneric    | MLModelGeneric    | our model                                                     |     12 |
| MLModelGeneric    | MLModelGeneric    | models                                                        |     12 |
| MLModelGeneric    | Method            | NPT                                                           |     19 |
| MLModelGeneric    | Method            | the flow                                                      |     16 |
| MLModelGeneric    | Method            | normalizing flows                                             |      8 |
| MLModelGeneric    | Method            | DKL                                                           |      8 |
| MLModelGeneric    | Method            | NPTs                                                          |      7 |
| MLModelGeneric    | ModelArchitecture | NPTs                                                          |      3 |
| MLModelGeneric    | ModelArchitecture | Axial Transformers                                            |      2 |
| MLModelGeneric    | ModelArchitecture | GNNs                                                          |      2 |
| MLModelGeneric    | ModelArchitecture | Random Forests                                                |      2 |
| MLModelGeneric    | ModelArchitecture | ResNet                                                        |      1 |
| MLModelGeneric    | NIL               | the model                                                     |     20 |
| MLModelGeneric    | NIL               | NPTs                                                          |     17 |
| MLModelGeneric    | NIL               | our model                                                     |      7 |
| MLModelGeneric    | NIL               | NPT                                                           |      7 |
| MLModelGeneric    | NIL               | classifier                                                    |      6 |
| Method            | DataSource        | GitHub                                                        |      2 |
| Method            | DataSource        | Amazon Web Services                                           |      1 |
| Method            | Dataset           | Pip                                                           |      1 |
| Method            | Dataset           | Conda                                                         |      1 |
| Method            | Dataset           | Trafilatura                                                   |      1 |
| Method            | Dataset           | Newspaper                                                     |      1 |
| Method            | Dataset           | Goose3                                                        |      1 |
| Method            | DatasetGeneric    | human performance                                             |      2 |
| Method            | DatasetGeneric    | the stochastic feature masking                                |      2 |
| Method            | DatasetGeneric    | Stochastic target masking                                     |      2 |
| Method            | DatasetGeneric    | automatic techniques                                          |      1 |
| Method            | DatasetGeneric    | dependency trees                                              |      1 |
| Method            | MLModel           | jusText                                                       |      2 |
| Method            | MLModel           | Gensim                                                        |      1 |
| Method            | MLModelGeneric    | the SK model                                                  |      5 |
| Method            | MLModelGeneric    | Their pattern matching baseline                               |      1 |
| Method            | MLModelGeneric    | Humans                                                        |      1 |
| Method            | MLModelGeneric    | a single noisy model snapshot                                 |      1 |
| Method            | MLModelGeneric    | The image - based only IBVS approach                          |      1 |
| Method            | Method            | the spin - glass phase                                        |     18 |
| Method            | Method            | denoising score matching                                      |     15 |
| Method            | Method            | semi - supervised learning                                    |      8 |
| Method            | Method            | unsupervised learning                                         |      7 |
| Method            | Method            | iterative filtering                                           |      7 |
| Method            | ModelArchitecture | dependency and constituency trees                             |      1 |
| Method            | ModelArchitecture | dependency trees                                              |      1 |
| Method            | ModelArchitecture | parametric attention mechanisms                               |      1 |
| Method            | ModelArchitecture | embedding matrices                                            |      1 |
| Method            | NIL               | jusText                                                       |      4 |
| Method            | NIL               | target masking                                                |      4 |
| Method            | NIL               | AI systems                                                    |      3 |
| Method            | NIL               | the annotation vectors                                        |      3 |
| Method            | NIL               | the SK model                                                  |      3 |
| Method            | Task              | cross - domain knowledge                                      |      1 |
| Method            | Task              | few - shot                                                    |      1 |
| Method            | Task              | machine translation                                           |      1 |
| Method            | Task              | OCR                                                           |      1 |
| Method            | Task              | spin - glass density estimation                               |      1 |
| ModelArchitecture | Dataset           | NRI                                                           |      1 |
| ModelArchitecture | DatasetGeneric    | NPTs                                                          |     21 |
| ModelArchitecture | DatasetGeneric    | NPT                                                           |     18 |
| ModelArchitecture | DatasetGeneric    | attention between datapoints                                  |      9 |
| ModelArchitecture | DatasetGeneric    | the GPT-2 tokenizer                                           |      1 |
| ModelArchitecture | DatasetGeneric    | ABA layers                                                    |      1 |
| ModelArchitecture | MLModel           | DARLA                                                         |      4 |
| ModelArchitecture | MLModel           | LayoutXLM                                                     |      3 |
| ModelArchitecture | MLModel           | NPT - Base                                                    |      3 |
| ModelArchitecture | MLModel           | Resnet26                                                      |      2 |
| ModelArchitecture | MLModel           | Resnet18                                                      |      2 |
| ModelArchitecture | MLModelGeneric    | NPTs                                                          |     62 |
| ModelArchitecture | MLModelGeneric    | NPT                                                           |     24 |
| ModelArchitecture | MLModelGeneric    | EBMs                                                          |      4 |
| ModelArchitecture | MLModelGeneric    | GANs                                                          |      4 |
| ModelArchitecture | MLModelGeneric    | DACNN                                                         |      3 |
| ModelArchitecture | Method            | NPT                                                           |     27 |
| ModelArchitecture | Method            | normalizing flows                                             |     21 |
| ModelArchitecture | Method            | DKL                                                           |     10 |
| ModelArchitecture | Method            | NPTs                                                          |      9 |
| ModelArchitecture | Method            | normalizing flow                                              |      8 |
| ModelArchitecture | ModelArchitecture | attention                                                     |     15 |
| ModelArchitecture | ModelArchitecture | NPT                                                           |      7 |
| ModelArchitecture | ModelArchitecture | Transformer                                                   |      6 |
| ModelArchitecture | ModelArchitecture | logistic regression                                           |      5 |
| ModelArchitecture | ModelArchitecture | Transformers                                                  |      5 |
| ModelArchitecture | NIL               | NPTs                                                          |     19 |
| ModelArchitecture | NIL               | NPT                                                           |     19 |
| ModelArchitecture | NIL               | attention                                                     |     11 |
| ModelArchitecture | NIL               | DACNN                                                         |      7 |
| ModelArchitecture | NIL               | attention between datapoints                                  |      7 |
| ModelArchitecture | Task              | GPT-3                                                         |      1 |
| ReferenceLink     | DatasetGeneric    | Founta et al . ( 2018 )                                       |      2 |
| ReferenceLink     | DatasetGeneric    | Wang and Jiang ( 2016 )                                       |      1 |
| ReferenceLink     | DatasetGeneric    | Gaikwad et al . , 2015                                        |      1 |
| ReferenceLink     | DatasetGeneric    | Founta et al . , 2018                                         |      1 |
| ReferenceLink     | DatasetGeneric    | Blodgett et al . ( 2016 )                                     |      1 |
| ReferenceLink     | MISSING           | 1                                                             |      1 |
| ReferenceLink     | MISSING           | 30                                                            |      1 |
| ReferenceLink     | MISSING           | 2                                                             |      1 |
| ReferenceLink     | Method            | Tarvainen & Valpola , 2017                                    |      2 |
| ReferenceLink     | Method            | ful , 2003                                                    |      1 |
| ReferenceLink     | Method            | Liu et al . , 2018                                            |      1 |
| ReferenceLink     | Method            | Grace et al . , 2018                                          |      1 |
| ReferenceLink     | Method            | Yudkowsky , 2013                                              |      1 |
| ReferenceLink     | NIL               | 24                                                            |      9 |
| ReferenceLink     | NIL               | Song and Ermon ( 2019 )                                       |      6 |
| ReferenceLink     | NIL               | 4                                                             |      5 |
| ReferenceLink     | NIL               | 15                                                            |      5 |
| ReferenceLink     | NIL               | 3                                                             |      4 |
| ReferenceLink     | ReferenceLink     | 25                                                            |     10 |
| ReferenceLink     | ReferenceLink     | 2                                                             |      9 |
| ReferenceLink     | ReferenceLink     | 24                                                            |      9 |
| ReferenceLink     | ReferenceLink     | Brown et al . , 2020                                          |      8 |
| ReferenceLink     | ReferenceLink     | 14                                                            |      8 |
| Task              | Dataset           | sim2sim                                                       |      1 |
| Task              | Dataset           | sim2real                                                      |      1 |
| Task              | DatasetGeneric    | reading comprehension                                         |      3 |
| Task              | DatasetGeneric    | reasoning                                                     |      2 |
| Task              | DatasetGeneric    | open - domain QA                                              |      2 |
| Task              | DatasetGeneric    | Open - domain question answering                              |      1 |
| Task              | DatasetGeneric    | Cloze datasets                                                |      1 |
| Task              | MLModelGeneric    | approximate the 2d Ising model                                |      1 |
| Task              | Method            | domain adaptation                                             |      8 |
| Task              | Method            | zero - shot reinforcement learning                            |      3 |
| Task              | Method            | discrete optimization                                         |      2 |
| Task              | Method            | solving 4th grade science exams                               |      1 |
| Task              | Method            | answer extraction                                             |      1 |
| Task              | NIL               | classification                                                |      8 |
| Task              | NIL               | regression                                                    |      6 |
| Task              | NIL               | sim2real                                                      |      3 |
| Task              | NIL               | image classification                                          |      3 |
| Task              | NIL               | RC                                                            |      2 |
| Task              | Task              | reading comprehension                                         |      6 |
| Task              | Task              | regression                                                    |      5 |
| Task              | Task              | reasoning                                                     |      4 |
| Task              | Task              | classification                                                |      4 |
| Task              | Task              | RC                                                            |      3 |
| URL               | DatasetGeneric    | https :/ / hatebase.org /                                     |      1 |
| URL               | DatasetGeneric    | https :/ / www.courtlistener.com /                            |      1 |
| URL               | DatasetGeneric    | https :/ / github.com / SpamScope /                           |      1 |
| URL               | DatasetGeneric    | https :/ / bulkdata.uspto.gov /                               |      1 |
| URL               | DatasetGeneric    | https :/ / irclogs.ubuntu.com /                               |      1 |
| URL               | Method            | https :/ / github.com / mlco2 / impact / tree / master / data |      1 |
| URL               | Method            | https :/ / github.com / EleutherAI / the - pile               |      1 |
| URL               | Method            | https :/ / archive.org / details / stackexchange              |      1 |
| URL               | Method            | https :/ / commoncrawl.org                                    |      1 |
| URL               | Method            | https :/ / github.com / microsoft / BlingFire                 |      1 |
| URL               | NIL               | https :/ / stanford - qa.com                                  |      1 |
| URL               | NIL               | https :/ / www.perspectiveapi.com                             |      1 |
| URL               | NIL               | www.fanfiction.net                                            |      1 |
| URL               | NIL               | http :/ / data.statmt . org / cc-100 /                        |      1 |
| URL               | NIL               | https :/ / www.courtlistener.com / api / bulk - info /        |      1 |
| URL               | URL               | https :/ / stanford - qa.com                                  |      1 |
| URL               | URL               | https :/ / news.ycombinator.com                               |      1 |
| URL               | URL               | github.com / OATML / Non - Parametric - Transformers          |      1 |

## RE — Relation Confusion Matrix

**Gold relations:** 3818  
**Predicted relations:** 1333  

Rows = gold labels · Columns = predicted labels · NIL = unmatched on the respective side.

|                 |   appliedTo |   architecture |   benchmarkFor |   citation |   coreference |   evaluatedOn |   generatedBy |   hasInstanceType |   isBasedOn |   isComparedTo |   isHyponymOf |   isPartOf |   processed |   size |   sourcedFrom |   trainedOn |   transformedFrom |   url |   usedFor |   versionOf |   NIL |
|:----------------|------------:|---------------:|---------------:|-----------:|--------------:|--------------:|--------------:|------------------:|------------:|---------------:|--------------:|-----------:|------------:|-------:|--------------:|------------:|------------------:|------:|----------:|------------:|------:|
| appliedTo       |          37 |              0 |              0 |          0 |             0 |             0 |             0 |                 0 |           0 |              0 |             1 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         0 |           0 |   139 |
| architecture    |           0 |             57 |              0 |          0 |             1 |             0 |             0 |                 0 |           5 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         0 |           0 |   460 |
| benchmarkFor    |           0 |              0 |             17 |          0 |             0 |             0 |             0 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         0 |           0 |    70 |
| citation        |           0 |              0 |              0 |        329 |             0 |             0 |             0 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         0 |           0 |   364 |
| coreference     |           0 |              2 |              0 |          0 |            83 |             0 |             0 |                 0 |           1 |              1 |             2 |          4 |           0 |      0 |             0 |           0 |                 1 |     0 |         2 |           0 |   136 |
| evaluatedOn     |           0 |              0 |              0 |          0 |             0 |            41 |             1 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |          20 |                 0 |     0 |         0 |           0 |   207 |
| generatedBy     |           0 |              0 |              0 |          0 |             0 |             0 |             8 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         0 |           0 |    97 |
| hasInstanceType |           0 |              0 |              0 |          0 |             0 |             0 |             0 |                 4 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 1 |     0 |         0 |           0 |    34 |
| isBasedOn       |           0 |              8 |              0 |          0 |             0 |             0 |             0 |                 0 |           3 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         1 |           0 |    28 |
| isComparedTo    |           0 |              0 |              0 |          0 |             0 |             3 |             0 |                 0 |           0 |             20 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         0 |           0 |   102 |
| isHyponymOf     |           0 |              0 |              0 |          0 |             1 |             0 |             0 |                 0 |           0 |              0 |            36 |          4 |           0 |      0 |             0 |           0 |                 0 |     0 |         2 |           0 |   143 |
| isPartOf        |           0 |              0 |              0 |          0 |             2 |             0 |             0 |                 0 |           0 |              0 |             4 |         31 |           0 |      0 |             0 |           0 |                 5 |     0 |         0 |           0 |   232 |
| processed       |           0 |              0 |              0 |          0 |             0 |             2 |             0 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |         0 |           0 |    39 |
| size            |           0 |              0 |              0 |          0 |             3 |             0 |             0 |                 0 |           0 |              0 |             0 |          0 |           0 |     14 |             0 |           0 |                 0 |     0 |         0 |           0 |    21 |
| sourcedFrom     |           0 |              0 |              0 |          0 |             0 |             0 |             0 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |            20 |           0 |                 0 |     0 |         0 |           0 |    39 |
| trainedOn       |           0 |              0 |              0 |          0 |             0 |             3 |             0 |                 0 |           1 |              3 |             0 |          0 |           0 |      0 |             1 |          75 |                 0 |     0 |         0 |           0 |   170 |
| transformedFrom |           0 |              0 |              0 |          0 |             1 |             0 |             1 |                 0 |           0 |              0 |             0 |          2 |           0 |      2 |             0 |           0 |                13 |     0 |         0 |           0 |   136 |
| url             |           0 |              0 |              0 |          0 |             0 |             0 |             0 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 0 |     2 |         0 |           0 |     5 |
| usedFor         |           1 |              0 |              0 |          0 |             0 |             0 |             0 |                 0 |           0 |              0 |             2 |          0 |           0 |      0 |             0 |           0 |                 0 |     0 |        82 |           0 |   426 |
| versionOf       |           0 |              0 |              0 |          0 |             0 |             0 |             0 |                 0 |           0 |              0 |             0 |          0 |           0 |      0 |             0 |           0 |                 1 |     0 |         0 |           1 |     2 |
| NIL             |          16 |             15 |             10 |         88 |            18 |            38 |            13 |                 5 |           1 |             27 |            13 |         19 |           8 |      3 |             4 |          28 |                14 |     1 |        44 |           0 |     0 |

## RE — Per-Label Accuracy

| Gold Label      |   Total |   Correct |   Accuracy |
|:----------------|--------:|----------:|-----------:|
| citation        |     693 |       329 |      0.475 |
| architecture    |     523 |        57 |      0.109 |
| usedFor         |     511 |        82 |      0.16  |
| isPartOf        |     274 |        31 |      0.113 |
| evaluatedOn     |     269 |        41 |      0.152 |
| trainedOn       |     253 |        75 |      0.296 |
| coreference     |     232 |        83 |      0.358 |
| isHyponymOf     |     186 |        36 |      0.194 |
| appliedTo       |     177 |        37 |      0.209 |
| transformedFrom |     155 |        13 |      0.084 |
| isComparedTo    |     125 |        20 |      0.16  |
| generatedBy     |     105 |         8 |      0.076 |
| benchmarkFor    |      87 |        17 |      0.195 |
| sourcedFrom     |      59 |        20 |      0.339 |
| processed       |      41 |         0 |      0     |
| isBasedOn       |      40 |         3 |      0.075 |
| hasInstanceType |      39 |         4 |      0.103 |
| size            |      38 |        14 |      0.368 |
| url             |       7 |         2 |      0.286 |
| versionOf       |       4 |         1 |      0.25  |

## RE — Examples (top 5 per cell)

| Gold Label      | Pred Label      | Subject → Object                                                                          |   Freq |
|:----------------|:----------------|:------------------------------------------------------------------------------------------|-------:|
| appliedTo       | appliedTo       | NPT → binary and multi - class classification                                             |      2 |
| appliedTo       | appliedTo       | Machine learning models → detect hate speech and abusive language                         |      1 |
| appliedTo       | appliedTo       | these models → identify abusive language                                                  |      1 |
| appliedTo       | appliedTo       | each classifier → predict                                                                 |      1 |
| appliedTo       | appliedTo       | this classifier → classify                                                                |      1 |
| appliedTo       | isHyponymOf     | adiabatic quantum computation → discrete optimization                                     |      1 |
| appliedTo       | NIL             | classification models → classification                                                    |      2 |
| appliedTo       | NIL             | The proposed algorithm → classification                                                   |      2 |
| appliedTo       | NIL             | NPTs → reasoning                                                                          |      2 |
| appliedTo       | NIL             | NPTs → image classification                                                               |      2 |
| appliedTo       | NIL             | training from scratch → image recognition                                                 |      1 |
| architecture    | architecture    | our logistic regression model → logistic regression                                       |      2 |
| architecture    | architecture    | attention models → attention                                                              |      2 |
| architecture    | architecture    | a strong logistic regression model → logistic regression                                  |      1 |
| architecture    | architecture    | a logistic regression model → logistic regression                                         |      1 |
| architecture    | architecture    | The logistic regression model → logistic regression                                       |      1 |
| architecture    | coreference     | a new architecture → DACNN                                                                |      1 |
| architecture    | isBasedOn       | the pre - trained LayoutXLM model → LayoutXLM                                             |      1 |
| architecture    | isBasedOn       | the pre -   trained LayoutXLM model → LayoutXLM                                           |      1 |
| architecture    | isBasedOn       | two models → DARLA                                                                        |      1 |
| architecture    | isBasedOn       | energy - based models → neural networks                                                   |      1 |
| architecture    | isBasedOn       | variants of NPT - Small → NPT - Small                                                     |      1 |
| architecture    | NIL             | NPTs → NPTs                                                                               |    100 |
| architecture    | NIL             | NPT → NPT                                                                                 |     64 |
| architecture    | NIL             | NPTs → attention between datapoints                                                       |     10 |
| architecture    | NIL             | DKL → DKL                                                                                 |      9 |
| architecture    | NIL             | k - NN → k - NN                                                                           |      7 |
| benchmarkFor    | benchmarkFor    | the dataset → reasoning                                                                   |      1 |
| benchmarkFor    | benchmarkFor    | Existing datasets → RC                                                                    |      1 |
| benchmarkFor    | benchmarkFor    | a large and high - quality reading comprehension dataset → reading comprehension          |      1 |
| benchmarkFor    | benchmarkFor    | previous manually labeled RC datasets → RC                                                |      1 |
| benchmarkFor    | benchmarkFor    | 600 real 3rd-6th grade reading comprehension questions → reading comprehension            |      1 |
| benchmarkFor    | NIL             | Protein → regression                                                                      |      4 |
| benchmarkFor    | NIL             | cloze - style queries → cloze - style queries                                             |      2 |
| benchmarkFor    | NIL             | tweets → predict                                                                          |      2 |
| benchmarkFor    | NIL             | black - aligned tweets → classify                                                         |      2 |
| benchmarkFor    | NIL             | a new reading comprehension dataset → reading comprehension                               |      1 |
| citation        | citation        | TabNet → 2                                                                                |      4 |
| citation        | citation        | Transformer → 90                                                                          |      3 |
| citation        | citation        | CatBoost → 71                                                                             |      3 |
| citation        | citation        | bootstrap sampling → Efron and Tibshirani , 1986                                          |      2 |
| citation        | citation        | EuroParl → Koehn , 2005                                                                   |      2 |
| citation        | NIL             | classifier → Founta et al . ( 2018 )                                                      |      3 |
| citation        | NIL             | AI systems → Bostrom , 2014                                                               |      3 |
| citation        | NIL             | classifier → Waseem and Hovy ( 2016 )                                                     |      2 |
| citation        | NIL             | language modeling → Raffel et al . , 2019                                                 |      2 |
| citation        | NIL             | language modeling → Brown et al . , 2020                                                  |      2 |
| coreference     | architecture    | GPT-2 → GPT-2                                                                             |      1 |
| coreference     | architecture    | GPT-3 → GPT-3                                                                             |      1 |
| coreference     | coreference     | NPT → NPT                                                                                 |      6 |
| coreference     | coreference     | the model → the model                                                                     |      3 |
| coreference     | coreference     | Non - Parametric Transformers → NPTs                                                      |      3 |
| coreference     | coreference     | the Pile → the Pile                                                                       |      2 |
| coreference     | coreference     | DARLA → DisentAngled Representation Learning Agent                                        |      2 |
| coreference     | isBasedOn       | NPTs → the models                                                                         |      1 |
| coreference     | isComparedTo    | black - aligned tweets → black - aligned tweets                                           |      1 |
| coreference     | isHyponymOf     | multiplicative attention → dot - product attention                                        |      1 |
| coreference     | isHyponymOf     | Transformer - based → Transformers                                                        |      1 |
| coreference     | isPartOf        | these datasets → black - aligned and white - aligned tweets                               |      1 |
| coreference     | isPartOf        | GPT-2 → these models                                                                      |      1 |
| coreference     | isPartOf        | GPT-3 → these models                                                                      |      1 |
| coreference     | isPartOf        | The network → ResNet                                                                      |      1 |
| coreference     | transformedFrom | new " test data " → the duplicates                                                        |      1 |
| coreference     | usedFor         | IF - SSL → Iterative Filtering + Semi - supervised Learning                               |      1 |
| coreference     | usedFor         | our model → IF - SSL                                                                      |      1 |
| coreference     | NIL             | cloze - style queries → cloze queries                                                     |      2 |
| coreference     | NIL             | the Pile → the Pile                                                                       |      2 |
| coreference     | NIL             | GPT-3 → GPT-3                                                                             |      2 |
| coreference     | NIL             | Multiscale Denoising Score Matching → MDSM                                                |      2 |
| coreference     | NIL             | Attention Between Attributes → ABA                                                        |      2 |
| evaluatedOn     | evaluatedOn     | GPT-3 → datasets                                                                          |      2 |
| evaluatedOn     | evaluatedOn     | these models → the data                                                                   |      2 |
| evaluatedOn     | evaluatedOn     | NPTs → CIFAR-10                                                                           |      2 |
| evaluatedOn     | evaluatedOn     | classifiers → black - aligned tweets                                                      |      1 |
| evaluatedOn     | evaluatedOn     | GPT-3 → domain - specific datasets                                                        |      1 |
| evaluatedOn     | generatedBy     | TabNet → Forest Cover                                                                     |      1 |
| evaluatedOn     | trainedOn       | NPTs → datapoints                                                                         |      2 |
| evaluatedOn     | trainedOn       | a general - purpose deep learning architecture → the entire dataset                       |      1 |
| evaluatedOn     | trainedOn       | the model → points                                                                        |      1 |
| evaluatedOn     | trainedOn       | deep learning models → datapoints                                                         |      1 |
| evaluatedOn     | trainedOn       | the model → the entire dataset                                                            |      1 |
| evaluatedOn     | NIL             | NPTs → datapoints                                                                         |      6 |
| evaluatedOn     | NIL             | NPTs → MNIST                                                                              |      3 |
| evaluatedOn     | NIL             | GPT-3 → Pile                                                                              |      2 |
| evaluatedOn     | NIL             | LayoutXLM → XFUND                                                                         |      2 |
| evaluatedOn     | NIL             | The proposed algorithm → CIFAR-10                                                         |      2 |
| generatedBy     | generatedBy     | passages → curating                                                                       |      1 |
| generatedBy     | generatedBy     | question - answers → crowdsourcing                                                        |      1 |
| generatedBy     | generatedBy     | Chatlog data → real - time human interactions                                             |      1 |
| generatedBy     | generatedBy     | the noisy data samples → Gaussian noise                                                   |      1 |
| generatedBy     | generatedBy     | the data → Monte Carlo sampling                                                           |      1 |
| generatedBy     | NIL             | questions → crowdworkers                                                                  |      1 |
| generatedBy     | NIL             | 660 stories → crowdworkers                                                                |      1 |
| generatedBy     | NIL             | the top 10000 articles → Project Nayuki 's Wikipedia 's internal PageRanks                |      1 |
| generatedBy     | NIL             | the dataset → stratify                                                                    |      1 |
| generatedBy     | NIL             | spans → the constituency parse                                                            |      1 |
| hasInstanceType | hasInstanceType | SQuAD → questions                                                                         |      2 |
| hasInstanceType | hasInstanceType | SQuAD → answers                                                                           |      1 |
| hasInstanceType | hasInstanceType | a corpus → tweets                                                                         |      1 |
| hasInstanceType | transformedFrom | SQuAD → questions                                                                         |      1 |
| hasInstanceType | NIL             | CIFAR-10 → images                                                                         |      2 |
| hasInstanceType | NIL             | MNIST → images                                                                            |      2 |
| hasInstanceType | NIL             | WikiQA → answers                                                                          |      1 |
| hasInstanceType | NIL             | SQuAD → SQuAD questions                                                                   |      1 |
| hasInstanceType | NIL             | the development set → the questions                                                       |      1 |
| isBasedOn       | architecture    | the existing GPT-2 and GPT-3 models → GPT-3                                               |      1 |
| isBasedOn       | architecture    | the existing GPT-2 and GPT-3 models → GPT-2                                               |      1 |
| isBasedOn       | architecture    | all available versions of GPT-2 → GPT-2                                                   |      1 |
| isBasedOn       | architecture    | all four versions of GPT-3 → GPT-3                                                        |      1 |
| isBasedOn       | architecture    | a GPT-3 model → GPT-3                                                                     |      1 |
| isBasedOn       | isBasedOn       | semi - supervised models → a Mean Teacher model                                           |      1 |
| isBasedOn       | isBasedOn       | recurrent neural networks → attention models                                              |      1 |
| isBasedOn       | isBasedOn       | each additional model → previous models                                                   |      1 |
| isBasedOn       | usedFor         | DKL → the neural network                                                                  |      1 |
| isBasedOn       | NIL             | DKL → a neural network                                                                    |      2 |
| isBasedOn       | NIL             | This model → demographicallyaligned language models                                       |      1 |
| isBasedOn       | NIL             | the GPT-2 - Pile model → GPT-2                                                            |      1 |
| isBasedOn       | NIL             | a GPT-3 model → GPT-3                                                                     |      1 |
| isBasedOn       | NIL             | a multilingual extension of the recent LayoutLMv2 model → LayoutLMv2                      |      1 |
| isComparedTo    | evaluatedOn     | the dataset → OWT2                                                                        |      1 |
| isComparedTo    | evaluatedOn     | the Pile → WikiText                                                                       |      1 |
| isComparedTo    | evaluatedOn     | the Pile → LAMBADA                                                                        |      1 |
| isComparedTo    | isComparedTo    | black - aligned tweets → white - aligned tweets                                           |      2 |
| isComparedTo    | isComparedTo    | NPT → CatBoost                                                                            |      2 |
| isComparedTo    | isComparedTo    | NPT → XGBoost                                                                             |      2 |
| isComparedTo    | isComparedTo    | a strong logistic regression model → a simple baseline                                    |      1 |
| isComparedTo    | isComparedTo    | SQuAD → previous manually labeled RC datasets                                             |      1 |
| isComparedTo    | NIL             | the black - aligned corpus → the white - aligned corpus                                   |      3 |
| isComparedTo    | NIL             | the Pile → Common Crawl                                                                   |      2 |
| isComparedTo    | NIL             | CC-100 → the Pile                                                                         |      2 |
| isComparedTo    | NIL             | NPT → the baselines                                                                       |      2 |
| isComparedTo    | NIL             | those → explicit reading comprehension questions                                          |      1 |
| isHyponymOf     | coreference     | LayoutXLM → a multimodal pretrained model                                                 |      1 |
| isHyponymOf     | isHyponymOf     | XFUND → a multilingual form understanding benchmark dataset                               |      2 |
| isHyponymOf     | isHyponymOf     | random hyperparameter search → hyperparameter search                                      |      1 |
| isHyponymOf     | isHyponymOf     | VGG → a model                                                                             |      1 |
| isHyponymOf     | isHyponymOf     | BERT → a model                                                                            |      1 |
| isHyponymOf     | isHyponymOf     | SQuAD → a new reading comprehension dataset                                               |      1 |
| isHyponymOf     | isPartOf        | Forest Cover → certain datasets                                                           |      1 |
| isHyponymOf     | isPartOf        | Kick → certain datasets                                                                   |      1 |
| isHyponymOf     | isPartOf        | Breast Cancer → certain datasets                                                          |      1 |
| isHyponymOf     | isPartOf        | these datasets → medium and large datasets                                                |      1 |
| isHyponymOf     | usedFor         | normalizing flows → Generative models                                                     |      1 |
| isHyponymOf     | usedFor         | Gaussian Processes → such models                                                          |      1 |
| isHyponymOf     | NIL             | LayoutXLM → a multimodal pre - trained model                                              |      2 |
| isHyponymOf     | NIL             | the filtered data → unlabeled samples                                                     |      2 |
| isHyponymOf     | NIL             | the image features → annotation vectors                                                   |      2 |
| isHyponymOf     | NIL             | NPTs → machine learning models                                                            |      2 |
| isHyponymOf     | NIL             | a model → ML architectures                                                                |      1 |
| isPartOf        | coreference     | model → such models                                                                       |      1 |
| isPartOf        | coreference     | missing data → the data                                                                   |      1 |
| isPartOf        | isHyponymOf     | XLM - R → the pre - trained models                                                        |      1 |
| isPartOf        | isHyponymOf     | InfoXLM → the pre - trained models                                                        |      1 |
| isPartOf        | isHyponymOf     | CatBoost → two popular state - of - the - art boosting methods                            |      1 |
| isPartOf        | isHyponymOf     | XGBoost → two popular state - of - the - art boosting methods                             |      1 |
| isPartOf        | isPartOf        | negative classes → the corpora                                                            |      1 |
| isPartOf        | isPartOf        | established natural language processing datasets → 22 diverse and high - quality datasets |      1 |
| isPartOf        | isPartOf        | Books3 → several existing highquality datasets                                            |      1 |
| isPartOf        | isPartOf        | Project Gutenberg → several existing highquality datasets                                 |      1 |
| isPartOf        | isPartOf        | Open - Subtitles → several existing highquality datasets                                  |      1 |
| isPartOf        | transformedFrom | a training set → the articles                                                             |      1 |
| isPartOf        | transformedFrom | data → Wikipedia talk comments                                                            |      1 |
| isPartOf        | transformedFrom | a global training set → the input data                                                    |      1 |
| isPartOf        | transformedFrom | smaller subsets → the data                                                                |      1 |
| isPartOf        | transformedFrom | a random subsample → the data                                                             |      1 |
| isPartOf        | NIL             | tweets → the black - aligned corpus                                                       |      4 |
| isPartOf        | NIL             | those → Existing datasets                                                                 |      2 |
| isPartOf        | NIL             | each dataset → the Pile                                                                   |      2 |
| isPartOf        | NIL             | noisy labels → the samples                                                                |      2 |
| isPartOf        | NIL             | the provided labels → all samples                                                         |      2 |
| processed       | evaluatedOn     | each classifier → each dataset                                                            |      1 |
| processed       | evaluatedOn     | other models → this dataset                                                               |      1 |
| processed       | NIL             | classifier → black - aligned tweets                                                       |      2 |
| processed       | NIL             | widely used language classifiers → AAE                                                    |      1 |
| processed       | NIL             | a TF - IDF matrix → each dataset                                                          |      1 |
| processed       | NIL             | Their validation analyses → tweets                                                        |      1 |
| processed       | NIL             | analysis → tweets                                                                         |      1 |
| size            | coreference     | a training set → 80 %                                                                     |      1 |
| size            | coreference     | a development set → 10 %                                                                  |      1 |
| size            | coreference     | a test set → 10 %                                                                         |      1 |
| size            | size            | SQuAD → 100 , 000 + questions                                                             |      1 |
| size            | size            | SQuAD → 107 , 785 question - answer pairs                                                 |      1 |
| size            | size            | a dataset → 600 real 3rd-6th grade reading comprehension questions                        |      1 |
| size            | size            | MCTest → 660 stories                                                                      |      1 |
| size            | size            | the 536 articles → 23 , 215 paragraphs                                                    |      1 |
| size            | NIL             | This dataset → 16 , 849 tweets                                                            |      1 |
| size            | NIL             | The dataset → 6 , 909 tweets                                                              |      1 |
| size            | NIL             | The dataset → 24 , 783 tweets                                                             |      1 |
| size            | NIL             | 91 , 951 tweets → a dataset                                                               |      1 |
| size            | NIL             | Their publiclyavailable dataset → 59.2 million tweets                                     |      1 |
| sourcedFrom     | sourcedFrom     | Wikipedia articles → Wikipedia                                                            |      1 |
| sourcedFrom     | sourcedFrom     | Wikipedia passages → Wikipedia                                                            |      1 |
| sourcedFrom     | sourcedFrom     | CNN / Daily News articles → CNN / Daily News                                              |      1 |
| sourcedFrom     | sourcedFrom     | Wikipedia talk comments → Wikipedia                                                       |      1 |
| sourcedFrom     | sourcedFrom     | their data → Common Crawl                                                                 |      1 |
| sourcedFrom     | NIL             | Wikipedia articles → Wikipedia                                                            |      2 |
| sourcedFrom     | NIL             | the Hatebase lexicon → Hatebase                                                           |      2 |
| sourcedFrom     | NIL             | PubMed Abstracts → PubMed                                                                 |      2 |
| sourcedFrom     | NIL             | Wikipedia → Wikipedia                                                                     |      2 |
| sourcedFrom     | NIL             | the top 10000 articles → English Wikipedia                                                |      1 |
| trainedOn       | evaluatedOn     | our approach → images                                                                     |      1 |
| trainedOn       | evaluatedOn     | NPT → Protein                                                                             |      1 |
| trainedOn       | evaluatedOn     | all boosting methods → Protein                                                            |      1 |
| trainedOn       | isBasedOn       | the Pile - CC topic model → Pile - CC                                                     |      1 |
| trainedOn       | isComparedTo    | models → CC-100                                                                           |      2 |
| trainedOn       | isComparedTo    | GPT-3 → OWT2                                                                              |      1 |
| trainedOn       | sourcedFrom     | raw and filtered Common Crawl models → Common Crawl                                       |      1 |
| trainedOn       | trainedOn       | models → Pile                                                                             |      3 |
| trainedOn       | trainedOn       | classifiers → these datasets                                                              |      2 |
| trainedOn       | trainedOn       | the model → the data                                                                      |      2 |
| trainedOn       | trainedOn       | NPTs → data                                                                               |      2 |
| trainedOn       | trainedOn       | NPTs → the data                                                                           |      2 |
| trainedOn       | NIL             | NPTs → datapoints                                                                         |      3 |
| trainedOn       | NIL             | the model → the training set                                                              |      2 |
| trainedOn       | NIL             | the model → the training data                                                             |      2 |
| trainedOn       | NIL             | models → Raw CC                                                                           |      2 |
| trainedOn       | NIL             | Random Forests → Higgs                                                                    |      2 |
| transformedFrom | coreference     | the entire dataset → all datapoints                                                       |      1 |
| transformedFrom | generatedBy     | test data → features                                                                      |      1 |
| transformedFrom | isPartOf        | 8 million scanned English documents → IIT - CDIP                                          |      1 |
| transformedFrom | isPartOf        | the targets → other training datapoints                                                   |      1 |
| transformedFrom | size            | MCTest → 4 questions                                                                      |      1 |
| transformedFrom | size            | datasets → millions of datapoints                                                         |      1 |
| transformedFrom | transformedFrom | MCTest → 4 answer choices                                                                 |      1 |
| transformedFrom | transformedFrom | abstractive summaries → CNN / Daily News articles                                         |      1 |
| transformedFrom | transformedFrom | our dataset → passages                                                                    |      1 |
| transformedFrom | transformedFrom | our dataset → question - answers                                                          |      1 |
| transformedFrom | transformedFrom | the original FUNSD documents → FUNSD                                                      |      1 |
| transformedFrom | NIL             | XFUND → key - value pairs                                                                 |      2 |
| transformedFrom | NIL             | the filtered data → the data                                                              |      2 |
| transformedFrom | NIL             | the entire dataset → datapoints                                                           |      2 |
| transformedFrom | NIL             | 100 , 000 + questions → Wikipedia articles                                                |      1 |
| transformedFrom | NIL             | SQuAD → text                                                                              |      1 |
| url             | url             | SQuAD → https :/ / stanford - qa.com                                                      |      1 |
| url             | url             | NPTs → github.com / OATML / Non - Parametric - Transformers                               |      1 |
| url             | NIL             | The data → https :/ / github.com / mlco2 / impact / tree / master / data                  |      1 |
| url             | NIL             | The dataset → https :/ / stanford - qa.com                                                |      1 |
| url             | NIL             | The data → http :/ / data.statmt . org / cc-100 /                                         |      1 |
| url             | NIL             | XFUND → https :/ / aka.ms / layoutxlm                                                     |      1 |
| url             | NIL             | The pre - trained LayoutXLM model → https :/ / aka.ms / layoutxlm                         |      1 |
| usedFor         | appliedTo       | the continuous formulation → spin - glass density estimation                              |      1 |
| usedFor         | isHyponymOf     | LAMB → optimization                                                                       |      1 |
| usedFor         | isHyponymOf     | Lookahead → optimization                                                                  |      1 |
| usedFor         | usedFor         | masking matrix → NPT                                                                      |      2 |
| usedFor         | usedFor         | task - specific fine - tuning → pre - trained models                                      |      1 |
| usedFor         | usedFor         | word embeddings → unsupervised learning                                                   |      1 |
| usedFor         | usedFor         | pre - trained embeddings → our models                                                     |      1 |
| usedFor         | usedFor         | language modeling → most existing large - scale language models                           |      1 |
| usedFor         | NIL             | IF - SSL → IF - SSL                                                                       |      4 |
| usedFor         | NIL             | the stochastic feature masking → NPTs                                                     |      3 |
| usedFor         | NIL             | deep reinforcement learning → robotic manipulators                                        |      2 |
| usedFor         | NIL             | the annotation vectors → our modified attention model                                     |      2 |
| usedFor         | NIL             | simulated annealing → Langevin dynamics                                                   |      2 |
| versionOf       | transformedFrom | OpenWebText2 → OpenWebText                                                                |      1 |
| versionOf       | versionOf       | BookCorpus2 → BookCorpus                                                                  |      1 |
| versionOf       | NIL             | BookCorpus2 → BookCorpus                                                                  |      1 |
| versionOf       | NIL             | LayoutLMv2 → LayoutLM                                                                     |      1 |
| NIL             | appliedTo       | pre - trained models → image recognition                                                  |      1 |
| NIL             | appliedTo       | pre - trained models → NLP                                                                |      1 |
| NIL             | appliedTo       | the model → cross - domain knowledge                                                      |      1 |
| NIL             | appliedTo       | language models → generalization                                                          |      1 |
| NIL             | appliedTo       | LayoutXLM → multilingual document understanding                                           |      1 |
| NIL             | architecture    | GNNs → self - attention                                                                   |      2 |
| NIL             | architecture    | NPTs → CNN encoder                                                                        |      2 |
| NIL             | architecture    | NPTs → linear patching encoder                                                            |      2 |
| NIL             | architecture    | GPT-2 → GPT-3                                                                             |      1 |
| NIL             | architecture    | GPT-3 → GPT-2                                                                             |      1 |
| NIL             | benchmarkFor    | a dataset → reading comprehension                                                         |      1 |
| NIL             | benchmarkFor    | a multilingual parallel corpus → machine translation                                      |      1 |
| NIL             | benchmarkFor    | real document datasets → multilingual VrDU                                                |      1 |
| NIL             | benchmarkFor    | XFUND → multilingual Form Understanding                                                   |      1 |
| NIL             | benchmarkFor    | FUNSD → multilingual Form Understanding                                                   |      1 |
| NIL             | citation        | The classifier → Davidson et al . ( 2017 )                                                |      2 |
| NIL             | citation        | energy - based models → 5                                                                 |      2 |
| NIL             | citation        | large - scale models → 1                                                                  |      1 |
| NIL             | citation        | large - scale models → 2                                                                  |      1 |
| NIL             | citation        | Reinforcement Learning → 16                                                               |      1 |
| NIL             | coreference     | geolocated tweets → the tweets                                                            |      1 |
| NIL             | coreference     | language modeling → language modeling                                                     |      1 |
| NIL             | coreference     | YouTube Subtitles → these datasets                                                        |      1 |
| NIL             | coreference     | BookCorpus → BookCorpus                                                                   |      1 |
| NIL             | coreference     | the model → GPT-2                                                                         |      1 |
| NIL             | evaluatedOn     | The classifier → black - aligned tweets                                                   |      2 |
| NIL             | evaluatedOn     | the classifier → black - aligned tweets                                                   |      2 |
| NIL             | evaluatedOn     | IF - SSL → CIFAR-100                                                                      |      2 |
| NIL             | evaluatedOn     | NPT → tabular data                                                                        |      2 |
| NIL             | evaluatedOn     | NPT → CIFAR-10                                                                            |      2 |
| NIL             | generatedBy     | Protein → minibatching                                                                    |      2 |
| NIL             | generatedBy     | our dataset → curating                                                                    |      1 |
| NIL             | generatedBy     | our dataset → crowdsourcing                                                               |      1 |
| NIL             | generatedBy     | our dataset → the dependency tree path features                                           |      1 |
| NIL             | generatedBy     | tweets → a crowdsourced hate speech lexicon                                               |      1 |
| NIL             | hasInstanceType | the black - aligned corpus → tweets                                                       |      3 |
| NIL             | hasInstanceType | the black - aligned dataset → tweets                                                      |      1 |
| NIL             | hasInstanceType | XFUND → key - value labeled forms                                                         |      1 |
| NIL             | isBasedOn       | a latent variable model → neural networks                                                 |      1 |
| NIL             | isComparedTo    | NPT → Random Forests                                                                      |      4 |
| NIL             | isComparedTo    | NPT → Gradient Boosting Trees                                                             |      4 |
| NIL             | isComparedTo    | black - aligned tweets → white - aligned tweets                                           |      2 |
| NIL             | isComparedTo    | NPT → XGBoost                                                                             |      2 |
| NIL             | isComparedTo    | NPT → CatBoost                                                                            |      2 |
| NIL             | isHyponymOf     | NPT → two popular state - of - the - art boosting methods                                 |      2 |
| NIL             | isHyponymOf     | OWT2 → a generalized web scrape dataset                                                   |      1 |
| NIL             | isHyponymOf     | PubMed Central → datasets                                                                 |      1 |
| NIL             | isHyponymOf     | PubMed Abstracts → datasets                                                               |      1 |
| NIL             | isHyponymOf     | ArXiv → datasets                                                                          |      1 |
| NIL             | isPartOf        | Resnext → The network                                                                     |      2 |
| NIL             | isPartOf        | AAE → the dataset                                                                         |      1 |
| NIL             | isPartOf        | GitHub → datasets                                                                         |      1 |
| NIL             | isPartOf        | the output dataset → the constituent datasets                                             |      1 |
| NIL             | isPartOf        | smaller sets → the data                                                                   |      1 |
| NIL             | processed       | semi - supervised learning → the raw data samples                                         |      1 |
| NIL             | processed       | unsupervised learning → the entire dataset                                                |      1 |
| NIL             | processed       | unsupervised learning → all samples                                                       |      1 |
| NIL             | processed       | Semi - supervised learning → the large images                                             |      1 |
| NIL             | processed       | deep reinforcement learning → raw ( pixel ) images                                        |      1 |
| NIL             | size            | BookCorpus → 11 , 038 books                                                               |      1 |
| NIL             | size            | test datapoints → 398                                                                     |      1 |
| NIL             | size            | medium and large datasets → 45 730 and 11 000 000 datapoints                              |      1 |
| NIL             | sourcedFrom     | Machine learning models → Facebook                                                        |      1 |
| NIL             | sourcedFrom     | YouTube Subtitles → Pip                                                                   |      1 |
| NIL             | sourcedFrom     | YouTube Subtitles → GitHub                                                                |      1 |
| NIL             | sourcedFrom     | jusText → Common Crawl                                                                    |      1 |
| NIL             | trainedOn       | NPTs → datapoints                                                                         |      3 |
| NIL             | trainedOn       | NPTs → the entire dataset                                                                 |      2 |
| NIL             | trainedOn       | NPTs → training data                                                                      |      2 |
| NIL             | trainedOn       | models → our dataset                                                                      |      1 |
| NIL             | trainedOn       | classifiers → a corpus                                                                    |      1 |
| NIL             | transformedFrom | WikiQA → Wikipedia passages                                                               |      1 |
| NIL             | transformedFrom | SQuAD → Wikipedia passages                                                                |      1 |
| NIL             | transformedFrom | tweets → Hatebase                                                                         |      1 |
| NIL             | transformedFrom | each dataset → tweets                                                                     |      1 |
| NIL             | transformedFrom | tweets → small , ad hoc sets of keywords                                                  |      1 |
| NIL             | url             | Stan - ford Question Answering Dataset v1.0 → https :/ / stanford - qa.com                |      1 |
| NIL             | usedFor         | normalizing flows → the SK model                                                          |      4 |
| NIL             | usedFor         | Gaussian Processes → Deep Gaussian Processes                                              |      2 |
| NIL             | usedFor         | semi - supervised learning → NPTs                                                         |      2 |
| NIL             | usedFor         | transductive learning → NPTs                                                              |      2 |
| NIL             | usedFor         | pretraining → NPT                                                                         |      2 |
