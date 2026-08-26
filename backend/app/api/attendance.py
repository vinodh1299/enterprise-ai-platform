from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.attendance import AttendanceAnomalySummary
from app.ai.analytics.anomaly import detect_attendance_anomalies

router = APIRouter()


@router.get(
    "/analytics/attendance/anomalies",
    response_model=AttendanceAnomalySummary,
    status_code=status.HTTP_200_OK,
    tags=["Predictive Analytics & HR AI"]
)
async def get_attendance_anomalies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Predictive Attendance Anomaly & Burnout Risk AI Endpoint.
    Analyzes clock-in/out patterns, late arrival trends, and employee burnout risks.
    """
    return await detect_attendance_anomalies(db=db)
