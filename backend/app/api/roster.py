from fastapi import APIRouter, Depends, status

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.roster import RosterOptimizationRequest, RosterOptimizationResponse
from app.ai.roster.optimizer import optimize_department_roster

router = APIRouter()


@router.post(
    "/ai/roster/optimize",
    response_model=RosterOptimizationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Predictive Analytics & HR AI"]
)
async def optimize_roster(
    request: RosterOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Smart Shift & Roster Optimization AI Endpoint.
    Schedules department shifts based on employee availability, leave dates, and skill coverage requirements.
    """
    return optimize_department_roster(request)
