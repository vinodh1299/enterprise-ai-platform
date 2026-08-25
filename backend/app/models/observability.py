from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class TelemetryMetric(Base):
    """
    SQLAlchemy ORM model for System Telemetry & Observability.
    Tracks latency spans (embedding, retrieval, LLM), token consumption,
    and financial cost ($ USD) per request across tenants.
    """
    __tablename__ = "telemetry_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'ollama', 'gemini', 'local-free-mock'
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    latency_embedding_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    latency_retrieval_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    latency_llm_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
