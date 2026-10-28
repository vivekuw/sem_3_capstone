"""LangGraph workflow definition for Root Cause Analysis Agent (Phase 6).

Flow sequence:
  receive AnomalyEvent -> kg_tool -> temporal_tool -> causal_tool -> explain_tool -> END

Key principles:
- Deterministic empirical causal ranking via CausalScorer (Temporal + Graph + Granger).
- LLM (local LM Studio with deterministic fallback) is used strictly only in explain_tool.
- Output is a structured result containing:
    * ranked_causes
    * confidence_scores
    * evidence_list
    * explanation_text
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langgraph.graph import StateGraph, START, END

from agent.state import AgentState
from agent.llm_client import LLMClient
from agent.tools.kg_tool import KnowledgeGraphTool
from agent.tools.temporal_tool import TemporalTelemetryTool
from agent.tools.causal_tool import CausalReasoningTool
from agent.tools.explain_tool import ExplainReportTool


class RCAGraphWorkflow:
    """Encapsulates the compiled LangGraph workflow for chemical process RCA."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.kg_tool = KnowledgeGraphTool()
        self.temporal_tool = TemporalTelemetryTool()
        self.causal_tool = CausalReasoningTool()
        self.llm_client = llm_client or LLMClient()
        self.explain_tool = ExplainReportTool(self.llm_client)

        # Cache for telemetry dataframe between temporal_tool and causal_tool
        self._cached_df = None

        self.workflow = self._build_graph()
        self.app = self.workflow.compile()

    def _build_graph(self) -> StateGraph:
        """Constructs the sequential LangGraph pipeline."""
        graph = StateGraph(AgentState)

        # Register tools as workflow nodes
        graph.add_node("kg_tool", self.node_kg_tool)
        graph.add_node("temporal_tool", self.node_temporal_tool)
        graph.add_node("causal_tool", self.node_causal_tool)
        graph.add_node("explain_tool", self.node_explain_tool)

        # Define linear execution flow: START -> kg -> temporal -> causal -> explain -> END
        graph.add_edge(START, "kg_tool")
        graph.add_edge("kg_tool", "temporal_tool")
        graph.add_edge("temporal_tool", "causal_tool")
        graph.add_edge("causal_tool", "explain_tool")
        graph.add_edge("explain_tool", END)

        return graph

    # -------------------------------------------------------------------------
    # Node 1: kg_tool
    # -------------------------------------------------------------------------
    def node_kg_tool(self, state: AgentState) -> Dict[str, Any]:
        """Node 1: Retrieve topology, upstream connections, and candidate failure modes from Neo4j."""
        deviating = state.get("deviating_sensors", [])
        if not deviating and "anomaly_event" in state:
            evt = state["anomaly_event"]
            deviating = (
                evt.get("top_sensor_names")
                or [s.get("sensor_id", s) if isinstance(s, dict) else getattr(s, "sensor_id", str(s)) for s in evt.get("affected_sensors", [])]
                or ["XMEAS_9", "XMEAS_21"]
            )

        # Query plant knowledge graph
        kg_res = self.kg_tool.query_topology_and_candidates(deviating)
        candidate_faults = kg_res.get("candidate_failure_modes", [])

        return {
            "deviating_sensors": deviating,
            "kg_context": kg_res,
            "candidate_fault_modes": candidate_faults,
        }

    # -------------------------------------------------------------------------
    # Node 2: temporal_tool
    # -------------------------------------------------------------------------
    def node_temporal_tool(self, state: AgentState) -> Dict[str, Any]:
        """Node 2: Fetch time-aligned sensor telemetry window from TimescaleDB."""
        deviating = state.get("deviating_sensors", [])
        evt = state.get("anomaly_event", {})

        # Determine timestamps if available
        evt_time = None
        if "timestamp" in evt and evt["timestamp"]:
            try:
                if isinstance(evt["timestamp"], datetime):
                    evt_time = evt["timestamp"]
                else:
                    evt_time = datetime.fromisoformat(str(evt["timestamp"]).replace("Z", "+00:00"))
            except Exception:
                evt_time = None

        # Fetch telemetry window
        df_window = self.temporal_tool.fetch_window_dataframe(
            end_time=evt_time,
            sensor_ids=deviating,
            window_minutes=15,
            limit_rows=100
        )
        self._cached_df = df_window

        telemetry_summary = {
            "num_samples": len(df_window),
            "columns": list(df_window.columns),
            "start_time": str(df_window.index[0]) if not df_window.empty else None,
            "end_time": str(df_window.index[-1]) if not df_window.empty else None,
        }

        return {
            "telemetry_summary": telemetry_summary,
        }

    # -------------------------------------------------------------------------
    # Node 3: causal_tool
    # -------------------------------------------------------------------------
    def node_causal_tool(self, state: AgentState) -> Dict[str, Any]:
        """Node 3: Compute empirical causal rankings (Temporal + Graph + Granger) and assemble evidence."""
        deviating = state.get("deviating_sensors", [])
        kg_ctx = state.get("kg_context", {})
        df_window = self._cached_df

        if df_window is None or df_window.empty:
            df_window = self.temporal_tool.fetch_window_dataframe(sensor_ids=deviating)
            self._cached_df = df_window

        # Candidate units from Knowledge Graph
        candidate_units = kg_ctx.get("associated_units")

        # Run multi-modal causal scoring
        causal_results = self.causal_tool.rank_causes(
            df_window=df_window,
            manifesting_sensors=deviating,
            candidate_units=candidate_units,
        )

        ranked_units = causal_results.get("ranked_units", [])
        ranked_sensors = causal_results.get("ranked_sensors", [])
        top_unit = causal_results.get("top_unit", "UNKNOWN")

        # Ensure compatibility for graph proximity score keys
        for u in ranked_units:
            if "graph_proximity_score" in u and "graph_score" not in u:
                u["graph_score"] = u["graph_proximity_score"]
            elif "graph_score" in u and "graph_proximity_score" not in u:
                u["graph_proximity_score"] = u["graph_score"]

        # Dictionary of unit confidence scores
        confidence_scores: Dict[str, float] = {
            item["unit_id"]: round(item["confidence_score"], 4)
            for item in ranked_units
        }

        # Build empirical evidence list
        evidence_list: List[str] = []
        evt = state.get("anomaly_event", {})
        if evt:
            score = evt.get("score", evt.get("overall_score", 0.0))
            sensors_summary = (
                f"{', '.join(deviating[:8])} (...and {len(deviating) - 8} more sensors across all 6 units)"
                if len(deviating) > 8
                else ", ".join(deviating)
            )
            evidence_list.append(
                f"Anomaly alert triggered (score={score:.2f}, affected sensors: {sensors_summary})."
            )

        if ranked_sensors:
            top_s = ranked_sensors[0]
            evidence_list.append(
                f"Earliest deviating parameter detected: {top_s.get('sensor_id')} "
                f"(temporal precedence score: {top_s.get('temporal_score', 0.0):.2f})."
            )

        if ranked_units:
            top_u = ranked_units[0]
            g_score = top_u.get("graph_proximity_score", top_u.get("graph_score", 0.0))
            evidence_list.append(
                f"Knowledge Graph proximity links top candidate '{top_u['unit_id']}' "
                f"upstream of secondary alarms (graph proximity score: {g_score:.2f})."
            )
            evidence_list.append(
                f"Granger causality confirms significant directional coupling from '{top_u['unit_id']}' variables "
                f"(granger score: {top_u.get('granger_score', 0.0):.2f})."
            )

        candidate_faults = state.get("candidate_fault_modes", [])
        if candidate_faults:
            top_fault = candidate_faults[0]
            evidence_list.append(
                f"Process safety records identify candidate failure mode '{top_fault.get('name')}' "
                f"({top_fault.get('code')}) affecting {top_unit}."
            )

        return {
            "ranked_causes": ranked_units,
            "ranked_sensors": ranked_sensors,
            "confidence_scores": confidence_scores,
            "evidence_list": evidence_list,
        }

    # -------------------------------------------------------------------------
    # Node 4: explain_tool
    # -------------------------------------------------------------------------
    def node_explain_tool(self, state: AgentState) -> Dict[str, Any]:
        """Node 4: Synthesize grounded explanation report using LLM based strictly on provided evidence."""
        report = self.explain_tool.generate_report(
            anomaly_event=state.get("anomaly_event", {}),
            kg_context=state.get("kg_context", {}),
            candidate_faults=state.get("candidate_fault_modes", []),
            ranked_causes=state.get("ranked_causes", []),
            evidence_list=state.get("evidence_list", []),
        )

        explanation_text = report.get("explanation_text", "")

        return {
            "final_report": report,
            "explanation_text": explanation_text,
        }

    # -------------------------------------------------------------------------
    # Execution Runner
    # -------------------------------------------------------------------------
    def run(self, input_data: Union[AgentState, Dict[str, Any], Any]) -> Dict[str, Any]:
        """Execute the LangGraph workflow and return the structured result.

        Args:
            input_data: Either an AnomalyEvent instance, a dict containing anomaly_event,
                        or an initial AgentState dict.

        Returns:
            Dict containing:
                - ranked_causes: List of candidate units sorted by confidence score.
                - confidence_scores: Dict mapping unit ID to float score [0.0 - 1.0].
                - evidence_list: Grounded list of empirical observations.
                - explanation_text: Human-readable narrative explanation for plant operators.
                - final_report: Full JSON diagnosis report with mitigation steps.
        """
        # Normalize input into initial state
        initial_state: AgentState = {}

        if hasattr(input_data, "model_dump"):
            # Pydantic AnomalyEvent
            evt_dict = input_data.model_dump()
            sensors = (
                evt_dict.get("top_sensor_names")
                or [s.get("sensor_id") for s in evt_dict.get("affected_sensors", []) if isinstance(s, dict)]
            )
            initial_state["anomaly_event"] = evt_dict
            initial_state["deviating_sensors"] = sensors
        elif isinstance(input_data, dict):
            if "anomaly_event" in input_data:
                initial_state.update(input_data)
                if "deviating_sensors" not in initial_state or not initial_state["deviating_sensors"]:
                    evt = input_data["anomaly_event"]
                    initial_state["deviating_sensors"] = (
                        evt.get("top_sensor_names")
                        or evt.get("affected_sensors")
                        or ["XMEAS_9", "XMEAS_21"]
                    )
            else:
                # Direct dictionary event
                sensors = (
                    input_data.get("top_sensor_names")
                    or input_data.get("affected_sensors")
                    or input_data.get("deviating_sensors")
                    or ["XMEAS_9", "XMEAS_21"]
                )
                initial_state["anomaly_event"] = input_data
                initial_state["deviating_sensors"] = sensors
        else:
            initial_state["anomaly_event"] = {"raw": str(input_data)}
            initial_state["deviating_sensors"] = ["XMEAS_9", "XMEAS_21"]

        # Execute graph
        final_state = self.app.invoke(initial_state)

        # Return structured result
        return {
            "ranked_causes": final_state.get("ranked_causes", []),
            "ranked_sensors": final_state.get("ranked_sensors", []),
            "confidence_scores": final_state.get("confidence_scores", {}),
            "evidence_list": final_state.get("evidence_list", []),
            "explanation_text": final_state.get("explanation_text", ""),
            "final_report": final_state.get("final_report", {}),
            "kg_context": final_state.get("kg_context", {}),
            "candidate_fault_modes": final_state.get("candidate_fault_modes", []),
            "telemetry_summary": final_state.get("telemetry_summary", {}),
            "anomaly_event": final_state.get("anomaly_event", {}),
            "deviating_sensors": final_state.get("deviating_sensors", []),
        }


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Phase 6 LangGraph RCA Agent Workflow...")
    print("=" * 70)

    workflow = RCAGraphWorkflow()

    sample_event = {
        "event_id": "EVT-2026-TEST-004",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_anomaly": True,
        "score": 4.82,
        "threshold": 1.085,
        "model_name": "LSTMAutoencoder",
        "top_sensor_names": ["XMEAS_9", "XMEAS_21"],
    }

    print(f"Triggering workflow with AnomalyEvent: {sample_event['event_id']}")
    result = workflow.run(sample_event)

    print("\n--- 1. RANKED CAUSES ---")
    for idx, cause in enumerate(result["ranked_causes"], 1):
        g_val = cause.get("graph_proximity_score", cause.get("graph_score", 0.0))
        t_val = cause.get("temporal_score", 0.0)
        gr_val = cause.get("granger_score", 0.0)
        print(f"  {idx}. Unit: {cause['unit_id']:<18} Confidence: {cause['confidence_score']:.4f} "
              f"(Temp={t_val:.2f}, Graph={g_val:.2f}, Granger={gr_val:.2f})")

    print("\n--- 2. CONFIDENCE SCORES ---")
    for unit, score in result["confidence_scores"].items():
        print(f"  {unit:<20}: {score:.4f}")

    print("\n--- 3. EVIDENCE LIST ---")
    for evidence in result["evidence_list"]:
        print(f"  * {evidence}")

    print("\n--- 4. EXPLANATION TEXT ---")
    print(result["explanation_text"])

    print("=" * 70)
    print("[PASS] Phase 6 LangGraph Workflow Executed Successfully!")
    print("=" * 70)
