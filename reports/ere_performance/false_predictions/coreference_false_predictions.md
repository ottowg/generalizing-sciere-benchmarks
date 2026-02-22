# coreference False Predictions (Unified GSAP Test)

Dataset: gsap
Split: test
Trained on: gsap

Total predicted relations: 227
Total gold relations: 243
True positive predictions: 188
False positive predictions: 39
False negative predictions: 57

## False Positives

### Method

- The system , besides incorporating one or more QA models , likely makes heavy use of implicit user feedback ( e.g. , information contained in billions of clicks , the structure of web links , etc . ) , in addition to explicit feedback from users and possibly some expert curation of answers to common questions .<br><br>[Method: "implicit user feedback"] -(coreference)-> [Method: "explicit feedback"]
- In the proposed adversarial nets framework , the generative model is pitted against an adversary : a discriminative model that learns to determine whether a sample is from the model distribution or the data distribution .<br><br>[MLModelGeneric: "adversary"] -(coreference)-> [MLModelGeneric: "discriminative"]
- Mimicking the adaptation of SGD to FedOpt , the momentum gradient descent method which is a variant of SGD has been modified to fit for federated learning ( MFL ) [ 24 ] .<br><br>[Method: "federated learning"] -(coreference)-> [Method: "MFL"]
- SCL : Domain adaptation methods attempt to overcome the feature mismatch between source and target domains by predicting missing features and/or learning a lower - dimensional embedding common to the two domains .<br><br>[Method: "SCL"] -(coreference)-> [Method: "Domain adaptation"]
- The resulting algorithm is a sequence of three standard training operations : masked LM ( MLM ) pre - training ( Devlin et al . , 2018 ) , task - specific distillation , and optional fine - tuning .<br><br>[Method: "masked LM"] -(coreference)-> [Method: "MLM"]

### Task

- To empirically study the effect of the damping factor on the classification accuracy of short - texts under the Global Feature Expansion method , we randomly select 1000 positive and 1000 negative sentiment labeled sentences from the Large Movie Review dataset as validation data , and evaluate the sentiment classification accuracy of the Global Feature Expansion method with different γ values .<br><br>[Task: "classification"] -(coreference)-> [Task: "sentiment classification"]

### Dataset

- However , by making use of multilingual training ( translate - trainall ) and leveraging training sets coming from multiple languages , XLM-7 can outperform the BERT models : our XLM-7 trained on CC obtains 80.0 % average accuracy on the 7 languages , while the average performance of BERT models trained on CC is 77.5 % .<br><br>[Dataset: "CC"] -(coreference)-> [Dataset: "CC"]
- The result shows that TAPEX endows BART with generic table understanding capabilities , which could be adapted to different downstream tasks , regardless of whether these tasks are highly similar to the TAPEX pre - training task or not .<br><br>[Dataset: "TAPEX"] -(coreference)-> [Dataset: "TAPEX"]
- On the other hand , we might observe such positive sentiments associated with iPhone 6 plus but not with iPhone 6 in other train instances , which will result in a high positive score for iPhone 6 plus in a classifier trained from those train reviews .<br><br>[Dataset: "iPhone 6 plus"] -(coreference)-> [Dataset: "iPhone 6 plus"]
- On the other hand , we might observe such positive sentiments associated with iPhone 6 plus but not with iPhone 6 in other train instances , which will result in a high positive score for iPhone 6 plus in a classifier trained from those train reviews .<br><br>[Dataset: "iPhone 6"] -(coreference)-> [Dataset: "iPhone 6 plus"]
- However , if Bing , a Web search engine similar to Google , appears in the local neighbourhood of Google in the ClassiNet , and if we can propagate from Bing to its parent company Microsoft via the ClassiNet , then we will be able to predict Microsoft as a relevant feature for Google .<br><br>[DataSource: "Bing"] -(coreference)-> [DataSource: "Bing"]

## False Negatives

### Method

- The results for test run using 5 - fold CV tasks for the optimized models are shown in Fig . 2. We found that the BiLM encoder with the LSTM layer performs slightly better than the GCN encoder , although their differences are not pronounced : the mean unsigned prediction error ( MUE ) for the BiLM / LSTM encoder model is 0. 19 kcal / mol , while the GCN model results in 0. 23 kcal / mol .<br><br>[Method: "mean unsigned prediction error"] -(coreference)-> [Method: "MUE"]
- In other words , D and G play the following two - player minimax game with value function V ( G , D ):<br><br>[MLModelGeneric: "D"] -(coreference)-> [MLModel: "D"]
- The disadvantages are primarily that there is no explicit representation of p g ( x ) , and that D must be synchronized well with G during training ( in particular , G must not be trained too much without updating D , in order to avoid " the Helvetica scenario " in which G collapses too many values of z to the same value of x to have enough diversity to model p data ) , much as the negative chains of a Boltzmann machine must be kept up to date between learning steps .<br><br>[MLModelGeneric: "D"] -(coreference)-> [MLModelGeneric: "D"]
- To learn the generator 's distribution p g over data x , we define a prior on input noise variables p z ( z ) , then represent a mapping to data space as G ( z ; θ g ) , where G is a differentiable function represented by a multilayer perceptron with parameters θ g .<br><br>[MLModelGeneric: "G"] -(coreference)-> [MLModelGeneric: "multilayer perceptron"]
- Considering that ( a ) ClassiNets can be created using unlabeled data , ( b ) the same ClassiNet can be used in principle for predicting features for different target tasks , ( c ) arbitrary features could be used in the feature predictors , not limited to lexical features , we believe that ClassiNets can be applied to a broad - range of machine learning tasks , not limited to short - text classification .<br><br>[MLModel: "ClassiNet"] -(coreference)-> [MLModelGeneric: "ClassiNets"]

### Task

- In terms of the different reasoning types , GOOAQ has an extremely long - tail of reasoning challenges , due to our data collection procedure .<br><br>[Task: "reasoning"] -(coreference)-> [Task: "reasoning"]
- Furthermore , we examine the effectiveness of TAPEX via two fundamental downstream tasks : table - based question answering ( TableQA ) and table - based fact verification ( TableFV ) .<br><br>[Task: "table - based fact verification"] -(coreference)-> [Task: "TableFV"]
- In this section , we first present the background of two fundamental table related downstream tasks : tablebased question answering ( TableQA ) and table - based fact verification ( TableFV ) .<br><br>[Task: "table - based fact verification"] -(coreference)-> [Task: "TableFV"]

### Dataset

- We evaluate the performance of our approach on weakly - supervised WikiSQL ( WIKISQL - WEAK ) ( Zhong et al . , 2017 ) , WIKITABLEQUESTIONS ( Pasupat & Liang , 2015 ) , SQA ( Iyyer et al . , 2017 ) , and TABFACT ( Chen et al . , 2020 ) .<br><br>[Dataset: "weakly - supervised WikiSQL"] -(coreference)-> [Dataset: "WIKISQL - WEAK"]
- We reaffirm this statement through experiments on Amazon Book Reviews in Figure 8 , given that Amazon Book Reviews have the biggest transfer set .<br><br>[Dataset: "Amazon Book Reviews"] -(coreference)-> [Dataset: "Amazon Book Reviews"]
- Three real datasets are chosen for overall performance , ablation study and DLG study , namely MNIST [ 18 ] , Human Activity Recognition Using Smartphones dataset ( HAR ) [ 3 ] and Epileptic Seizure Recognition dataset ( ESR ) [ 2 ] .<br><br>[Dataset: "Epileptic Seizure Recognition"] -(coreference)-> [Dataset: "ESR"]
