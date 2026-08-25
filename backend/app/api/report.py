from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.report import ReportGenerationRequest, ReportGenerationResponse
from app.ai.reports.generator import generate_enterprise_report

router = APIRouter()


@router.post("/ai/reports/generate", response_model=ReportGenerationResponse, tags=["Business Report Generation"])
async def generate_report(
    request: ReportGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Multi-Section Business Report Generation Endpoint:
    Combines document RAG context + SQL database metrics into a formal Markdown report,
    and saves a downloadable .md file artifact.
    """
    try:
        response = await generate_enterprise_report(
            db=db,
            topic=request.topic,
            owner_id=current_user.id,
            period=request.period or "2025 Q3"
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report Generation Failed: {str(e)}"
        )
