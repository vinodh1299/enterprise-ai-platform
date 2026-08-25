from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class TelemetryMetricResponse(BaseModel):
    """
    Pydantic schema for returning individual request telemetry traces.
    """
    id: int
    user_id: int
    endpoint: str
    provider: str
    total_tokens: int
    cost_usd: float
    latency_embedding_ms: float
    latency_retrieval_ms: float
    latency_llm_ms: float
    total_latency_ms: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ObservabilitySummaryResponse(BaseModel):
    """
    Pydantic schema for system-wide observability & telemetry metrics dashboard.
    """
    total_requests: int
    total_tokens_consumed: int
    total_cost_usd: float
    avg_total_latency_ms: float
    p90_total_latency_ms: float
    provider_breakdown: Dict[str, int]
    recent_traces: List[TelemetryMetricResponse]
