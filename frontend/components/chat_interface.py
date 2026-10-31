import json
import base64
from typing import List, Dict, Any, Optional
import streamlit as st
import streamlit.components.v1 as components
from frontend.components.audio_controls import play_speech_audio

def render_citations(citations: List[Dict[str, Any]]):
    """Renders grounded RAG source citations with document names and page numbers."""
    if not citations:
        return

    with st.expander(f"📑 Grounded Citations ({len(citations)} sources verified)", expanded=False):
        for idx, cit in enumerate(citations):
            doc_name = cit.get("document_name", "Indexed Document")
            page = cit.get("page", 1)
            score = cit.get("score")
            snippet = cit.get("snippet", "")

            score_str = f" | Relevance: {int(score * 100)}%" if score else ""
            st.markdown(
                f"""
                <div style="background: rgba(0, 112, 243, 0.08); border-left: 3px solid #00f0ff; padding: 6px 12px; margin-bottom: 8px; border-radius: 4px; font-size: 13px;">
                    <div style="font-family: 'Orbitron', monospace; font-size: 11px; color: #00f0ff; font-weight: 600;">
                        Source #{idx + 1}: {doc_name} (Page {page}{score_str})
                    </div>
                    <div style="color: #c0d8f0; font-size: 12px; margin-top: 4px; font-style: italic;">
                        "{snippet}"
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

def render_message_bubble(msg: Dict[str, Any], backend_url: str, msg_idx: int = 0):
    """Renders a single message bubble with avatar, metadata, citations, and TTS."""
    role = msg.get("role", "user")
    content = msg.get("content", "")
    citations = msg.get("citations", [])
    meta = msg.get("metadata_json")
    audio_b64 = msg.get("audio_base64")

    avatar = "🛡️" if role == "user" else "⚡"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

        # Citations
        if citations:
            render_citations(citations)

        # Action tag if 3D actions occurred
        if meta:
            try:
                parsed_meta = json.loads(meta) if isinstance(meta, str) else meta
                if parsed_meta and "viewer_actions" in parsed_meta and parsed_meta["viewer_actions"]:
                    acts = parsed_meta["viewer_actions"]
                    action_summary = ", ".join([f"{a.get('action')}" for a in acts])
                    st.caption(f"🔮 Viewport Action Dispatched: `{action_summary}`")
            except Exception:
                pass

        # Spoken Audio playback
        if role == "assistant":
            col_a, col_b = st.columns([1, 4])
            with col_a:
                if st.button("🔊 Speak", key=f"speak_btn_{msg_idx}_{hash(content[:20])}"):
                    play_speech_audio(content, backend_url)
            if audio_b64:
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    st.audio(audio_bytes, format="audio/mp3", autoplay=False)
                except Exception:
                    pass
