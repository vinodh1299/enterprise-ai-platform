# Phase 12: RAG & LLM Evaluation Framework (RAG Triad & LLM-as-a-Judge)

## Explain Like I'm 10
Imagine being a school teacher grading exam papers:
1. **Context Relevance (The Open Book Check):** Did the student flip to the right page of the textbook? (0.0 to 1.0)
2. **Faithfulness / Groundedness (The Cheat Check):** Did the student answer ONLY using what's on the textbook page, or did they invent fake facts? (0.0 to 1.0)
3. **Answer Relevance (The Directness Check):** Did the student actually answer the question asked by the teacher? (0.0 to 1.0)
4. **The Benchmark Report:** The teacher adds up all 3 grades to give your RAG system an overall score card out of 1.0!

---

## Technical Definition
* **RAG Triad Evaluation:** An automated evaluation methodology measuring the 3 core pillars of RAG quality: Context Relevance, Faithfulness (Groundedness), and Answer Relevance.
* **LLM-as-a-Judge:** Utilizing a deterministic, zero-temperature evaluator LLM model to score qualitative generation attributes against ground truth benchmarks.
* **Regression Testing for AI:** Running automated benchmark test suites on every codebase change to ensure model upgrades or prompt modifications do not degrade accuracy.

---

## How the RAG Triad Evaluator Works

```text
[ Ground Truth Test Dataset (test_dataset.json) ]
                       │
                       ▼
            [ 1. Run RAG Pipeline ]
            (Generates Answer + Retrieves Chunks)
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
[ 2. Context Rel ] [ 3. Faithfulness ] [ 4. Answer Rel ]
 (Is context relevant?) (Is answer grounded?) (Is answer direct?)
       │               │               │
       └───────────────┼───────────────┘
                       ▼
            [ 5. RAG Triad Score ]
   (Averages metrics & saves eval_report.json)
```

---

## Where We Use It in Our Project
* [`evaluation/test_dataset.json`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/evaluation/test_dataset.json): Ground truth evaluation benchmark dataset.
* [`backend/app/ai/evaluation/evaluator.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/evaluation/evaluator.py): RAG Triad LLM-as-a-Judge evaluation engine.
* [`backend/app/schemas/evaluation.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/schemas/evaluation.py): Pydantic validation schemas.
* [`backend/app/api/evaluation.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/api/evaluation.py): Authenticated `POST /api/ai/evaluation/run` endpoint.
* [`backend/tests/test_evaluation.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/tests/test_evaluation.py): Integration test suite verifying automated benchmark execution.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: What is the RAG Triad, and why is it better than traditional BLEU / ROUGE string matching metrics?**
   * *A:* Traditional string overlap metrics (like BLEU/ROUGE) fail because LLMs paraphrase answers using different vocabulary. The RAG Triad evaluates semantic quality across 3 independent axes using LLM-as-a-Judge: (1) **Context Relevance** (Retriever precision), (2) **Faithfulness** (Hallucination detection), and (3) **Answer Relevance** (Prompt fulfillment).
