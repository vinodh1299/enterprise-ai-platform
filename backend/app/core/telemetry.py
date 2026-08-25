import time
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observability import TelemetryMetric

logger = logging.getLogger(__name__)


class SpanTimer:
    """
    Context manager for measuring execution span latency in milliseconds.
    """
    def __init__(self):
        self.start_time = 0.0
        self.elapsed_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0


async def record_telemetry(
    db: AsyncSession,
    user_id: int,
    endpoint: str,
    provider: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    latency_embedding_ms: float = 0.0,
    latency_retrieval_ms: float = 0.0,
    latency_llm_ms: float = 0.0,
    total_latency_ms: float = 0.0
) -> TelemetryMetric:
    """
    Asynchronously records telemetry metrics for request tracing and cost attribution.
    """
    if total_latency_ms <= 0.0:
        total_latency_ms = latency_embedding_ms + latency_retrieval_ms + latency_llm_ms

    metric = TelemetryMetric(
        user_id=user_id,
        endpoint=endpoint,
        provider=provider,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost_usd=round(cost_usd, 6),
        latency_embedding_ms=round(latency_embedding_ms, 2),
        latency_retrieval_ms=round(latency_retrieval_ms, 2),
        latency_llm_ms=round(latency_llm_ms, 2),
        total_latency_ms=round(total_latency_ms, 2)
    )
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric
