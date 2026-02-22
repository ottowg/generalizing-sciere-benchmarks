# isHyponymOf False Predictions (Unified GSAP Test)

Dataset: gsap
Split: test
Trained on: gsap

Total predicted relations: 106
Total gold relations: 170
True positive predictions: 62
False positive predictions: 44
False negative predictions: 108

## False Positives

### Method

- Each model has L2 regularization to prevent excessive changes on weights and to minimize the variance , and uses the RMSprop algorithm with 10 −3 of learning rate and ρ = 0. 9 for optimizing its loss function , the mean squared error ( MSE ) .<br><br>[Method: "mean squared error"] -(isHyponymOf)-> [Method: "optimizing its loss function"]
- The results for test run using 5 - fold CV tasks for the optimized models are shown in Fig . 2. We found that the BiLM encoder with the LSTM layer performs slightly better than the GCN encoder , although their differences are not pronounced : the mean unsigned prediction error ( MUE ) for the BiLM / LSTM encoder model is 0. 19 kcal / mol , while the GCN model results in 0. 23 kcal / mol .<br><br>[MLModelGeneric: "BiLM encoder"] -(isHyponymOf)-> [MLModelGeneric: "optimized"]
- FTS : FTS is the frequent term sets method proposed by Man ( Man , 2014 ) .<br><br>[Method: "FTS"] -(isHyponymOf)-> [Method: "frequent term sets method"]
- VGG-16 is a commonly used architecture consisting of 13 convolutional layers of kernel size 3 × 3 and 3 dense or fully - connected layers .<br><br>[ModelArchitecture: "3 dense or fully - connected"] -(isHyponymOf)-> [MLModel: "VGG-16"]
- This interaction matrix renders the networked dynamical system ( 1 ) stable and with a support graph of interactions given by G . To generate the support graph G , we considered the realization of random graph models as Erdős - Rényi for undirected graphs , binomial random graphs for directed graphs , and real - world networks .<br><br>[ModelArchitecture: "binomial random graphs"] -(isHyponymOf)-> [MLModelGeneric: "random graph"]

### Task

- As for the pre - training task , existing works proposed several pretraining tasks , such as Mask Column Prediction ( Yin et al . , 2020 ) , Multi - choice Cloze at the Cell Level ( Wang et al . , 2021b ) and Structure Grounding ( Deng et al . , 2021 ) .<br><br>[Task: "Mask Column Prediction"] -(isHyponymOf)-> [Method: "several pretraining tasks"]
- As for the pre - training task , existing works proposed several pretraining tasks , such as Mask Column Prediction ( Yin et al . , 2020 ) , Multi - choice Cloze at the Cell Level ( Wang et al . , 2021b ) and Structure Grounding ( Deng et al . , 2021 ) .<br><br>[Task: "Multi - choice Cloze at the Cell Level"] -(isHyponymOf)-> [Method: "several pretraining tasks"]
- As for the pre - training task , existing works proposed several pretraining tasks , such as Mask Column Prediction ( Yin et al . , 2020 ) , Multi - choice Cloze at the Cell Level ( Wang et al . , 2021b ) and Structure Grounding ( Deng et al . , 2021 ) .<br><br>[Task: "Structure Grounding"] -(isHyponymOf)-> [Method: "several pretraining tasks"]

### Dataset

- XLM - R performs particularly well on low - resource languages , improving 15.7 % in XNLI accuracy for Swahili and 11.4 % for Urdu over previous XLM models .<br><br>[Dataset: "Swahili"] -(isHyponymOf)-> [Dataset: "XNLI"]
- However , if Bing , a Web search engine similar to Google , appears in the local neighbourhood of Google in the ClassiNet , and if we can propagate from Bing to its parent company Microsoft via the ClassiNet , then we will be able to predict Microsoft as a relevant feature for Google .<br><br>[DataSource: "Bing"] -(isHyponymOf)-> [Method: "Web search engine"]

## False Negatives

### Method

- Moreover , in MR and CR datasets its performance is significantly better than the second best methods ( respectively SCL and All Neigbour Expansion ) on those two datasets .<br><br>[Method: "All Neigbour Expansion"] -(isHyponymOf)-> [Method: "second best methods"]
- We compare the performance of monolingual models ( BERT ) versus multilingual models ( XLM ) on seven languages , using a BERT - BASE architecture .<br><br>[ModelArchitecture: "BERT - BASE"] -(isHyponymOf)-> [ModelArchitecture: "BERT"]
- We measure domain shift using the Spearman rank correlation coefficient ( which we refer to as Spearman or simply S ) , introduced as a general metric in ( Spearman , 1904 ) and first used as a corpus similarity metric in ( Johansson et al . , 1989 ) .<br><br>[Method: "Spearman"] -(isHyponymOf)-> [Method: "corpus similarity metric"]
- Given D u we construct a ClassiNet in two steps : ( a ) learn feature predictors h i for each vertex v i ∈ V , and ( b ) compute the conditional probabilities p ( h j ( x ) = 1|h i ( x ) = 1 ) using the labels predicted by the feature predictors h i and h j for an instance x.<br><br>[MLModelGeneric: "h j"] -(isHyponymOf)-> [MLModelGeneric: "feature predictors"]
- Although we do not have two domains in our setting , we can still apply domain adaptation methods such as the structural correspondence learning ( SCL ) proposed by Blitzer et al . ( Blitzer et al . , 2006 ) to predict missing features in a given short - text .<br><br>[Method: "structural correspondence learning"] -(isHyponymOf)-> [Method: "domain adaptation"]

### Task

- Furthermore , we examine the effectiveness of TAPEX via two fundamental downstream tasks : table - based question answering ( TableQA ) and table - based fact verification ( TableFV ) .<br><br>[Task: "table - based fact verification"] -(isHyponymOf)-> [Task: "two fundamental downstream tasks"]
- Textual entailment is similar to NLI , but restricted to binary classification ( entailment vs nonentailment ) .<br><br>[Task: "Textual entailment"] -(isHyponymOf)-> [Task: "binary classification"]
- Although for text classification purposes it is sufficient to represent short - texts in implicit feature spaces , there are numerous tasks that require explicit interpretable predictions such as query suggestion in information retrieval ( Carpineto and Romano , 2012 ) , reverse dictionary mapping ( Hill et al . , 2016b ) , and hashtag suggestion in social media ( Weston et al . , 2014 ) .<br><br>[Task: "query suggestion"] -(isHyponymOf)-> [Task: "information retrieval"]
- The structural reasoning process is associated with the executability of tables , i.e. , tables are inherently capable of supporting various reasoning operations ( e.g. , summing over a column in the table ) .<br><br>[Task: "structural reasoning"] -(isHyponymOf)-> [Task: "reasoning"]
- Furthermore , we examine the effectiveness of TAPEX via two fundamental downstream tasks : table - based question answering ( TableQA ) and table - based fact verification ( TableFV ) .<br><br>[Task: "table - based question answering"] -(isHyponymOf)-> [Task: "two fundamental downstream tasks"]

### Dataset

- Additionally , we test our algorithm on SST-2 ( Socher et al . , 2013 ) , which is a binary sentence classification task , and our results are directly comparable with prior work on the GLUE leaderboard ( Wang et al . , 2018 ) .<br><br>[Dataset: "SST-2"] -(isHyponymOf)-> [Dataset: "GLUE"]
