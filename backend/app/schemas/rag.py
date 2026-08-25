from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.document import SearchResult


class SearchRequest(BaseModel):
    """
    Request schema for vector search endpoint (POST /api/search).
    """
    query: str = Field(..., description="The search query text", min_length=1)
    top_k: int = Field(default=3, ge=1, le=20, description="Number of top matching chunks to retrieve")


class SearchResponse(BaseModel):
    """
    Response schema for vector search endpoint.
    """
    query: str
    results: List[SearchResult]


class RAGRequest(BaseModel):
    """
    Request schema for RAG endpoint (POST /api/ai/rag).
    """
    query: str = Field(..., description="The user's question to answer using company documents", min_length=1)
    top_k: int = Field(default=3, ge=1, le=10, description="Number of retrieved context chunks")


class Citation(BaseModel):
    """
    Citation metadata pointing back to the exact source file and page.
    """
    filename: str
    page_number: int
    chunk_id: int
    text_snippet: str


class RAGResponse(BaseModel):
    """
    Response schema returning the grounded answer, citations, and execution metrics.
    """
    answer: str
    citations: List[Citation]
    retrieved_chunks_count: int
    model_name: str
    total_tokens: int
    estimated_cost_usd: float
