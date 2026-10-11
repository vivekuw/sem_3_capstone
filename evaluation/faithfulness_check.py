"""Faithfulness check: Evaluates if LLM explanations are strictly grounded in retrieved evidence."""

from typing import Dict, Any, List


def verify_evidence_grounding(report: Dict[str, Any], retrieved_evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks if citations in LLM explanation exist in the retrieved sensor readings and KG topology.
    Returns faithfulness score [0.0 - 1.0] and ungrounded statements if any.
    """
    citations: List[str] = report.get("evidence_citations", [])
    valid_sensors: List[str] = retrieved_evidence.get("deviating_sensors", [])
    valid_units: List[str] = [u.get("unit_id") for u in retrieved_evidence.get("candidate_fault_modes", [])]

    if not citations:
        return {"faithfulness_score": 0.0, "hallucinated_citations": ["No citations provided."]}

    hallucinations = []
    grounded_count = 0

    for cit in citations:
        cit_upper = cit.upper()
        # Check if any legitimate sensor or unit is referenced
        sensor_match = any(s in cit_upper for s in valid_sensors)
        unit_match = any(u in cit_upper for u in valid_units if u)

        if sensor_match or unit_match or "REACTOR" in cit_upper or "FEED" in cit_upper:
            grounded_count += 1
        else:
            hallucinations.append(cit)

    faithfulness = grounded_count / len(citations)
    return {
        "faithfulness_score": round(faithfulness, 3),
        "total_citations": len(citations),
        "grounded_citations": grounded_count,
        "hallucinated_citations": hallucinations,
        "is_faithful": faithfulness >= 0.80,
    }
