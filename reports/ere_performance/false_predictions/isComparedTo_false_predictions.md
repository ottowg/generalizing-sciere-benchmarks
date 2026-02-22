# isComparedTo False Predictions (Unified GSAP Test)

Dataset: gsap
Split: test
Trained on: gsap

Total predicted relations: 126
Total gold relations: 154
True positive predictions: 92
False positive predictions: 34
False negative predictions: 64

## False Positives

### Method

- The structure - property relationship ( SPR ) is rather a new approach , which predicts the solvation free energy with a completely different point of view when compared to computer simulation approaches with precisely defined theoretical backgrounds [ 34 , 35 ] .<br><br>[Method: "SPR"] -(isComparedTo)-> [MLModelGeneric: "computer simulation approaches"]
- Distillation achieves the same performance with Transformer BASE , which is 10x larger than Transformer MINI .<br><br>[Method: "Distillation"] -(isComparedTo)-> [MLModel: "Transformer BASE"]
- We demonstrate that Convolutional Neural Networks ( CNN ) trained with our features outperform state - of - the - art methods in terms of accuracy and sample complexity .<br><br>[MLModelGeneric: "CNN"] -(isComparedTo)-> [MLModelGeneric: "state - of - the - art methods"]
- Distillation achieves the same performance with Transformer BASE , which is 10x larger than Transformer MINI .<br><br>[Method: "Distillation"] -(isComparedTo)-> [MLModelGeneric: "Transformer MINI"]
- We see that l 2 group norm outperforms its l ∞ counterpart for both datasets .<br><br>[Method: "l 2 group norm"] -(isComparedTo)-> [Method: "l ∞"]

### Task

No false positives found.

### Dataset

- Compared to WIKISQL - WEAK , which only requires filtering and optionally aggregating on table cell values , WIKITABLE - QUESTIONS requires more complicated reasoning capabilities .<br><br>[Dataset: "WIKISQL - WEAK"] -(isComparedTo)-> [Dataset: "WIKITABLE - QUESTIONS"]
- Specifically , for MNIST , the label is set to 0 when it is smaller or equal to 5 and 1 otherwise ; for HAR , the label is set to 0 when it is smaller or equal to 3 and 1 otherwise ; For ESR , it has two classes that match well with binary logistic regression .<br><br>[Dataset: "ESR"] -(isComparedTo)-> [ModelArchitecture: "binary logistic regression"]

## False Negatives

### Method

- We investigate the interaction between pretraining and distillation by applying them sequentially on the same data .<br><br>[Method: "pretraining"] -(isComparedTo)-> [Method: "distillation"]
- In practice , Scalar Quantization ( SQ ) is preferred over VQ due to its simplicity and effectiveness without additional encoding complexity .<br><br>[Method: "SQ"] -(isComparedTo)-> [Method: "VQ"]
- In Section 4. 1 , we describe local feature expansion methods that consider only the nearest neighbours of the vertices in the ClassiNet that correspond to nonzero features in an instance , whereas in Section 4. 2 we propose a global feature expansion method that propagates the original features across the ClassiNet to predict the related features .<br><br>[Method: "local feature expansion"] -(isComparedTo)-> [Method: "global feature expansion method"]
- In contrast to our proposed method which explicitly append features to the original feature vectors to overcome the feature sparseness problem , sentence - level embedding methods can be seen as an implicit feature representation method .<br><br>[Method: "proposed method"] -(isComparedTo)-> [Method: "sentence - level embedding methods"]
- We compare the following two algorithms : Pre - training + Finetuning with D LM = X and Pre - trained Distillation with D LM = D T = X .<br><br>[Method: "Pre - training + Finetuning"] -(isComparedTo)-> [Method: "Pre - trained Distillation"]

### Task

- Textual entailment is similar to NLI , but restricted to binary classification ( entailment vs nonentailment ) .<br><br>[Task: "Textual entailment"] -(isComparedTo)-> [Task: "NLI"]

### Dataset

- A comparison with the bigram distribution of NQ ( Fig . 3 ; right ) highlights that GOOAQ represents a different and wider class of questions .<br><br>[Dataset: "NQ"] -(isComparedTo)-> [Dataset: "GOOAQ"]
- We hypothesize that despite GOOAQ being collected differently than ELI5 , a notable portion of ELI5 is covered by GOOAQ , indicating good coverage of common questions posed by ordinary users .<br><br>[Dataset: "GOOAQ"] -(isComparedTo)-> [Dataset: "ELI5"]
