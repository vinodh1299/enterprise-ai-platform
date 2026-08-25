from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TestCaseEvalResult(BaseModel):
    """
    RAG Triad metrics result for a single test case.
    """
    test_id: int
    question: str
    context_relevance: float = Field(..., ge=0.0, le=1.0)
    faithfulness: float = Field(..., ge=0.0, le=1.0)
    answer_relevance: float = Field(..., ge=0.0, le=1.0)
    rag_triad_score: float = Field(..., ge=0.0, le=1.0)
    generated_answer: str


class RAGEvalReportResponse(BaseModel):
    """
    Response schema returning aggregated benchmark scores across all test cases.
    """
    total_test_cases: int
    avg_context_relevance: float
    avg_faithfulness: float
    avg_answer_relevance: float
    overall_rag_score: float
    results: List[TestCaseEvalResult]
    report_file: str
