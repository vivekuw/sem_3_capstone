"""Baseline Isolation Forest anomaly detector for tabular and windowed features."""

import pickle
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest

SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent / "saved_models"


class IsolationForestDetector:
    """Wrapper around scikit-learn Isolation Forest for baseline anomaly scoring."""

    def __init__(self, contamination: float = 0.05, n_estimators: int = 150, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> "IsolationForestDetector":
        """
        Fit Isolation Forest on normal baseline data.
        X: 2D array of shape (samples, features).
        """
        if X.ndim == 3:
            # Flatten window dimension if 3D tensor is passed
            X = X.reshape(X.shape[0], -1)
        self.model.fit(X)
        self.is_fitted = True
        return self

    def score(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute anomaly predictions and normalized anomaly scores.
        Returns:
            is_anomaly: boolean array (True if anomaly, False if normal)
            scores: float array where higher indicates more anomalous
        """
        if not self.is_fitted:
            raise RuntimeError("IsolationForest model is not fitted.")

        if X.ndim == 3:
            X = X.reshape(X.shape[0], -1)

        raw_scores = -self.model.score_samples(X)  # Higher is more abnormal
        preds = self.model.predict(X)  # -1 for anomaly, 1 for inlier
        is_anomaly = preds == -1
        return is_anomaly, raw_scores

    def save(self, filepath: Optional[Path] = None) -> None:
        """Persist trained model to disk."""
        target = filepath or (SAVED_MODELS_DIR / "isolation_forest.pkl")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            pickle.dump(self.model, f)

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "IsolationForestDetector":
        """Load trained model from disk."""
        source = filepath or (SAVED_MODELS_DIR / "isolation_forest.pkl")
        with open(source, "rb") as f:
            model = pickle.load(f)
        obj = cls()
        obj.model = model
        obj.is_fitted = True
        return obj
