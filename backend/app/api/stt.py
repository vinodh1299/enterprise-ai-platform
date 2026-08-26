from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.stt import TranscriptionResponse
from app.ai.stt.transcriber import transcribe_audio_blob

router = APIRouter()


@router.post(
    "/ai/stt/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Voice & Speech AI"]
)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en-IN"),
    current_user: User = Depends(get_current_user)
):
    """
    Speech-to-Text (STT) Audio Transcription Endpoint.
    Transcribes audio blobs (.wav, .mp3, .m4a, .ogg) into text with Indian-English accent adaptation and intent extraction.
    """
    filename = file.filename or "audio.wav"
    allowed_exts = {".wav", ".mp3", ".m4a", ".ogg", ".aac"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format '{ext}'. Allowed formats: .wav, .mp3, .m4a, .ogg"
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty."
        )

    return await transcribe_audio_blob(
        audio_bytes=contents,
        filename=filename,
        language=language or "en-IN"
    )
