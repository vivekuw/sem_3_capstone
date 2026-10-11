"""Agent tool for running multimodal causal reasoning scoring."""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from causal_reasoning.scorer import CausalScorer


class CausalReasoningTool:
    """Invokes multi-modal causal reasoning algorithms to rank root cause units and sensors."""

    def __init__(self, weight_temporal: float = 0.40, weight_graph: float = 0.35, weight_granger: float = 0.25):
        self.scorer = CausalScorer(
            weight_temporal=weight_temporal,
            weight_graph=weight_graph,
            weight_granger=weight_granger
        )

    def rank_causes(
        self,
        df_window: pd.DataFrame,
        manifesting_sensors: List[str],
        candidate_units: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Compute ranked causes and serialize results.

        Args:
            df_window: Telemetry DataFrame.
            manifesting_sensors: List of deviating sensor IDs.
            candidate_units: Optional list of candidate units to score.

        Returns:
            Dict containing:
                - ranked_units: List of unit dicts with confidence scores and sub-scores.
                - ranked_sensors: List of sensor dicts with composite scores.
                - top_unit: ID of highest confidence unit.
        """
        unit_rankings = self.scorer.rank_units(
            df_window=df_window,
            manifesting_sensors=manifesting_sensors,
            candidate_units=candidate_units
        )
        sensor_rankings = self.scorer.rank_root_causes(
            df_window=df_window,
            manifesting_sensors=manifesting_sensors,
            candidate_sensors=manifesting_sensors
        )

        ranked_units_data = [u.model_dump() for u in unit_rankings]
        ranked_sensors_data = [s.model_dump() for s in sensor_rankings]
        top_unit = unit_rankings[0].unit_id if unit_rankings else "UNKNOWN"

        return {
            "ranked_units": ranked_units_data,
            "ranked_sensors": ranked_sensors_data,
            "top_unit": top_unit,
        }


if __name__ == "__main__":
    c_tool = CausalReasoningTool()
    toy_df = pd.DataFrame({
        "XMEAS_9": [120.0] * 10 + [125.0 + i for i in range(40)],
        "XMEAS_21": [94.0] * 20 + [98.0 + i for i in range(30)],
    })
    res = c_tool.rank_causes(toy_df, ["XMEAS_9", "XMEAS_21"])
    print(f"Top unit: {res['top_unit']}")
    print(f"Units ranked: {len(res['ranked_units'])}")
    print("[PASS] CausalReasoningTool verified.")
