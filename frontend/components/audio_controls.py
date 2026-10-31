import base64
from typing import Optional
import requests
import streamlit as st

def play_speech_audio(text: str, backend_url: str) -> Optional[str]:
    """
    Plays a SINGLE, high-definition voice output using F.R.I.D.A.Y.'s authentic British accent.
    Falls back gracefully to the browser's native Web Speech API if network latency occurs.
    """
    if not text:
        return None

    import re
    import json
    import streamlit.components.v1 as components

    # Extract short speech snippet (first 1-2 sentences, max 200 chars) for responsive voice playback
    clean = re.sub(r"\[ACTION:[^\]]+\]", "", text)
    clean = re.sub(r"[`*#_>~]", "", clean)
    clean = re.sub(r"https?://\S+", "", clean).strip()

    sentences = re.split(r"(?<=[.!?])\s+", clean)
    snippet = sentences[0] if sentences else clean
    if len(snippet) > 200:
        snippet = snippet[:197] + "..."

    # Attempt 1: High-Definition British Voice via Backend gTTS
    try:
        res = requests.post(
            f"{backend_url}/api/audio/speak",
            json={"text": snippet},
            timeout=25
        )
        if res.status_code == 200:
            data = res.json()
            b64_audio = data.get("audio_base64")
            if b64_audio:
                audio_bytes = base64.b64decode(b64_audio)
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                return b64_audio
    except Exception:
        pass

    # Attempt 2: Instant Zero-Latency Browser Web Speech API Fallback
    try:
        js_speak = f"""
        <script>
        (function() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const text = {json.dumps(snippet)};
                const utt = new SpeechSynthesisUtterance(text);
                utt.rate = 1.05;
                utt.pitch = 1.0;
                const voices = window.speechSynthesis.getVoices();
                const ukVoice = voices.find(v => v.lang.includes('en-GB') || v.name.includes('UK') || v.name.includes('British') || v.name.includes('Female'));
                if (ukVoice) utt.voice = ukVoice;
                window.speechSynthesis.speak(utt);
            }}
        }})();
        </script>
        """
        components.html(js_speak, height=0)
    except Exception:
        pass

    return None

def render_voice_input_widget(backend_url: str) -> Optional[str]:
    """
    Renders high-visibility microphone voice control.
    Listens to speech, transcribes it with Gemini, and returns the spoken text.
    """
    if hasattr(st, "audio_input"):
        audio_data = st.audio_input("🎙️ Push to Speak to F.R.I.D.A.Y.", key="voice_mic_input")
        if audio_data is not None:
            audio_bytes = audio_data.getvalue()
            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
            
            with st.spinner("⚡ F.R.I.D.A.Y. is listening and transcribing your voice..."):
                try:
                    res = requests.post(
                        f"{backend_url}/api/audio/transcribe",
                        json={"audio_base64": b64_audio},
                        timeout=20
                    )
                    if res.status_code == 200:
                        data = res.json()
                        text = data.get("text", "").strip()
                        if text:
                            st.success(f"🎙️ You said: *\"{text}\"*")
                            return text
                        else:
                            st.warning("Could not clearly detect speech. Please speak closer to your microphone.")
                    else:
                        st.error(f"Transcription error: {res.text}")
                except Exception as e:
                    st.error(f"Voice link error: {e}")
    return None
