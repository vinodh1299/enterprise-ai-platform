from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.evaluation import RAGEvalReportResponse
from app.ai.evaluation.evaluator import run_rag_evaluation_suite

router = APIRouter()


@router.post("/ai/evaluation/run", response_model=RAGEvalReportResponse, tags=["RAG & LLM Evaluation"])
async def run_evaluation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Automated RAG & LLM Evaluation Endpoint:
    Runs the benchmark test suite against evaluation/test_dataset.json,
    computes RAG Triad scores (Context Relevance, Faithfulness, Answer Relevance),
    and saves report to evaluation/eval_report.json.
    """
    try:
        response = await run_rag_evaluation_suite(
            db=db,
            owner_id=current_user.id
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation Suite Error: {str(e)}"
        )
