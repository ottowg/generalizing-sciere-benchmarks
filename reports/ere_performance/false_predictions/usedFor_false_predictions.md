# usedFor False Predictions (Unified GSAP Test)

Dataset: gsap
Split: test
Trained on: gsap

Total predicted relations: 496
Total gold relations: 626
True positive predictions: 307
False positive predictions: 174
False negative predictions: 304

## False Positives

### Method

- First , we train binary classifiers which we call feature predictors for predicting whether a particular feature v i occurs in a given instance x.<br><br>[MLModelGeneric: "feature predictors"] -(usedFor)-> [MLModelGeneric: "binary"]
- Since the teacher could potentially transfer the knowledge it has obtained via pre - training to the student through distillation , it is a priori unclear whether pre - training the student would bring additional benefits .<br><br>[Method: "pre - training"] -(usedFor)-> [MLModelGeneric: "student"]
- • A novel FedOpt algorithm is proposed , i.e. , LoSAC .<br><br>[Method: "novel FedOpt algorithm"] -(usedFor)-> [MLModel: "LoSAC"]
- In this expansion method , first , we use edge - weights to find the k - nearest neighbours of each vertex v i , and connect all the neighbours for each vertex to create a k - nearest neighbour graph from the trained ClassiNet .<br><br>[Method: "k - nearest neighbour graph"] -(usedFor)-> [MLModelGeneric: "trained ClassiNet"]
- Sequential Denoising Autoencoder ( SDAE ) ( Hill et al . , 2016a ) is an encoder - decoder model with a Long Short - Term Memory ( LSTM ) ( Hochreiter and Schmidhuber , 1997 ) unit .<br><br>[ModelArchitecture: "Long Short - Term Memory"] -(usedFor)-> [MLModelGeneric: "SDAE"]

### Task

No false positives found.

### Dataset

No false positives found.

## False Negatives

### Method

- While feature - based unsupervised representations have been successfully used in compact models ( Johnson & Zhang , 2015 ; Gururangan et al . , 2019 ) , inter alia , the pretraining + fine - tuning approach has not been studied in depth for such small models .<br><br>[Method: "pretraining + fine - tuning approach"] -(usedFor)-> [MLModelGeneric: "such small"]
- Many theoretical advances have been introduced to construct the continuum solvation model , which involves parameterized solvent properties : the polarizable continuum model ( PCM ) [ 9 ] , the conductor - like screening model ( COSMO ) [ 1 ] and its variations [ 6 , 33 ] , generalized Born approximations like solvation model based on density ( SMD ) [ 5 ] or solvation model 6 , 8 , 12 , etc .<br><br>[ModelArchitecture: "COSMO"] -(usedFor)-> [MLModelGeneric: "variations"]
- Following BERT , we perform pre - training with the masked LM ( MLM ) and next sentence objectives ( collectively referred to as MLM + from here on ) .<br><br>[Method: "next sentence objectives"] -(usedFor)-> [MLModel: "BERT"]
- We therefore conclude that the LilNetX framework outperforms state - of - the - art approaches in model compression by a significant margin while also achieving sparsification of the network weights for computational gains .<br><br>[Method: "model compression"] -(usedFor)-> [Method: "LilNetX"]
- To verify it , we conducted multi - task fine - tuning experiments and obtained the following findings : ( 1 ) when initialized by BART , multi - task fine - tuning boosts the performance of the target task significantly ;<br><br>[Method: "multi - task fine - tuning"] -(usedFor)-> [Method: "multi - task fine - tuning experiments"]

### Task

No false negatives found.

### Dataset

No false negatives found.
