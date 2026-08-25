import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_rag_pipeline_end_to_end(async_client: AsyncClient):
    """
    End-to-End RAG Integration Test:
    1. Upload document -> 2. Vector similarity search -> 3. Grounded RAG answer + Citations.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "raguser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "raguser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload document containing specific company policy
    doc_content = (
        "Enterprise Travel Policy 2025.\n"
        "Section 1: Daily meal allowance for international business trips is capped at $75 USD per day.\n"
        "Section 2: Employees must book all flights at least 14 days in advance through the corporate travel portal.\n"
        "Section 3: Taxi receipts over $25 USD require manager itemized signature."
    )
    files = {"file": ("Travel_Policy_2025.txt", doc_content.encode("utf-8"), "text/plain")}

    upload_resp = await async_client.post("/api/documents/upload", files=files, headers=headers)
    assert upload_resp.status_code == 201

    # 3. Test Vector Search endpoint (POST /api/search)
    search_payload = {"query": "What is the daily meal allowance?", "top_k": 2}
    search_resp = await async_client.post("/api/search", json=search_payload, headers=headers)
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert len(search_data["results"]) > 0
    assert isinstance(search_data["results"][0]["similarity_score"], float)

    # 4. Test Full RAG Endpoint (POST /api/ai/rag)
    rag_payload = {"query": "What is the meal allowance for international trips?", "top_k": 2}
    rag_resp = await async_client.post("/api/ai/rag", json=rag_payload, headers=headers)
    assert rag_resp.status_code == 200
    rag_data = rag_resp.json()

    assert "answer" in rag_data
    assert rag_data["retrieved_chunks_count"] > 0
    assert len(rag_data["citations"]) > 0
    assert rag_data["citations"][0]["filename"] == "Travel_Policy_2025.txt"
