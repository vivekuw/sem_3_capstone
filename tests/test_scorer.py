"""Comprehensive unit tests for Phase 5: Causal Reasoning Scorer.

Tests:
1. Temporal Precedence chronological ordering detection.
2. Pairwise Granger causality statistical significance on synthetic lagged processes.
3. Graph proximity hop scoring from plant topology.
4. End-to-end multi-modal CausalScorer on a hand-crafted ground truth test case.
5. Configurable weight sensitivity.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from causal_reasoning.temporal_precedence import (
    detect_first_deviation_time,
    calculate_temporal_precedence_scores,
)
from causal_reasoning.granger import compute_pairwise_granger
from causal_reasoning.graph_proximity import PlantGraphTopology
from causal_reasoning.scorer import CausalScorer


def test_temporal_precedence_order():
    """Verify that earlier deviating sensors receive strictly higher scores."""
    df = pd.DataFrame({
        "Sensor_A": [10.0] * 10 + [25.0] * 40,   # Deviates at index 10
        "Sensor_B": [50.0] * 25 + [80.0] * 25,   # Deviates at index 25
        "Sensor_C": [100.0] * 40 + [120.0] * 10, # Deviates at index 40
    })

    scores = calculate_temporal_precedence_scores(df, ["Sensor_A", "Sensor_B", "Sensor_C"])
    assert scores["Sensor_A"] > scores["Sensor_B"] > scores["Sensor_C"]
    assert scores["Sensor_A"] == 1.0


def test_granger_causality_detection():
    """Verify Granger test detects true causal relationship in synthetic lagged pair."""
    np.random.seed(42)
    n = 120
    # Independent driving signal
    cause = np.cumsum(np.random.normal(0, 1, n))
    # Effect is driven by cause with 2-step lag
    effect = np.zeros(n)
    for t in range(2, n):
        effect[t] = 0.85 * cause[t - 2] + np.random.normal(0, 0.1)

    df = pd.DataFrame({"Sensor_Cause": cause, "Sensor_Effect": effect})
    res = compute_pairwise_granger(df, [("Sensor_Cause", "Sensor_Effect"), ("Sensor_Effect", "Sensor_Cause")])

    assert res["Sensor_Cause->Sensor_Effect"]["is_causal"] == 1.0
    assert res["Sensor_Cause->Sensor_Effect"]["p_value"] < 0.05
    # Reverse should not be causal
    assert res["Sensor_Effect->Sensor_Cause"]["p_value"] > res["Sensor_Cause->Sensor_Effect"]["p_value"]


def test_graph_proximity_hops():
    """Verify directed shortest path hop calculation in flowsheet topology."""
    topo = PlantGraphTopology(use_neo4j=False)
    # Directed material flow: Feed -> Reactor -> Condenser -> Separator
    assert topo.get_unit_hop_distance("UNIT_FEED", "UNIT_REACTOR") == 1
    assert topo.get_unit_hop_distance("UNIT_REACTOR", "UNIT_CONDENSER") == 1
    assert topo.get_unit_hop_distance("UNIT_REACTOR", "UNIT_SEPARATOR") == 2
    assert topo.get_unit_hop_distance("UNIT_REACTOR", "UNIT_STRIPPER") == 3


def test_causal_scorer_known_ground_truth():
    """End-to-end test on hand-crafted scenario where true cause is known to be UNIT_REACTOR."""
    np.random.seed(42)
    n = 100

    # 1. True root cause occurs in UNIT_REACTOR (XMEAS_9) at t=20
    xmeas_9 = np.array([120.0] * 20 + [120.0 + 0.6 * i for i in range(80)])

    # 2. Disturbance flows to UNIT_CONDENSER (XMEAS_22) at t=35 with lag
    xmeas_22 = np.zeros(n)
    xmeas_22[:35] = 77.0
    for t in range(35, n):
        xmeas_22[t] = 0.7 * xmeas_9[t - 2] - 7.0 + np.random.normal(0, 0.1)

    # 3. Further propagates to UNIT_SEPARATOR (XMEAS_11) at t=50 with lag
    xmeas_11 = np.zeros(n)
    xmeas_11[:50] = 80.0
    for t in range(50, n):
        xmeas_11[t] = 0.6 * xmeas_22[t - 3] + 34.0 + np.random.normal(0, 0.1)

    test_df = pd.DataFrame({
        "XMEAS_9": xmeas_9,
        "XMEAS_22": xmeas_22,
        "XMEAS_11": xmeas_11
    })

    scorer = CausalScorer(weight_temporal=0.40, weight_graph=0.35, weight_granger=0.25)
    rankings = scorer.rank_units(
        test_df,
        manifesting_sensors=["XMEAS_9", "XMEAS_22", "XMEAS_11"]
    )

    # Verify ranking structure
    assert len(rankings) >= 3
    top_unit = rankings[0]

    # Ground truth assertion: UNIT_REACTOR must be ranked #1
    assert top_unit.unit_id == "UNIT_REACTOR", f"Expected UNIT_REACTOR as top cause, got {top_unit.unit_id}"
    assert top_unit.confidence_score > rankings[1].confidence_score
    assert top_unit.temporal_score == 1.0  # Deviated earliest
    assert top_unit.graph_proximity_score >= 0.8  # Upstream of condenser & separator
    assert "weights_used" in top_unit.evidence


def test_configurable_weights():
    """Verify that changing weights affects composite confidence calculation."""
    test_df = pd.DataFrame({
        "XMEAS_9": [120.0] * 10 + [130.0] * 40,
        "XMEAS_22": [77.0] * 30 + [85.0] * 20,
    })

    # Heavy temporal weight
    scorer_temp = CausalScorer(weight_temporal=0.90, weight_graph=0.05, weight_granger=0.05)
    rank_temp = scorer_temp.rank_units(test_df, ["XMEAS_9", "XMEAS_22"])

    # Heavy graph weight
    scorer_graph = CausalScorer(weight_temporal=0.05, weight_graph=0.90, weight_granger=0.05)
    rank_graph = scorer_graph.rank_units(test_df, ["XMEAS_9", "XMEAS_22"])

    assert rank_temp[0].unit_id == "UNIT_REACTOR"
    assert rank_temp[0].confidence_score != rank_graph[0].confidence_score


if __name__ == "__main__":
    test_temporal_precedence_order()
    test_granger_causality_detection()
    test_graph_proximity_hops()
    test_causal_scorer_known_ground_truth()
    test_configurable_weights()
    print("[PASS] All Phase 5 causal reasoning unit tests passed successfully.")
