"""Preprocessing utilities for multivariate sensor time-series."""

import pickle
from pathlib import Path
from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

SAVED_MODELS_DIR = Path(__file__).resolve().parent / "saved_models"


class TelemetryPreprocessor:
    """Handles normalization, scaling, and rolling window generation."""

    def __init__(self, feature_cols: Optional[List[str]] = None):
        self.feature_cols = feature_cols or []
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "TelemetryPreprocessor":
        """Fit scaler on normal operational data."""
        if not self.feature_cols:
            self.feature_cols = [c for c in df.columns if c not in ["time", "timestamp", "fault", "fault_label"]]
        self.scaler.fit(df[self.feature_cols].values)
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform dataframe to scaled numpy array."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transforming.")
        return self.scaler.transform(df[self.feature_cols].values)

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit scaler and return transformed numpy array."""
        return self.fit(df).transform(df)

    @staticmethod
    def create_sliding_windows(
        data: np.ndarray, window_size: int = 30, step_size: int = 1
    ) -> np.ndarray:
        """
        Create 3D tensor: (num_samples, window_size, num_features)
        suitable for recurrent / LSTM models.
        """
        num_samples = (len(data) - window_size) // step_size + 1
        if num_samples <= 0:
            return np.empty((0, window_size, data.shape[1] if data.ndim > 1 else 1))

        windows = []
        for i in range(0, len(data) - window_size + 1, step_size):
            windows.append(data[i : i + window_size])
        return np.array(windows)

    def save(self, filepath: Optional[Path] = None) -> None:
        """Save scaler and feature list to disk."""
        target = filepath or (SAVED_MODELS_DIR / "scaler.pkl")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            pickle.dump({"scaler": self.scaler, "feature_cols": self.feature_cols}, f)

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "TelemetryPreprocessor":
        """Load scaler from disk."""
        source = filepath or (SAVED_MODELS_DIR / "scaler.pkl")
        with open(source, "rb") as f:
            data = pickle.load(f)
        obj = cls(feature_cols=data["feature_cols"])
        obj.scaler = data["scaler"]
        obj.is_fitted = True
        return obj
