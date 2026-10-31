"""
FRIDAY Multimodal Voice Assistant
Author: Ayushmaan Shukla
Roll / Enrollment No.: 202510101240164
Department: Computer Science & Engineering (AI & ML)
Institution: Shri Ramswaroop Memorial University
Notice: This project is strictly for academic evaluation. 
        Unauthorized reproduction or submission is a violation of academic integrity.
"""
import os
import io
import uuid
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from gtts import gTTS
from backend.core.config import settings
from backend.core.logging import logger
from backend.services.ai_service import ai_service

class AudioService:
    def __init__(self):
        os.makedirs(settings.generated_dir, exist_ok=True)

    def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        Converts text to speech audio using gTTS and returns base64 encoded MP3 audio.
        Includes fast MD5 caching and sentence extraction to prevent network timeouts.
        """
        import re
        import hashlib

        # Clean text
        clean = re.sub(r"\[ACTION:[^\]]+\]", "", text)
        clean = re.sub(r"[`*#_>~]", "", clean)
        clean = re.sub(r"https?://\S+", "", clean).strip()

        # For conversational speech, focus on the first 1-2 complete sentences (max 220 chars)
        if len(clean) > 220:
            sentences = re.split(r"(?<=[.!?])\s+", clean)
            if sentences and len(sentences[0]) > 10:
                speech_text = sentences[0]
                if len(sentences) > 1 and len(speech_text) + len(sentences[1]) <= 220:
                    speech_text += " " + sentences[1]
            else:
                speech_text = clean[:217] + "..."
        else:
            speech_text = clean

        if not speech_text:
            return {"success": False, "error": "Empty text provided."}

        # Fast MD5 Cache Check
        text_hash = hashlib.md5(speech_text.encode("utf-8")).hexdigest()
        filename = f"speech_{text_hash}.mp3"
        filepath = Path(settings.generated_dir) / filename

        if filepath.exists() and filepath.stat().st_size > 0:
            try:
                with open(filepath, "rb") as f:
                    audio_bytes = f.read()
                return {
                    "success": True,
                    "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
                    "file_path": str(filepath),
                    "filename": filename
                }
            except Exception:
                pass

        try:
            # tld="co.uk" provides the classic British/Irish accent characteristic of F.R.I.D.A.Y.
            tts = gTTS(text=speech_text, lang="en", tld="co.uk", slow=False)
            tts.save(str(filepath))

            with open(filepath, "rb") as f:
                audio_bytes = f.read()

            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
            return {
                "success": True,
                "audio_base64": b64_audio,
                "file_path": str(filepath),
                "filename": filename
            }
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return {"success": False, "error": str(e)}

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> Dict[str, Any]:
        """
        Transcribes speech audio to text using Gemini multimodal audio capabilities.
        """
        # Auto-detect audio mime-type from magic bytes
        if audio_bytes.startswith(b"\x1a\x45\xdf\xa3") or b"webm" in audio_bytes[:50].lower():
            mime_type = "audio/webm"
        elif audio_bytes.startswith(b"RIFF"):
            mime_type = "audio/wav"
        elif audio_bytes.startswith(b"\xff\xfb") or audio_bytes.startswith(b"ID3"):
            mime_type = "audio/mp3"
        elif audio_bytes.startswith(b"OggS"):
            mime_type = "audio/ogg"
        elif audio_bytes.startswith(b"fLaC"):
            mime_type = "audio/flac"
        else:
            mime_type = "audio/webm"

        client = ai_service._get_genai_client()
        if client and ai_service.is_configured():
            candidate_models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-3-flash-preview", "gemini-2.5-flash-lite"]
            for m in candidate_models:
                try:
                    from google.genai import types
                    part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
                    res = client.models.generate_content(
                        model=m,
                        contents=[part, types.Part.from_text(text="Transcribe the spoken words in this audio exactly. Output ONLY the transcribed words with no introduction or markdown.")]
                    )
                    text = (res.text or "").strip()
                    if text:
                        return {"success": True, "text": text}
                except Exception as e:
                    logger.warning(f"Transcription attempt with {m} failed: {e}")
                    continue

            return {"success": False, "error": "Transcription models temporarily busy.", "text": ""}

        
        return {
            "success": False,
            "error": "Transcription requires an active Gemini API key.",
            "text": ""
        }

audio_service = AudioService()

