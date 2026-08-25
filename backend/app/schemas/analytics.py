from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BIAnalyticsRequest(BaseModel):
    """
    Request schema for BI & Analytics endpoint (POST /api/ai/bi/analytics).
    """
    prompt: str = Field(..., description="Natural language BI request e.g. 'Analyze revenue growth by department'", min_length=1)
    period: Optional[str] = Field("Q3", description="Time period filter e.g. 'Q1', 'Q3', '2025'")


class KPICard(BaseModel):
    """
    Key Performance Indicator card for executive dashboard display.
    """
    label: str
    value: str
    change: Optional[str] = None
    trend: str = "up"  # 'up', 'down', 'neutral'


class ChartDataPoint(BaseModel):
    """
    Data point schema compatible with UI chart libraries (Recharts / Chart.js).
    """
    label: str
    value: float
    category: Optional[str] = None


class BIAnalyticsResponse(BaseModel):
    """
    Response schema containing structured KPIs, UI chart data series, and executive summary.
    """
    query: str
    period: str
    kpis: List[KPICard]
    chart_type: str  # 'bar', 'pie', 'line'
    chart_data: List[ChartDataPoint]
    executive_summary: str
    recommendations: List[str]
    model_name: str
    total_tokens: int
    estimated_cost_usd: float
