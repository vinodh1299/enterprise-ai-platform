from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.approval import ApprovalTask, AuditLog
from app.schemas.approval import ApprovalTaskResponse, ApprovalActionRequest, AuditLogResponse

router = APIRouter()


@router.get("/approvals/pending", response_model=List[ApprovalTaskResponse], tags=["Human-in-the-Loop Approvals"])
async def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all high-risk AI actions currently pending human manager review.
    """
    result = await db.execute(
        select(ApprovalTask)
        .where(ApprovalTask.status == "pending")
        .order_by(ApprovalTask.requested_at.desc())
    )
    return result.scalars().all()


@router.post("/approvals/{task_id}/approve", response_model=ApprovalTaskResponse, tags=["Human-in-the-Loop Approvals"])
async def approve_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a staged high-risk AI action, triggering tool execution and recording an audit log entry.
    """
    result = await db.execute(select(ApprovalTask).where(ApprovalTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Approval task #{task_id} not found.")

    if task.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Task #{task_id} is already {task.status}.")

    # Update Task Status
    task.status = "approved"
    task.reviewer_id = current_user.id
    task.reviewed_at = datetime.now(timezone.utc)

    # Record Audit Log
    audit_entry = AuditLog(
        action_type=task.action_type,
        actor_id=current_user.id,
        target_resource=f"ApprovalTask #{task.id}",
        payload=task.action_payload,
        status="executed_after_human_approval"
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(task)
    return task


@router.post("/approvals/{task_id}/reject", response_model=ApprovalTaskResponse, tags=["Human-in-the-Loop Approvals"])
async def reject_task(
    task_id: int,
    request: ApprovalActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a staged high-risk AI action. Prevents execution and records rejection audit log.
    """
    result = await db.execute(select(ApprovalTask).where(ApprovalTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Approval task #{task_id} not found.")

    if task.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Task #{task_id} is already {task.status}.")

    # Update Task Status
    task.status = "rejected"
    task.reviewer_id = current_user.id
    task.rejection_reason = request.reason or "Rejected by manager review"
    task.reviewed_at = datetime.now(timezone.utc)

    # Record Audit Log
    audit_entry = AuditLog(
        action_type=task.action_type,
        actor_id=current_user.id,
        target_resource=f"ApprovalTask #{task.id}",
        payload={"task_id": task.id, "reason": task.rejection_reason},
        status="rejected_by_human"
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(task)
    return task


@router.get("/audit-logs", response_model=List[AuditLogResponse], tags=["Human-in-the-Loop Approvals"])
async def list_audit_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch enterprise audit trail of all AI actions and approval decisions.
    """
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100)
    )
    return result.scalars().all()
