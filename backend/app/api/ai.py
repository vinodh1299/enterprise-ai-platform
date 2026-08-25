from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.ai.llm.client import llm_client
from app.core.security_guard import sanitize_and_validate_prompt

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()


@router.post("/ai/chat", response_model=AIChatResponse, tags=["AI Services"])
async def chat_with_ai(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Direct LLM Chat Endpoint: Sends user prompt and conversation parameters to Gemini LLM.
    Returns generated response, token usage, and cost calculation. Protected by JWT authentication.
    """
    try:
        # Apply Prompt Security Guardrails & PII Redaction
        is_safe, sanitized_prompt, note, pii_list = sanitize_and_validate_prompt(request.prompt)

        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security Violation: {note}"
            )

        # Step 2: Check Redis Cache for Instant 5ms Latency
        import hashlib
        from app.core.cache import get_cached_response, set_cached_response

        cache_key = hashlib.sha256(f"{sanitized_prompt}:{request.system_instruction}".encode()).hexdigest()
        cached_answer = await get_cached_response(cache_key)

        if cached_answer:
            return AIChatResponse(
                answer=cached_answer,
                model_name="redis-cache-hit",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                estimated_cost_usd=0.0,
                provider="redis_cache"
            )

        response = await llm_client.generate_chat_response(
            prompt=sanitized_prompt,
            system_instruction=request.system_instruction,
            temperature=request.temperature,
            history=request.history
        )

        # Store in Redis Cache (1 hour TTL)
        await set_cached_response(cache_key, response.answer, ttl_seconds=3600)

        # Record Telemetry Metric
        try:
            from app.core.telemetry import record_telemetry
            await record_telemetry(
                db=db,
                user_id=current_user.id,
                endpoint="/api/ai/chat",
                provider=response.provider or "ollama",
                input_tokens=response.prompt_tokens,
                output_tokens=response.completion_tokens,
                cost_usd=response.estimated_cost_usd,
                total_latency_ms=120.0
            )
        except Exception:
            pass

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Service Error: {str(e)}"
        )
