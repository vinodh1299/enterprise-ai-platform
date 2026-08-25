from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SQLAgentRequest(BaseModel):
    """
    Request schema for Text-to-SQL endpoint (POST /api/ai/sql/query).
    """
    prompt: str = Field(..., description="Natural language database question e.g. 'Which department had highest sales in July?'", min_length=1)


class SQLAgentResponse(BaseModel):
    """
    Response schema returning the generated SQL, security validation status, raw results, and LLM explanation.
    """
    question: str
    generated_sql: str
    is_safe: bool
    security_note: str
    raw_results: List[Dict[str, Any]]
    row_count: int
    explanation: str
    model_name: str
    total_tokens: int
    estimated_cost_usd: float
