import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_automated_resume_parsing_and_candidate_scoring(async_client: AsyncClient):
    """
    Integration Test: Verifies Automated Resume Parsing & Candidate Scoring AI (Feature 1).
    Uploads candidate resume file -> LLM parses & scores qualifications -> Returns CandidateScoreResponse.
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "recruiter@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "recruiter@enterprise.com", "password": "PassWord123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Sample Resume Content
    sample_resume = """
    JOHN DOE - SENIOR SOFTWARE & AI ENGINEER
    Email: john.doe@example.com | Phone: +1-555-0199 | Location: San Francisco, CA

    SUMMARY:
    Senior Software Engineer with 5 years of experience architecting cloud applications, REST APIs,
    FastAPI microservices, PostgreSQL databases, and LLM RAG pipelines.

    EXPERIENCE:
    Senior AI Engineer - TechCorp Inc (2022 - Present)
    - Built high-throughput FastAPI REST microservices handling 1M daily requests.
    - Designed hybrid vector RAG retrieval systems using PostgreSQL pgvector and FastEmbed.

    Software Engineer - DataSystems Corp (2019 - 2022)
    - Developed backend services in Python and Dockerized container environments.

    EDUCATION:
    B.S. in Computer Science - University of California, Berkeley (2019)

    SKILLS:
    Python, FastAPI, PostgreSQL, pgvector, Docker, REST APIs, LLM, Ollama, Git, Redis.
    """

    files = {"file": ("john_doe_resume.txt", sample_resume.encode("utf-8"), "text/plain")}
    data = {
        "job_description": "Senior AI Engineer: Requires 4+ years of Python, FastAPI, PostgreSQL, and LLM RAG systems."
    }

    # 3. Post to Candidate Resume Scoring Endpoint
    response = await async_client.post(
        "/api/recruitment/resumes/score",
        files=files,
        data=data,
        headers=headers
    )

    assert response.status_code == 200
    res_json = response.json()
    
    assert "candidate_name" in res_json
    assert "overall_score" in res_json
    assert isinstance(res_json["overall_score"], int)
    assert res_json["overall_score"] >= 50
    assert "key_skills" in res_json
    assert len(res_json["key_skills"]) > 0
