import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_hybrid_search_and_rag_pipeline(async_client: AsyncClient):
    """
    Integration Test: Verifies Hybrid Search (Vector + Lexical) and RRF Reranking.
    Tests exact keyword matching (e.g. employee code EMP-9942).
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "hybriduser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "hybriduser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload document with exact employee codes
    doc_content = (
        "Enterprise Employee Roster 2025.\n"
        "Employee EMP-9942 is Senior Security Architect assigned to Project Alpha.\n"
        "Employee EMP-1047 is Financial Auditor assigned to Compliance Division.\n"
        "Employee EMP-3021 is Lead Backend Engineer assigned to Platform Division."
    )
    files = {"file": ("Employee_Roster_2025.txt", doc_content.encode("utf-8"), "text/plain")}
    upload_resp = await async_client.post("/api/documents/upload", files=files, headers=headers)
    assert upload_resp.status_code == 201

    # 3. Test Hybrid Search endpoint (POST /api/search/hybrid) searching for exact code EMP-9942
    search_payload = {"query": "Find details for EMP-9942", "top_k": 2}
    search_resp = await async_client.post("/api/search/hybrid", json=search_payload, headers=headers)
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert len(search_data["results"]) > 0
    assert "EMP-9942" in search_data["results"][0]["content"]

    # 4. Test Hybrid RAG endpoint (POST /api/ai/rag/hybrid)
    rag_payload = {"query": "What is the role of EMP-9942?", "top_k": 2}
    rag_resp = await async_client.post("/api/ai/rag/hybrid", json=rag_payload, headers=headers)
    assert rag_resp.status_code == 200
    rag_data = rag_resp.json()
    assert "answer" in rag_data
    assert rag_data["retrieved_chunks_count"] > 0
    assert len(rag_data["citations"]) > 0
    assert rag_data["citations"][0]["filename"] == "Employee_Roster_2025.txt"
