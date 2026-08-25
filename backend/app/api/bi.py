from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.analytics import BIAnalyticsRequest, BIAnalyticsResponse
from app.ai.analytics.bi_engine import run_bi_analytics_pipeline

router = APIRouter()


@router.post("/ai/bi/analytics", response_model=BIAnalyticsResponse, tags=["BI & Analytics"])
async def bi_analytics_query(
    request: BIAnalyticsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Automated BI & Business Intelligence Analytics Endpoint:
    Computes key performance indicators (KPIs), aggregates sales revenue metrics,
    structures JSON data series for frontend UI charts, and synthesizes C-level executive insights.
    """
    try:
        response = await run_bi_analytics_pipeline(
            db=db,
            query=request.prompt,
            period=request.period or "Q3"
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BI Analytics Pipeline Error: {str(e)}"
        )
