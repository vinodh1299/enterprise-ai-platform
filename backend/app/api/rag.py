from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.rag import SearchRequest, SearchResponse, RAGRequest, RAGResponse
from app.ai.rag.retriever import retrieve_top_k_chunks
from app.ai.rag.lexical import lexical_keyword_search
from app.ai.rag.reranker import reciprocal_rank_fusion, rerank_candidate_chunks
from app.ai.rag.pipeline import run_rag_pipeline, run_hybrid_rag_pipeline

router = APIRouter()


@router.post("/search", response_model=SearchResponse, tags=["RAG & Retrieval"])
async def vector_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vector Search Endpoint: Performs 384-dim Cosine Similarity search over uploaded document chunks.
    """
    try:
        results = await retrieve_top_k_chunks(
            db=db,
            query_text=request.query,
            owner_id=current_user.id,
            top_k=request.top_k
        )
        return SearchResponse(query=request.query, results=results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector Search Failed: {str(e)}"
        )


@router.post("/search/hybrid", response_model=SearchResponse, tags=["RAG & Retrieval"])
async def hybrid_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Hybrid Search Endpoint: Combines Vector Search (Semantic) + Lexical Search (Keyword/BM25)
    using Reciprocal Rank Fusion (RRF) and Cross-Encoder Reranking.
    """
    try:
        vec_res = await retrieve_top_k_chunks(db, query_text=request.query, owner_id=current_user.id, top_k=request.top_k * 2)
        lex_res = await lexical_keyword_search(db, query_text=request.query, owner_id=current_user.id, top_k=request.top_k * 2)
        fused = reciprocal_rank_fusion(vec_res, lex_res)
        final_reranked = rerank_candidate_chunks(request.query, fused, top_k=request.top_k)

        return SearchResponse(query=request.query, results=final_reranked)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid Search Failed: {str(e)}"
        )


@router.post("/ai/rag", response_model=RAGResponse, tags=["RAG & Retrieval"])
async def rag_query(
    request: RAGRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Standard Vector RAG Pipeline Endpoint.
    """
    try:
        return await run_rag_pipeline(
            db=db,
            query=request.query,
            owner_id=current_user.id,
            top_k=request.top_k
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG Pipeline Error: {str(e)}"
        )


@router.post("/ai/rag/hybrid", response_model=RAGResponse, tags=["RAG & Retrieval"])
async def hybrid_rag_query(
    request: RAGRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upgraded Hybrid RAG Pipeline Endpoint: Uses Vector + Lexical Search + RRF Fusion + Reranking.
    """
    try:
        return await run_hybrid_rag_pipeline(
            db=db,
            query=request.query,
            owner_id=current_user.id,
            top_k=request.top_k
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid RAG Pipeline Error: {str(e)}"
        )
