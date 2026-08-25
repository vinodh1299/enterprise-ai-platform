import re
from typing import Tuple, List, Dict


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s+override",
    r"developer\s+mode",
    r"\bdan\s+mode\b",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"dump\s+(all\s+)?passwords",
    r"bypass\s+security",
    r"you\s+are\n+now\s+unrestricted",
]

PII_PATTERNS: Dict[str, str] = {
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "SECRET_API_KEY": r"\b(?:bearer|token|api_key|key|password|secret)\s*[:=]\s*[A-Za-z0-9_\-]{8,}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
}


def sanitize_and_validate_prompt(prompt: str) -> Tuple[bool, str, str, List[str]]:
    """
    Enterprise Prompt Security Inspector:
    1. Detects Direct Prompt Injection & Jailbreak attack patterns.
    2. Redacts Personally Identifiable Information (PII) & API Secrets.
    
    Returns: (is_safe: bool, sanitized_prompt: str, warning_note: str, redacted_pii_types: List[str])
    """
    prompt_lower = prompt.lower()
    redacted_pii_types: List[str] = []

    # Step 1: Detect Prompt Injection / Jailbreak Attacks
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            return (
                False,
                "[BLOCKED_DUE_TO_SECURITY_VIOLATION]",
                "Threat Detected: Direct Prompt Injection or System Override attempt blocked.",
                []
            )

    # Step 2: Redact PII Data & Secrets
    sanitized_prompt = prompt

    # Redact Secrets / API Keys
    if re.search(PII_PATTERNS["SECRET_API_KEY"], sanitized_prompt, re.IGNORECASE):
        sanitized_prompt = re.sub(PII_PATTERNS["SECRET_API_KEY"], "[REDACTED_SECRET]", sanitized_prompt, flags=re.IGNORECASE)
        redacted_pii_types.append("SECRET_API_KEY")

    # Redact SSN
    if re.search(PII_PATTERNS["SSN"], sanitized_prompt):
        sanitized_prompt = re.sub(PII_PATTERNS["SSN"], "[REDACTED_SSN]", sanitized_prompt)
        redacted_pii_types.append("SSN")

    # Redact Credit Cards
    if re.search(PII_PATTERNS["CREDIT_CARD"], sanitized_prompt):
        sanitized_prompt = re.sub(PII_PATTERNS["CREDIT_CARD"], "[REDACTED_CREDIT_CARD]", sanitized_prompt)
        redacted_pii_types.append("CREDIT_CARD")

    warning_note = "Prompt validated successfully."
    if redacted_pii_types:
        warning_note = f"Prompt validated with PII redaction applied for: {', '.join(redacted_pii_types)}"

    return True, sanitized_prompt, warning_note, redacted_pii_types
