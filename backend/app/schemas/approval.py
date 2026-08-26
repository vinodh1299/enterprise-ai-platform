from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class ApprovalTaskResponse(BaseModel):
    """
    Pydantic schema for returning staged approval tasks.
    """
    id: int
    action_type: str
    action_payload: Dict[str, Any]
    risk_level: str
    status: str
    requester_id: int
    reviewer_id: Optional[int] = None
    rejection_reason: Optional[str] = None
    requested_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalActionRequest(BaseModel):
    """
    Request schema for approving or rejecting a staged task.
    """
    reason: Optional[str] = None


class AuditLogResponse(BaseModel):
    """
    Pydantic schema for returning audit log entries.
    """
    id: int
    action_type: str
    actor_id: int
    target_resource: str
    payload: Dict[str, Any]
    status: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalCopilotSummary(BaseModel):
    """
    Pydantic schema for AI Manager Approval Copilot summaries.
    """
    task_id: int = Field(..., description="ID of the pending approval task")
    recommendation: str = Field(..., description="RECOMMEND_APPROVAL, REQUIRES_REVIEW, or RECOMMEND_REJECTION")
    confidence_score: float = Field(..., description="Confidence score from 0.0 to 1.0")
    executive_summary: str = Field(..., description="1-paragraph AI copilot reasoning summary for the manager")
    key_factors: List[str] = Field(default_factory=list, description="Bullet points of key evidence")
    policy_compliance: str = Field(..., description="Verification against corporate policy")
    conflict_risks: List[str] = Field(default_factory=list, description="Team calendar overlaps or staffing conflict warnings")
