from typing import List, Optional
from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    company: str = Field(..., description="Name of the company or organization")
    role: str = Field(..., description="Job title or role held")
    duration_years: float = Field(..., description="Estimated duration in years")
    highlights: List[str] = Field(default_factory=list, description="Key achievements or responsibilities")


class EducationItem(BaseModel):
    degree: str = Field(..., description="Degree or certification name")
    institution: str = Field(..., description="University or institution name")
    graduation_year: Optional[int] = Field(None, description="Year of graduation if available")


class CandidateScoreResponse(BaseModel):
    candidate_name: str = Field(..., description="Extracted full name of candidate")
    email: Optional[str] = Field(None, description="Extracted contact email")
    phone: Optional[str] = Field(None, description="Extracted contact phone number")
    overall_score: int = Field(..., description="Fit score from 0 to 100 based on job description")
    summary: str = Field(..., description="Executive summary of candidate qualification")
    key_skills: List[str] = Field(default_factory=list, description="Extracted primary skills")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="Structured work experience history")
    education: List[EducationItem] = Field(default_factory=list, description="Structured education history")
    match_analysis: List[str] = Field(default_factory=list, description="Key strengths matching the job requirements")
    red_flags: List[str] = Field(default_factory=list, description="Potential gaps, missing requirements, or concerns")
