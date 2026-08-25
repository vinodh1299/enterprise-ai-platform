import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_chat_endpoint_protected_and_returns_response(async_client: AsyncClient):
    """
    Test: POST /api/ai/chat returns 401 without auth token, and returns valid response when authenticated.
    """
    # 1. Verify endpoint rejects unauthenticated requests
    unauth_resp = await async_client.post("/api/ai/chat", json={"prompt": "Hello AI"})
    assert unauth_resp.status_code == 401

    # 2. Register & login user
    await async_client.post("/api/users", json={"email": "aiuser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "aiuser@enterprise.com", "password": "PassWord123!"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 3. Call /api/ai/chat with token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "prompt": "What is enterprise AI?",
        "temperature": 0.5,
        "system_instruction": "You are a concise tech expert."
    }
    chat_resp = await async_client.post("/api/ai/chat", json=payload, headers=headers)
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert "answer" in data
    assert "model_name" in data
    assert data["input_tokens"] > 0
    assert "total_tokens" in data
    assert "estimated_cost_usd" in data
