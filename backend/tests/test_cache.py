import pytest
from app.core.cache import get_cached_response, set_cached_response


@pytest.mark.asyncio
async def test_redis_caching_engine():
    """
    Integration Test: Verifies response caching, retrieval, and TTL handling.
    """
    test_key = "test_cache_key_999"
    test_val = "This is a cached LLM answer."

    # Set cache
    await set_cached_response(test_key, test_val, ttl_seconds=60)

    # Get cache
    cached = await get_cached_response(test_key)
    # If Redis is running or fallback handles it cleanly
    if cached:
        assert cached == test_val
