import os
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_enterprise_ai_platform_e2e_lifecycle(async_client: AsyncClient):
    """
    Master End-to-End Integration Test Suite (Phase 15):
    Verifies the complete enterprise AI platform lifecycle across all 14 previous phases:
    Auth -> Chat -> Document Ingestion -> Hybrid RAG -> AI Agent -> Text-to-SQL -> 
    HITL Approvals -> Stateful Memory -> BI Analytics -> Business Reports -> 
    RAG Evaluation -> Telemetry Metrics -> Security Defenses.
    """
    # ==========================================
    # Step 1: Phase 1 — User Signup & Authentication
    # ==========================================
    signup_payload = {"email": "e2e_cfo@enterprise.com", "password": "SecurePassword123!"}
    signup_resp = await async_client.post("/api/users", json=signup_payload)
    assert signup_resp.status_code == 201

    login_resp = await async_client.post("/api/auth/login", json=signup_payload)
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ==========================================
    # Step 2: Phase 2 — Free Local LLM Chat
    # ==========================================
    chat_resp = await async_client.post("/api/ai/chat", json={"prompt": "What are your enterprise capabilities?"}, headers=headers)
    assert chat_resp.status_code == 200
    assert "answer" in chat_resp.json()

    # ==========================================
    # Step 3: Phase 3 — Document Ingestion & Chunking
    # ==========================================
    doc_content = (
        "Enterprise Travel Policy 2025:\n"
        "Employee EMP-9942 is Senior Security Architect.\n"
        "International meal allowance is $75 per day."
    )
    files = {"file": ("Travel_Policy_2025.txt", doc_content.encode("utf-8"), "text/plain")}
    upload_resp = await async_client.post("/api/documents/upload", files=files, headers=headers)
    assert upload_resp.status_code == 201

    # ==========================================
    # Step 4: Phase 4 & 5 — Hybrid Vector + Lexical Search & RAG
    # ==========================================
    hybrid_search_resp = await async_client.post("/api/search/hybrid", json={"query": "EMP-9942", "top_k": 2}, headers=headers)
    assert hybrid_search_resp.status_code == 200
    assert len(hybrid_search_resp.json()["results"]) > 0

    rag_resp = await async_client.post("/api/ai/rag/hybrid", json={"query": "What is meal allowance?"}, headers=headers)
    assert rag_resp.status_code == 200
    assert len(rag_resp.json()["citations"]) > 0

    # ==========================================
    # Step 5: Phase 6 — AI Agent & Tool Calling
    # ==========================================
    agent_resp = await async_client.post("/api/ai/agent/chat", json={"prompt": "Look up employee details for EMP-9942"}, headers=headers)
    assert agent_resp.status_code == 200
    assert len(agent_resp.json()["tool_calls"]) > 0

    # ==========================================
    # Step 6: Phase 7 — Text-to-SQL & Query Security
    # ==========================================
    sql_resp = await async_client.post("/api/ai/sql/query", json={"prompt": "Which department had highest sales?"}, headers=headers)
    assert sql_resp.status_code == 200
    assert sql_resp.json()["is_safe"] is True

    # ==========================================
    # Step 7: Phase 8 — HITL Staging Queue & Manager Approval
    # ==========================================
    await async_client.post("/api/ai/agent/chat", json={"prompt": "Create an urgent support ticket for Server Down"}, headers=headers)
    pending_resp = await async_client.get("/api/approvals/pending", headers=headers)
    assert pending_resp.status_code == 200
    tasks = pending_resp.json()
    assert len(tasks) > 0

    task_id = tasks[0]["id"]
    approve_resp = await async_client.post(f"/api/approvals/{task_id}/approve", headers=headers)
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "approved"

    # ==========================================
    # Step 8: Phase 9 — Stateful Multi-Turn Memory
    # ==========================================
    conv_create = await async_client.post("/api/conversations", json={"title": "E2E Thread"}, headers=headers)
    conv_id = conv_create.json()["id"]

    await async_client.post(f"/api/conversations/{conv_id}/chat", json={"prompt": "Project codename is Phoenix."}, headers=headers)
    mem_resp = await async_client.post(f"/api/conversations/{conv_id}/chat", json={"prompt": "What is our codename?"}, headers=headers)
    assert mem_resp.status_code == 200

    # ==========================================
    # Step 9: Phase 10 — BI Analytics & Chart Data Series
    # ==========================================
    bi_resp = await async_client.post("/api/ai/bi/analytics", json={"prompt": "Analyze Q3 sales revenue"}, headers=headers)
    assert bi_resp.status_code == 200
    assert len(bi_resp.json()["chart_data"]) > 0

    # ==========================================
    # Step 10: Phase 11 — Business Report Generation Artifacts
    # ==========================================
    report_resp = await async_client.post("/api/ai/reports/generate", json={"topic": "E2E Platform Report"}, headers=headers)
    assert report_resp.status_code == 200
    assert os.path.exists(report_resp.json()["file_path"])

    # ==========================================
    # Step 11: Phase 12 — RAG Triad Evaluation Suite
    # ==========================================
    eval_resp = await async_client.post("/api/ai/evaluation/run", headers=headers)
    assert eval_resp.status_code == 200
    assert eval_resp.json()["overall_rag_score"] > 0.0

    # ==========================================
    # Step 12: Phase 13 — System Telemetry & Observability
    # ==========================================
    obs_resp = await async_client.get("/api/observability/metrics", headers=headers)
    assert obs_resp.status_code == 200
    assert "total_requests" in obs_resp.json()
    assert "total_tokens_consumed" in obs_resp.json()
    assert "total_cost_usd" in obs_resp.json()
    assert "p90_total_latency_ms" in obs_resp.json()

    # ==========================================
    # Step 13: Phase 14 — Security Guardrails & PII Redaction
    # ==========================================
    sec_resp = await async_client.post("/api/ai/security/sanitize", json={"prompt": "My SSN is 123-45-6789"}, headers=headers)
    assert sec_resp.status_code == 200
    assert "[REDACTED_SSN]" in sec_resp.json()["sanitized_prompt"]
