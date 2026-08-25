import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_and_login_flow(async_client: AsyncClient):
    """
    Integration Test: Verifies registration, login token issuance, and protected profile retrieval.
    """
    # 1. Register a new user
    reg_payload = {
        "email": "testuser@enterprise.com",
        "password": "SecurePassword123!",
        "full_name": "Test Engineer"
    }
    reg_resp = await async_client.post("/api/users", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert reg_data["email"] == "testuser@enterprise.com"
    assert reg_data["full_name"] == "Test Engineer"
    assert "password" not in reg_data
    assert "hashed_password" not in reg_data

    # 2. Login to receive JWT token
    login_payload = {
        "email": "testuser@enterprise.com",
        "password": "SecurePassword123!"
    }
    login_resp = await async_client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 3. Access protected /users/me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await async_client.get("/api/users/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "testuser@enterprise.com"
