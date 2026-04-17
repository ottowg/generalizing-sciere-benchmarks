# Parenthesized Mentions — train

| Dataset | Annotator | Split | Entity Type | Count | Total | % | Examples |
| ------- | --------- | ----- | ----------- | ----: | ----: | --: | -------- |
| scier | gold | train | Dataset | 24 | 3220 | 0.7% | "Caltech - 2 5 6 ( C )"; "Protein - Protein Interactions(PPI )"; "Protein - Protein interactions(PPI )"; "arXiv(Astro - PH )"; "FERPlus ( test )" |
| scier | gold | train | Method | 97 | 11424 | 0.8% | "(HRNet)~\cite{SunXLW"; "ReLU 6 (x+ 3 ) 6"; "ReLU 6 (x + 3 ) 6"; "real - time - capable ( 2 5 Hz ) semantic mapping system"; "Conv + BN + ReLU + Conv ( score )" |
| scier | gold | train | Task | 0 | 3397 | 0.0% |  |
| scier | scier | train | Dataset | 22 | 3214 | 0.7% | "Caltech - 2 5 6 ( C )"; "Protein - Protein Interactions(PPI )"; "Protein - Protein interactions(PPI )"; "arXiv(Astro - PH )"; "FERPlus ( test )" |
| scier | scier | train | Method | 92 | 11383 | 0.8% | "ReLU 6 (x+ 3 ) 6"; "ReLU 6 (x + 3 ) 6"; "Conv + BN + ReLU + Conv ( score )"; "LS - DeconvNets ( RGB - D )"; "CFN ( VGG - 1 6 , RGB - D )" |
| scier | scier | train | Task | 0 | 3391 | 0.0% |  |
| scier | scinlp | train | Dataset | 41 | 2173 | 1.9% | "Protein - Protein Interactions(PPI )"; "Protein - Protein interactions(PPI )"; "arXiv(Astro - PH )"; "Berkeley Deep Drive Segmentation ( BDDS )"; "Affect - Net ( validation )" |
| scier | scinlp | train | Method | 511 | 9168 | 5.6% | "convolutional neural networks ( ConvNets )"; "region proposal network ( RPN )"; "Point Linking Network ( PLN )"; "non - maximal suppression ( NMS )"; "fullyconvolutional network ( FCN )" |
| scier | scinlp | train | Task | 48 | 3168 | 1.5% | "Generative Adversarial Networks ( GAN )"; "Single Image Super - Resolution ( SISR )"; "Computer Aided Diagnostic ( CAD )"; "machine learning ( ML )"; "natural language processing ( NLP )" |
| scier | gsap-ere | train | Dataset | 0 | 2897 | 0.0% |  |
| scier | gsap-ere | train | Method | 42 | 11273 | 0.4% | "ReLU 6 (x+ 3 ) 6"; "ReLU 6 (x + 3 ) 6"; "Conv + BN + ReLU + Conv ( score )"; "Computer Aided Diagnostic ( CAD )"; "Part - of - Speech ( POS ) tags" |
| scier | gsap-ere | train | Task | 0 | 2831 | 0.0% |  |
| scinlp | gold | train | Dataset | 18 | 813 | 2.2% | "Brown Corpus ( BC )"; "Wall Street Journal ( WSJ )"; "RTE - 5 ( 2009 )"; "RTE6 ( 2010 )"; "English Web Treebank ( LDC2012T13 )" |
| scinlp | gold | train | Method | 120 | 2596 | 4.6% | "BoW ( Linear )"; "bag-of-words ( BoW )"; "BoW ( MLP )"; "BoW ( bag of words )"; "reinforcement learning ( RL )" |
| scinlp | gold | train | Task | 25 | 823 | 3.0% | "Traditional Question Generation ( TQG )"; "Sequential Question Generation ( SQG )"; "Question Generation ( QG )"; "Traditional Question Generation ( TQG )"; "Sequential Question Generation ( SQG )" |
| scinlp | scier | train | Dataset | 5 | 1487 | 0.3% | "RTE - 5 ( 2009 )"; "RTE6 ( 2010 )"; "New York Times ( NYT )"; "Air Travel Information System ( ATIS ) dataset"; "SQuAD ( v1.1 ) dataset" |
| scinlp | scier | train | Method | 32 | 4062 | 0.8% | "BoW ( Linear )"; "BoW ( bag of words )"; "MDL-based ( Minimum Description Length ) tree cut model"; "Expectation Maximization ( EM ) algorithm"; "trained P ( tag I suffix ) model" |
| scinlp | scier | train | Task | 0 | 1129 | 0.0% |  |
| scinlp | scinlp | train | Dataset | 18 | 810 | 2.2% | "Brown Corpus ( BC )"; "Wall Street Journal ( WSJ )"; "RTE - 5 ( 2009 )"; "RTE6 ( 2010 )"; "English Web Treebank ( LDC2012T13 )" |
| scinlp | scinlp | train | Method | 118 | 2593 | 4.6% | "BoW ( Linear )"; "bag-of-words ( BoW )"; "BoW ( MLP )"; "BoW ( bag of words )"; "reinforcement learning ( RL )" |
| scinlp | scinlp | train | Task | 24 | 815 | 2.9% | "Traditional Question Generation ( TQG )"; "Sequential Question Generation ( SQG )"; "Question Generation ( QG )"; "Traditional Question Generation ( TQG )"; "Sequential Question Generation ( SQG )" |
| scinlp | gsap-ere | train | Dataset | 2 | 1019 | 0.2% | "RTE6 ( 2010 )"; "New York Times ( NYT ) corpus" |
| scinlp | gsap-ere | train | Method | 28 | 4181 | 0.7% | "log-linear ( maximum-entropy ) parameterizations"; "MDL-based ( Minimum Description Length ) tree cut"; "MDL-based ( Minimum Description Length ) tree cut"; "Expectation Maximization ( EM ) algorithm"; "trained P ( tag I suffix )" |
| scinlp | gsap-ere | train | Task | 1 | 956 | 0.1% | "part-of-speech ( POS ) tagging" |
| gsap-ere | gold | train | Dataset | 7 | 3058 | 0.2% | "Solcast ( 2021 )"; "Alzheimer 's Disease Neuroimaging Initiative ( ADNI ) database"; "Alzheimer 's Disease Neuroimaging Initiative ( ADNI ) database"; "DR ( eye ) VE"; "DR ( eye ) VE" |
| gsap-ere | gold | train | Method | 232 | 19454 | 1.2% | "standard Left - to - Right ( LTR ) LM"; "masked language model ( MLM ) objective"; "lower - cased byte pair encoding ( BPE ) representation"; "increasing the width ( Mahajan et al . , 2018 ) or depth"; "1 , 2 , 4 , 8 , 16shot ( when possible ) , and a fully supervised linear" |
| gsap-ere | gold | train | Task | 5 | 2678 | 0.2% | "zero - shot ( or fewshot ) generalization"; "Definition - Restrictive ( 0SHOT - TC )"; "Definition - Wild ( 0SHOT - TC )"; "part - of - speech ( POS ) tagging"; "designing capacity - approaching Irregular Low - Density Parity - Check ( LDPC ) codes" |
| gsap-ere | scier | train | Dataset | 47 | 7624 | 0.6% | "BooksCorpus ( 800 M words )"; "English Wikipedia ( 2 , 500 M words )"; "BooksCorpus ( 800 M words )"; "BooksCorpus ( 800 M words )"; "400 million ( image , text ) pairs" |
| gsap-ere | scier | train | Method | 172 | 17898 | 1.0% | "Logeswaran and Lee ( 2018 )"; "masked language model ( MLM ) objective"; "a bag - of - words ( BoW ) encoding"; "Zhang ( 2019 )"; "a lower - cased byte pair encoding ( BPE ) representation" |
| gsap-ere | scier | train | Task | 13 | 5120 | 0.3% | "contrastive ( text , image ) representation learning"; "context ( sentence ) similarity"; "judgments involving agreement ( Singular / Pl )"; "contrasts involving agreement ( Singular / Pl and Reflexive )"; "2 de - identification ( de - ID ) tasks" |
| gsap-ere | scinlp | train | Dataset | 52 | 3399 | 1.5% | "General Language Understanding Evaluation ( GLUE )"; "Situations With Adversarial Generations ( SWAG )"; "Varadarajan & Odobez ( 2009 )"; "Google 's Celebrity Recognition ( Google )"; "MNIST ( LeCun )" |
| gsap-ere | scinlp | train | Method | 299 | 14232 | 2.1% | "Generative Pre - trained Transformer ( OpenAI GPT )"; "masked language model ( MLM ) objective"; "Vision Transformer ( ViT )"; "Linzen ( 2020 )"; "Google Cloud Vision ( GCV )" |
| gsap-ere | scinlp | train | Task | 74 | 5795 | 1.3% | "zero - shot ( or fewshot ) generalization"; "optical character recognition ( OCR )"; "open information extraction ( OpenIE )"; "question answering ( QA )"; "Natural Questions ( NQ )" |
| gsap-ere | gsap-ere | train | Dataset | 7 | 3075 | 0.2% | "Solcast ( 2021 )"; "Alzheimer 's Disease Neuroimaging Initiative ( ADNI ) database"; "Alzheimer 's Disease Neuroimaging Initiative ( ADNI ) database"; "DR ( eye ) VE"; "DR ( eye ) VE" |
| gsap-ere | gsap-ere | train | Method | 212 | 19505 | 1.1% | "standard Left - to - Right ( LTR ) LM"; "masked language model ( MLM ) objective"; "Li et al . ( 2017 )"; "lower - cased byte pair encoding ( BPE ) representation"; "3 ( or more ) pre - trained subsystems" |
| gsap-ere | gsap-ere | train | Task | 4 | 2639 | 0.2% | "zero - shot ( or fewshot ) generalization"; "Definition - Restrictive ( 0SHOT - TC )"; "Definition - Wild ( 0SHOT - TC )"; "part - of - speech ( POS ) tagging" |
