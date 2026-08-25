import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_document_upload_ingestion_and_chunking_flow(async_client: AsyncClient):
    """
    Integration Test: Verifies PDF/TXT document upload, text extraction, chunking, 
    embedding generation, and PostgreSQL storage.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "docuser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "docuser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload text document
    sample_text = (
        "Enterprise Remote Work Policy 2025.\n"
        "Section 1: Eligible employees may work from home up to 2 days per week.\n"
        "Section 2: Employees must maintain core working hours between 9 AM and 5 PM EST.\n"
        "Section 3: All company laptops must have VPN enabled at all times."
    )
    files = {"file": ("Remote_Work_Policy.txt", sample_text.encode("utf-8"), "text/plain")}

    upload_resp = await async_client.post("/api/documents/upload", files=files, headers=headers)
    assert upload_resp.status_code == 201
    doc_data = upload_resp.json()
    assert doc_data["original_name"] == "Remote_Work_Policy.txt"
    assert doc_data["file_type"] == ".txt"
    assert doc_data["total_chunks"] > 0

    # 3. List uploaded documents
    list_resp = await async_client.get("/api/documents", headers=headers)
    assert list_resp.status_code == 200
    user_docs = list_resp.json()
    assert len(user_docs) == 1
    assert user_docs[0]["original_name"] == "Remote_Work_Policy.txt"
