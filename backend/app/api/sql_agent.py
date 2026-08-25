from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.sql import SQLAgentRequest, SQLAgentResponse
from app.ai.tools.sql_agent import run_text_to_sql_pipeline

router = APIRouter()


@router.post("/ai/sql/query", response_model=SQLAgentResponse, tags=["Text-to-SQL & Analytics"])
async def text_to_sql_query(
    request: SQLAgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Natural Language Text-to-SQL Endpoint:
    Translates plain English questions into safe SQL SELECT queries, validates query security,
    executes read-only queries against PostgreSQL, and returns data findings + explanation.
    """
    try:
        response = await run_text_to_sql_pipeline(
            db=db,
            user_question=request.prompt
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-SQL Pipeline Failed: {str(e)}"
        )
