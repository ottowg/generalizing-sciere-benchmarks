# appliedTo False Predictions (Unified GSAP Test)

Dataset: gsap
Split: test
Trained on: gsap

Total predicted relations: 90
Total gold relations: 126
True positive predictions: 65
False positive predictions: 25
False negative predictions: 61

## False Positives

### Method

- For our evaluation , we use the T5 model ( Raffel et al . , 2020 ) , a recent text - to - text framework that has achieved state - of - the - art results on a variety of tasks , including open QA ( Roberts et al . , 2020 ) .<br><br>[MLModel: "T5"] -(appliedTo)-> [Task: "open QA"]
- In this paper , we regard the pre - training as a sequence generation task and employ an encoder - decoder model .<br><br>[Method: "pre - training"] -(appliedTo)-> [Task: "sequence generation"]
- Our experimental results show that the global feature expansion method significantly improves the classification accuracy of a sentence - level sentiment classification tasks outperforming previously proposed methods such as structural correspondence learning ( SCL ) , and frequent term sets ( FTS ) , Skip - thought vectors , FastSent , and Paragraph2Vec on multiple datasets .<br><br>[Method: "global feature expansion method"] -(appliedTo)-> [Task: "classification"]
- We show that it provides strong gains over previous multilingual models like mBERT and XLM on classification , sequence labeling and question answering .<br><br>[MLModelGeneric: "previous multilingual"] -(appliedTo)-> [Task: "sequence labeling"]
- To empirically study the effect of the damping factor on the classification accuracy of short - texts under the Global Feature Expansion method , we randomly select 1000 positive and 1000 negative sentiment labeled sentences from the Large Movie Review dataset as validation data , and evaluate the sentiment classification accuracy of the Global Feature Expansion method with different γ values .<br><br>[Method: "Global Feature Expansion method"] -(appliedTo)-> [Task: "sentiment classification"]

### Task

No false positives found.

### Dataset

- Experimental results on four datasets show that TAPEX can broadly improve the model ability on understanding tables , especially in the low data regime .<br><br>[Dataset: "TAPEX"] -(appliedTo)-> [Task: "understanding tables"]

## False Negatives

### Method

- We show that it provides strong gains over previous multilingual models like mBERT and XLM on classification , sequence labeling and question answering .<br><br>[MLModel: "XLM"] -(appliedTo)-> [Task: "question answering"]
- Instead , we perform an extrinsic evaluation of the created ClassiNet by using it to expand feature vectors representing sentences in several binary text classification tasks .<br><br>[MLModel: "ClassiNet"] -(appliedTo)-> [Task: "binary text classification"]
- We show that it provides strong gains over previous multilingual models like mBERT and XLM on classification , sequence labeling and question answering .<br><br>[MLModel: "mBERT"] -(appliedTo)-> [Task: "classification"]
- For FedADMM [ 34 ] solving low rank matrix estimation , the details are in Appendix E .<br><br>[Method: "FedADMM"] -(appliedTo)-> [Task: "low rank matrix estimation"]
- Before we empirically evaluate the performance of the proposed ClassiNets for feature expansion in short - text classification , let us analyze some interesting properties of ClassiNets .<br><br>[MLModelGeneric: "ClassiNets"] -(appliedTo)-> [Task: "short - text classification"]

### Task

No false negatives found.

### Dataset

No false negatives found.
