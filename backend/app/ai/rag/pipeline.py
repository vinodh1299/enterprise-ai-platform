import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.rag import RAGResponse, Citation
from app.ai.rag.retriever import retrieve_top_k_chunks
from app.ai.rag.lexical import lexical_keyword_search
from app.ai.rag.reranker import reciprocal_rank_fusion, rerank_candidate_chunks
from app.ai.llm.client import llm_client

logger = logging.getLogger(__name__)


async def run_rag_pipeline(
    db: AsyncSession,
    query: str,
    owner_id: int,
    top_k: int = 3
) -> RAGResponse:
    """
    Standard Vector RAG Pipeline.
    """
    retrieved_chunks = await retrieve_top_k_chunks(db, query_text=query, owner_id=owner_id, top_k=top_k)
    return await _generate_rag_response_from_chunks(query, retrieved_chunks)


async def run_hybrid_rag_pipeline(
    db: AsyncSession,
    query: str,
    owner_id: int,
    top_k: int = 3
) -> RAGResponse:
    """
    Upgraded Hybrid RAG Pipeline:
    1. Runs Vector Search (Semantic meaning) AND Lexical Search (Exact keyword/code match).
    2. Combines results using Reciprocal Rank Fusion (RRF).
    3. Refines candidates with Reranker Cross-Encoder scoring.
    4. Generates grounded LLM response with verifiable citations.
    """
    # 1. Fetch Vector & Lexical candidate pools
    vector_results = await retrieve_top_k_chunks(db, query_text=query, owner_id=owner_id, top_k=top_k * 2)
    lexical_results = await lexical_keyword_search(db, query_text=query, owner_id=owner_id, top_k=top_k * 2)

    # 2. Reciprocal Rank Fusion
    fused_candidates = reciprocal_rank_fusion(vector_results, lexical_results, k_constant=60)

    # 3. Reranker
    reranked_chunks = rerank_candidate_chunks(query, fused_candidates, top_k=top_k)

    # 4. Generate grounded LLM response
    return await _generate_rag_response_from_chunks(query, reranked_chunks)


async def _generate_rag_response_from_chunks(
    query: str,
    retrieved_chunks: List
) -> RAGResponse:

    if not retrieved_chunks:
        return RAGResponse(
            answer="I could not find any relevant documents in your uploaded files to answer this question.",
            citations=[],
            retrieved_chunks_count=0,
            model_name="none",
            total_tokens=0,
            estimated_cost_usd=0.0
        )

    context_str = ""
    citations: List[Citation] = []

    for idx, chunk in enumerate(retrieved_chunks, 1):
        context_str += (
            f"--- EXCERPT {idx} [Source: {chunk.filename}, Page {chunk.page_number}] ---\n"
            f"{chunk.content}\n\n"
        )
        citations.append(Citation(
            filename=chunk.filename,
            page_number=chunk.page_number,
            chunk_id=chunk.chunk_id,
            text_snippet=chunk.content[:150] + ("..." if len(chunk.content) > 150 else "")
        ))

    system_instruction = (
        "You are an authoritative Enterprise AI Assistant. "
        "Answer the user's question using ONLY the provided EXCERPT CONTEXT below. "
        "Do NOT use outside knowledge or make assumptions. "
        "If the provided context does not contain the answer, explicitly state: "
        "'Based on the provided documents, I cannot find the answer to your question.' "
        "Keep your answer factual, direct, and concise. Mention the source document names when referencing facts."
    )

    full_prompt = (
        f"CONTEXT EXCERPTS:\n{context_str}\n"
        f"USER QUESTION:\n{query}"
    )

    llm_response = await llm_client.generate_chat_response(
        prompt=full_prompt,
        system_instruction=system_instruction,
        temperature=0.2
    )

    return RAGResponse(
        answer=llm_response.answer,
        citations=citations,
        retrieved_chunks_count=len(retrieved_chunks),
        model_name=llm_response.model_name,
        total_tokens=llm_response.total_tokens,
        estimated_cost_usd=llm_response.estimated_cost_usd
    )
