"""FastAPI routes for anomaly monitoring and Root Cause Analysis triggering."""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from api.schemas import AnomalyEventSchema, AnalysisRequest, RCAResultSchema
from agent.graph import RCAGraphWorkflow
from anomaly_detection.detect import AnomalyDetector, AnomalyEvent
from ingestion.timescale_client import TimescaleClient

router = APIRouter(prefix="/anomalies", tags=["Anomalies & RCA"])

# In-memory store of recent detected anomalies for quick demo retrieval
RECENT_ANOMALIES: List[Dict[str, Any]] = [
    {
        "event_id": "AE-EVT-1004",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_anomaly": True,
        "overall_score": 4.82,
        "threshold": 1.085,
        "model_name": "LSTMAutoencoder",
        "fault_label": "IDV(4)",
        "top_sensor_names": ["XMEAS_9", "XMEAS_21", "XMEAS_7"],
        "deviating_sensors": [
            {
                "sensor_id": "XMEAS_9",
                "reconstruction_error": 6.84,
                "current_value": 134.2,
                "z_score": 3.8,
                "direction": "HIGH"
            },
            {
                "sensor_id": "XMEAS_21",
                "reconstruction_error": 5.12,
                "current_value": 110.4,
                "z_score": 3.2,
                "direction": "HIGH"
            },
            {
                "sensor_id": "XMEAS_7",
                "reconstruction_error": 2.45,
                "current_value": 2835.0,
                "z_score": 2.1,
                "direction": "HIGH"
            }
        ]
    },
    {
        "event_id": "AE-EVT-1006",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_anomaly": True,
        "overall_score": 3.95,
        "threshold": 1.085,
        "model_name": "LSTMAutoencoder",
        "fault_label": "IDV(6)",
        "top_sensor_names": ["XMEAS_1", "XMEAS_6", "XMEAS_7"],
        "deviating_sensors": [
            {
                "sensor_id": "XMEAS_1",
                "reconstruction_error": 7.42,
                "current_value": 0.01,
                "z_score": -4.2,
                "direction": "LOW"
            },
            {
                "sensor_id": "XMEAS_6",
                "reconstruction_error": 3.15,
                "current_value": 31.2,
                "z_score": -2.6,
                "direction": "LOW"
            }
        ]
    }
]

# Shared RCA agent workflow runner
WORKFLOW_RUNNER = RCAGraphWorkflow()


@router.get("", response_model=List[Dict[str, Any]])
async def list_recent_anomalies():
    """Get list of recently detected plant anomalies."""
    return RECENT_ANOMALIES


@router.get("/{event_id}", response_model=Dict[str, Any])
async def get_anomaly_by_id(event_id: str):
    """Retrieve details for a specific anomaly event."""
    for event in RECENT_ANOMALIES:
        if event.get("event_id") == event_id:
            return event
    raise HTTPException(status_code=404, detail=f"Anomaly event '{event_id}' not found.")


@router.post("/analyze", response_model=RCAResultSchema)
async def trigger_rca_analysis(req: AnalysisRequest):
    """Trigger the LangGraph Root Cause Analysis workflow on an anomaly event."""
    deviating = req.deviating_sensors or ["XMEAS_9", "XMEAS_21"]
    event_id = req.event_id or f"AE-EVT-{uuid.uuid4().hex[:6].upper()}"

    # Build input event dictionary for agent
    input_payload = req.anomaly_event or {
        "event_id": event_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": 4.5,
        "overall_score": 4.5,
        "threshold": 1.085,
        "top_sensor_names": deviating,
        "affected_sensors": [{"sensor_id": s} for s in deviating],
    }

    try:
        final_state = WORKFLOW_RUNNER.run(input_payload)

        return RCAResultSchema(
            event_id=event_id,
            ranked_causes=final_state.get("ranked_causes", []),
            confidence_scores=final_state.get("confidence_scores", {}),
            evidence_list=final_state.get("evidence_list", []),
            explanation_text=final_state.get("explanation_text", ""),
            final_report=final_state.get("final_report", {}),
            explanation_report=final_state.get("final_report", {}),
            candidate_fault_modes=final_state.get("candidate_fault_modes", []),
            telemetry_summary=final_state.get("telemetry_summary", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RCA Workflow execution failed: {str(e)}")
