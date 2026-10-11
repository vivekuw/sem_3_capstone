"""FastAPI routes for operator feedback on root cause diagnoses."""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter
from api.schemas import OperatorFeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Operator Feedback"])

OPERATOR_FEEDBACK_LOG: List[Dict[str, Any]] = []


@router.post("", response_model=FeedbackResponse)
async def submit_operator_feedback(req: OperatorFeedbackRequest):
    """Record operator confirmation or rejection of the RCA diagnosis."""
    feedback_id = f"FB-{uuid.uuid4().hex[:8].upper()}"
    entry = {
        "feedback_id": feedback_id,
        "event_id": req.event_id,
        "suggested_root_cause": req.suggested_root_cause,
        "is_confirmed": req.is_confirmed,
        "operator_notes": req.operator_notes,
        "actual_cause_if_different": req.actual_cause_if_different,
        "timestamp": datetime.now(timezone.utc)
    }
    OPERATOR_FEEDBACK_LOG.append(entry)

    return FeedbackResponse(
        status="recorded",
        feedback_id=feedback_id,
        timestamp=entry["timestamp"]
    )


@router.get("")
async def list_feedback():
    """Retrieve history of operator feedback."""
    return OPERATOR_FEEDBACK_LOG
