import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_agent_tool_calling_flow(async_client: AsyncClient):
    """
    Integration Test: Verifies AI Agent reasoning loop, tool selection, 
    tool execution trace, and final response synthesis.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "agentuser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "agentuser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Call AI Agent Chat Endpoint asking for HR employee details
    agent_payload = {"prompt": "Find employee details for EMP-9942"}
    agent_resp = await async_client.post("/api/ai/agent/chat", json=agent_payload, headers=headers)
    assert agent_resp.status_code == 200
    data = agent_resp.json()

    assert "answer" in data
    assert "iterations" in data
    assert data["iterations"] > 0
    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0
    assert data["tool_calls"][0]["tool_name"] == "get_employee_info"
    assert "EMP-9942" in str(data["tool_calls"][0]["tool_args"])
