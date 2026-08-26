from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class AttendanceRecord(BaseModel):
    employee_id: int
    employee_name: str
    date: date
    clock_in: datetime
    clock_out: Optional[datetime] = None
    total_hours: float
    is_late: bool
    status: str  # ON_TIME, LATE, ABSENT, OVERTIME


class EmployeeBurnoutRisk(BaseModel):
    employee_id: int
    employee_name: str
    department: str
    burnout_risk_score: float = Field(..., description="Burnout probability percentage (0 to 100)")
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH, CRITICAL")
    key_indicators: List[str]
    recommended_action: str


class AttendanceAnomalySummary(BaseModel):
    total_records_analyzed: int
    anomalies_detected_count: int
    overall_department_health: str
    burnout_risk_list: List[EmployeeBurnoutRisk]
    flagged_anomalies: List[dict]
