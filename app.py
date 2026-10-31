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
import json
import base64
from pathlib import Path
import requests
import streamlit as st

# Configure Page
st.set_page_config(
    page_title="F.R.I.D.A.Y. â€” Futuristic AI Assistant",
    page_icon="âš¡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants & Paths
BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "frontend" / "styles" / "friday.css"
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Inject Custom Futuristic CSS
if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Imports from frontend components
from frontend.components.holographic_viewer import render_holographic_viewer
from frontend.components.chat_interface import render_message_bubble
from frontend.components.file_uploader import render_file_attachment_widget
from frontend.components.audio_controls import render_voice_input_widget, play_speech_audio
from frontend.components.vad_mic import render_vad_microphone

# ------------------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------------------
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "use_rag" not in st.session_state:
    st.session_state.use_rag = True
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True
if "pending_viewer_actions" not in st.session_state:
    st.session_state.pending_viewer_actions = []
if "system_health" not in st.session_state:
    st.session_state.system_health = None

def fetch_health():
    try:
        res = requests.get(f"{BACKEND_URL}/api/health", timeout=3)
        if res.status_code == 200:
            st.session_state.system_health = res.json()
    except Exception:
        st.session_state.system_health = {"status": "offline", "database": {"connected": False}}

fetch_health()

# ------------------------------------------------------------------------------
# Sidebar Navigation & Telemetry
# ------------------------------------------------------------------------------
with st.sidebar:
    # Futuristic HUD Brand Header
    st.markdown(
        """
        <div class="friday-hero-card" style="padding: 12px 14px; margin-bottom: 12px;">
            <div>
                <h2 class="friday-hero-title" style="font-size: 20px;">F.R.I.D.A.Y.</h2>
                <div class="friday-hero-subtitle" style="font-size: 11px;">DIGITAL ASSISTANT // MK-IV</div>
            </div>
            <div class="status-pill online">ONLINE</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation Selector
    nav_option = st.radio(
        "OPERATIONAL SUBSYSTEMS",
        [
            "ðŸ’¬ Tactical Chat",
            "ðŸ”® 3D Holographic Viewport",
            "ðŸ“š RAG Knowledge Base",
            "ðŸ–¥ï¸ Desktop & Screen Ops",
            "ðŸ’™ Emotional Support Mode",
            "âš™ï¸ Settings & System Health"
        ],
        index=0
    )

    st.markdown("---")

    # Conversation Management
    col_new, col_refresh = st.columns(2)
    with col_new:
        if st.button("âž• New Chat", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()

    with col_refresh:
        if st.button("ðŸ”„ Sync", use_container_width=True):
            fetch_health()
            st.rerun()

    # Load Conversation History
    try:
        conv_res = requests.get(f"{BACKEND_URL}/api/conversations", timeout=2)
        if conv_res.status_code == 200:
            conversations = conv_res.json()
            if conversations:
                st.caption("SAVED OPERATIONS")
                for c in conversations[:6]:
                    label = f"ðŸ“ {c['title'][:22]}"
                    if st.button(label, key=f"conv_{c['id']}", use_container_width=True):
                        st.session_state.current_conversation_id = c['id']
                        # Fetch messages
                        detail = requests.get(f"{BACKEND_URL}/api/conversations/{c['id']}").json()
                        st.session_state.messages = detail.get("messages", [])
                        st.rerun()
    except Exception:
        pass

    st.markdown("---")

    # Diagnostics Pills
    health = st.session_state.system_health or {}
    db_conn = health.get("database", {}).get("connected", False)
    db_badge = "ðŸŸ¢ MySQL Synced" if db_conn else "ðŸŸ¡ MySQL Setup Pending"
    ai_configured = health.get("ai_provider", {}).get("is_configured", False)
    ai_badge = "ðŸŸ¢ Neural Core Live" if ai_configured else "ðŸŸ¡ AI Key Required"

    st.caption(f"**Database:** {db_badge}")
    st.caption(f"**Cognition:** {ai_badge}")
    st.caption(f"**Vector Store:** ðŸŸ¢ ChromaDB Ready")

# ------------------------------------------------------------------------------
# View 1: Tactical Chat
# ------------------------------------------------------------------------------
if nav_option == "ðŸ’¬ Tactical Chat":
    st.markdown(
        """
        <div class="friday-hero-card">
            <div>
                <h1 class="friday-hero-title">TACTICAL CONVERSATIONAL INTERFACE</h1>
                <div class="friday-hero-subtitle">MULTIMODAL REASONING â€¢ RAG GROUNDING â€¢ NATURAL COMMANDS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Control Toggles Bar
    col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
    with col_t1:
        st.session_state.use_rag = st.checkbox("ðŸ§  Ground in Knowledge Base", value=st.session_state.use_rag)
    with col_t2:
        st.session_state.tts_enabled = st.checkbox("ðŸ”Š Voice Speech Feedback", value=st.session_state.tts_enabled)
    with col_t3:
        enable_mic = st.checkbox("ðŸŽ™ï¸ Microphone Voice Mode", value=True)

    if st.session_state.pending_viewer_actions:
        st.info(f"ðŸ”® {len(st.session_state.pending_viewer_actions)} 3D Viewport Action(s) Ready.")

    # Render Chat History
    for idx, msg in enumerate(st.session_state.messages):
        render_message_bubble(msg, BACKEND_URL, msg_idx=idx)

    # Check for incoming VAD voice directive from auto-stop microphone
    query_voice = None
    if "voice" in st.query_params and st.query_params["voice"]:
        query_voice = str(st.query_params["voice"]).strip()
        try:
            del st.query_params["voice"]
        except Exception:
            pass


    # Prominent VAD Voice Component (Auto-detects silence and auto-stops!)
    if enable_mic:
        render_vad_microphone(backend_url=BACKEND_URL, silence_timeout_ms=2000, volume_threshold=15, height=90)

    # Multimodal Attachments Accordion
    with st.expander("ðŸ“Ž Attach Multimodal Payload (Image, PDF, DOCX)", expanded=False):
        file_bytes, filename, mime_type = render_file_attachment_widget()

    # Chat Input Box
    user_input = st.chat_input("Enter tactical query or command, Boss (e.g. 'Rotate 3D model 45 degrees' or 'Analyze attached document')...")

    # If voice text arrived or user typed
    effective_prompt = query_voice or user_input

    if effective_prompt:
        # Append User Message to UI
        st.session_state.messages.append({
            "role": "user",
            "content": effective_prompt,
            "modality": "text",
            "citations": []
        })

        with st.chat_message("user", avatar="ðŸ›¡ï¸"):
            st.markdown(effective_prompt)

        # AI Processing Indicator
        with st.chat_message("assistant", avatar="âš¡"):
            with st.spinner("âš¡ Processing tactical directive, Boss..."):
                try:
                    payload = {
                        "prompt": effective_prompt,
                        "conversation_id": st.session_state.current_conversation_id,
                        "use_rag": st.session_state.use_rag,
                        "support_mode": False
                    }
                    res = requests.post(f"{BACKEND_URL}/api/chat", json=payload, timeout=40)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.current_conversation_id = data.get("conversation_id")
                        response_text = data.get("response", "")
                        citations = data.get("citations", [])
                        viewer_actions = data.get("viewer_actions")

                        if viewer_actions:
                            st.session_state.pending_viewer_actions = viewer_actions
                            st.caption(f"ðŸ”® Dispatched 3D Action: `{viewer_actions[0].get('action')}`")

                        st.markdown(response_text)

                        # Render citations
                        if citations:
                            from frontend.components.chat_interface import render_citations
                            render_citations(citations)

                        # Spoken Audio TTS
                        audio_b64 = None
                        if st.session_state.tts_enabled and response_text:
                            audio_b64 = play_speech_audio(response_text, BACKEND_URL)

                        # Save to session messages
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "citations": citations,
                            "audio_base64": audio_b64,
                            "metadata_json": json.dumps({"viewer_actions": viewer_actions}) if viewer_actions else None
                        })
                    else:
                        st.error(f"Operational Core Exception: {res.text}")
                except Exception as e:
                    st.error(f"Communication Link Error: {str(e)}")

# ------------------------------------------------------------------------------
# View 2: 3D Holographic Viewport
# ------------------------------------------------------------------------------
elif nav_option == "ðŸ”® 3D Holographic Viewport":
    st.markdown(
        """
        <div class="friday-hero-card">
            <div>
                <h1 class="friday-hero-title">3D HOLOGRAPHIC VIEWPORT</h1>
                <div class="friday-hero-subtitle">THREE.JS ENGINE â€¢ NATURAL LANGUAGE ACTIONS â€¢ GLTF ASSETS</div>
            </div>
            <div class="status-pill online">HUD ACTIVE</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Embed Interactive Three.js Viewer
    actions_to_run = st.session_state.pending_viewer_actions
    st.session_state.pending_viewer_actions = []
    render_holographic_viewer(actions=actions_to_run, height=600)

    # Natural Language Controls Input
    st.markdown("### ðŸ—£ï¸ Natural Language Viewport Control")
    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        cmd_input = st.text_input(
            "Viewport Directive",
            placeholder="e.g. 'Rotate 45 degrees on the Y-axis', 'Enable wireframe', 'Zoom in', 'Project orbital satellite', 'Reset view'",
            label_visibility="collapsed"
        )
    with col_c2:
        exec_btn = st.button("âš¡ Execute Directive", use_container_width=True)

    if exec_btn and cmd_input:
        with st.spinner("Translating command into Three.js viewport action..."):
            try:
                res = requests.post(f"{BACKEND_URL}/api/viewer/command", json={"command": cmd_input}, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    st.success(data.get("message", "Action dispatched."))
                    st.session_state.pending_viewer_actions = [a for a in data.get("actions", [])]
                    st.rerun()
                else:
                    st.error(f"Command translation failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Custom Model Uploader
    with st.expander("ðŸ“ Project Custom GLB / GLTF 3D Asset", expanded=False):
        uploaded_3d = st.file_uploader("Upload 3D Asset", type=["glb", "gltf"])
        if uploaded_3d:
            st.info("Drag and drop your .glb / .gltf file directly onto the holographic canvas above for instant parsing and hierarchy extraction!")

# ------------------------------------------------------------------------------
# View 3: RAG Knowledge Base
# ------------------------------------------------------------------------------
elif nav_option == "ðŸ“š RAG Knowledge Base":
    st.markdown(
        """
        <div class="friday-hero-card">
            <div>
                <h1 class="friday-hero-title">RAG KNOWLEDGE RETRIEVAL BASE</h1>
                <div class="friday-hero-subtitle">INGESTION â€¢ OVERLAPPING CHUNKS â€¢ CHROMADB VECTOR STORE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_up, col_search = st.columns([1, 1])

    # Upload Section
    with col_up:
        st.markdown("### ðŸ“„ Document Ingestion")
        doc_file = st.file_uploader(
            "Upload Document (PDF, DOCX, TXT, MD)",
            type=["pdf", "docx", "txt", "md", "csv", "json"],
            key="rag_doc_uploader"
        )
        if doc_file is not None:
            if st.button("ðŸš€ Ingest & Index Document", use_container_width=True):
                with st.spinner(f"Ingesting '{doc_file.name}' into vector database..."):
                    try:
                        files = {"file": (doc_file.name, doc_file.getvalue(), doc_file.type)}
                        res = requests.post(f"{BACKEND_URL}/api/documents/upload", files=files, timeout=40)
                        if res.status_code == 200:
                            doc_data = res.json()
                            st.success(f"Successfully indexed '{doc_data['filename']}' ({doc_data['chunk_count']} semantic chunks).")
                            st.rerun()
                        else:
                            st.error(f"Upload failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Semantic Query Tester
    with col_search:
        st.markdown("### ðŸ” Semantic Vector Search")
        search_query = st.text_input("Query Indexed Knowledge Base", placeholder="Search document contents...")
        if st.button("Search Vectors", use_container_width=True) and search_query:
            with st.spinner("Searching ChromaDB vector embeddings..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/api/knowledge/query",
                        json={"query": search_query, "top_k": 3},
                        timeout=10
                    )
                    if res.status_code == 200:
                        results = res.json().get("results", [])
                        st.markdown(f"**Found {len(results)} relevant chunks:**")
                        for r in results:
                            st.markdown(
                                f"""
                                <div class="citation-box">
                                    <div class="citation-header">{r['document_name']} (Page {r.get('page', 1)} | Score: {r['score']})</div>
                                    <div class="citation-item">{r['content']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                except Exception as e:
                    st.error(f"Search failed: {e}")

    st.markdown("---")
    st.markdown("### ðŸ“š Indexed Knowledge Repository")
    try:
        res = requests.get(f"{BACKEND_URL}/api/documents", timeout=5)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            if not docs:
                st.info("No documents currently indexed. Ingest a PDF or document above to empower F.R.I.D.A.Y.'s RAG reasoning.")
            else:
                for d in docs:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{d['filename']}** ({d['file_type'].upper()})")
                    with col2:
                        st.caption(f"{d['chunk_count']} chunks")
                    with col3:
                        st.caption(f"{d['file_size'] // 1024} KB")
                    with col4:
                        if st.button("ðŸ—‘ï¸ Delete", key=f"del_{d['id']}", use_container_width=True):
                            requests.delete(f"{BACKEND_URL}/api/documents/{d['id']}")
                            st.success(f"Deleted {d['filename']}")
                            st.rerun()
    except Exception as e:
        st.error(f"Could not load documents: {e}")

# ------------------------------------------------------------------------------
# View 4: Desktop & Screen Ops
# ------------------------------------------------------------------------------
elif nav_option == "ðŸ–¥ï¸ Desktop & Screen Ops":
    st.markdown(
        """
        <div class="friday-hero-card">
            <div>
                <h1 class="friday-hero-title">DESKTOP INTEGRATION & SCREEN VISION</h1>
                <div class="friday-hero-subtitle">SCREEN ANALYSIS â€¢ ALLOWLIST AUTOMATION â€¢ SYSTEM TELEMETRY</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_screen, tab_apps, tab_music = st.tabs(["ðŸ“¸ Screen Vision Analysis", "âš¡ Approved App Launcher", "ðŸŽµ Free Music Player"])

    with tab_screen:
        st.markdown("### ðŸ–¥ï¸ Desktop Screen Capture & Analysis")
        st.caption("F.R.I.D.A.Y. captures your active desktop display with explicit permission and inspects it using multimodal AI.")

        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            screen_prompt = st.text_input("Screen Analysis Prompt", value="Analyze what is on my screen and summarize errors or open work, Boss.")
            if st.button("ðŸ“¸ Capture & Analyze Screen Now", use_container_width=True):
                with st.spinner("Capturing display and analyzing visible telemetry..."):
                    try:
                        res = requests.post(f"{BACKEND_URL}/api/desktop/screen/capture", params={"prompt": screen_prompt}, timeout=30)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["last_screen_analysis"] = data
                        else:
                            st.error(f"Screen analysis failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col_s2:
            if "last_screen_analysis" in st.session_state:
                analysis_data = st.session_state["last_screen_analysis"]
                st.markdown("#### Optical Sensor Telemetry")
                st.markdown(analysis_data.get("analysis", ""))
                if analysis_data.get("image_base64"):
                    st.image(analysis_data["image_base64"], caption="Captured Primary Display", use_container_width=True)

    with tab_apps:
        st.markdown("### ðŸ›¡ï¸ Allowlisted Application Automation")
        st.caption("Permission-controlled execution. Launches system tools and Google Chrome safely.")

        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
        with col_a1:
            if st.button("ðŸŒ Chrome", use_container_width=True):
                requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "open_chrome", "target": "chrome"})
                st.success("Launched Google Chrome.")
        with col_a2:
            if st.button("ðŸ§® Calculator", use_container_width=True):
                requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "open_app", "target": "calc"})
                st.success("Launched Calculator.")
        with col_a3:
            if st.button("ðŸ“ Notepad", use_container_width=True):
                requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "open_app", "target": "notepad"})
                st.success("Launched Notepad.")
        with col_a4:
            if st.button("ðŸŽ¨ MS Paint", use_container_width=True):
                requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "open_app", "target": "paint"})
                st.success("Launched MS Paint.")
        with col_a5:
            if st.button("ðŸ“ Explorer", use_container_width=True):
                requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "open_app", "target": "explorer"})
                st.success("Launched Windows Explorer.")

        st.markdown("---")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### ðŸ” Google Chrome Search")
            c_search_q = st.text_input("Search Google in Chrome", placeholder="e.g. machine learning tutorials")
            if st.button("Search in Chrome", use_container_width=True) and c_search_q:
                r = requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "search_google", "target": c_search_q}).json()
                st.info(r.get("output", ""))

        with col_c2:
            st.markdown("#### ðŸŒ Open Website in Chrome")
            c_site_q = st.text_input("Open Website or Service", placeholder="e.g. YouTube, Google Classroom, Wikipedia")
            if st.button("Navigate in Chrome", use_container_width=True) and c_site_q:
                r = requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "open_website", "target": c_site_q}).json()
                st.info(r.get("output", ""))

        st.markdown("---")
        st.markdown("#### âš¡ Chrome DevTools MCP Integration")
        st.caption("Direct Model Context Protocol bridge connecting Friday to `chrome-devtools-mcp@latest` via stdio JSON-RPC.")
        col_m1, col_m2, col_m3 = st.columns([1, 1, 2])
        with col_m1:
            if st.button("ðŸ”Œ Check MCP Status", use_container_width=True):
                mcp_st = requests.get(f"{BACKEND_URL}/api/desktop/mcp/status").json()
                if mcp_st.get("npx_available"):
                    st.success(f"ðŸŸ¢ NPX Ready | {mcp_st.get('tools_count', 0)} MCP Tools Loaded")
                else:
                    st.warning("Node.js / npx not detected in PATH.")
        with col_m2:
            if st.button("ðŸ“¸ DevTools Viewport", use_container_width=True):
                s_res = requests.post(f"{BACKEND_URL}/api/desktop/mcp/screenshot").json()
                st.info("Dispatched Chrome DevTools snapshot directive.")
        with col_m3:
            col_in, col_go = st.columns([2, 1])
            with col_in:
                mcp_nav_url = st.text_input("DevTools URL", value="https://www.youtube.com", label_visibility="collapsed")
            with col_go:
                if st.button("ðŸš€ MCP Go", use_container_width=True) and mcp_nav_url:
                    r = requests.post(f"{BACKEND_URL}/api/desktop/mcp/navigate", params={"url": mcp_nav_url}).json()
                    st.success("Navigated via Chrome DevTools MCP.")

        st.markdown("---")
        st.markdown("#### System Diagnostics")

        if st.button("ðŸ“Š Fetch Hardware Diagnostics"):
            res = requests.post(f"{BACKEND_URL}/api/desktop/execute", json={"action": "diagnostics", "target": "system"}).json()
            st.info(res.get("output", ""))

    with tab_music:
        st.markdown("### ðŸŽµ Free Music Streaming & Playback Engine")
        st.caption("100% Free YouTube Audio Streaming powered by yt-dlp & native Windows audio. Zero subscription required.")

        # Playback controls bar
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
        with col_p1:
            if st.button("â¸ï¸ Pause", use_container_width=True):
                res = requests.post(f"{BACKEND_URL}/api/music/pause").json()
                st.info(res.get("message", "Paused."))
        with col_p2:
            if st.button("â–¶ï¸ Resume", use_container_width=True):
                res = requests.post(f"{BACKEND_URL}/api/music/resume").json()
                st.info(res.get("message", "Resumed."))
        with col_p3:
            if st.button("â¹ï¸ Stop", use_container_width=True):
                res = requests.post(f"{BACKEND_URL}/api/music/stop").json()
                st.info(res.get("message", "Stopped."))
        with col_p4:
            if st.button("â­ï¸ Next Song", use_container_width=True):
                res = requests.post(f"{BACKEND_URL}/api/music/next").json()
                st.info(res.get("message", "Skipped track."))
        with col_p5:
            if st.button("ðŸ”„ Check Status", use_container_width=True):
                status_res = requests.get(f"{BACKEND_URL}/api/music/status").json()
                track = status_res.get("current_track") or "None"
                st.caption(f"Engine: `{status_res.get('engine')}` | Playing: `{status_res.get('is_playing')}` | Volume: `{status_res.get('volume')}%`")

        # Volume control bar
        col_v1, col_v2 = st.columns([3, 1])
        with col_v1:
            music_vol = st.slider("Audio Volume", min_value=0, max_value=100, value=75, step=5)
        with col_v2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Apply Volume", use_container_width=True):
                v_res = requests.post(f"{BACKEND_URL}/api/music/volume", params={"volume": music_vol}).json()
                st.info(v_res.get("message", f"Volume set to {music_vol}%"))

        st.markdown("---")
        col_sp1, col_sp2 = st.columns([2, 1])
        with col_sp1:
            spot_query = st.text_input("Play Song or Artist (Free Streaming)", placeholder="e.g. Believer by Imagine Dragons or Arijit Singh songs")
        with col_sp2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("â–¶ï¸ Stream Now", use_container_width=True) and spot_query:
                with st.spinner("Locating best audio stream and starting playback..."):
                    res = requests.post(f"{BACKEND_URL}/api/music/play", json={"query": spot_query}).json()
                    st.info(res.get("message", ""))

        st.markdown("#### ðŸ” Search Free Audio Catalog")
        spot_search_input = st.text_input("Search Music", placeholder="e.g. Arijit Singh, Queen, Hans Zimmer")
        if st.button("Search Music") and spot_search_input:
            res = requests.post(f"{BACKEND_URL}/api/music/search", json={"query": spot_search_input}).json()
            st.info(res.get("message", ""))
            for item in res.get("items", []):
                st.markdown(f"**[{item['name']}]({item['url']})** â€” *{item.get('artist', '')}*")


# ------------------------------------------------------------------------------
# View 5: Emotional Support Mode
# ------------------------------------------------------------------------------
elif nav_option == "ðŸ’™ Emotional Support Mode":
    st.markdown(
        """
        <div class="friday-hero-card" style="border-left-color: #00ffaa;">
            <div>
                <h1 class="friday-hero-title" style="color: #00ffaa;">EMOTIONAL SUPPORT MODE</h1>
                <div class="friday-hero-subtitle">COMPASSIONATE LISTENING â€¢ GROUNDING EXERCISES â€¢ SAFETY PROTOCOLS</div>
            </div>
            <div class="status-pill online">SAFE MODE ACTIVE</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        *Boss, I'm here to listen without judgment. Take a moment to pause. What's on your mind?*
        """
    )

    # Grounding exercises accordion
    with st.expander("ðŸŒ± Grounding Exercises & Calming Techniques", expanded=False):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#### ðŸŒ¬ï¸ 4-7-8 Breathing Technique")
            st.markdown(
                """
                1. **Inhale** gently through your nose for **4 seconds**.
                2. **Hold** your breath calmly for **7 seconds**.
                3. **Exhale** completely through your mouth for **8 seconds**.
                *Repeat 3-4 cycles to lower stress hormones and regulate heart rate.*
                """
            )
        with col_g2:
            st.markdown("#### ðŸ–ï¸ 5-4-3-2-1 Sensory Grounding")
            st.markdown(
                """
                Notice around you right now:
                - **5** things you can see
                - **4** things you can physically feel
                - **3** things you can hear
                - **2** things you can smell
                - **1** positive thought or affirmation
                """
            )

    # Verified Crisis Resources Card
    with st.expander("ðŸ†˜ Verified Crisis Support Hotlines", expanded=False):
        st.markdown(
            """
            If you or someone you know is struggling or in crisis, help is always available:
            - **India**: 
              * **Tele-MANAS**: Call **14416** or **1800-891-4416** (24/7, Toll-Free, Govt. of India)
              * **Vandrevala Foundation**: **9999 666 555** (24/7)
              * **KIRAN Mental Health Helpline**: **1800-599-0019**
            - **US / Canada**: Call or text **988** (24/7 Suicide & Crisis Lifeline)
            - **UK**: Call **111** (NHS) or Samaritans at **116 123**
            - **International**: [Find A Helpline](https://findahelpline.com)
            """
        )

    # Support Mode Chat
    support_input = st.chat_input("Talk to F.R.I.D.A.Y. in confidence, Boss...")
    if support_input:
        with st.chat_message("user", avatar="ðŸ›¡ï¸"):
            st.markdown(support_input)

        with st.chat_message("assistant", avatar="âš¡"):
            with st.spinner("Listening with full attention, Boss..."):
                res = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={"prompt": support_input, "support_mode": True, "use_rag": False},
                    timeout=20
                ).json()
                st.markdown(res.get("response", ""))

# ------------------------------------------------------------------------------
# View 6: Settings & System Health
# ------------------------------------------------------------------------------
elif nav_option == "âš™ï¸ Settings & System Health":
    st.markdown(
        """
        <div class="friday-hero-card">
            <div>
                <h1 class="friday-hero-title">SYSTEM CONFIGURATION & DIAGNOSTICS</h1>
                <div class="friday-hero-subtitle">DATABASE â€¢ NEURAL CORES â€¢ VECTOR RETRIEVAL â€¢ SECURITY</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    health = st.session_state.system_health or {}

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        st.markdown("### ðŸ—„ï¸ MySQL Database")
        db_stat = health.get("database", {})
        if db_stat.get("connected"):
            st.success(f"Connected to MySQL ({db_stat.get('host')}:{db_stat.get('port')}/{db_stat.get('database')})")
        else:
            st.warning("MySQL connection deferred or unconfigured.")
            st.markdown(
                f"""
                ```text
                {db_stat.get('setup_guide', '')}
                ```
                """
            )
            st.caption(f"Reported error: `{db_stat.get('error', 'None')}`")

    with col_h2:
        st.markdown("### ðŸ§  AI Provider & Cognition")
        ai_stat = health.get("ai_provider", {})
        st.markdown(f"**Provider:** `{ai_stat.get('provider')}`")
        st.markdown(f"**Model:** `{ai_stat.get('model')}`")
        if ai_stat.get("is_configured"):
            st.success("Cognitive model live and responsive.")
        else:
            st.warning("No API key detected. Add `GEMINI_API_KEY` to your `.env` file to activate live neural responses.")

    st.markdown("---")
    st.markdown("### ðŸ“Š Vector Store & Telemetry")
    vec = health.get("vector_store", {})
    st.markdown(f"- **Engine:** {vec.get('engine')} ({vec.get('collection')})")
    st.markdown(f"- **Total Indexed Vectors:** {vec.get('total_vectors')}")

    telemetry = health.get("telemetry", {})
    if telemetry:
        st.markdown(f"- **Host Platform:** {telemetry.get('os')} {telemetry.get('os_release')} ({telemetry.get('architecture')})")
        st.markdown(f"- **Node:** {telemetry.get('hostname')}")
        st.markdown(f"- **Python Runtime:** {telemetry.get('python_version')}")

