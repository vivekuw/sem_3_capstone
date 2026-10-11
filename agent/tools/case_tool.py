"""Agent tool for retrieving similar historical incident cases."""

from typing import List, Dict, Any

PAST_INCIDENT_DATABASE = [
    {
        "case_id": "INC-2024-001",
        "title": "Cooling Water Pump Header Pressure Drop",
        "symptoms": ["XMEAS_9", "XMEAS_21"],
        "root_cause": "Reactor Cooling Water Inlet Temp Step Increase (IDV 4)",
        "resolution": "Auxiliary cooling chiller energized; valve XMV_10 repositioned to 68%."
    },
    {
        "case_id": "INC-2024-002",
        "title": "Feed Stream 1 Supply Line Blockage",
        "symptoms": ["XMEAS_1", "XMEAS_7"],
        "root_cause": "A Feed Loss (IDV 6)",
        "resolution": "Filter screen flushed on Stream 1 feed manifold."
    },
    {
        "case_id": "INC-2023-089",
        "title": "Reactor Temperature Controller Oscillation",
        "symptoms": ["XMEAS_9", "XMEAS_21", "XMV_10"],
        "root_cause": "Reactor Cooling Water Valve Sticking (IDV 11)",
        "resolution": "Pneumatic actuator lubricated and recalibrated during scheduled maintenance."
    }
]


class CaseBasedReasoningTool:
    """Finds similar historical chemical plant incidents matching symptom profiles."""

    def find_similar_cases(self, deviating_sensors: List[str], top_k: int = 2) -> List[Dict[str, Any]]:
        """Calculate Jaccard similarity between current symptoms and historical cases."""
        current_set = set(deviating_sensors)
        scored_cases = []

        for case in PAST_INCIDENT_DATABASE:
            case_set = set(case["symptoms"])
            intersection = len(current_set.intersection(case_set))
            union = len(current_set.union(case_set))
            sim = intersection / union if union > 0 else 0.0

            scored_cases.append({
                **case,
                "similarity_score": round(sim, 2)
            })

        scored_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_cases[:top_k]
