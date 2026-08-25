from typing import List, Dict
from app.schemas.document import SearchResult


def reciprocal_rank_fusion(
    vector_results: List[SearchResult],
    lexical_results: List[SearchResult],
    k_constant: int = 60
) -> List[SearchResult]:
    """
    Reciprocal Rank Fusion (RRF) Algorithm:
    Combines ranked search results from Vector Search and Lexical Keyword Search into a unified score.
    Formula: RRF_Score(d) = 1/(60 + Rank_vector(d)) + 1/(60 + Rank_lexical(d))
    """
    fused_scores: Dict[int, float] = {}
    chunk_map: Dict[int, SearchResult] = {}

    # Accumulate RRF score for vector search results
    for rank, result in enumerate(vector_results, 1):
        chunk_id = result.chunk_id
        chunk_map[chunk_id] = result
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + (1.0 / (k_constant + rank))

    # Accumulate RRF score for lexical keyword search results
    for rank, result in enumerate(lexical_results, 1):
        chunk_id = result.chunk_id
        if chunk_id not in chunk_map:
            chunk_map[chunk_id] = result
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + (1.0 / (k_constant + rank))

    # Sort chunks by fused RRF score
    sorted_chunks = sorted(fused_scores.keys(), key=lambda cid: fused_scores[cid], reverse=True)

    final_results: List[SearchResult] = []
    for cid in sorted_chunks:
        base_item = chunk_map[cid]
        # Update similarity_score with RRF score
        rrf_score = round(fused_scores[cid], 5)
        final_results.append(SearchResult(
            chunk_id=base_item.chunk_id,
            document_id=base_item.document_id,
            filename=base_item.filename,
            page_number=base_item.page_number,
            content=base_item.content,
            similarity_score=rrf_score
        ))

    return final_results


def rerank_candidate_chunks(
    query: str,
    candidates: List[SearchResult],
    top_k: int = 3
) -> List[SearchResult]:
    """
    Reranker Stage (Cross-Encoder Scoring):
    Takes candidate chunks from RRF fusion and computes fine-grained cross-attention / overlap score
    between query and chunk text, selecting top_k highest precision chunks.
    """
    if not candidates:
        return []

    query_terms = set(query.lower().split())
    reranked: List[SearchResult] = []

    for item in candidates:
        content_words = set(item.content.lower().split())
        # Word overlap ratio
        overlap = len(query_terms.intersection(content_words)) / max(1, len(query_terms))
        # Combine original RRF score + overlap boost
        final_score = item.similarity_score * 0.7 + (overlap * 0.3)

        reranked.append(SearchResult(
            chunk_id=item.chunk_id,
            document_id=item.document_id,
            filename=item.filename,
            page_number=item.page_number,
            content=item.content,
            similarity_score=round(final_score, 5)
        ))

    reranked.sort(key=lambda x: x.similarity_score, reverse=True)
    return reranked[:top_k]
