from typing import List, Optional
from pydantic import BaseModel, Field


class ReportGenerationRequest(BaseModel):
    """
    Request schema for Business Report Generation (POST /api/ai/reports/generate).
    """
    topic: str = Field(..., description="Report topic e.g. 'Executive Security & Performance Report'", min_length=1)
    period: Optional[str] = Field("2025 Q3", description="Reporting period e.g. 'Q3', '2025', 'Annual'")


class ReportGenerationResponse(BaseModel):
    """
    Response schema returning generated markdown report content and downloadable file path.
    """
    report_title: str
    period: str
    markdown_content: str
    file_path: str
    sections_count: int
    model_name: str
    total_tokens: int
    estimated_cost_usd: float
