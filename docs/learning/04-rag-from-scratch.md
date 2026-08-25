# Phase 4: Building RAG From Scratch (No Black-Box Frameworks)

## Explain Like I'm 10
Imagine taking an open-book exam:
1. **Retrieval (Finding the open book page):** When you ask: *"What is the international meal allowance?"*, our computer converts your question into a vector and searches PostgreSQL to find the 3 pages that match your topic.
2. **Context Injection (Handing the page to the AI):** We glue those 3 exact pages to your prompt and tell the AI: *"Answer ONLY using these 3 pages!"*
3. **Generation (Writing the answer):** The AI reads the 3 pages, writes a clear answer, and points to the exact book name and page number (**Citations**).
4. **Why the best LLM doesn't equal the best RAG:** If you give a Harvard professor (a super-smart LLM) the wrong page of instructions, they will still fail the exam! Retrieval quality is even more important than model intelligence.

---

## Technical Definition
* **Retrieval-Augmented Generation (RAG):** An architectural pattern that grounds Large Language Model generation on dynamic, domain-specific external knowledge by performing vector similarity search over an indexed document store before prompt completion.
* **Cosine Similarity:** A metric measuring the cosine of the angle between two non-zero vectors in an inner product space ($\cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$).
* **Top-K Retrieval:** Extracting the $K$ highest-scoring document chunks from the vector database.
* **Grounded Answer & Citations:** Prompt instructions constraining the LLM to generate outputs strictly conditioned on provided context strings while returning provenance metadata (document name, page number, chunk ID).

---

## How the RAG Pipeline Works Step-by-Step

```text
[ User Question: "What is international meal allowance?" ]
                       │
                       ▼
[ 1. Query Embedder ] ──> Generates 384-dim Query Vector (FastEmbed)
                       │
                       ▼
[ 2. Vector Search ]   ──> Computes Cosine Similarity across PostgreSQL DocumentChunks
                       │
                       ▼
[ 3. Top-K Chunks ]    ──> Retrieves Top 3 closest chunks (e.g. Travel_Policy_2025.txt Page 1)
                       │
                       ▼
[ 4. Grounded Prompt ] ──> Injects Excerpts + Zero-Hallucination System Prompt
                       │
                       ▼
[ 5. LLM Response ]    ──> Generates Answer + Clickable Document Citations
```

---

## Where We Use It in Our Project
* [`backend/app/ai/rag/retriever.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/rag/retriever.py): Vector similarity search engine using Cosine Similarity.
* [`backend/app/ai/rag/pipeline.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/rag/pipeline.py): End-to-end RAG orchestrator with grounded prompt templates.
* [`backend/app/api/rag.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/api/rag.py): Authenticated `POST /api/search` and `POST /api/ai/rag` API endpoints.
* [`backend/tests/test_rag.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/tests/test_rag.py): Automated integration test suite.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: Why does RAG significantly reduce hallucinations compared to zero-shot LLM prompts?**
   * *A:* Zero-shot prompts force the LLM to rely entirely on parametric memory (weights frozen during training), which can synthesize false associations. RAG shifts the task from unconstrained generation to reading comprehension by supplying authoritative external context in the prompt and instructing the model to constrain its output strictly to that context.
2. **Q: What happens if the retrieved Top-K chunks do not contain the answer to the user's question?**
   * *A:* If unconstrained, the LLM will attempt to answer using general knowledge or guess. To prevent this, grounded RAG prompts include explicit fallback instructions: *"If the answer is not present in the provided context, state that the documents do not contain the answer."*
