import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_bi_analytics_pipeline(async_client: AsyncClient):
    """
    Integration Test: Verifies BI Analytics engine, KPI calculations, 
    UI chart data series generation, and executive summary synthesis.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "biuser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "biuser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Call BI Analytics Endpoint
    payload = {"prompt": "Analyze sales revenue growth across departments", "period": "Q3"}
    bi_resp = await async_client.post("/api/ai/bi/analytics", json=payload, headers=headers)
    assert bi_resp.status_code == 200
    data = bi_resp.json()

    assert "kpis" in data
    assert len(data["kpis"]) > 0
    assert "chart_data" in data
    assert len(data["chart_data"]) > 0
    assert data["chart_data"][0]["value"] > 0
    assert "executive_summary" in data
    assert len(data["recommendations"]) > 0
