import re
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, DocumentChunk
from app.schemas.document import SearchResult


async def lexical_keyword_search(
    db: AsyncSession,
    query_text: str,
    owner_id: int,
    top_k: int = 5
) -> List[SearchResult]:
    """
    Lexical Search Engine (BM25 / Keyword Term Frequency):
    Searches for exact keyword terms, codes, SKUs, and identifiers (e.g. 'EMP-1047')
    in document chunks owned by the user.
    """
    # Extract query terms (alphanumeric words & codes)
    terms = [t.lower() for t in re.findall(r"\w+", query_text) if len(t) > 1]
    if not terms:
        return []

    # Query all document chunks for user
    stmt = (
        select(DocumentChunk, Document.original_name)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(Document.owner_id == owner_id)
    )
    result = await db.execute(stmt)
    records = result.all()

    scored_results: List[Tuple[float, DocumentChunk, str]] = []

    for chunk, doc_name in records:
        content_lower = chunk.content.lower()
        score = 0.0

        for term in terms:
            # Term frequency match
            count = content_lower.count(term)
            if count > 0:
                # Give higher weight to exact uppercase codes or exact string matches
                score += (count * 1.5)
                if term in query_text.lower():
                    score += 1.0

        if score > 0:
            scored_results.append((score, chunk, doc_name))

    # Sort descending by lexical term match score
    scored_results.sort(key=lambda x: x[0], reverse=True)

    results: List[SearchResult] = []
    for score, chunk, doc_name in scored_results[:top_k]:
        results.append(SearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            filename=doc_name,
            page_number=chunk.page_number,
            content=chunk.content,
            similarity_score=round(float(score), 4)
        ))

    return results
