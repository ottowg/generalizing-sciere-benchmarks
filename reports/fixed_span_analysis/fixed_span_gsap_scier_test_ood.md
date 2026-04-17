# Fixed-Span NER + RE — GSAP on SCIER (test_ood)

**Generated:** 2026-03-16 09:30:10

## Method

In the **fixed-span experiment** the model receives the gold entity spans and only predicts a label for each span (NER) and the relations between them (RE). This isolates *label classification* from *span detection*.

**NER:** For every span the gold label is compared to the predicted label. The count confusion matrix (rows = gold, cols = predicted) shows occurrence counts; the probability matrix shows mean `prob1 / prob2` from `predicted_ner_proba`.

**RE:** Gold and predicted relations are matched by `(sub_begin, sub_end, obj_begin, obj_end)`. Unmatched gold relations are mapped to NIL predicted; unmatched predicted relations are mapped to NIL gold. Examples show the top 5 most-frequent `subject → object` texts per label pair.

**File:** `gsap_scier_test_ood.jsonl`  
**Gold NER spans:** 1295  
**NER overall accuracy:** 0.770

## NER — Count Confusion Matrix

Rows = gold labels · Columns = predicted labels

|         |   Dataset |   DatasetGeneric |   MLModel |   MLModelGeneric |   Method |   ModelArchitecture |   Task |
|:--------|----------:|-----------------:|----------:|-----------------:|---------:|--------------------:|-------:|
| Dataset |         8 |                5 |         1 |                0 |       69 |                   0 |      0 |
| Method  |         0 |                2 |         0 |               15 |      982 |                  19 |      0 |
| Task    |         0 |                0 |         0 |                0 |      187 |                   0 |      7 |

## NER — Mean Probability Confusion Matrix

Each cell: `mean_prob1 / mean_prob2` from `predicted_ner_proba`. `—` = no data.

|         | Dataset       | DatasetGeneric   | MLModel       | MLModelGeneric   | Method        | ModelArchitecture   | Task          |
|:--------|:--------------|:-----------------|:--------------|:-----------------|:--------------|:--------------------|:--------------|
| Dataset | 0.900 / 0.904 | 0.043 / 0.497    | 0.009 / 0.393 | —                | 0.164 / 0.709 | —                   | —             |
| Method  | —             | 0.006 / 0.339    | —             | 0.024 / 0.457    | 0.100 / 0.788 | 0.060 / 0.528       | —             |
| Task    | —             | —                | —             | —                | 0.093 / 0.803 | —                   | 0.352 / 0.808 |

## NER — Per-Label Accuracy

| Gold Label   |   Total |   Correct |   Accuracy |
|:-------------|--------:|----------:|-----------:|
| Method       |    1018 |       982 |      0.965 |
| Task         |     194 |         7 |      0.036 |
| Dataset      |      83 |         8 |      0.096 |

## NER — Examples (top 5 per cell)

| Gold Label   | Pred Label        | Mention Text                                      |   Freq |
|:-------------|:------------------|:--------------------------------------------------|-------:|
| Dataset      | Dataset           | Stanford Sentiment Treebank Binary                |      1 |
| Dataset      | Dataset           | SST - 2                                           |      1 |
| Dataset      | Dataset           | Text REtrieval Conference Question Classification |      1 |
| Dataset      | Dataset           | TREC                                              |      1 |
| Dataset      | Dataset           | AG's news topic classification dataset            |      1 |
| Dataset      | DatasetGeneric    | KITTI                                             |      2 |
| Dataset      | DatasetGeneric    | protein data bank                                 |      1 |
| Dataset      | DatasetGeneric    | 3DMatch                                           |      1 |
| Dataset      | DatasetGeneric    | 3DLoMatch                                         |      1 |
| Dataset      | MLModel           | U3M                                               |      1 |
| Dataset      | Method            | 3DLoMatch                                         |     15 |
| Dataset      | Method            | 3DMatch                                           |     13 |
| Dataset      | Method            | BW-DB                                             |      8 |
| Dataset      | Method            | MISATO                                            |      6 |
| Dataset      | Method            | U3M                                               |      4 |
| Method       | DatasetGeneric    | GxVAEs                                            |      1 |
| Method       | DatasetGeneric    | MAC                                               |      1 |
| Method       | MLModelGeneric    | large language models                             |      3 |
| Method       | MLModelGeneric    | deep generative models                            |      2 |
| Method       | MLModelGeneric    | VAEs                                              |      1 |
| Method       | MLModelGeneric    | GxVAEs                                            |      1 |
| Method       | MLModelGeneric    | discrete GANs                                     |      1 |
| Method       | Method            | MAC                                               |     56 |
| Method       | Method            | ICL                                               |     47 |
| Method       | Method            | GxVAEs                                            |     36 |
| Method       | Method            | NeuralMD                                          |     22 |
| Method       | Method            | maximal cliques                                   |     19 |
| Method       | ModelArchitecture | GPT                                               |      2 |
| Method       | ModelArchitecture | attention mechanism                               |      2 |
| Method       | ModelArchitecture | GemNet-OC                                         |      2 |
| Method       | ModelArchitecture | MolGAN                                            |      1 |
| Method       | ModelArchitecture | attention interaction                             |      1 |
| Task         | Method            | registration                                      |     28 |
| Task         | Method            | drug discovery                                    |      8 |
| Task         | Method            | PCR                                               |      8 |
| Task         | Method            | protein-ligand binding                            |      7 |
| Task         | Method            | carbon capture                                    |      7 |
| Task         | Task              | question type classification                      |      2 |
| Task         | Task              | topic classification                              |      2 |
| Task         | Task              | text classification                               |      1 |
| Task         | Task              | sentiment analysis                                |      1 |
| Task         | Task              | emotion classification                            |      1 |

## RE — Relation Confusion Matrix

**Gold relations:** 582  
**Predicted relations:** 4  

Rows = gold labels · Columns = predicted labels · NIL = unmatched on the respective side.

|                |   coreference |   NIL |
|:---------------|--------------:|------:|
| Benchmark-For  |             0 |    28 |
| Compare-With   |             0 |    54 |
| Evaluated-With |             0 |    49 |
| Part-Of        |             0 |   111 |
| SubClass-Of    |             0 |    73 |
| SubTask-Of     |             0 |     9 |
| Synonym-Of     |             4 |    85 |
| Trained-With   |             0 |     2 |
| Used-For       |             0 |   167 |

## RE — Per-Label Accuracy

| Gold Label     |   Total |   Correct |   Accuracy |
|:---------------|--------:|----------:|-----------:|
| Used-For       |     167 |         0 |          0 |
| Part-Of        |     111 |         0 |          0 |
| Synonym-Of     |      89 |         0 |          0 |
| SubClass-Of    |      73 |         0 |          0 |
| Compare-With   |      54 |         0 |          0 |
| Evaluated-With |      49 |         0 |          0 |
| Benchmark-For  |      28 |         0 |          0 |
| SubTask-Of     |       9 |         0 |          0 |
| Trained-With   |       2 |         0 |          0 |

## RE — Examples (top 5 per cell)

| Gold Label     | Pred Label   | Subject → Object                                                                 |   Freq |
|:---------------|:-------------|:---------------------------------------------------------------------------------|-------:|
| Benchmark-For  | NIL          | 3DLoMatch → registration                                                         |      7 |
| Benchmark-For  | NIL          | 3DMatch → registration                                                           |      6 |
| Benchmark-For  | NIL          | Stanford Sentiment Treebank Binary → sentiment analysis                          |      2 |
| Benchmark-For  | NIL          | Text REtrieval Conference Question Classification → question type classification |      2 |
| Benchmark-For  | NIL          | AG's news topic classification dataset → topic classification                    |      2 |
| Compare-With   | NIL          | GxVAEs → TRIOMPHE                                                                |      4 |
| Compare-With   | NIL          | FPFH → FCGF                                                                      |      4 |
| Compare-With   | NIL          | GxVAEs → DRAGONET                                                                |      2 |
| Compare-With   | NIL          | shallow layers → deep layers                                                     |      2 |
| Compare-With   | NIL          | GPT-J → GPT2 - XL                                                                |      2 |
| Evaluated-With | NIL          | MAC → 3DMatch                                                                    |      4 |
| Evaluated-With | NIL          | MAC → 3DLoMatch                                                                  |      4 |
| Evaluated-With | NIL          | FPFH → 3DMatch                                                                   |      3 |
| Evaluated-With | NIL          | FCGF → 3DMatch                                                                   |      3 |
| Evaluated-With | NIL          | FPFH → 3DLoMatch                                                                 |      3 |
| Part-Of        | NIL          | VAEs → GxVAEs                                                                    |      4 |
| Part-Of        | NIL          | ProfileVAE → GxVAEs                                                              |      4 |
| Part-Of        | NIL          | MolVAE → GxVAEs                                                                  |      4 |
| Part-Of        | NIL          | MAC → deep-learned methods                                                       |      4 |
| Part-Of        | NIL          | FPFH → NG                                                                        |      3 |
| SubClass-Of    | NIL          | ProfileVAE → VAEs                                                                |      3 |
| SubClass-Of    | NIL          | MolVAE → VAEs                                                                    |      3 |
| SubClass-Of    | NIL          | NeuralMD → ML                                                                    |      3 |
| SubClass-Of    | NIL          | BindingNet → multi-grained SE ( 3 ) - equivariant geometric model                |      2 |
| SubClass-Of    | NIL          | MOFDiff → coarse-grained diffusion model                                         |      2 |
| SubTask-Of     | NIL          | de novo generation → computer-aided drug discovery                               |      1 |
| SubTask-Of     | NIL          | Hit identification → drug discovery                                              |      1 |
| SubTask-Of     | NIL          | novo molecular generation → computer-aided drug discovery                        |      1 |
| SubTask-Of     | NIL          | Learning Protein-Ligand Binding Dynamics → drug discovery                        |      1 |
| SubTask-Of     | NIL          | protein-ligand binding → drug discovery                                          |      1 |
| Synonym-Of     | coreference  | Stanford Sentiment Treebank Binary → SST - 2                                     |      1 |
| Synonym-Of     | coreference  | Text REtrieval Conference Question Classification → TREC                         |      1 |
| Synonym-Of     | coreference  | AG's news topic classification dataset → AGNews                                  |      1 |
| Synonym-Of     | coreference  | Emo-Context → EmoC                                                               |      1 |
| Synonym-Of     | NIL          | molecular dynamics → MD                                                          |      3 |
| Synonym-Of     | NIL          | variational autoencoders → VAEs                                                  |      2 |
| Synonym-Of     | NIL          | large language models → LLMs                                                     |      2 |
| Synonym-Of     | NIL          | machine learning → ML                                                            |      2 |
| Synonym-Of     | NIL          | second-order ordinary differential equation → ODE                                |      2 |
| Trained-With   | NIL          | MOFDiff → BW-DB                                                                  |      2 |
| Used-For       | NIL          | MAC → registration                                                               |      9 |
| Used-For       | NIL          | MOFDiff → carbon capture                                                         |      4 |
| Used-For       | NIL          | GxVAEs → molecular generation                                                    |      3 |
| Used-For       | NIL          | NeuralMD → binding dynamics                                                      |      3 |
| Used-For       | NIL          | RANSAC → registration                                                            |      3 |
