# Avatar-Chat-Interface & F.R.I.D.A.Y. Chrome Automation Bridge

A production-grade, cybernetic 3D AI assistant combining real-time Three.js behavioral gestures, continuous hands-free voice turn-taking (STT/TTS), and a local Python backend bridge for desktop Chrome browser automation.

---

## 🏛️ System Architecture

```
+-------------------------------------------------------+
|  React 19 + Vite Frontend (http://localhost:5173)     |
|  - 3D Avatar with 60 FPS Cursor Lerp & Lip-Sync       |
|  - Web Speech API + 1.2s Silence Auto-Send            |
|  - Chrome Intent Classifier (Search, Sites, Hotkeys)  |
+---------------------------+---------------------------+
                            |
           POST /api/chrome | (CORS Enabled)
                            v
+-------------------------------------------------------+
|  FastAPI Backend Bridge (http://localhost:8000)       |
|  - Search queries -> Google Chrome Execution          |
|  - Direct Website Routing (YouTube, GitHub, etc.)     |
|  - Tab & Window Hotkeys via PyAutoGUI                 |
+-------------------------------------------------------+
```

---

## 🚀 Quick Start

### 1. Requirements & Dependencies
Ensure your Python virtual environment has the required dependencies:
```bash
pip install -r requirements.txt
```
Key packages include:
- `fastapi` & `uvicorn` (REST API server)
- `pyautogui` (Desktop window & tab hotkey automation)
- `pydantic` & `requests`

### 2. Launching Both Servers

You can start both servers simultaneously using the provided batch script:
```powershell
.\start_servers.bat
```

Or run each service in separate terminals:

**Terminal 1 — Local Python Bridge (Port 8000):**
```powershell
.\venv\Scripts\python.exe backend/app.py
```

**Terminal 2 — React Avatar Frontend (Port 5173):**
```powershell
npm --prefix avatar-chat-interface run dev
```

---

## 🌐 Supported Chrome Automation Directives

The React frontend automatically parses spoken or typed commands before sending to conversational AI:

| Category | Voice / Text Directive | Action Dispatched |
|:---|:---|:---|
| **Google Search** | `"Search Python tutorials in Chrome"`<br>`"Google the weather"`<br>`"Search machine learning"` | Opens search results in Chrome (`https://www.google.com/search?q=...`) |
| **Direct Websites** | `"Open YouTube"`<br>`"Open GitHub"`<br>`"Open Gmail"`<br>`"Go to Reddit.com"` | Directly opens mapped domain in Google Chrome |
| **Launch Browser** | `"Open Chrome"`<br>`"Launch browser"` | Direct executable launch |
| **Tab Management** | `"New tab"` / `"Open a new tab"`<br>`"Close tab"` / `"Close this tab"`<br>`"Reopen tab"`<br>`"Next tab"` / `"Previous tab"` | Dispatches native hotkeys (`Ctrl+T`, `Ctrl+W`, `Ctrl+Shift+T`, etc.) |
| **Window Controls** | `"Minimize window"`<br>`"Maximize window"`<br>`"Refresh page"`<br>`"Scroll down"` / `"Scroll up"` | Dispatches window hotkeys (`Win+Down`, `Win+Up`, `Ctrl+R`, mouse scroll) |

---

## 📡 API Endpoint Reference

### `POST /api/chrome`
**Payload Example:**
```json
{
  "command": "search Python tutorials in chrome",
  "action": "search",
  "query": "Python tutorials"
}
```

**Response Example:**
```json
{
  "success": true,
  "action": "search",
  "message": "Searching Google for 'Python tutorials' in Chrome now, Boss.",
  "details": {
    "query": "Python tutorials",
    "url": "https://www.google.com/search?q=Python%20tutorials"
  }
}
```

