"""Comprehensive API endpoint tests for Phase 8: FastAPI backend."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.main import app

client = TestClient(app)


def test_root_and_health_endpoints():
    """Verify root discovery endpoint and health check."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    resp_root = client.get("/")
    assert resp_root.status_code == 200
    assert resp_root.json()["service"] == "Chemical RCA Agent API"
    assert "routes" in resp_root.json()


def test_list_anomalies_endpoint():
    """Verify listing recent anomalies."""
    resp = client.get("/api/anomalies")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    first_event = data[0]
    assert "event_id" in first_event
    assert "is_anomaly" in first_event
    assert first_event["is_anomaly"] is True


def test_get_anomaly_by_id():
    """Verify querying an anomaly by specific event ID."""
    resp = client.get("/api/anomalies/AE-EVT-1004")
    assert resp.status_code == 200
    assert resp.json()["event_id"] == "AE-EVT-1004"
    assert "deviating_sensors" in resp.json()


def test_trigger_rca_analysis_endpoint():
    """Verify triggering Root Cause Analysis returns full Phase 6 structured result."""
    payload = {
        "event_id": "TEST-API-EVT-01",
        "deviating_sensors": ["XMEAS_9", "XMEAS_21"],
    }
    resp = client.post("/api/anomalies/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Verify structured Phase 6 result fields
    assert data["event_id"] == "TEST-API-EVT-01"
    assert "ranked_causes" in data
    assert isinstance(data["ranked_causes"], list)
    assert len(data["ranked_causes"]) > 0

    assert "confidence_scores" in data
    assert isinstance(data["confidence_scores"], dict)

    assert "evidence_list" in data
    assert isinstance(data["evidence_list"], list)

    assert "explanation_text" in data
    assert len(data["explanation_text"]) > 20

    assert "final_report" in data
    assert "root_cause_summary" in data["final_report"]


def test_knowledge_graph_subgraph_endpoint():
    """Verify Cytoscape graph serialization endpoint."""
    resp = client.get("/api/graph/subgraph")
    assert resp.status_code == 200
    data = resp.json()

    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)
    assert len(data["nodes"]) >= 5
    assert len(data["edges"]) >= 5

    # Check for core plant units in nodes
    node_ids = {n["id"] for n in data["nodes"]}
    assert "UNIT_REACTOR" in node_ids
    assert "UNIT_CONDENSER" in node_ids


def test_simulator_status_and_fault_listing():
    """Verify simulator status inspection and available faults endpoint."""
    resp_status = client.get("/api/simulator/status")
    assert resp_status.status_code == 200
    status_data = resp_status.json()
    assert "is_running" in status_data
    assert "latest_readings" in status_data
    assert "available_faults" in status_data

    resp_faults = client.get("/api/simulator/faults")
    assert resp_faults.status_code == 200
    faults_list = resp_faults.json()
    assert isinstance(faults_list, list)
    fault_ids = {f["id"] for f in faults_list}
    assert "cooling_water_loss" in fault_ids
    assert "feed_valve_closing" in fault_ids


def test_simulator_fault_injection_and_clearing():
    """Verify on-demand fault injection and clearing."""
    # Inject named fault
    resp_inject = client.post("/api/simulator/inject", json={"fault_code": "cooling_water_loss"})
    assert resp_inject.status_code == 200
    assert resp_inject.json()["status"] == "injected"
    assert resp_inject.json()["fault_code"] == "IDV(4)"

    # Check status reflects active fault
    resp_status = client.get("/api/simulator/status")
    assert resp_status.json()["active_fault"] == "IDV(4)"

    # Clear fault
    resp_clear = client.post("/api/simulator/clear")
    assert resp_clear.status_code == 200
    assert resp_clear.json()["status"] == "cleared"

    # Status reflects cleared
    resp_status_cleared = client.get("/api/simulator/status")
    assert resp_status_cleared.json()["active_fault"] is None


def test_operator_feedback_lifecycle():
    """Verify operator feedback submission and history retrieval."""
    feedback_payload = {
        "event_id": "TEST-EVT-FEEDBACK",
        "suggested_root_cause": "UNIT_REACTOR (Cooling Water Loss)",
        "is_confirmed": True,
        "operator_notes": "Confirmed by field inspection of valve XMV_10.",
    }
    resp_post = client.post("/api/feedback", json=feedback_payload)
    assert resp_post.status_code == 200
    fb_data = resp_post.json()
    assert fb_data["status"] == "recorded"
    assert "feedback_id" in fb_data

    # Retrieve feedback history
    resp_get = client.get("/api/feedback")
    assert resp_get.status_code == 200
    history = resp_get.json()
    assert isinstance(history, list)
    assert any(h["event_id"] == "TEST-EVT-FEEDBACK" for h in history)
