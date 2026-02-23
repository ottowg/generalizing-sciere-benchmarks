# Cross-Dataset Annotation Comparison: Sentence-BERT & FinBERT (GSAP vs SciER)

**Generated:** 2026-02-22 22:40:07

This report compares gold annotations for two papers that appear in both the **GSAP** and **SciER** datasets: *Sentence-BERT* and *FinBERT*. Because SciER annotates only a subset of sentences, the comparison is done at three levels:

1. **Raw** — all annotations in each dataset's native label scheme
2. **Unified** — after applying each dataset's unification mapping
3. **Reduced** — unified annotations restricted to the common sentences (sentences whose text appears in both GSAP and SciER)

The confusion matrix in Section 3 uses partial span matching (gsaphub `partial`) to align entities on the common sentences.

## Sentence-BERT

### 1. Raw Annotations (native label scheme)

GSAP: **223** sentences, **628** entities, **381** relations  
SciER: **98** sentences, **322** entities, **164** relations

#### GSAP Entity Types (raw)

| Label             |   Count |
|:------------------|--------:|
| Method            |     152 |
| MLModel           |     132 |
| DatasetGeneric    |      85 |
| ReferenceLink     |      63 |
| Task              |      60 |
| Dataset           |      58 |
| ModelArchitecture |      37 |
| MLModelGeneric    |      36 |
| DataSource        |       5 |

#### GSAP Relation Types (raw)

| Label           |   Count |
|:----------------|--------:|
| usedFor         |      57 |
| evaluatedOn     |      52 |
| citation        |      49 |
| appliedTo       |      38 |
| isComparedTo    |      36 |
| coreference     |      31 |
| architecture    |      29 |
| trainedOn       |      23 |
| isPartOf        |      19 |
| benchmarkFor    |      15 |
| transformedFrom |      12 |
| hasInstanceType |       6 |
| isBasedOn       |       5 |
| sourcedFrom     |       5 |
| isHyponymOf     |       3 |
| size            |       1 |

#### SciER Entity Types (raw)

| Label   |   Count |
|:--------|--------:|
| Method  |     181 |
| Task    |      74 |
| Dataset |      67 |

#### SciER Relation Types (raw)

| Label          |   Count |
|:---------------|--------:|
| Used-For       |      52 |
| Compare-With   |      37 |
| Evaluated-With |      21 |
| Trained-With   |      16 |
| Synonym-Of     |      11 |
| Part-Of        |      11 |
| Benchmark-For  |       9 |
| SubClass-Of    |       4 |
| SubTask-Of     |       3 |

### 2. Unified Annotations

GSAP: **442** entities, **202** relations  
SciER: **322** entities, **164** relations

#### Entity Types (unified)

| Label   |   GSAP |   SciER |
|:--------|-------:|--------:|
| Method  |    338 |     181 |
| Dataset |     58 |      67 |
| Task    |     46 |      74 |

#### Relation Types (unified)

| Label              |   GSAP |   SciER |
|:-------------------|-------:|--------:|
| usedFor            |     74 |      11 |
| appliedTo          |     28 |      52 |
| isComparedTo       |     33 |      37 |
| trainedEvaluatedOn |     30 |      37 |
| coreference        |     23 |      11 |
| isHyponymOf        |      9 |       7 |
| benchmarkFor       |      5 |       9 |

### 3. Common Sentences & Confusion Analysis

Sentence matching by normalised text content:  
- **82** sentences in common  
- **141** sentences only in GSAP  
- **16** sentences only in SciER

On common sentences —  
GSAP: **258** entities, **146** relations  
SciER: **248** entities, **132** relations

### 4. Entity Label Confusion Matrix (unified labels, common sentences)

Built on the **unified** label scheme (Dataset / Method / Task) restricted to the sentences shared between both datasets. Rows = GSAP labels, Columns = SciER labels. NIL = entity present in one dataset with no partially-overlapping span in the other.

| GSAP \ SciER   |   Dataset |   Method |   Task |   NIL |
|:---------------|----------:|---------:|-------:|------:|
| Dataset        |        36 |        0 |      0 |     0 |
| Method         |         0 |      142 |     25 |    27 |
| Task           |         0 |        0 |     20 |     8 |
| NIL            |         5 |        6 |      8 |     0 |


**Dataset → Dataset** (36 total, up to 5 random):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `Multi - Genre NLI dataset` | `MultiGenre NLI` | InferSent ( Conneau et al . , 2017 ) uses labeled data of the Stanford Natural Language Inference dataset ( Bowman et al . , 2015 ) and the Multi - Genre NLI dataset ( Williams et al . , 2018 ) to train a siamese BiLSTM network with max - pooling over the output . |
| `Argument Facet Similarity` | `Argument Facet Similarity` | The paper is structured in the following way : Section 3 presents SBERT , section 4 evaluates SBERT on common STS tasks and on the challenging Argument Facet Similarity ( AFS ) corpus ( Misra et al . , 2016 ) . |
| `Argument Facet Similarity` | `Argument Facet Similarity` | We evaluate SBERT on the Argument Facet Similarity ( AFS ) corpus by Misra et al . ( 2016 ) . |
| `NLI` | `NLI` | We experimented with two setups : Only training on STSb , and first training on NLI , then training on STSb . |
| `STSb` | `STSb` | We experimented with two setups : Only training on STSb , and first training on NLI , then training on STSb . |

**Method → Method** (142 total, up to 5 random):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `BERT` | `BERT` | Using this setup , BERT set a new state - of - the - art performance on the Semantic Textual Semilarity ( STS ) benchmark ( Cer et al . , 2017 ) . |
| `Universal Sentence Encoder` | `Universal Sentence Encoder .` | On seven Semantic Textual Similarity ( STS ) tasks , SBERT achieves an improvement of 11.7 points compared to InferSent and 5. 5 points compared to Universal Sentence Encoder . |
| `Universal Sentence Encoder` | `Universal Sentence Encoder` | On a GPU , it is about 9 % faster than InferSent and about 55 % faster than Universal Sentence Encoder . |
| `InferSent` | `InferSent` | We fine - tune SBERT on NLI data , which creates sentence embeddings that significantly outperform other state - of - the - art sentence embedding methods like InferSent ( Conneau et al . , 2017 ) and Universal Sentence Encoder ( Cer et al . , 2018 ) . |
| `regression objective function` | `regression objective function` | For the regression objective function , we train on the training set of the STS benchmark dataset . |

**Method → Task** (25 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `semantically meaningful sentence` | `sentence embeddings` | In this publication , we present Sentence - BERT ( SBERT ) , a modification of the pretrained BERT network that use siamese and triplet network structures to derive semantically meaningful sentence embeddings that can be compared using cosine - similarity . |
| `other state - of - the - art sentence embeddings methods` | `sentence embeddings` | We evaluate SBERT and SRoBERTa on common STS tasks and transfer learning tasks , where it outperforms other state - of - the - art sentence embeddings methods . 1 |
| `semantically meaningful sentence` | `sentence embeddings` | In this publication , we present Sentence - BERT ( SBERT ) , a modification of the BERT network using siamese and triplet networks that is able to derive semantically meaningful sentence embeddings 2. |
| `fixedsize sentence` | `sentence embeddings` | Researchers have started to input individual sentences into BERT and to derive fixedsize sentence embeddings . |
| `rather bad sentence` | `sentence embeddings` | As we will show , this common practice yields rather bad sentence embeddings , often worse than averaging GloVe embeddings ( Pennington et al . , 2014 ) . |
| `GloVe` | `averaging GloVe embeddings` | As we will show , this common practice yields rather bad sentence embeddings , often worse than averaging GloVe embeddings ( Pennington et al . , 2014 ) . |
| `sentence` | `sentence embedding` | We fine - tune SBERT on NLI data , which creates sentence embeddings that significantly outperform other state - of - the - art sentence embedding methods like InferSent ( Conneau et al . , 2017 ) and Universal Sentence Encoder ( Cer et al . , 2018 ) . |
| `sentence` | `sentence embeddings` | On SentEval ( Conneau and Kiela , 2018 ) , an evaluation toolkit for sentence embeddings , we achieve an improvement of 2. 1 and 2. 6 points , respectively . |
| `stateof - the - art sentence embedding methods` | `sentence embedding` | We first introduce BERT , then , we discuss stateof - the - art sentence embedding methods . |
| `independent sentence` | `sentence embeddings` | A large disadvantage of the BERT network structure is that no independent sentence embeddings are computed , which makes it difficult to derive sentence embeddings from BERT . |
| `sentence` | `sentence embeddings` | A large disadvantage of the BERT network structure is that no independent sentence embeddings are computed , which makes it difficult to derive sentence embeddings from BERT . |
| `sentence` | `sentence embeddings` | In this publication , we use the pre - trained BERT and RoBERTa network and only fine - tune it to yield useful sentence embeddings . |
| `comparable sentence embedding methods` | `sentence embedding` | This reduces significantly the needed training time : SBERT can be tuned in less than 20 minutes , while yielding better results than comparable sentence embedding methods . |
| `fixed sized sentence` | `sentence embedding` | SBERT adds a pooling operation to the output of BERT / RoBERTa to derive a fixed sized sentence embedding . |
| `produced sentence` | `sentence embeddings` | In order to fine - tune BERT / RoBERTa , we create siamese and triplet networks ( Schroff et al . , 2015 ) to update the weights such that the produced sentence embeddings are semantically meaningful and can be compared with cosine - similarity . |
| `sentence` | `generating sentence embeddings` | While RoBERTa was able to improve the performance for several supervised tasks , we only observe minor difference between SBERT and SRoBERTa for generating sentence embeddings . |
| `Sentence` | `Sentence embeddings` | Sentence embeddings are used as features for a logistic regression classifier . |
| `sentence` | `sentence embeddings` | However , SentEval can still give an impression on the quality of our sentence embeddings for various tasks . |
| `sentence` | `sentence embeddings` | It appears that the sentence embeddings from SBERT capture well sentiment information : We observe large improvements for all sentiment tasks ( MR , CR , and SST ) from SentEval in comparison to InferSent and Universal Sentence Encoder . |
| `sentence` | `sentence embeddings` | For the STS tasks , we used cosine - similarity to estimate the similarities between sentence embeddings . |
| `sentence` | `sentence embeddings` | In contrast , SentEval fits a logistic regression classifier to the sentence embeddings . |
| `sentence` | `sentence embeddings` | We conclude that average BERT embeddings / CLS - token output from BERT return sentence embeddings that are infeasible to be used with cosinesimilarity or with Manhatten / Euclidean distance . |
| `sentence` | `sentence embeddings` | However , using the described fine - tuning setup with a siamese network structure on NLI datasets yields sentence embeddings that achieve a new state - of - the - art for the SentEval toolkit . |
| `sentence embeddings u and v` | `sentence embeddings` | At inference , when predicting similarities for the STS benchmark dataset , only the sentence embeddings u and v are used in combination with cosine - similarity . |
| `sentence` | `sentence embeddings` | Average GloVe embeddings is obviously by a large margin the fastest method to compute sentence embeddings . |

**Method → NIL** (27 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `RoBERTa` | `—` | and RoBERTa ( Liu et al . , 2019 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `pretrained BERT network` | `—` | In this publication , we present Sentence - BERT ( SBERT ) , a modification of the pretrained BERT network that use siamese and triplet network structures to derive semantically meaningful sentence embeddings that can be compared using cosine - similarity . |
| `siamese and triplet network structures` | `—` | In this publication , we present Sentence - BERT ( SBERT ) , a modification of the pretrained BERT network that use siamese and triplet network structures to derive semantically meaningful sentence embeddings that can be compared using cosine - similarity . |
| `modification of the BERT network` | `—` | In this publication , we present Sentence - BERT ( SBERT ) , a modification of the BERT network using siamese and triplet networks that is able to derive semantically meaningful sentence embeddings 2. |
| `siamese and triplet networks` | `—` | In this publication , we present Sentence - BERT ( SBERT ) , a modification of the BERT network using siamese and triplet networks that is able to derive semantically meaningful sentence embeddings 2. |
| `[ CLS ] token` | `—` | The most commonly used approach is to average the BERT output layer ( known as BERT embeddings ) or by using the output of the first token ( the [ CLS ] token ) . |
| `BERT` | `—` | The complexity for finding the most similar sentence pair in a collection of 10 , 000 sentences is reduced from 65 hours with BERT to the computation of 10 , 000 sentence embeddings ( ~5 seconds with SBERT ) and computing cosinesimilarity ( ~0.01 seconds ) . |
| `10 , 000 sentence` | `—` | The complexity for finding the most similar sentence pair in a collection of 10 , 000 sentences is reduced from 65 hours with BERT to the computation of 10 , 000 sentence embeddings ( ~5 seconds with SBERT ) and computing cosinesimilarity ( ~0.01 seconds ) . |
| `SBERT` | `—` | The complexity for finding the most similar sentence pair in a collection of 10 , 000 sentences is reduced from 65 hours with BERT to the computation of 10 , 000 sentence embeddings ( ~5 seconds with SBERT ) and computing cosinesimilarity ( ~0.01 seconds ) . |
| `other state - of - the - art sentence embedding methods` | `—` | We fine - tune SBERT on NLI data , which creates sentence embeddings that significantly outperform other state - of - the - art sentence embedding methods like InferSent ( Conneau et al . , 2017 ) and Universal Sentence Encoder ( Cer et al . , 2018 ) . |
| `other state - of - the - art sentence embedding methods` | `—` | In section 7 , we compare the computational efficiency of SBERT sentence embeddings in contrast to other state - of - the - art sentence embedding methods . |
| `fixed sized vector` | `—` | To bypass this limitations , researchers passed single sentences through BERT and then derive a fixed sized vector by either averaging the outputs ( similar to average word embeddings ) or by using the output of the special CLS token ( for example : May et al . ( 2019 ) ; Zhang et al . ( 2019 ) ; Qiao et al . ( 2019 ) ) . |
| `averaging the outputs` | `—` | To bypass this limitations , researchers passed single sentences through BERT and then derive a fixed sized vector by either averaging the outputs ( similar to average word embeddings ) or by using the output of the special CLS token ( for example : May et al . ( 2019 ) ; Zhang et al . ( 2019 ) ; Qiao et al . ( 2019 ) ) . |
| `using the output of the special CLS token` | `—` | To bypass this limitations , researchers passed single sentences through BERT and then derive a fixed sized vector by either averaging the outputs ( similar to average word embeddings ) or by using the output of the special CLS token ( for example : May et al . ( 2019 ) ; Zhang et al . ( 2019 ) ; Qiao et al . ( 2019 ) ) . |
| `unsupervised methods` | `—` |   Conneau et al . showed , that InferSent consistently outperforms unsupervised methods like SkipThought . |
| `fine - tune` | `—` | In this publication , we use the pre - trained BERT and RoBERTa network and only fine - tune it to yield useful sentence embeddings . |
| `pooling operation` | `—` | SBERT adds a pooling operation to the output of BERT / RoBERTa to derive a fixed sized sentence embedding . |
| `fine - tune` | `—` | In order to fine - tune BERT / RoBERTa , we create siamese and triplet networks ( Schroff et al . , 2015 ) to update the weights such that the produced sentence embeddings are semantically meaningful and can be compared with cosine - similarity . |
| `siamese and triplet networks` | `—` | In order to fine - tune BERT / RoBERTa , we create siamese and triplet networks ( Schroff et al . , 2015 ) to update the weights such that the produced sentence embeddings are semantically meaningful and can be compared with cosine - similarity . |
| `fine - tuning mechanism` | `—` | Using the described siamese network structure and fine - tuning mechanism substantially improves the correlation , outperforming both InferSent and Universal Sentence Encoder substantially . |
| `supervised STS` | `—` | The STS benchmark ( STSb ) ( Cer et al . , 2017 ) provides is a popular dataset to evaluate supervised STS systems . |
| `Unsupervised methods` | `—` | Unsupervised methods like tf - idf , average GloVe embeddings or InferSent perform rather badly on this dataset with low scores . |
| `fine - tuning` | `—` | Here , we think fine - tuning BERT as described by Devlin et al . ( 2018 ) for new tasks is the more suitable method , as it updates all layers of the BERT network . |
| `using the CLStoken output` | `—` | Average BERT embeddings or using the CLStoken output from a BERT network achieved bad results for various STS tasks ( Table 1 ) , worse than average GloVe embeddings . |
| `described fine - tuning setup` | `—` | However , using the described fine - tuning setup with a siamese network structure on NLI datasets yields sentence embeddings that achieve a new state - of - the - art for the SentEval toolkit . |
| `smart batching` | `—` | There , SBERT with smart batching is about 9 % faster than InferSent and about 55 % faster than Universal Sentence Encoder . |
| `siamese / triplet network architecture` | `—` | SBERT fine - tunes BERT in a siamese / triplet network architecture . |

**Task → Task** (20 total, up to 5 random):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `semantic similarity search` | `semantic similarity search` | The construction of BERT makes it unsuitable for semantic similarity search as well as for unsupervised tasks like clustering . |
| `semantic textual similarity` | `sentence - pair regression` | and RoBERTa ( Liu et al . , 2019 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `STS` | `STS` | We evaluate SBERT and SRoBERTa on common STS tasks and transfer learning tasks , where it outperforms other state - of - the - art sentence embeddings methods . 1 |
| `semantic similarity search` | `semantic similarity` | These similarity measures can be performed extremely efficient on modern hardware , allowing SBERT to be used for semantic similarity search as well as for clustering . |
| `Semantic Textual Similarity` | `Semantic Textual Similarity` | On seven Semantic Textual Similarity ( STS ) tasks , SBERT achieves an improvement of 11.7 points compared to InferSent and 5. 5 points compared to Universal Sentence Encoder . |

**Task → NIL** (8 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `sentence - pair regression` | `—` | and RoBERTa ( Liu et al . , 2019 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `STS` | `—` | and RoBERTa ( Liu et al . , 2019 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `unsupervised tasks` | `—` | The construction of BERT makes it unsuitable for semantic similarity search as well as for unsupervised tasks like clustering . |
| `clustering` | `—` | The construction of BERT makes it unsuitable for semantic similarity search as well as for unsupervised tasks like clustering . |
| `clustering` | `—` | These similarity measures can be performed extremely efficient on modern hardware , allowing SBERT to be used for semantic similarity search as well as for clustering . |
| `supervised tasks` | `—` | While RoBERTa was able to improve the performance for several supervised tasks , we only observe minor difference between SBERT and SRoBERTa for generating sentence embeddings . |
| `classification` | `—` | The objective function ( classification vs. regression ) depends on the annotated dataset . |
| `regression` | `—` | The objective function ( classification vs. regression ) depends on the annotated dataset . |

**NIL → Dataset** (5 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `—` | `STS benchmark` | We use the STS tasks 2 0 1 2 - 2 0 1 6 ( Agirre et al. , 2 0 1 2 ( Agirre et al. , , 2 0 1 3 ( Agirre et al. , , 2 0 1 4 ( Agirre et al. , , 2 0 1 5 ( Agirre et al. , , 2 0 1 6 , the STS benchmark ( Cer et al. , 2 0 1 7 ) , and the SICK - Relatedness dataset ( Marelli et al. , 2 0 1 4 ) . |
| `—` | `NLI datasets` | SBERT was fine - tuned on the STSb dataset , SBERT - NLI was pretrained on the NLI datasets , then fine - tuned on the STSb dataset . |
| `—` | `STS` | STS data is usually descriptive , while AFS data are argumentative excerpts from dialogs . |
| `—` | `NLI datasets` | However , using the described fine - tuning setup with a siamese network structure on NLI datasets yields sentence embeddings that achieve a new state - of - the - art for the SentEval toolkit . |
| `—` | `NLI data` | When trained with the classification objective function on NLI data , the pooling strategy has a rather minor impact . |

**NIL → Method** (6 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `—` | `BERT` | BERT ( Devlin et al. , 2 0 1 8) and RoBERTa ( Liu et al. , 2 0 1 9 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `—` | `RoBERTa` | BERT ( Devlin et al. , 2 0 1 8) and RoBERTa ( Liu et al. , 2 0 1 9 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `—` | `BERT embeddings` | The most commonly used approach is to average the BERT output layer ( known as BERT embeddings ) or by using the output of the first token ( the [ CLS ] token ) . |
| `—` | `BERT` | The complexity for finding the most similar sentence pair in a collection of 1 0 , 0 0 0 sentences is reduced from 6 5 hours with BERT to the computation of 1 0 , 0 0 0 sentence embeddings ( ~ 5 seconds with SBERT ) and computing cosinesimilarity ( ~ 0 . 0 1 seconds ) . |
| `—` | `SBERT` | The complexity for finding the most similar sentence pair in a collection of 1 0 , 0 0 0 sentences is reduced from 6 5 hours with BERT to the computation of 1 0 , 0 0 0 sentence embeddings ( ~ 5 seconds with SBERT ) and computing cosinesimilarity ( ~ 0 . 0 1 seconds ) . |
| `—` | `cosine - similarity` | In order to fine - tune BERT / RoBERTa , we create siamese and triplet networks ( Schroff et al. , 2 0 1 5 ) to update the weights such that the produced sentence embeddings are semantically meaningful and can be compared with cosine - similarity . |

**NIL → Task** (8 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `—` | `semantic textual similarity` | BERT ( Devlin et al. , 2 0 1 8) and RoBERTa ( Liu et al. , 2 0 1 9 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `—` | `STS` | BERT ( Devlin et al. , 2 0 1 8) and RoBERTa ( Liu et al. , 2 0 1 9 ) has set a new state - of - the - art performance on sentence - pair regression tasks like semantic textual similarity ( STS ) . |
| `—` | `sentence embeddings` | The complexity for finding the most similar sentence pair in a collection of 1 0 , 0 0 0 sentences is reduced from 6 5 hours with BERT to the computation of 1 0 , 0 0 0 sentence embeddings ( ~ 5 seconds with SBERT ) and computing cosinesimilarity ( ~ 0 . 0 1 seconds ) . |
| `—` | `cosinesimilarity` | The complexity for finding the most similar sentence pair in a collection of 1 0 , 0 0 0 sentences is reduced from 6 5 hours with BERT to the computation of 1 0 , 0 0 0 sentence embeddings ( ~ 5 seconds with SBERT ) and computing cosinesimilarity ( ~ 0 . 0 1 seconds ) . |
| `—` | `NLI` | We fine - tune SBERT on NLI data , which creates sentence embeddings that significantly outperform other state - of - the - art sentence embedding methods like InferSent ( Conneau et al. , 2 0 1 7 ) and Universal Sentence Encoder . |
| `—` | `NLP` | BERT ( Devlin et al. , 2 0 1 8 ) is a pre - trained transformer network ( Vaswani et al. , 2 0 1 7 ) , which set for various NLP tasks new state - of - the - art results , including question answering , sentence classification , and sentence - pair regression . |
| `—` | `STS` | Average BERT embeddings or using the CLStoken output from a BERT network achieved bad results for various STS tasks ( Table 1 ) , worse than average GloVe embeddings . |
| `—` | `STS` | The performance for seven STS tasks was below the performance of average GloVe embeddings . |

## FinBERT

### 1. Raw Annotations (native label scheme)

GSAP: **296** sentences, **758** entities, **444** relations  
SciER: **73** sentences, **207** entities, **98** relations

#### GSAP Entity Types (raw)

| Label             |   Count |
|:------------------|--------:|
| MLModelGeneric    |     159 |
| Method            |     144 |
| DatasetGeneric    |     127 |
| MLModel           |      98 |
| Task              |      75 |
| ModelArchitecture |      73 |
| ReferenceLink     |      54 |
| Dataset           |      21 |
| URL               |       5 |
| DataSource        |       2 |

#### GSAP Relation Types (raw)

| Label           |   Count |
|:----------------|--------:|
| usedFor         |      72 |
| trainedOn       |      58 |
| appliedTo       |      48 |
| coreference     |      44 |
| architecture    |      43 |
| isPartOf        |      35 |
| evaluatedOn     |      34 |
| isComparedTo    |      32 |
| citation        |      23 |
| isHyponymOf     |      22 |
| isBasedOn       |      12 |
| benchmarkFor    |      10 |
| url             |       5 |
| transformedFrom |       3 |
| sourcedFrom     |       2 |
| size            |       1 |

#### SciER Entity Types (raw)

| Label   |   Count |
|:--------|--------:|
| Method  |     145 |
| Task    |      45 |
| Dataset |      17 |

#### SciER Relation Types (raw)

| Label          |   Count |
|:---------------|--------:|
| Used-For       |      35 |
| Compare-With   |      20 |
| SubClass-Of    |      12 |
| Part-Of        |      10 |
| Synonym-Of     |       7 |
| SubTask-Of     |       5 |
| Evaluated-With |       3 |
| Benchmark-For  |       3 |
| Trained-With   |       3 |

### 2. Unified Annotations

GSAP: **487** entities, **203** relations  
SciER: **207** entities, **98** relations

#### Entity Types (unified)

| Label   |   GSAP |   SciER |
|:--------|-------:|--------:|
| Method  |    396 |     145 |
| Task    |     71 |      45 |
| Dataset |     20 |      17 |

#### Relation Types (unified)

| Label              |   GSAP |   SciER |
|:-------------------|-------:|--------:|
| usedFor            |     81 |      10 |
| appliedTo          |     38 |      35 |
| isComparedTo       |     23 |      20 |
| isHyponymOf        |     23 |      17 |
| coreference        |     26 |       7 |
| trainedEvaluatedOn |      9 |       6 |
| benchmarkFor       |      3 |       3 |

### 3. Common Sentences & Confusion Analysis

Sentence matching by normalised text content:  
- **62** sentences in common  
- **232** sentences only in GSAP  
- **11** sentences only in SciER

On common sentences —  
GSAP: **203** entities, **114** relations  
SciER: **170** entities, **81** relations

### 4. Entity Label Confusion Matrix (unified labels, common sentences)

Built on the **unified** label scheme (Dataset / Method / Task) restricted to the sentences shared between both datasets. Rows = GSAP labels, Columns = SciER labels. NIL = entity present in one dataset with no partially-overlapping span in the other.

| GSAP \ SciER   |   Dataset |   Method |   Task |   NIL |
|:---------------|----------:|---------:|-------:|------:|
| Dataset        |         7 |        0 |      0 |     0 |
| Method         |         0 |      123 |      5 |    40 |
| Task           |         1 |        0 |     22 |     5 |
| NIL            |         2 |        4 |      8 |     0 |


**Dataset → Dataset** (7 total, up to 5 random):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `Financial PhraseBank` | `Financial PhraseBank` | Since our data , Financial PhraseBank suffers from label imbalance ( almost 60 % of all sentences are neutral ) , this gives another good measure of the classification performance . |
| `Financial Phrasebank` | `Financial Phrasebank` | We think that the last explanation is the likeliest , because for the subset of Financial Phrasebank that all of the annotators agree on the result , accuracy of Vanilla BERT is already 0. 96 . |
| `Financial PhraseBank` | `Financial PhraseBank` | For that , sentiment of a sentence from a financial news article towards the financial actor depicted in the sentence will be tried to be predicted , using the Financial PhraseBank created by Malo et al . ( 2014 ) [ 17 ] and FiQA Task 1 sentiment scoring dataset [ 15 ] . |
| `FiQA Task 1` | `FiQA Task 1 sentiment scoring` | For that , sentiment of a sentence from a financial news article towards the financial actor depicted in the sentence will be tried to be predicted , using the Financial PhraseBank created by Malo et al . ( 2014 ) [ 17 ] and FiQA Task 1 sentiment scoring dataset [ 15 ] . |
| `SST-5` | `SST - 5` | For text classification tasks like SST-5 , it achieved state - of - the - art performance when used together with a bi - attentive classification network [ 20 ] . |

**Method → Method** (123 total, up to 5 random):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `machine learning based` | `machine learning based models` | It also handily beats the machine learning based models LPS and HSC . |
| `FinBERT` | `FinBERT` | FinBERT outperforms ULMFit , and consequently all of the other methods in all metrics . |
| `FinBERT` | `FinBERT` | For all of the measured metrics , FinBERT performs clearly the best among both the methods we implemented ourselves ( LSTM and ULMFit ) and the models reported by other papers ( LPS [ 17 ] , HSC [ 8 ] , FinSSLX [ 14 ] ) . |
| `BERT` | `BERT` | In this subsection we will describe our implementation of BERT : 1 ) how further pre - training on domain corpus is done , 2 - 3 ) how we implemented BERT for classification and regression tasks , 4 ) training strategies we used during fine - tuning to prevent catastrophic forgetting . |
| `ELMo` | `ELMo` | Unlike ELMo , with ULMFit , the whole language model is fine - tuned together with the task - specific layers . |

**Method → Task** (5 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `natural language processing ( NLP ) methods` | `natural language processing` | Hence , automated sentiment or polarity analysis of texts produced by financial actors using natural language processing ( NLP ) methods has gained popularity during the last decade [ 4 ] . |
| `NLP transfer learning methods` | `NLP transfer learning` | NLP transfer learning methods look like a promising solution to both of the challenges mentioned above , and are the focus of this thesis . |
| `any LSTM natural language processing` | `natural language processing` | Since a text is a sequence of tokens , the first choice for any LSTM natural language processing model is determining how to initially represent a single token . |
| `transfer learning` | `transfer learning` | ULMFit is a transfer learning model for down - stream NLP tasks , that make use of language model pre - training [ 5 ] . |
| `text simplification step` | `text simplification` | ULMFit also outperforms FinSSLX , which has a text simplification step as well as pre - training of word embeddings on a large financial corpus with sentiment labels . |

**Method → NIL** (40 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `pre - trained language` | `—` | This section describes previous research conducted on sentiment analysis in finance ( 2. 1 ) and text classification using pre - trained language models ( 2. 2 ) . |
| `best performing neural network architecture` | `—` |   Sohangir et al . ( 2018 ) [ 26 ] apply several generic neural network architectures to a StockTwits dataset , finding CNN as the best performing neural network architecture . |
| `fine - tuned` | `—` | One of the most important recent developments in natural language processing is the realization that a model trained for language modeling can be successfully fine - tuned for most down - stream NLP tasks with small modifications . |
| `embeddings` | `—` | Initializing embeddings for down - stream tasks with those were shown to improve performance on most tasks compared to static word embeddings such as word2vec or GloVe . |
| `bi - attentive classification network` | `—` | For text classification tasks like SST-5 , it achieved state - of - the - art performance when used together with a bi - attentive classification network [ 20 ] . |
| `fine - tuning` | `—` | ULMFit 's main idea of efficiently fine - tuning a pre - trained a language model for down - stream tasks was brought to another level with Bidirectional Encoder Representations from Transformers ( BERT ) [ 3 ] , which is also the main focus of this paper . |
| `pre - trained a language` | `—` | ULMFit 's main idea of efficiently fine - tuning a pre - trained a language model for down - stream tasks was brought to another level with Bidirectional Encoder Representations from Transformers ( BERT ) [ 3 ] , which is also the main focus of this paper . |
| `fine - tuning` | `—` | The specifics of fine - tuning BERT for text classification has not been researched thoroughly . |
| `relevant neural architectures` | `—` | In this section , we will present our BERT implementation for financial domain named as FinBERT , after giving a brief background on relevant neural architectures . |
| `recurrent neural network` | `—` | Long short - term memory ( LSTM ) is a type of recurrent neural network that allows long - term dependencies in a sequence to persist in the network by using " forget " and " update " gates . |
| `One such pre - training algorithm` | `—` | One such pre - training algorithm is GLoVe ( Global Vectors for Word Representation ) [ 22 ] . |
| `bidirectional language` | `—` | In the center of ELMo , there is a bidirectional language model with multiple LSTM layers . |
| `contextualized representations` | `—` | Once the contextualized representations are extracted , these can be used to initialize any down - stream NLP task 2 . |
| `language model pre - training` | `—` | ULMFit is a transfer learning model for down - stream NLP tasks , that make use of language model pre - training [ 5 ] . |
| `whole language` | `—` | Unlike ELMo , with ULMFit , the whole language model is fine - tuned together with the task - specific layers . |
| `fine - tuned` | `—` | Unlike ELMo , with ULMFit , the whole language model is fine - tuned together with the task - specific layers . |
| `underlying language` | `—` | The underlying language model used in ULMFit is AWD - LSTM , which uses sophisticated dropout tuning strategies to better regularize its LSTM model [ 21 ] . |
| `attention - based` | `—` | The Transformer is an attention - based architecture for modeling sequential information , that is an alternative to recurrent neural networks [ 29 ] . |
| `[ CLS ] token` | `—` | For all classification tasks , including the next sentence prediction , [ CLS ] token is used . |
| `encoder` | `—` | BERT has two versions : BERT - base , with 12 encoder layers , hidden size of 768 , 12 multi - head attention heads and 110 M parameters in total and BERT - large , with 24 encoder layers , hidden size of 1024 , 16 multi - head attention heads and 340 M parameters . |
| `encoder` | `—` | BERT has two versions : BERT - base , with 12 encoder layers , hidden size of 768 , 12 multi - head attention heads and 110 M parameters in total and BERT - large , with 24 encoder layers , hidden size of 1024 , 16 multi - head attention heads and 340 M parameters . |
| `Both of these` | `—` | Both of these models have been trained on BookCorpus [ 33 ] and English Wikipedia , which have in total more than 3 , 500 M words 3. |
| `further pre - training` | `—` | In this subsection we will describe our implementation of BERT : 1 ) how further pre - training on domain corpus is done , 2 - 3 ) how we implemented BERT for classification and regression tasks , 4 ) training strategies we used during fine - tuning to prevent catastrophic forgetting . |
| `fine - tuning` | `—` | In this subsection we will describe our implementation of BERT : 1 ) how further pre - training on domain corpus is done , 2 - 3 ) how we implemented BERT for classification and regression tasks , 4 ) training strategies we used during fine - tuning to prevent catastrophic forgetting . |
| `implementation` | `—` | For our implementation BERT , we use a dropout probability of p = 0. 1 , warm - up proportion of 0. 2 , maximum sequence length of 64 tokens , a learning rate of 2e − 5 and a mini - batch size of 64 . |
| `methods we implemented ourselves` | `—` | For all of the measured metrics , FinBERT performs clearly the best among both the methods we implemented ourselves ( LSTM and ULMFit ) and the models reported by other papers ( LPS [ 17 ] , HSC [ 8 ] , FinSSLX [ 14 ] ) . |
| `static` | `—` | LSTM classifier with ELMo embeddings improves upon LSTM with static embeddings in all of the measured metrics . |
| `it` | `—` | But it 's performance is comparable with LPS and HSC , besting them in accuracy . |
| `pre - training` | `—` | ULMFit also outperforms FinSSLX , which has a text simplification step as well as pre - training of word embeddings on a large financial corpus with sentiment labels . |
| `all of the other methods` | `—` | FinBERT outperforms ULMFit , and consequently all of the other methods in all metrics . |
| `All of the methods` | `—` | All of the methods consistently get better with more data , but ULMFit and FinBERT does better with 250 examples than LSTM classifiers do with the whole dataset . |
| `three` | `—` | We compare three models : 1 ) No further pre - training ( denoted by Vanilla BERT ) , 2 ) Further pre - training on classification training set ( denoted by FinBERT - task ) , 3 ) Further pre - training on domain corpus , TRC2 - financial ( denoted by FinBERT - domain ) . |
| `further pre - training` | `—` | We compare three models : 1 ) No further pre - training ( denoted by Vanilla BERT ) , 2 ) Further pre - training on classification training set ( denoted by FinBERT - task ) , 3 ) Further pre - training on domain corpus , TRC2 - financial ( denoted by FinBERT - domain ) . |
| `Further pre - training` | `—` | We compare three models : 1 ) No further pre - training ( denoted by Vanilla BERT ) , 2 ) Further pre - training on classification training set ( denoted by FinBERT - task ) , 3 ) Further pre - training on domain corpus , TRC2 - financial ( denoted by FinBERT - domain ) . |
| `Further pre - training` | `—` | We compare three models : 1 ) No further pre - training ( denoted by Vanilla BERT ) , 2 ) Further pre - training on classification training set ( denoted by FinBERT - task ) , 3 ) Further pre - training on domain corpus , TRC2 - financial ( denoted by FinBERT - domain ) . |
| `GU )` | `—` | For measuring the performance of the techniques against catastrophic forgetting , we try four different settings : No adjustment ( NA ) , only with slanted triangular learning rate ( STL ) , slanted triangular learning rate and gradual unfreezing ( STL + GU ) and the techniques in the previous one , together with discriminative finetuning . |
| `further pre - training` | `—` | In this paper , we implemented BERT for the financial domain by further pre - training it on a financial corpus and fine - tuning it for sentiment analysis ( FinBERT ) . |
| `fine - tuning` | `—` | In this paper , we implemented BERT for the financial domain by further pre - training it on a financial corpus and fine - tuning it for sentiment analysis ( FinBERT ) . |
| `other pre - training language` | `—` | In addition to BERT , we also implemented other pre - training language models like ELMo and ULMFit for comparison purposes . |
| `previous state - of - the art` | `—` | ULMFit , further pre - trained on a financial corpus , beat the previous state - of - the art for the classification task , only to a smaller degree than BERT . |

**Task → Dataset** (1 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `sentiment scoring` | `FiQA Task 1 sentiment scoring` | For that , sentiment of a sentence from a financial news article towards the financial actor depicted in the sentence will be tried to be predicted , using the Financial PhraseBank created by Malo et al . ( 2014 ) [ 17 ] and FiQA Task 1 sentiment scoring dataset [ 15 ] . |

**Task → Task** (22 total, up to 5 random):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `classification` | `classification` | In this subsection we will describe our implementation of BERT : 1 ) how further pre - training on domain corpus is done , 2 - 3 ) how we implemented BERT for classification and regression tasks , 4 ) training strategies we used during fine - tuning to prevent catastrophic forgetting . |
| `sentiment analysis` | `sentiment analysis` | In this paper , we implemented BERT for the financial domain by further pre - training it on a financial corpus and fine - tuning it for sentiment analysis ( FinBERT ) . |
| `text classification` | `text classification` | The specifics of fine - tuning BERT for text classification has not been researched thoroughly . |
| `sentiment analysis in finance` | `sentiment analysis` | This section describes previous research conducted on sentiment analysis in finance ( 2. 1 ) and text classification using pre - trained language models ( 2. 2 ) . |
| `transfer learning` | `transfer learning` | ULMFit ( Universal Language Model Fine - tuning ) [ 5 ] was the first paper to achieve true transfer learning for NLP , as using novel techniques such as discriminative fine - tuning , slanted triangular learning rates and gradual unfreezing . |

**Task → NIL** (5 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `sentiment or polarity analysis` | `—` | Hence , automated sentiment or polarity analysis of texts produced by financial actors using natural language processing ( NLP ) methods has gained popularity during the last decade [ 4 ] . |
| `language modeling` | `—` | One of the most important recent developments in natural language processing is the realization that a model trained for language modeling can be successfully fine - tuned for most down - stream NLP tasks with small modifications . |
| `modeling sequential information` | `—` | The Transformer is an attention - based architecture for modeling sequential information , that is an alternative to recurrent neural networks [ 29 ] . |
| `language modeling` | `—` | However it defines the language modeling task differently from ELMo and AWD - LSTM . |
| `classification` | `—` | This is the recommended practice for using BERT for any classification task [ 3 ] . |

**NIL → Dataset** (2 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `—` | `StockTwits` | Sohangir et al. ( 2 0 1 8) [ 2 6 ] apply several generic neural network architectures to a StockTwits dataset , finding CNN as the best performing neural network architecture . |
| `—` | `English Wikipedia` | Both of these models have been trained on BookCorpus [ 3 3 ] and English Wikipedia , which have in total more than 3, 5 0 0 M words 3 . |

**NIL → Method** (4 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `—` | `LSTM` | In this section , we will present our BERT implementation for financial domain named as FinBERT , after giving a brief background on relevant neural architectures . 3. 1 . 1 LSTM . |
| `—` | `ULMFit` | Once the contextualized representations are extracted , these can be used to initialize any down - stream NLP task 2 . 3. 1 . 3 ULMFit . |
| `—` | `BERT` | Because of RNNs ' sequential nature , they are much harder to parallelize on GPUs and too many steps between far away elements in a sequence make it hard for information to persist . 3. 1 . 5 BERT . |
| `—` | `STL+GU` | For measuring the performance of the techniques against catastrophic forgetting , we try four different settings : No adjustment ( NA ) , only with slanted triangular learning rate ( STL ) , slanted triangular learning rate and gradual unfreezing ( STL+GU ) and the techniques in the previous one , together with discriminative finetuning . |

**NIL → Task** (8 total, all):

| GSAP mention | SciER mention | Sentence |
|---|---|---|
| `—` | `NLP` | We introduce FinBERT , a language model based on BERT , to tackle NLP tasks in the financial domain . |
| `—` | `natural language processing` | One of the most important recent developments in natural language processing is the realization that a model trained for language modeling can be successfully fine - tuned for most down - stream NLP tasks with small modifications . |
| `—` | `NLP` | One of the most important recent developments in natural language processing is the realization that a model trained for language modeling can be successfully fine - tuned for most down - stream NLP tasks with small modifications . |
| `—` | `NLP` | ULMFit ( Universal Language Model Fine - tuning ) [ 5 ] was the first paper to achieve true transfer learning for NLP , as using novel techniques such as discriminative fine - tuning , slanted triangular learning rates and gradual unfreezing . |
| `—` | `NLP` | These two factors enabled in to achieve state - of - the - art results in multiple NLP tasks such as , natural language inference or question answering . |
| `—` | `NLP` | Once the contextualized representations are extracted , these can be used to initialize any down - stream NLP task 2 . 3. 1 . 3 ULMFit . |
| `—` | `NLP` | ULMFit is a transfer learning model for down - stream NLP tasks , that make use of language model pre - training [ 5 ] . |
| `—` | `natural language processing` | Another possible extension can be using FinBERT for other natural language processing tasks such as named entity recognition or question answering in financial domain . |
