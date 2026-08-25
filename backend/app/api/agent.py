from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.agent import AgentRequest, AgentResponse
from app.ai.agents.orchestrator import run_agent_loop

router = APIRouter()


@router.post("/ai/agent/chat", response_model=AgentResponse, tags=["AI Agents & Tools"])
async def agent_chat(
    request: AgentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Autonomous AI Agent Endpoint:
    Processes user requests by dynamically selecting and executing registered enterprise tools
    (Document Search, HR Lookup, Sales BI Analytics, Support Ticketing) in a reasoning loop.
    """
    try:
        response = await run_agent_loop(
            db=db,
            prompt=request.prompt,
            owner_id=current_user.id,
            max_iterations=5
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent Execution Failed: {str(e)}"
        )
