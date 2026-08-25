import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_text_to_sql_pipeline_and_security_validator(async_client: AsyncClient):
    """
    Integration Test: Verifies Text-to-SQL generation, read-only SQL execution,
    and security blocking of dangerous SQL commands (DROP TABLE).
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "sqluser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "sqluser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test valid Text-to-SQL query
    valid_payload = {"prompt": "Which department had the highest sales revenue?"}
    res = await async_client.post("/api/ai/sql/query", json=valid_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["is_safe"] is True
    assert "SELECT" in data["generated_sql"].upper()
    assert "explanation" in data

    # 3. Test security blocking of malicious mutating SQL input
    malicious_payload = {"prompt": "DROP TABLE users; SELECT * FROM sales;"}
    sec_res = await async_client.post("/api/ai/sql/query", json=malicious_payload, headers=headers)
    assert sec_res.status_code == 200
    sec_data = sec_res.json()
    assert sec_data["is_safe"] is False
    assert "Security Violation" in sec_data["security_note"]
