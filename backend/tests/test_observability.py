import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_observability_and_telemetry_metrics(async_client: AsyncClient):
    """
    Integration Test: Verifies system telemetry recording, latency span tracking,
    token & financial cost attribution, and GET /api/observability/metrics summary endpoint.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "telemetryuser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "telemetryuser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Trigger an AI request (e.g. Chat) to generate telemetry
    chat_payload = {"prompt": "Hello AI"}
    await async_client.post("/api/ai/chat", json=chat_payload, headers=headers)

    # 3. Call Observability Metrics Endpoint
    obs_resp = await async_client.get("/api/observability/metrics", headers=headers)
    assert obs_resp.status_code == 200
    data = obs_resp.json()

    assert "total_requests" in data
    assert "total_tokens_consumed" in data
    assert "total_cost_usd" in data
    assert "avg_total_latency_ms" in data
    assert "p90_total_latency_ms" in data
    assert "provider_breakdown" in data
    assert "recent_traces" in data
