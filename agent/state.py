"""Agent state definitions for LangGraph Root Cause Analysis workflow."""

from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field


class AgentState(TypedDict, total=False):
    """LangGraph execution state representing evidence collection and synthesis."""
    anomaly_event: Dict[str, Any]
    deviating_sensors: List[str]
    time_window_start: Optional[str]
    time_window_end: Optional[str]
    kg_context: Dict[str, Any]
    candidate_fault_modes: List[Dict[str, Any]]
    telemetry_summary: Dict[str, Any]
    telemetry_data: Optional[Any]
    ranked_causes: List[Dict[str, Any]]
    ranked_sensors: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    evidence_list: List[str]
    explanation_text: str
    similar_cases: List[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    error: Optional[str]
