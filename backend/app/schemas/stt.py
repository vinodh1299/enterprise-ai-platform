from typing import Optional, List
from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    filename: str
    audio_duration_seconds: float
    detected_language: str
    transcript_text: str
    confidence_score: float = Field(..., description="Audio transcription confidence (0.0 to 1.0)")
    word_count: int
    accent_detected: Optional[str] = "en-IN (Indian English)"
    extracted_intents: List[str] = Field(default_factory=list)
