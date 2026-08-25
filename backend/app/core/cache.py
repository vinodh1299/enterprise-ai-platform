import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Redis Client Instance & In-Memory Fallback Cache
_redis_client: Any = None
_memory_cache: Dict[str, str] = {}


async def get_redis_client() -> Any:
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
            from app.core.config import settings
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0
            )
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory fallback cache: {e}")
            _redis_client = False
    return _redis_client if _redis_client is not False else None


async def get_cached_response(key: str) -> Optional[str]:
    """
    Retrieves cached response string from Redis or in-memory fallback.
    """
    try:
        r = await get_redis_client()
        if r:
            return await r.get(f"ai_cache:{key}")
        else:
            return _memory_cache.get(key)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return _memory_cache.get(key)


async def set_cached_response(key: str, value: str, ttl_seconds: int = 3600) -> bool:
    """
    Stores response string in Redis or in-memory fallback.
    """
    try:
        r = await get_redis_client()
        if r:
            await r.setex(f"ai_cache:{key}", ttl_seconds, value)
            return True
        else:
            _memory_cache[key] = value
            return True
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
        _memory_cache[key] = value
        return True
