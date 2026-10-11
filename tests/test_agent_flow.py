"""Unit and integration tests for Phase 6: LangGraph RCA Agent workflow."""

import sys
from pathlib import Path
from datetime import datetime, timezone
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.graph import RCAGraphWorkflow
from anomaly_detection.detect import AnomalyEvent, SensorDeviation


def test_agent_graph_execution_with_dict():
    """Verify workflow executes sequentially from dict input and returns structured outputs."""
    workflow = RCAGraphWorkflow()
    initial_event = {
        "event_id": "TEST-EVT-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": 3.5,
        "threshold": 1.5,
        "top_sensor_names": ["XMEAS_9", "XMEAS_21"],
    }

    result = workflow.run(initial_event)

    # 1. Ranked causes
    assert "ranked_causes" in result
    assert isinstance(result["ranked_causes"], list)
    assert len(result["ranked_causes"]) > 0
    top_cause = result["ranked_causes"][0]
    assert "unit_id" in top_cause
    assert "confidence_score" in top_cause

    # 2. Confidence scores
    assert "confidence_scores" in result
    assert isinstance(result["confidence_scores"], dict)
    assert len(result["confidence_scores"]) > 0
    for unit, score in result["confidence_scores"].items():
        assert 0.0 <= score <= 1.0

    # 3. Evidence list
    assert "evidence_list" in result
    assert isinstance(result["evidence_list"], list)
    assert len(result["evidence_list"]) > 0

    # 4. Explanation text
    assert "explanation_text" in result
    assert isinstance(result["explanation_text"], str)
    assert len(result["explanation_text"]) > 20

    # 5. Final report
    assert "final_report" in result
    assert result["final_report"] is not None
    assert "root_cause_summary" in result["final_report"]


def test_agent_graph_execution_with_pydantic_anomaly_event():
    """Verify workflow works seamlessly with AnomalyEvent pydantic model from Phase 4."""
    workflow = RCAGraphWorkflow()
    event = AnomalyEvent(
        event_id="EVT-IDV4-001",
        timestamp=datetime.now(timezone.utc),
        is_anomaly=True,
        score=4.95,
        threshold=1.085,
        model_name="LSTMAutoencoder",
        affected_sensors=[
            SensorDeviation(
                sensor_id="XMEAS_9",
                reconstruction_error=2.45,
                current_value=128.5,
                z_score=3.8,
                direction="HIGH"
            ),
            SensorDeviation(
                sensor_id="XMEAS_21",
                reconstruction_error=1.95,
                current_value=102.1,
                z_score=3.1,
                direction="HIGH"
            )
        ],
        top_sensor_names=["XMEAS_9", "XMEAS_21"],
        fault_label="IDV(4)"
    )

    result = workflow.run(event)

    assert result["ranked_causes"] is not None
    assert len(result["ranked_causes"]) > 0
    assert "UNIT_REACTOR" in result["confidence_scores"]
    assert len(result["evidence_list"]) >= 3
    assert "Reactor" in result["explanation_text"] or "UNIT_REACTOR" in result["explanation_text"]


def test_tool_node_isolation():
    """Ensure tools run cleanly in standalone fashion."""
    workflow = RCAGraphWorkflow()

    # Step 1: KG Tool
    state_after_kg = workflow.node_kg_tool({
        "deviating_sensors": ["XMEAS_9", "XMEAS_21"],
        "anomaly_event": {"event_id": "TEST-ISOLATION"}
    })
    assert "kg_context" in state_after_kg
    assert "candidate_fault_modes" in state_after_kg

    # Step 2: Temporal Tool
    state_after_temp = workflow.node_temporal_tool({
        "deviating_sensors": ["XMEAS_9", "XMEAS_21"],
        "anomaly_event": {}
    })
    assert "telemetry_summary" in state_after_temp

    # Step 3: Causal Tool
    state_after_causal = workflow.node_causal_tool({
        "deviating_sensors": ["XMEAS_9", "XMEAS_21"],
        "kg_context": state_after_kg["kg_context"],
        "candidate_fault_modes": state_after_kg["candidate_fault_modes"],
        "anomaly_event": {"score": 3.0}
    })
    assert "ranked_causes" in state_after_causal
    assert "confidence_scores" in state_after_causal
    assert "evidence_list" in state_after_causal

    # Step 4: Explain Tool
    state_after_explain = workflow.node_explain_tool({
        "anomaly_event": {"score": 3.0},
        "kg_context": state_after_kg["kg_context"],
        "candidate_fault_modes": state_after_kg["candidate_fault_modes"],
        "ranked_causes": state_after_causal["ranked_causes"],
        "evidence_list": state_after_causal["evidence_list"],
    })
    assert "explanation_text" in state_after_explain
    assert "final_report" in state_after_explain
