"""Temporal Precedence: Computes earliest deviation timestamp and chronological ordering.

Identifies the first time index where each sensor's measurement departs from normal
steady-state baseline. The sensor that deviates earliest in time receives the highest score.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def detect_first_deviation_time(
    series: pd.Series,
    baseline_mean: Optional[float] = None,
    baseline_std: Optional[float] = None,
    threshold_z: float = 2.5
) -> Optional[int]:
    """Find index of the earliest deviation exceeding threshold_z.

    Args:
        series: Process variable telemetry series.
        baseline_mean: Optional nominal mean. If None, computes from initial 20% warmup.
        baseline_std: Optional nominal std. If None, computes from initial 20% warmup.
        threshold_z: Standard deviation departure threshold (default 2.5).

    Returns:
        Optional[int]: 0-indexed position of earliest threshold crossing, or None.
    """
    if baseline_mean is None:
        warmup_len = max(5, int(len(series) * 0.2))
        baseline_mean = float(series.iloc[:warmup_len].mean())
        baseline_std = float(series.iloc[:warmup_len].std())

    if baseline_std is None or baseline_std < 1e-5:
        baseline_std = 1.0

    z_scores = np.abs((series.values - baseline_mean) / baseline_std)
    deviations = np.where(z_scores >= threshold_z)[0]

    if len(deviations) > 0:
        return int(deviations[0])
    return None


def calculate_temporal_precedence_scores(
    df: pd.DataFrame,
    candidate_sensors: List[str],
    threshold_z: float = 2.0
) -> Dict[str, float]:
    """Rank candidate sensors by earliest deviation time.

    Sensor that deviated earliest receives score ~ 1.0; downstream lagging sensors
    receive linearly decayed scores.

    Args:
        df: Telemetry DataFrame containing continuous time series.
        candidate_sensors: List of sensors to evaluate.
        threshold_z: Z-score threshold for deviation detection.

    Returns:
        Dict[str, float]: Map of sensor_id -> normalized temporal precedence score [0.0, 1.0].
    """
    earliest_indices: Dict[str, int] = {}

    for sensor in candidate_sensors:
        if sensor not in df.columns:
            continue
        idx = detect_first_deviation_time(df[sensor], threshold_z=threshold_z)
        if idx is not None:
            earliest_indices[sensor] = idx

    if not earliest_indices:
        return {s: 0.0 for s in candidate_sensors}

    min_idx = min(earliest_indices.values())
    max_idx = max(earliest_indices.values())

    scores: Dict[str, float] = {}
    for s in candidate_sensors:
        if s not in earliest_indices:
            scores[s] = 0.0
        elif max_idx == min_idx:
            scores[s] = 1.0
        else:
            # Earliest deviation gets 1.0; latest gets ~0.1
            normalized = 1.0 - 0.9 * ((earliest_indices[s] - min_idx) / (max_idx - min_idx))
            scores[s] = round(float(max(0.0, normalized)), 4)

    return scores


if __name__ == "__main__":
    print("--- Temporal Precedence Standalone Test ---")
    test_df = pd.DataFrame({
        "Sensor_A": [10.0] * 10 + [25.0] * 40,   # Deviates at index 10
        "Sensor_B": [50.0] * 25 + [80.0] * 25,   # Deviates at index 25
        "Sensor_C": [100.0] * 40 + [120.0] * 10, # Deviates at index 40
    })

    t_scores = calculate_temporal_precedence_scores(test_df, ["Sensor_A", "Sensor_B", "Sensor_C"])
    print("Computed Temporal Scores:")
    for sens, sc in sorted(t_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sens}: {sc:.4f}")
    assert t_scores["Sensor_A"] > t_scores["Sensor_B"] > t_scores["Sensor_C"]
    print("[PASS] temporal_precedence.py verified successfully.")
