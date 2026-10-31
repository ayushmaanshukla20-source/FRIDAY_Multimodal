import base64
from fastapi import APIRouter, HTTPException
from backend.schemas.models import (
    AudioSpeakRequest, AudioSpeakResponse,
    AudioTranscribeRequest, AudioTranscribeResponse
)
from backend.services.audio_service import audio_service

router = APIRouter(prefix="/api/audio", tags=["Audio & Speech"])

@router.post("/speak", response_model=AudioSpeakResponse)
def speak_text(request: AudioSpeakRequest):
    """
    Synthesizes speech audio from text using gTTS.
    """
    result = audio_service.text_to_speech(request.text)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate speech audio."))

    return AudioSpeakResponse(
        audio_base64=result.get("audio_base64"),
        success=True
    )

@router.post("/transcribe", response_model=AudioTranscribeResponse)
def transcribe_audio(request: AudioTranscribeRequest):
    """
    Transcribes base64 speech audio to text.
    """
    if not request.audio_base64:
        raise HTTPException(status_code=400, detail="Missing audio_base64 data.")

    try:
        raw_b64 = request.audio_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]
        audio_bytes = base64.b64decode(raw_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio payload.")

    res = audio_service.transcribe_audio(audio_bytes)
    return AudioTranscribeResponse(
        text=res.get("text", ""),
        success=res.get("success", False)
    )
