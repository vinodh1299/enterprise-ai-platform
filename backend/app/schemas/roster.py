from datetime import date
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EmployeeAvailability(BaseModel):
    employee_id: int
    employee_name: str
    department: str
    skills: List[str]
    leave_dates: List[date] = Field(default_factory=list)


class ShiftRequirement(BaseModel):
    shift_name: str  # e.g., Morning, Evening, Night
    start_time: str  # e.g., "09:00"
    end_time: str    # e.g., "17:00"
    min_staff_required: int
    required_skills: List[str] = Field(default_factory=list)


class RosterOptimizationRequest(BaseModel):
    department: str
    target_week_start: date
    shift_requirements: List[ShiftRequirement]
    available_employees: List[EmployeeAvailability]


class AssignedShift(BaseModel):
    date: date
    shift_name: str
    employee_id: int
    employee_name: str
    role_skill_matched: str


class RosterOptimizationResponse(BaseModel):
    department: str
    target_week_start: date
    total_shifts_assigned: int
    unfilled_shifts_count: int
    coverage_score_percentage: float
    schedule: List[AssignedShift]
    optimization_summary: str
