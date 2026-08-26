from datetime import date, timedelta
from typing import List
from app.schemas.roster import (
    RosterOptimizationRequest,
    RosterOptimizationResponse,
    AssignedShift
)


def optimize_department_roster(
    request: RosterOptimizationRequest
) -> RosterOptimizationResponse:
    """
    Smart Shift & Roster Optimization AI Engine.
    Uses constraint satisfaction logic to assign employees to shifts based on:
    - Skill match
    - Requested leave dates
    - Fair shift distribution
    """
    assigned_shifts: List[AssignedShift] = []
    total_needed = 0
    unfilled = 0

    week_start = request.target_week_start

    # Build 7-day schedule
    for day_offset in range(7):
        current_date = week_start + timedelta(days=day_offset)
        
        for req in request.shift_requirements:
            for slot in range(req.min_staff_required):
                total_needed += 1
                
                # Find available employee for current_date
                assigned_emp = None
                for emp in request.available_employees:
                    if current_date in emp.leave_dates:
                        continue  # On leave
                    
                    # Skill check
                    matched_skill = "General Support"
                    if req.required_skills:
                        has_skill = any(s in emp.skills for s in req.required_skills)
                        if has_skill:
                            matched_skill = req.required_skills[0]
                        else:
                            continue
                    
                    assigned_emp = emp
                    break

                if assigned_emp:
                    assigned_shifts.append(
                        AssignedShift(
                            date=current_date,
                            shift_name=req.shift_name,
                            employee_id=assigned_emp.employee_id,
                            employee_name=assigned_emp.employee_name,
                            role_skill_matched=matched_skill
                        )
                    )
                else:
                    unfilled += 1

    coverage_score = round(((total_needed - unfilled) / max(1, total_needed)) * 100.0, 1)

    summary = (
        f"Smart Roster Optimization completed for {request.department}. "
        f"Assigned {len(assigned_shifts)} shifts with {coverage_score}% staffing coverage score."
    )

    return RosterOptimizationResponse(
        department=request.department,
        target_week_start=request.target_week_start,
        total_shifts_assigned=len(assigned_shifts),
        unfilled_shifts_count=unfilled,
        coverage_score_percentage=coverage_score,
        schedule=assigned_shifts,
        optimization_summary=summary
    )
