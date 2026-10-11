"""Granger Causality analysis between multivariate process sensor time-series.

Evaluates whether past observations of candidate sensor X contain information that
statistically helps predict current deviations in sensor Y beyond Y's own past history.
Uses statsmodels.tsa.stattools.grangercausalitytests.
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def compute_pairwise_granger(
    df: pd.DataFrame,
    sensor_pairs: List[Tuple[str, str]],
    max_lag: int = 3,
    significance_level: float = 0.05
) -> Dict[str, Dict[str, float]]:
    """Test Granger causality for given pairs: (cause_sensor, effect_sensor).

    Tests H0: cause_sensor does NOT Granger-cause effect_sensor.
    Rejection of H0 (p-value < alpha) indicates statistical predictive causality.

    Args:
        df: Telemetry DataFrame.
        sensor_pairs: List of (cause, effect) tuples.
        max_lag: Maximum lag steps to test (default 3).
        significance_level: Alpha cutoff (default 0.05).

    Returns:
        Dict: {f"{cause}->{effect}": {"p_value": float, "is_causal": float, "f_stat": float}}
    """
    results: Dict[str, Dict[str, float]] = {}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for cause, effect in sensor_pairs:
            pair_key = f"{cause}->{effect}"
            if cause not in df.columns or effect not in df.columns:
                continue

            sub_df = df[[effect, cause]].dropna()
            # Require adequate degrees of freedom
            if len(sub_df) < (max_lag * 3 + 10):
                continue

            # Skip invariant signals (variance near zero)
            if sub_df[cause].std() < 1e-6 or sub_df[effect].std() < 1e-6:
                results[pair_key] = {"p_value": 1.0, "is_causal": 0.0, "f_stat": 0.0}
                continue

            try:
                gc_res = grangercausalitytests(sub_df, maxlag=max_lag, verbose=False)
                # Select lowest p-value (strongest causality) across evaluated lags
                min_p = 1.0
                max_f = 0.0
                for lag, lag_res in gc_res.items():
                    f_stat, p_val = lag_res[0]["ssr_ftest"][0], lag_res[0]["ssr_ftest"][1]
                    if p_val < min_p:
                        min_p = p_val
                        max_f = f_stat

                results[pair_key] = {
                    "p_value": round(float(min_p), 5),
                    "is_causal": 1.0 if min_p < significance_level else 0.0,
                    "f_stat": round(float(max_f), 3),
                }
            except Exception:
                results[pair_key] = {"p_value": 1.0, "is_causal": 0.0, "f_stat": 0.0}

    return results


def compute_granger_outbound_score(
    df: pd.DataFrame,
    candidate: str,
    target_sensors: List[str],
    max_lag: int = 3
) -> float:
    """Calculate outbound Granger causality score [0.0, 1.0] for candidate.

    Higher score indicates candidate strongly Granger-causes target sensors.
    """
    pairs = [(candidate, target) for target in target_sensors if target != candidate]
    if not pairs:
        return 0.5

    res = compute_pairwise_granger(df, pairs, max_lag=max_lag)
    if not res:
        return 0.2

    # Collect p-values
    p_values = [v["p_value"] for v in res.values()]
    # Lower p-value means stronger causality; score = 1 - min(p)
    avg_p = sum(p_values) / len(p_values)
    causal_ratio = sum(1.0 for p in p_values if p < 0.05) / len(p_values)
    # Combine average p-value inversion with fraction of significant links
    score = 0.5 * (1.0 - avg_p) + 0.5 * causal_ratio
    return round(float(max(0.0, min(1.0, score))), 4)


if __name__ == "__main__":
    print("--- Granger Causality Standalone Test ---")
    np.random.seed(42)
    n = 100
    # True cause: x
    x = np.cumsum(np.random.normal(0, 1, n))
    # y is directly driven by past of x with 2 lags
    y = np.zeros(n)
    for t in range(2, n):
        y[t] = 0.8 * x[t - 2] + np.random.normal(0, 0.2)

    toy_df = pd.DataFrame({"Sensor_X": x, "Sensor_Y": y})
    granger_out = compute_pairwise_granger(toy_df, [("Sensor_X", "Sensor_Y"), ("Sensor_Y", "Sensor_X")])
    print(f"Sensor_X -> Sensor_Y: {granger_out.get('Sensor_X->Sensor_Y')}")
    print(f"Sensor_Y -> Sensor_X: {granger_out.get('Sensor_Y->Sensor_X')}")
    assert granger_out["Sensor_X->Sensor_Y"]["is_causal"] == 1.0
    print("[PASS] granger.py verified successfully.")
