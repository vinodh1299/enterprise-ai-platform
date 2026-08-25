from typing import List, Optional
from pydantic import BaseModel, Field


class SecurityCheckRequest(BaseModel):
    """
    Request schema for Prompt Security Inspector (POST /api/ai/security/sanitize).
    """
    prompt: str = Field(..., description="Prompt text to inspect for prompt injection or PII leaks", min_length=1)


class SecurityCheckResponse(BaseModel):
    """
    Response schema returning sanitization results, threat flags, and PII redaction types.
    """
    is_safe: bool
    original_prompt: str
    sanitized_prompt: str
    threat_detected: bool
    threat_type: Optional[str] = None
    redacted_pii_types: List[str]
    warning_note: str
