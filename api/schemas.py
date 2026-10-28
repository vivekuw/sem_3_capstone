"""Pydantic schemas for FastAPI endpoints."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# --- Anomaly Schemas ---
class SensorDeviationSchema(BaseModel):
    sensor_id: str
    reconstruction_error: float
    current_value: float
    z_score: float
    direction: str


class AnomalyEventSchema(BaseModel):
    event_id: str
    timestamp: datetime
    is_anomaly: bool
    overall_score: float
    threshold: float
    deviating_sensors: List[SensorDeviationSchema] = Field(default_factory=list)
    top_sensor_names: List[str] = Field(default_factory=list)
    model_name: Optional[str] = None
    fault_label: Optional[str] = None


class AnalysisRequest(BaseModel):
    event_id: Optional[str] = None
    deviating_sensors: Optional[List[str]] = None
    anomaly_event: Optional[Dict[str, Any]] = None
    lookback_minutes: int = 5


class RCAResultSchema(BaseModel):
    event_id: str
    ranked_causes: List[Dict[str, Any]] = Field(default_factory=list)
    ranked_sensors: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    evidence_list: List[str] = Field(default_factory=list)
    explanation_text: str = ""
    final_report: Dict[str, Any] = Field(default_factory=dict)
    explanation_report: Dict[str, Any] = Field(default_factory=dict)
    candidate_fault_modes: List[Dict[str, Any]] = Field(default_factory=list)
    telemetry_summary: Dict[str, Any] = Field(default_factory=dict)


# --- Graph Schemas ---
class GraphNode(BaseModel):
    id: str
    label: str
    name: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None


class GraphEdge(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    type: str
    label: Optional[str] = None


class SubgraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    elements: List[Dict[str, Any]] = Field(default_factory=list)


# --- Simulator Schemas ---
class FaultInjectionRequest(BaseModel):
    fault_code: str = Field(..., description="E.g., cooling_water_loss, feed_valve_closing, IDV(4), IDV(6)")


class SimulatorStatusResponse(BaseModel):
    is_running: bool
    active_fault: Optional[str] = None
    total_ticks: int = 0
    latest_readings: Dict[str, float] = Field(default_factory=dict)
    available_faults: List[Dict[str, Any]] = Field(default_factory=list)


# --- Feedback Schemas ---
class OperatorFeedbackRequest(BaseModel):
    event_id: str
    suggested_root_cause: str
    is_confirmed: bool
    operator_notes: Optional[str] = None
    actual_cause_if_different: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    feedback_id: str
    timestamp: datetime
