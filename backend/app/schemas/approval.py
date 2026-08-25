from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


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
