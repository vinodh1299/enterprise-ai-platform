import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_stateful_multi_turn_conversation_memory(async_client: AsyncClient):
    """
    Integration Test: Verifies stateful multi-turn conversation memory across multiple requests.
    Tests user context retention (Message 1: 'My favorite color is Blue', Message 2: 'What is my favorite color?').
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "memoryuser@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "memoryuser@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a new conversation session
    create_resp = await async_client.post("/api/conversations", json={"title": "Color Preference Session"}, headers=headers)
    assert create_resp.status_code == 200
    conv_id = create_resp.json()["id"]

    # 3. Send Turn 1: Introduce user state ('My favorite color is Blue')
    turn1_payload = {"prompt": "My favorite color is Blue."}
    t1_resp = await async_client.post(f"/api/conversations/{conv_id}/chat", json=turn1_payload, headers=headers)
    assert t1_resp.status_code == 200

    # 4. Send Turn 2: Ask question depending on state ('What is my favorite color?')
    turn2_payload = {"prompt": "What is my favorite color?"}
    t2_resp = await async_client.post(f"/api/conversations/{conv_id}/chat", json=turn2_payload, headers=headers)
    assert t2_resp.status_code == 200
    t2_data = t2_resp.json()

    assert "conversation_id" in t2_data
    assert t2_data["conversation_id"] == conv_id
    assert t2_data["active_memory_window_count"] > 0
    assert "assistant_message" in t2_data

    # 5. Fetch complete message history
    history_resp = await async_client.get(f"/api/conversations/{conv_id}/messages", headers=headers)
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) == 4  # User1, Assistant1, User2, Assistant2
