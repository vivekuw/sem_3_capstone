"""Multimodal Root Cause Scorer combining Granger causality, Temporal precedence, and KG topology.

Synthesizes three deterministic physical and statistical signals into a calibrated
confidence score per candidate unit and sensor:
1. Temporal Precedence (Who deviated first from steady state?)
2. Graph Proximity (Directed hop distance along physical process flow in Neo4j)
3. Granger Causality (Statistical predictive power over downstream sensors)
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from causal_reasoning.temporal_precedence import calculate_temporal_precedence_scores
from causal_reasoning.granger import compute_granger_outbound_score
from causal_reasoning.graph_proximity import PlantGraphTopology, SENSOR_TO_UNIT


class CandidateUnitRootCause(BaseModel):
    """Ranked physical unit diagnosis with causal evidence breakdown."""
    unit_id: str
    confidence_score: float
    temporal_score: float
    graph_proximity_score: float
    granger_score: float
    associated_sensors: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class CandidateRootCause(BaseModel):
    """Ranked sensor-level root cause candidate."""
    sensor_id: str
    unit_id: str
    composite_score: float
    temporal_score: float
    graph_proximity_score: float
    granger_score: float
    evidence: Dict[str, Any] = Field(default_factory=dict)


class CausalScorer:
    """Combines statistical time-series causality, temporal precedence, and knowledge graph structure."""

    def __init__(
        self,
        weight_temporal: float = 0.40,
        weight_graph: float = 0.35,
        weight_granger: float = 0.25,
        topology: Optional[PlantGraphTopology] = None,
    ):
        """Initialize scorer with configurable signal weights."""
        total_w = weight_temporal + weight_graph + weight_granger
        self.w_temp = weight_temporal / total_w
        self.w_graph = weight_graph / total_w
        self.w_granger = weight_granger / total_w
        self.topology = topology or PlantGraphTopology()

    def rank_units(
        self,
        df_window: pd.DataFrame,
        manifesting_sensors: List[str],
        candidate_units: Optional[List[str]] = None,
    ) -> List[CandidateUnitRootCause]:
        """Rank candidate units as potential root causes of observed anomalies.

        Args:
            df_window: Time-series telemetry window.
            manifesting_sensors: List of sensors that exceeded threshold.
            candidate_units: Optional subset of units to evaluate. If None, considers all affected units.

        Returns:
            List[CandidateUnitRootCause]: Candidate units ordered by confidence score descending.
        """
        if not manifesting_sensors or df_window.empty:
            return []

        # Identify all units containing manifesting sensors
        unit_to_sensors: Dict[str, List[str]] = {}
        for s in df_window.columns:
            if s in SENSOR_TO_UNIT:
                u = SENSOR_TO_UNIT[s]
                unit_to_sensors.setdefault(u, []).append(s)

        if candidate_units is None:
            candidate_units = list(unit_to_sensors.keys())

        # Determine manifestation units
        manifesting_units = list({SENSOR_TO_UNIT[s] for s in manifesting_sensors if s in SENSOR_TO_UNIT})
        if not manifesting_units:
            manifesting_units = candidate_units

        # 1. Temporal precedence per sensor
        all_eval_sensors = [s for s in df_window.columns if s in SENSOR_TO_UNIT and SENSOR_TO_UNIT[s] in candidate_units]
        temp_sensor_scores = calculate_temporal_precedence_scores(df_window, all_eval_sensors)

        ranked_units: List[CandidateUnitRootCause] = []

        for unit in candidate_units:
            sensors_for_unit = unit_to_sensors.get(unit, [])
            if not sensors_for_unit:
                continue

            # Unit Temporal Score: maximum temporal score among its sensors (earliest deviator in unit)
            unit_temp_scores = [temp_sensor_scores.get(s, 0.0) for s in sensors_for_unit]
            s_temp = max(unit_temp_scores) if unit_temp_scores else 0.0

            # Unit Graph Proximity Score: physical closeness to all manifesting anomaly units
            s_graph = self.topology.compute_unit_proximity(unit, manifesting_units)

            # Unit Granger Score: statistical influence of unit sensors on other manifesting sensors
            other_manifesting = [s for s in manifesting_sensors if SENSOR_TO_UNIT.get(s) != unit]
            granger_sub_scores = []
            for s in sensors_for_unit:
                if other_manifesting:
                    granger_sub_scores.append(compute_granger_outbound_score(df_window, s, other_manifesting))
            s_granger = max(granger_sub_scores) if granger_sub_scores else 0.3

            # Composite confidence score
            confidence = (
                self.w_temp * s_temp +
                self.w_graph * s_graph +
                self.w_granger * s_granger
            )

            evidence_summary = {
                "temporal_rank": f"Earliest deviation score: {s_temp:.2f}",
                "graph_hop_proximity": f"Topology flow proximity: {s_graph:.2f}",
                "granger_predictive_power": f"Outbound Granger influence: {s_granger:.2f}",
                "monitored_sensors": sensors_for_unit,
                "weights_used": {
                    "temporal": round(self.w_temp, 2),
                    "graph": round(self.w_graph, 2),
                    "granger": round(self.w_granger, 2),
                }
            }

            ranked_units.append(
                CandidateUnitRootCause(
                    unit_id=unit,
                    confidence_score=round(float(confidence), 4),
                    temporal_score=round(float(s_temp), 4),
                    graph_proximity_score=round(float(s_graph), 4),
                    granger_score=round(float(s_granger), 4),
                    associated_sensors=sensors_for_unit,
                    evidence=evidence_summary,
                )
            )

        ranked_units.sort(key=lambda u: u.confidence_score, reverse=True)
        return ranked_units

    def rank_root_causes(
        self,
        df_window: pd.DataFrame,
        manifesting_sensors: List[str],
        candidate_sensors: Optional[List[str]] = None,
    ) -> List[CandidateRootCause]:
        """Rank individual sensors as candidate root causes."""
        if not candidate_sensors:
            candidate_sensors = manifesting_sensors

        if not candidate_sensors or df_window.empty:
            return []

        temp_scores = calculate_temporal_precedence_scores(df_window, candidate_sensors)
        graph_scores = self.topology.score_sensors_against_manifestations(candidate_sensors, manifesting_sensors)

        ranked_sensors: List[CandidateRootCause] = []
        for sensor in candidate_sensors:
            s_temp = temp_scores.get(sensor, 0.0)
            s_graph = graph_scores.get(sensor, 0.0)
            other_sensors = [m for m in manifesting_sensors if m != sensor]
            s_granger = compute_granger_outbound_score(df_window, sensor, other_sensors) if other_sensors else 0.5

            composite = (
                self.w_temp * s_temp +
                self.w_graph * s_graph +
                self.w_granger * s_granger
            )
            unit = SENSOR_TO_UNIT.get(sensor, "UNKNOWN_UNIT")

            ranked_sensors.append(
                CandidateRootCause(
                    sensor_id=sensor,
                    unit_id=unit,
                    composite_score=round(float(composite), 4),
                    temporal_score=round(float(s_temp), 4),
                    graph_proximity_score=round(float(s_graph), 4),
                    granger_score=round(float(s_granger), 4),
                    evidence={
                        "temporal": s_temp,
                        "graph": s_graph,
                        "granger": s_granger,
                    }
                )
            )

        ranked_sensors.sort(key=lambda s: s.composite_score, reverse=True)
        return ranked_sensors


if __name__ == "__main__":
    print("--- Causal Scorer Standalone Test ---")
    np.random.seed(42)
    n = 100
    # Simulate known propagation: Reactor -> Condenser -> Separator
    # Reactor temperature drifts at step 20
    s_reac = np.array([120.0] * 20 + [120.0 + 0.5 * i for i in range(80)])
    # Condenser cooling return lags at step 35
    s_cond = np.zeros(n)
    s_cond[:35] = 77.0
    for t in range(35, n):
        s_cond[t] = 0.7 * s_reac[t - 3] - 7.0 + np.random.normal(0, 0.1)
    # Separator temperature lags at step 50
    s_sep = np.zeros(n)
    s_sep[:50] = 80.0
    for t in range(50, n):
        s_sep[t] = 0.6 * s_cond[t - 4] + 34.0 + np.random.normal(0, 0.1)

    toy_df = pd.DataFrame({
        "XMEAS_9": s_reac,
        "XMEAS_22": s_cond,
        "XMEAS_11": s_sep
    })

    scorer = CausalScorer()
    unit_rankings = scorer.rank_units(
        toy_df,
        manifesting_sensors=["XMEAS_9", "XMEAS_22", "XMEAS_11"]
    )

    print("\nRanked Units by Root Cause Confidence:")
    for rank, u in enumerate(unit_rankings, 1):
        print(f"#{rank} {u.unit_id:<16} Confidence: {u.confidence_score:.4f} "
              f"(Temp={u.temporal_score:.2f}, Graph={u.graph_proximity_score:.2f}, Granger={u.granger_score:.2f})")

    assert unit_rankings[0].unit_id == "UNIT_REACTOR", "Top root cause must be UNIT_REACTOR!"
    print("\n[PASS] CausalScorer verified successfully.")
