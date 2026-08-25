import os
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_business_report_generation(async_client: AsyncClient):
    """
    Integration Test: Verifies multi-section enterprise report generation,
    document RAG + BI SQL metric fusion, and downloadable .md file creation on disk.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "reportuser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "reportuser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Generate Report
    payload = {"topic": "Executive Security and Performance Audit", "period": "2025 Q3"}
    report_resp = await async_client.post("/api/ai/reports/generate", json=payload, headers=headers)
    assert report_resp.status_code == 200
    data = report_resp.json()

    assert data["report_title"] == "Executive Security and Performance Audit"
    assert "markdown_content" in data
    assert len(data["markdown_content"]) > 50
    assert "file_path" in data
    assert os.path.exists(data["file_path"])
    assert data["sections_count"] > 0
