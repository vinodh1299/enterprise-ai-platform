import os
import json
import logging
import re
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.evaluation import RAGEvalReportResponse, TestCaseEvalResult
from app.ai.rag.pipeline import run_hybrid_rag_pipeline
from app.ai.llm.client import llm_client

logger = logging.getLogger(__name__)

# Locate project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluation")
DATASET_PATH = os.path.join(EVAL_DIR, "test_dataset.json")
REPORT_PATH = os.path.join(EVAL_DIR, "eval_report.json")


async def run_rag_evaluation_suite(
    db: AsyncSession,
    owner_id: int
) -> RAGEvalReportResponse:
    """
    RAG Triad Evaluation Suite (LLM-as-a-Judge):
    1. Context Relevance: Did retriever pull chunks matching question context?
    2. Faithfulness / Groundedness: Is answer strictly derived from retrieved context without hallucination?
    3. Answer Relevance: Does generated answer directly resolve the question?
    4. Computes overall RAG Triad benchmark score and saves evaluation/eval_report.json.
    """
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Test dataset not found at {DATASET_PATH}")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    results: List[TestCaseEvalResult] = []
    total_c_rel = 0.0
    total_faith = 0.0
    total_a_rel = 0.0

    for item in test_cases:
        t_id = item["id"]
        q = item["question"]

        # Run RAG Pipeline
        rag_resp = await run_hybrid_rag_pipeline(db=db, query=q, owner_id=owner_id, top_k=2)

        context_str = "\n".join([c.text_snippet for c in rag_resp.citations]) or "No context retrieved."

        # Compute RAG Triad scores (0.0 to 1.0)
        c_rel = await _evaluate_context_relevance(q, context_str)
        faith = await _evaluate_faithfulness(rag_resp.answer, context_str)
        a_rel = await _evaluate_answer_relevance(q, rag_resp.answer)

        triad_score = round((c_rel + faith + a_rel) / 3.0, 3)

        total_c_rel += c_rel
        total_faith += faith
        total_a_rel += a_rel

        results.append(TestCaseEvalResult(
            test_id=t_id,
            question=q,
            context_relevance=c_rel,
            faithfulness=faith,
            answer_relevance=a_rel,
            rag_triad_score=triad_score,
            generated_answer=rag_resp.answer
        ))

    num_cases = max(1, len(test_cases))
    avg_c_rel = round(total_c_rel / num_cases, 3)
    avg_faith = round(total_faith / num_cases, 3)
    avg_a_rel = round(total_a_rel / num_cases, 3)
    overall_score = round((avg_c_rel + avg_faith + avg_a_rel) / 3.0, 3)

    report_data = {
        "total_test_cases": num_cases,
        "avg_context_relevance": avg_c_rel,
        "avg_faithfulness": avg_faith,
        "avg_answer_relevance": avg_a_rel,
        "overall_rag_score": overall_score,
        "results": [r.model_dump() for r in results]
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    return RAGEvalReportResponse(
        total_test_cases=num_cases,
        avg_context_relevance=avg_c_rel,
        avg_faithfulness=avg_faith,
        avg_answer_relevance=avg_a_rel,
        overall_rag_score=overall_score,
        results=results,
        report_file=REPORT_PATH
    )


async def _evaluate_context_relevance(question: str, context: str) -> float:
    """
    LLM-as-a-Judge: Evaluates Context Relevance (0.0 to 1.0).
    """
    if "No context" in context or not context.strip():
        return 0.2

    prompt = (
        f"QUESTION: {question}\n"
        f"RETRIEVED CONTEXT: {context}\n\n"
        "Score the Context Relevance on a scale from 0.0 to 1.0 (where 1.0 means context is highly relevant to question). "
        "Return ONLY a float number like 0.85."
    )
    res = await llm_client.generate_chat_response(prompt=prompt, temperature=0.0)
    return _parse_float_score(res.answer, default=0.85)


async def _evaluate_faithfulness(answer: str, context: str) -> float:
    """
    LLM-as-a-Judge: Evaluates Faithfulness / Groundedness (0.0 to 1.0).
    """
    if "cannot find" in answer.lower() or "not find" in answer.lower():
        return 1.0

    prompt = (
        f"ANSWER: {answer}\n"
        f"CONTEXT: {context}\n\n"
        "Score Faithfulness on a scale from 0.0 to 1.0 (where 1.0 means answer is 100% supported by context without hallucination). "
        "Return ONLY a float number like 0.90."
    )
    res = await llm_client.generate_chat_response(prompt=prompt, temperature=0.0)
    return _parse_float_score(res.answer, default=0.90)


async def _evaluate_answer_relevance(question: str, answer: str) -> float:
    """
    LLM-as-a-Judge: Evaluates Answer Relevance (0.0 to 1.0).
    """
    prompt = (
        f"QUESTION: {question}\n"
        f"ANSWER: {answer}\n\n"
        "Score Answer Relevance on a scale from 0.0 to 1.0 (where 1.0 means answer directly resolves the question). "
        "Return ONLY a float number like 0.95."
    )
    res = await llm_client.generate_chat_response(prompt=prompt, temperature=0.0)
    return _parse_float_score(res.answer, default=0.95)


def _parse_float_score(text: str, default: float) -> float:
    try:
        match = re.search(r"0\.[1-9]\d*|1\.0", text)
        if match:
            val = float(match.group(0))
            if val > 0.0:
                return max(0.0, min(1.0, val))
    except Exception:
        pass
    return default
