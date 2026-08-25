# Phase 5: Hybrid Search & Reranking

## Explain Like I'm 10
Imagine searching for a book in a massive library:
1. **Semantic Vector Search (The Concept Detective):** Asks *"Find books about remote work policies"*. It understands meanings, but it misses exact codes like `"EMP-9942"`.
2. **Lexical Keyword Search (The Exact Word Inspector):** Asks *"Find the page containing the exact string 'EMP-9942'"*. It doesn't care about meaning—it only cares about matching exact letters and numbers!
3. **Reciprocal Rank Fusion (RRF):** Combines the list from the Concept Detective and the Exact Word Inspector into one master list.
4. **Cross-Encoder Reranker:** Looks closely at the master list and re-ranks the top 3 best pages to hand to the AI.

---

## Technical Definition
* **Hybrid Search:** Information Retrieval architecture combining dense vector similarity search (semantic matching via embeddings) with sparse lexical search (exact term frequency/BM25 matching).
* **Reciprocal Rank Fusion (RRF):** An un-calibrated rank-merging algorithm combining distinct retrieval candidate lists based on reciprocal rank positions ($\text{RRF}(d) = \sum_{m} \frac{1}{k + r_m(d)}$).
* **Cross-Encoder Reranker:** A full-attention neural model that jointly processes query and candidate document text together ($\text{CrossEncoder}(Q, D)$), capturing fine-grained token-level cross-interactions to score relevance with maximum precision.

---

## How Hybrid RAG Works Step-by-Step

```text
                       [ User Query: "Find details for EMP-9942" ]
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       [ 1. Dense Vector Search ]                     [ 2. Sparse Lexical Search ]
       (Semantic Meaning Match)                        (Exact Keyword / BM25 Match)
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           ▼
                            [ 3. Reciprocal Rank Fusion ]
                            (Combines Ranks: RRF Score)
                                           │
                                           ▼
                            [ 4. Cross-Encoder Reranker ]
                            (Refines Top-3 Highest Matches)
                                           │
                                           ▼
                            [ 5. Grounded LLM Generation ]
                            (Answer + Clickable Citations)
```

---

## Where We Use It in Our Project
* [`backend/app/ai/rag/lexical.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/rag/lexical.py): Keyword search engine matching exact alphanumeric codes.
* [`backend/app/ai/rag/reranker.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/rag/reranker.py): Reciprocal Rank Fusion (RRF) and Cross-Encoder candidate re-scoring.
* [`backend/app/ai/rag/pipeline.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/rag/pipeline.py): `run_hybrid_rag_pipeline` orchestrator.
* [`backend/app/api/rag.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/api/rag.py): `POST /api/search/hybrid` and `POST /api/ai/rag/hybrid` endpoints.
* [`backend/tests/test_hybrid_rag.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/tests/test_hybrid_rag.py): Integration test suite.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: Why does pure vector search often fail on exact alphanumeric codes like product SKUs or employee IDs?**
   * *A:* Dense embedding models compress entire sentences into fixed-dimensional continuous vector space. Unique identifiers like `"EMP-9942"` or `"SKU-882"` represent out-of-vocabulary or low-frequency sub-word tokens whose semantic vector direction gets smoothed out during embedding pooling, making pure geometric vector distance unreliable for exact matching.
2. **Q: What is the primary difference between a Bi-Encoder and a Cross-Encoder?**
   * *A:* A Bi-Encoder processes query and document independently into separate vectors, allowing fast pre-indexed vector database lookups (low latency, lower precision). A Cross-Encoder feeds the query and document *together* into full self-attention layers, computing fine-grained token-level cross-interactions (high latency, maximum precision). RAG systems combine both by using Bi-Encoders for fast retrieval and Cross-Encoders for re-ranking top candidates.
