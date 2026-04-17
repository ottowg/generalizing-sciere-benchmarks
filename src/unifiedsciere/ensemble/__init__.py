"""Ensemble methods for combining predictions from multiple models."""

from .majority_vote import majority_vote_ensemble

__all__ = ["majority_vote_ensemble"]
