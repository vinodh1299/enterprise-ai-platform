import math
import numpy as np
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, DocumentChunk
from app.schemas.document import SearchResult
from app.ai.embeddings.client import embedding_client


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Computes mathematical Cosine Similarity between two N-dimensional vectors.
    Returns similarity score between -1.0 and 1.0 (1.0 = identical direction/meaning).
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


async def retrieve_top_k_chunks(
    db: AsyncSession,
    query_text: str,
    owner_id: int,
    top_k: int = 3
) -> List[SearchResult]:
    """
    Retrieval Pipeline:
    1. Embeds the user query into a 384-dim vector.
    2. Queries all document chunks owned by the authenticated user.
    3. Calculates Cosine Similarity between query vector and every chunk embedding.
    4. Ranks results and returns top K most relevant chunks.
    """
    # Step 1: Embed search query
    query_vector = embedding_client.generate_single_embedding(query_text)
    if not query_vector:
        return []

    # Step 2: Fetch user document chunks from PostgreSQL
    stmt = (
        select(DocumentChunk, Document.original_name)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(Document.owner_id == owner_id)
    )
    result = await db.execute(stmt)
    records = result.all()

    # Step 3: Compute Cosine Similarity scores
    scored_results: List[Tuple[float, DocumentChunk, str]] = []
    for chunk, doc_name in records:
        if chunk.embedding:
            score = cosine_similarity(query_vector, chunk.embedding)
            scored_results.append((score, chunk, doc_name))

    # Step 4: Sort by similarity score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # Step 5: Format Top-K SearchResults
    top_results: List[SearchResult] = []
    for score, chunk, doc_name in scored_results[:top_k]:
        top_results.append(SearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            filename=doc_name,
            page_number=chunk.page_number,
            content=chunk.content,
            similarity_score=round(score, 4)
        ))

    return top_results
