"""Agent tool for generating grounded LLM explanation report."""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.prompts import RCA_SYSTEM_PROMPT, USER_ANALYSIS_TEMPLATE
from agent.llm_client import LLMClient


class ExplainReportTool:
    """Invokes LLM with strictly provided multi-modal evidence to produce operator explanation."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    def generate_report(
        self,
        anomaly_event: Dict[str, Any],
        kg_context: Dict[str, Any],
        candidate_faults: List[Dict[str, Any]],
        ranked_causes: List[Dict[str, Any]],
        evidence_list: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Constructs prompt context and queries LLM for grounded JSON RCA report.

        Args:
            anomaly_event: AnomalyEvent alert dictionary.
            kg_context: Plant flowsheet topology and upstream paths.
            candidate_faults: FailureMode records from Knowledge Graph.
            ranked_causes: Ranked candidate units and confidence scores.
            evidence_list: Optional list of specific evidence citations.

        Returns:
            Dict[str, Any]: Grounded report with explanation_text, citations, and operator actions.
        """
        user_prompt = USER_ANALYSIS_TEMPLATE.format(
            anomaly_json=json.dumps(anomaly_event, indent=2, default=str),
            kg_context_json=json.dumps(kg_context, indent=2, default=str),
            candidate_faults_json=json.dumps(candidate_faults, indent=2, default=str),
            ranked_causes_json=json.dumps(ranked_causes, indent=2, default=str),
            evidence_list_json=json.dumps(evidence_list or [], indent=2, default=str),
        )

        report = self.llm.generate_json_response(
            system_prompt=RCA_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        # Build comprehensive narrative explanation text
        summary = report.get("root_cause_summary", "Process disturbance detected.")
        fault = report.get("probable_failure_mode", "Unknown Disturbance")
        unit = report.get("primary_unit", "UNIT_REACTOR")
        citations = report.get("evidence_citations", [])
        path = report.get("propagation_path", [])
        actions = report.get("operator_actions", [])

        citations_md = "\n".join([f"- {c}" for c in citations])
        actions_md = "\n".join([f"1. {a}" if not a.startswith(("1.", "2.", "Step")) else a for a in actions])
        path_str = " -> ".join(path) if path else f"{unit} -> Downstream Units"

        explanation_text = (
            f"### Root Cause Diagnosis: {fault}\n\n"
            f"**Executive Summary**: {summary}\n\n"
            f"**Primary Disturbed Unit**: `{unit}`\n\n"
            f"**Physical Propagation Trajectory**: {path_str}\n\n"
            f"**Grounded Evidence Citations**:\n{citations_md}\n\n"
            f"**Recommended Operator Mitigation**:\n{actions_md}"
        )

        report["explanation_text"] = explanation_text
        return report


if __name__ == "__main__":
    tool = ExplainReportTool()
    sample_evt = {"event_id": "EVT-1", "score": 25.0, "affected_sensors": ["XMEAS_9", "XMEAS_21"]}
    sample_kg = {"associated_units": ["UNIT_REACTOR"]}
    sample_causes = [{"unit_id": "UNIT_REACTOR", "confidence_score": 0.92}]
    res = tool.generate_report(sample_evt, sample_kg, [], sample_causes)
    print(f"Generated explanation summary: {res.get('root_cause_summary')}")
    print("[PASS] ExplainReportTool verified.")
