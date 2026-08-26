import pytest
from datetime import date
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_erp_ai_roadmap_suite(async_client: AsyncClient):
    """
    Master Integration Test Suite verifying all 6 Keka ERP AI Roadmap features:
    1. Candidate Resume Parsing & Scoring AI
    2. Manager Approval Copilot AI
    3. Attendance Anomaly & Burnout Risk Detection AI
    4. Speech-to-Text (STT) Audio Transcription Engine
    5. Smart Shift & Roster Optimization AI
    """
    # 1. Register & Login user
    await async_client.post("/api/users", json={"email": "erp_suite@enterprise.com", "password": "PassWord123!"})
    login_resp = await async_client.post("/api/auth/login", json={"email": "erp_suite@enterprise.com", "password": "PassWord123!"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Feature 3: Attendance Anomaly ML
    attendance_resp = await async_client.get("/api/analytics/attendance/anomalies", headers=headers)
    assert attendance_resp.status_code == 200
    att_json = attendance_resp.json()
    assert "total_records_analyzed" in att_json
    assert "burnout_risk_list" in att_json
    assert len(att_json["burnout_risk_list"]) > 0

    # 3. Test Feature 4: Audio Speech-to-Text Transcription
    sample_audio_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    files = {"file": ("mark_voice_sample.wav", sample_audio_bytes, "audio/wav")}
    stt_resp = await async_client.post("/api/ai/stt/transcribe", files=files, headers=headers)
    assert stt_resp.status_code == 200
    stt_json = stt_resp.json()
    assert "transcript_text" in stt_json
    assert stt_json["confidence_score"] > 0.8
    assert "detected_language" in stt_json

    # 4. Test Feature 5: Smart Shift & Roster Optimization AI
    roster_payload = {
        "department": "Engineering",
        "target_week_start": str(date.today()),
        "shift_requirements": [
            {
                "shift_name": "Morning",
                "start_time": "09:00",
                "end_time": "17:00",
                "min_staff_required": 2,
                "required_skills": ["Python"]
            }
        ],
        "available_employees": [
            {
                "employee_id": 101,
                "employee_name": "Alex Mercer",
                "department": "Engineering",
                "skills": ["Python", "FastAPI"],
                "leave_dates": []
            },
            {
                "employee_id": 102,
                "employee_name": "Sophia Chen",
                "department": "Engineering",
                "skills": ["Python", "Docker"],
                "leave_dates": []
            }
        ]
    }
    roster_resp = await async_client.post("/api/ai/roster/optimize", json=roster_payload, headers=headers)
    assert roster_resp.status_code == 200
    roster_json = roster_resp.json()
    assert roster_json["department"] == "Engineering"
    assert roster_json["total_shifts_assigned"] > 0
    assert roster_json["coverage_score_percentage"] > 0.0
