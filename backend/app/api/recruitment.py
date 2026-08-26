from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.recruitment import CandidateScoreResponse
from app.ai.recruitment.evaluator import parse_and_score_resume

router = APIRouter()


@router.post(
    "/recruitment/resumes/score",
    response_model=CandidateScoreResponse,
    status_code=status.HTTP_200_OK,
    tags=["Recruitment & HR AI"]
)
async def score_candidate_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(
        "Senior AI/Software Engineer: 3+ years experience with Python, FastAPI, PostgreSQL, Vector Databases, and REST APIs."
    ),
    current_user: User = Depends(get_current_user)
):
    """
    Automated Candidate Resume Parser & AI Scoring Endpoint.
    Extracts candidate text from PDF/DOCX/TXT resume files, evaluates qualifications
    against the Job Description using local Ollama LLM, and outputs structured candidate scores.
    """
    allowed_extensions = {".pdf", ".docx", ".txt"}
    filename = file.filename or "resume.pdf"
    file_ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: .pdf, .docx, .txt"
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    score_result = await parse_and_score_resume(
        file_content=contents,
        filename=filename,
        job_description=job_description or "Software Engineer"
    )

    return score_result
