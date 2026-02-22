# trainedEvaluatedOn False Predictions (Unified GSAP Test)

Dataset: gsap
Split: test
Trained on: gsap

Total predicted relations: 113
Total gold relations: 126
True positive predictions: 80
False positive predictions: 33
False negative predictions: 46

## False Positives

### Method

- Our closing remarks describe why we are n't simply replicating an existing QA system at Google , place our findings in context , and discuss future uses of GOOAQ , such as creating a neural knowledge - base or a question generation system .<br><br>[Method: "question generation"] -(trainedEvaluatedOn)-> [Dataset: "GOOAQ"]
- The result shows that TAPEX endows BART with generic table understanding capabilities , which could be adapted to different downstream tasks , regardless of whether these tasks are highly similar to the TAPEX pre - training task or not .<br><br>[MLModel: "BART"] -(trainedEvaluatedOn)-> [Dataset: "TAPEX"]
- XLM - R performs particularly well on low - resource languages , improving 15.7 % in XNLI accuracy for Swahili and 11.4 % for Urdu over previous XLM models .<br><br>[MLModel: "XLM - R"] -(trainedEvaluatedOn)-> [Dataset: "Urdu"]
- SCL was described in detail in Section 2. Specifically , we train SCL using the same set of vertices as used by the ClassiNet as pivots .<br><br>[MLModel: "ClassiNet"] -(trainedEvaluatedOn)-> [Method: "same set of vertices"]
- In addition to the comparison of XLM - R and RoBERTa , we provide the first comprehensive study to assess this claim on the XNLI benchmark .<br><br>[MLModelGeneric: "RoBERTa"] -(trainedEvaluatedOn)-> [Dataset: "XNLI"]

### Task

No false positives found.

### Dataset

No false positives found.

## False Negatives

### Method

- Moroever , HAR and ESR are chosen due to the increasing interests and the large potential for the FedOpt applications in mobile devices and healthcare , respectively .<br><br>[Method: "FedOpt applications"] -(trainedEvaluatedOn)-> [Dataset: "ESR"]
- Among the four local expansion methods , All neighbour Expansion reports the best performance in TR and CR datasets , whereas the Mutual neighbour Expansion reports the best performance in MR and SUBJ datasets .<br><br>[Method: "four local expansion methods"] -(trainedEvaluatedOn)-> [Dataset: "CR"]
- Our model , dubbed XLM - R , significantly outperforms multilingual BERT ( mBERT ) on a variety of cross - lingual benchmarks , including +14.6 % average accuracy on XNLI , +13 % average F1 score on MLQA , and +2.4 % F1 score on NER .<br><br>[MLModel: "XLM - R"] -(trainedEvaluatedOn)-> [Dataset: "XNLI"]
- Specifically , the overall XNLI accuracy decreases from 71.8 % to 67.7 % as we go from XLM-7 to XLM-100 .<br><br>[MLModel: "XLM-100"] -(trainedEvaluatedOn)-> [Dataset: "XNLI"]
- It outperforms the previous state of the art by 5. 1 % average accuracy on XNLI , 2. 42 % average F1 - score on Named Entity Recognition , and 9. 1 % average F1 - score on cross - lingual Question Answering .<br><br>[MLModelGeneric: "It"] -(trainedEvaluatedOn)-> [Dataset: "cross - lingual Question Answering"]

### Task

No false negatives found.

### Dataset

No false negatives found.
