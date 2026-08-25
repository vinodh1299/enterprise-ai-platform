import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_hitl_approval_queue_and_audit_logs(async_client: AsyncClient):
    """
    Integration Test: Verifies Human-in-the-Loop staging of urgent AI tasks,
    pending approval queue listing, manager approval, and audit trail generation.
    """
    # 1. Register & Login user (Requester / Manager)
    await async_client.post("/api/users", json={"email": "hitlmanager@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "hitlmanager@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Agent invokes high-risk urgent ticket tool
    agent_payload = {"prompt": "Create an urgent support ticket for Server Down"}
    agent_resp = await async_client.post("/api/ai/agent/chat", json=agent_payload, headers=headers)
    assert agent_resp.status_code == 200

    # 3. Check pending approval queue
    pending_resp = await async_client.get("/api/approvals/pending", headers=headers)
    assert pending_resp.status_code == 200
    pending_tasks = pending_resp.json()
    assert len(pending_tasks) > 0

    task_id = pending_tasks[0]["id"]
    assert pending_tasks[0]["status"] == "pending"

    # 4. Manager approves task
    approve_resp = await async_client.post(f"/api/approvals/{task_id}/approve", headers=headers)
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "approved"

    # 5. Check audit logs
    audit_resp = await async_client.get("/api/audit-logs", headers=headers)
    assert audit_resp.status_code == 200
    audit_entries = audit_resp.json()
    assert len(audit_entries) > 0
    assert audit_entries[0]["status"] == "executed_after_human_approval"
