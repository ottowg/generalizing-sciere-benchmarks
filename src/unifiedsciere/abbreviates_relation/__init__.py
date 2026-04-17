"""Abbreviation-relation detection, normalization, and classification.

Modules
-------
signals   Primitive signal functions shared by rule-based detector and ML features.
detect    Subtask A (mention-pair) and Subtask B (single-span) detectors.
normalize Corpus-level normalization: relabel, canonicalize direction, split spans.
features  Feature extraction for supervised classification.
classify  Weak labeling, Random Forest / SVM training, uncertainty scoring.
"""
