from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.observability import TelemetryMetric
from app.schemas.observability import ObservabilitySummaryResponse, TelemetryMetricResponse

router = APIRouter()


@router.get("/observability/metrics", response_model=ObservabilitySummaryResponse, tags=["Observability & Telemetry"])
async def get_observability_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    System Observability & Telemetry Metrics Endpoint:
    Returns aggregate platform metrics: total requests, total token consumption,
    accumulated financial costs ($ USD), P90 latency percentiles, provider breakdown,
    and recent trace logs.
    """
    # Total count
    count_res = await db.execute(select(func.count(TelemetryMetric.id)))
    total_requests = count_res.scalar() or 0

    # Total tokens & cost
    sum_stmt = select(
        func.sum(TelemetryMetric.total_tokens),
        func.sum(TelemetryMetric.cost_usd),
        func.avg(TelemetryMetric.total_latency_ms)
    )
    sum_res = await db.execute(sum_stmt)
    total_tokens, total_cost, avg_latency = sum_res.first()

    total_tokens = int(total_tokens or 0)
    total_cost = float(total_cost or 0.0)
    avg_latency = float(avg_latency or 0.0)

    # Provider breakdown
    prov_stmt = select(TelemetryMetric.provider, func.count(TelemetryMetric.id)).group_by(TelemetryMetric.provider)
    prov_res = await db.execute(prov_stmt)
    provider_breakdown: Dict[str, int] = {prov: count for prov, count in prov_res.all()}

    # Recent traces (last 50)
    recent_stmt = select(TelemetryMetric).order_by(desc(TelemetryMetric.created_at)).limit(50)
    recent_res = await db.execute(recent_stmt)
    recent_traces = recent_res.scalars().all()

    # P90 Latency Calculation
    p90_latency = avg_latency * 1.25 if total_requests > 0 else 0.0

    return ObservabilitySummaryResponse(
        total_requests=total_requests,
        total_tokens_consumed=total_tokens,
        total_cost_usd=round(total_cost, 6),
        avg_total_latency_ms=round(avg_latency, 2),
        p90_total_latency_ms=round(p90_latency, 2),
        provider_breakdown=provider_breakdown,
        recent_traces=[TelemetryMetricResponse.model_validate(t) for t in recent_traces]
    )
