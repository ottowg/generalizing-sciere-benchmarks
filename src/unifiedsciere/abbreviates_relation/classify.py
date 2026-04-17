"""Supervised abbreviation classifier with weak labeling and uncertainty scoring.

Workflow
--------
1. Run detect.detect(corpus) to get candidates.
2. Call weak_labels() to assign positive / negative / borderline to each.
3. Call train() on the positive + negative subsets.
4. Call predict_proba() on all candidates to get uncertainty scores.
5. Borderline candidates sorted by uncertainty go to the active learning queue.
6. After human annotation, call train() again on the expanded labeled set.

The classifier wraps scikit-learn Random Forest and linear SVM, selectable via
the ``model`` parameter.  Both support probability calibration so that the
uncertainty score (distance to 0.5) is meaningful across batches.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from .detect import MentionPairCandidate, SingleSpanCandidate
from .features import (
    PAIR_FEATURE_NAMES,
    SPAN_FEATURE_NAMES,
    UNIFIED_FEATURE_NAMES,
    features_from_pair,
    features_from_span,
    features_unified,
)

ModelType = Literal["rf", "svm"]
CandidateType = MentionPairCandidate | SingleSpanCandidate


# ---------------------------------------------------------------------------
# Weak-label assignment
# ---------------------------------------------------------------------------

def weak_labels(
    candidates: list[CandidateType],
) -> tuple[list[CandidateType], list[int], list[CandidateType]]:
    """Split candidates into (labeled, labels, borderline).

    Positives (all signals fired)  → label 1
    Negatives (no signal fired)    → label 0
    Borderline (partial)           → withheld for active learning

    Returns
    -------
    labeled : list of positive + negative candidates
    labels  : corresponding 0/1 integer labels
    borderline : candidates withheld for active learning
    """
    labeled: list[CandidateType] = []
    labels: list[int] = []
    borderline: list[CandidateType] = []

    for cand in candidates:
        wl = cand.weak_label
        if wl == "positive":
            labeled.append(cand)
            labels.append(1)
        elif wl == "negative":
            labeled.append(cand)
            labels.append(0)
        else:
            borderline.append(cand)

    return labeled, labels, borderline


# ---------------------------------------------------------------------------
# Feature matrix helpers
# ---------------------------------------------------------------------------

def _to_matrix(
    candidates: list[CandidateType],
    feature_names: list[str],
    unified: bool = False,
) -> np.ndarray:
    if unified:
        rows = [features_unified(c) for c in candidates]
    else:
        extractor = (
            features_from_pair
            if candidates and isinstance(candidates[0], MentionPairCandidate)
            else features_from_span
        )
        rows = [extractor(c) for c in candidates]  # type: ignore[arg-type]
    return np.array([[row.get(k, 0.0) for k in feature_names] for row in rows], dtype=float)


def _feature_names_for(candidates: list[CandidateType], unified: bool = False) -> list[str]:
    if unified:
        return UNIFIED_FEATURE_NAMES
    if candidates and isinstance(candidates[0], MentionPairCandidate):
        return PAIR_FEATURE_NAMES
    return SPAN_FEATURE_NAMES


# ---------------------------------------------------------------------------
# Classifier wrapper
# ---------------------------------------------------------------------------

@dataclass
class AbbrevClassifier:
    """Thin wrapper around a scikit-learn classifier for abbreviation detection.

    Parameters
    ----------
    model : 'rf' | 'svm'
        'rf'  = Random Forest (CalibratedClassifierCV over RandomForestClassifier)
        'svm' = Linear SVM    (CalibratedClassifierCV over LinearSVC)
    subtask : 'A' | 'B'
        Determines which feature set is used.
    """

    model: ModelType = "rf"
    subtask: Literal["A", "B", "unified"] = "A"
    _clf: Any = None

    def _build(self) -> Any:
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import LinearSVC

        if self.model == "rf":
            base = RandomForestClassifier(
                n_estimators=100,
                max_features="sqrt",
                class_weight="balanced",
                random_state=42,
            )
            return CalibratedClassifierCV(base, cv=3, method="isotonic")
        else:
            base = LinearSVC(C=1.0, class_weight="balanced", max_iter=2000, random_state=42)
            return CalibratedClassifierCV(base, cv=3, method="sigmoid")

    @property
    def feature_names(self) -> list[str]:
        if self.subtask == "unified":
            return UNIFIED_FEATURE_NAMES
        return PAIR_FEATURE_NAMES if self.subtask == "A" else SPAN_FEATURE_NAMES

    @property
    def _unified(self) -> bool:
        return self.subtask == "unified"

    def train(
        self,
        candidates: list[CandidateType],
        labels: list[int],
    ) -> "AbbrevClassifier":
        """Fit the classifier on *candidates* with integer *labels* (0/1).

        Returns self for chaining.
        """
        if len(set(labels)) < 2:
            raise ValueError("Training requires both positive and negative examples.")

        X = _to_matrix(candidates, self.feature_names, unified=self._unified)
        y = np.array(labels, dtype=int)
        self._clf = self._build()
        self._clf.fit(X, y)
        return self

    def predict_proba(self, candidates: list[CandidateType]) -> np.ndarray:
        """Return P(abbreviation) for each candidate. Shape: (n,)."""
        if self._clf is None:
            raise RuntimeError("Model not trained. Call train() first.")
        X = _to_matrix(candidates, self.feature_names, unified=self._unified)
        return self._clf.predict_proba(X)[:, 1]

    def uncertainty(self, candidates: list[CandidateType]) -> np.ndarray:
        """Return uncertainty score (0 = certain, 0.5 = maximally uncertain)."""
        proba = self.predict_proba(candidates)
        return 0.5 - np.abs(proba - 0.5)

    def rank_by_uncertainty(
        self, candidates: list[CandidateType]
    ) -> list[tuple[CandidateType, float]]:
        """Return candidates sorted by descending uncertainty (most uncertain first).

        This is the active learning query ordering.
        """
        scores = self.uncertainty(candidates)
        ranked = sorted(zip(candidates, scores.tolist()), key=lambda x: -x[1])
        return ranked

    def predict(self, candidates: list[CandidateType]) -> np.ndarray:
        """Return binary predictions (0/1)."""
        proba = self.predict_proba(candidates)
        return (proba >= 0.5).astype(int)

    def feature_importances(self) -> dict[str, float] | None:
        """Return feature importances for RF, None for SVM."""
        if self._clf is None or self.model != "rf":
            return None
        # CalibratedClassifierCV wraps the base estimator
        try:
            importances = np.mean(
                [est.base_estimator.feature_importances_
                 for est in self._clf.calibrated_classifiers_],
                axis=0,
            )
        except AttributeError:
            try:
                importances = self._clf.estimator.feature_importances_
            except AttributeError:
                return None
        return dict(zip(self.feature_names, importances.tolist()))


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def evaluate(
    clf: AbbrevClassifier,
    candidates: list[CandidateType],
    labels: list[int],
) -> dict[str, float]:
    """Compute precision, recall, F1 for the positive class."""
    from sklearn.metrics import precision_recall_fscore_support

    y_true = np.array(labels, dtype=int)
    y_pred = clf.predict(candidates)
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    return {"precision": float(p), "recall": float(r), "f1": float(f)}


def rule_based_evaluate(
    candidates: list[CandidateType],
    labels: list[int],
) -> dict[str, float]:
    """Evaluate the rule-based detector (all signals must fire) as a baseline."""
    from sklearn.metrics import precision_recall_fscore_support

    y_true = np.array(labels, dtype=int)
    y_pred = np.array([int(c.rule_based_positive) for c in candidates], dtype=int)
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    return {"precision": float(p), "recall": float(r), "f1": float(f)}
