import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_manager_approval_copilot_feature(async_client: AsyncClient):
    """
    Integration Test: Verifies Manager Approval Copilot AI (Feature 2).
    1. Stages a high-risk AI action -> 2. Requests GET /api/approvals/{task_id}/copilot-summary ->
    3. Verifies AI recommendation, conflict analysis, and confidence score.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "copilot_manager@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "copilot_manager@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Stage a high-risk task using Agent
    agent_resp = await async_client.post(
        "/api/ai/agent/chat",
        json={"prompt": "Create an urgent support ticket for Production Database Outage"},
        headers=headers
    )
    assert agent_resp.status_code == 200

    # 3. List Pending Approvals
    pending_resp = await async_client.get("/api/approvals/pending", headers=headers)
    assert pending_resp.status_code == 200
    pending_tasks = pending_resp.json()
    assert len(pending_tasks) > 0

    target_task = pending_tasks[0]
    task_id = target_task["id"]

    # 4. Fetch AI Copilot Summary
    copilot_resp = await async_client.get(f"/api/approvals/{task_id}/copilot-summary", headers=headers)
    assert copilot_resp.status_code == 200
    summary_json = copilot_resp.json()

    assert summary_json["task_id"] == task_id
    assert "recommendation" in summary_json
    assert summary_json["recommendation"] in ["RECOMMEND_APPROVAL", "REQUIRES_REVIEW", "RECOMMEND_REJECTION"]
    assert "executive_summary" in summary_json
    assert len(summary_json["executive_summary"]) > 0
    assert "policy_compliance" in summary_json
