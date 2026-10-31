import base64
from typing import Optional, Dict, Any, Tuple
import streamlit as st

def render_file_attachment_widget() -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Renders an attachment widget for multimodal inputs (Images, Documents, Audio).
    Returns (file_bytes, filename, mime_type).
    """
    uploaded_file = st.file_uploader(
        "Attach Multimodal Payload (Image, PDF, DOCX, TXT, Audio)",
        type=["png", "jpg", "jpeg", "webp", "pdf", "docx", "txt", "md", "mp3", "wav"],
        help="Attached files are securely analyzed by F.R.I.D.A.Y.'s multimodal neural pipeline.",
        key="chat_file_attachment"
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name
        mime_type = uploaded_file.type

        # Visual preview
        col1, col2 = st.columns([1, 4])
        with col1:
            if mime_type.startswith("image/"):
                st.image(file_bytes, width=120)
            elif mime_type == "application/pdf":
                st.markdown("📄 **PDF Document**")
            elif "audio" in mime_type:
                st.audio(file_bytes)
            else:
                st.markdown("📝 **Text Document**")
        with col2:
            st.caption(f"**{filename}** ({len(file_bytes) // 1024} KB)")

        return file_bytes, filename, mime_type

    return None, None, None
