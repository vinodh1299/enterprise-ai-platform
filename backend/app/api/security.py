from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.security import SecurityCheckRequest, SecurityCheckResponse
from app.core.security_guard import sanitize_and_validate_prompt

router = APIRouter()


@router.post("/ai/security/sanitize", response_model=SecurityCheckResponse, tags=["Security & Prompt Defenses"])
async def inspect_prompt_security(
    request: SecurityCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Prompt Security Inspector Endpoint:
    Inspects incoming prompts for Prompt Injection / Jailbreak attacks,
    automatically redacts sensitive Personally Identifiable Information (PII, SSN, Credit Cards, Secrets),
    and enforces system security guardrails.
    """
    is_safe, sanitized, note, pii_list = sanitize_and_validate_prompt(request.prompt)

    threat_type = "PROMPT_INJECTION_ATTACK" if not is_safe else None

    return SecurityCheckResponse(
        is_safe=is_safe,
        original_prompt=request.prompt,
        sanitized_prompt=sanitized,
        threat_detected=not is_safe,
        threat_type=threat_type,
        redacted_pii_types=pii_list,
        warning_note=note
    )
