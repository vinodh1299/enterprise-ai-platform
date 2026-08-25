import os
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rag_evaluation_framework_suite(async_client: AsyncClient):
    """
    Integration Test: Verifies RAG Triad Evaluation Engine (LLM-as-a-Judge),
    benchmark score aggregation, and report generation in evaluation/eval_report.json.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "evaluser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "evaluser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload test document
    doc_content = "Travel Policy 2025: International meal allowance for business travel is $75 per day."
    files = {"file": ("Travel_Policy_2025.txt", doc_content.encode("utf-8"), "text/plain")}
    await async_client.post("/api/documents/upload", files=files, headers=headers)

    # 3. Call RAG Evaluation Endpoint
    eval_resp = await async_client.post("/api/ai/evaluation/run", headers=headers)
    assert eval_resp.status_code == 200
    data = eval_resp.json()

    assert data["total_test_cases"] > 0
    assert data["overall_rag_score"] > 0.0
    assert data["avg_context_relevance"] > 0.0
    assert data["avg_faithfulness"] > 0.0
    assert data["avg_answer_relevance"] > 0.0
    assert "report_file" in data
    assert os.path.exists(data["report_file"])
