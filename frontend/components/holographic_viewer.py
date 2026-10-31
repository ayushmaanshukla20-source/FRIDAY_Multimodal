import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent.parent.parent
VIEWER_DIR = BASE_DIR / "viewer"

def render_holographic_viewer(actions: Optional[List[Dict[str, Any]]] = None, height: int = 620):
    """
    Renders the interactive Three.js 3D Holographic Viewport inside Streamlit.
    Optionally executes structured actions (rotation, zoom, wireframe, procedural generation).
    """
    html_file = VIEWER_DIR / "index.html"
    css_file = VIEWER_DIR / "viewer.css"
    js_file = VIEWER_DIR / "viewer.js"

    if not html_file.exists() or not css_file.exists() or not js_file.exists():
        st.error("Holographic Viewport files missing in viewer/ directory.")
        return

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    with open(css_file, "r", encoding="utf-8") as f:
        css_content = f.read()
    with open(js_file, "r", encoding="utf-8") as f:
        js_content = f.read()

    # Inline CSS & JS for standalone iframe execution
    inlined_html = html_content.replace(
        '<link rel="stylesheet" href="viewer.css">',
        f'<style>{css_content}</style>'
    ).replace(
        '<script src="viewer.js"></script>',
        f'<script>{js_content}</script>'
    )

    # If actions are passed, inject immediate dispatch
    if actions and len(actions) > 0:
        actions_json = json.dumps(actions)
        action_dispatch_script = f"""
        <script>
            window.addEventListener('load', () => {{
                setTimeout(() => {{
                    const pendingActions = {actions_json};
                    if (window.fridayViewer && Array.isArray(pendingActions)) {{
                        pendingActions.forEach(action => window.fridayViewer.executeAction(action));
                    }}
                }}, 350);
            }});
        </script>
        """
        inlined_html = inlined_html.replace("</body>", f"{action_dispatch_script}</body>")

    components.html(inlined_html, height=height, scrolling=False)
