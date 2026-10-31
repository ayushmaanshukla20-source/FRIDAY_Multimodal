# 🌌 FRIDAY — Voice-Controlled Desktop & Antigravity Assistant

[![Developer](https://img.shields.io/badge/Developer-Ayushmaan%20Shukla-cyan?style=for-the-badge)](#creator--author)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Antigravity-Online-00f7ff?style=for-the-badge)](#antigravity-module)
[![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge)](LICENSE)

> *"Online and systems initialized. I am Friday, created by Ayushmaan Shukla. Antigravity systems and automation drives are standing by."*

---

## 📖 Overview

**FRIDAY** is an intelligent, voice-activated desktop assistant engineered in Python by **Ayushmaan Shukla**. Designed with Tony Stark–inspired aesthetics and seamless productivity tooling, FRIDAY listens to vocal triggers in real time, automates web browsing workflows via Chrome, controls ambient media through Spotify, and monitors experimental **Antigravity subsystem protocols**.

---

## 🚀 Key Features

- 🎙️ **Natural Voice Interaction**: Real-time speech-to-text input paired with customizable vocal synthesis engine feedback (`pyttsx3`).
- 🌐 **Web Automation (Chrome Engine)**: Instant tab management, automated searches, queries, and navigation workflows.
- 🎵 **Spotify Media Controls**: Control playback, search artists/tracks, shuffle playlists, and adjust system audio without lifting a finger.
- 🛸 **Antigravity Protocol Mode**: Visual status checks, physics/simulation telemetry hooks, and easter egg triggers (including Python's built-in `import antigravity` utility hook).
- ⚡ **Asynchronous Event Loop**: Responsive multi-threaded command listener ensuring minimal latency between wake word and action execution.

---

## 🛠️ Tech Stack & Dependencies

| Component | Library / Tool | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application logic |
| **Voice Synthesis** | `pyttsx3` | Offline Text-to-Speech (TTS) |
| **Speech Recognition** | `SpeechRecognition` / `pyaudio` | Wake-word & command parsing |
| **Browser Control** | `selenium` / `webbrowser` | Automated Chrome navigation |
| **Music Streaming** | `spotipy` | Official Spotify Web API integration |
| **OS Automation** | `os`, `sys`, `pyautogui` | System-level tasks and controls |

---

## 📂 Project Architecture

```text
FRIDAY-AI/
├── assets/
│   └── friday_banner.png        # Holographic HUD branding banner
├── modules/
│   ├── speech_engine.py         # TTS and audio capture pipelines
│   ├── chrome_controller.py     # Browser automation & search hooks
│   ├── spotify_player.py        # Spotify API wrapper & track controls
│   └── antigravity_core.py      # Antigravity telemetry & Easter eggs
├── config/
│   └── settings.json            # Voice rate, volume, and API keys
├── .env.example                 # Spotify Client ID / Secret template
├── main.py                      # Application bootstrap & listener loop
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## ⚡ Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/AyushmaanShukla/friday-assistant.git
cd friday-assistant
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note for PyAudio on Windows:** If you encounter issues installing `pyaudio`, run:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
SPOTIPY_CLIENT_ID="your_spotify_client_id_here"
SPOTIPY_CLIENT_SECRET="your_spotify_client_secret_here"
SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
```

### 5. Launch FRIDAY
```bash
python main.py
```

---

## 🗣️ Supported Commands

| Category | Example Voice Command | Action Executed |
| :--- | :--- | :--- |
| **Greeting** | *"Friday, system status"* | Reports operational state and creator credits |
| **Web / Search**| *"Search Chrome for quantum computing"* | Opens Google Chrome directly to results |
| **Web Navigation**| *"Open GitHub"* | Launches default browser directly to repository |
| **Music** | *"Play Synthwave on Spotify"* | Triggers Spotify playback search & stream |
| **Playback** | *"Pause music"* / *"Next track"* | Adjusts active Spotify playback |
| **Antigravity** | *"Friday, engage antigravity"* | Activates zero-g telemetry routine |

---

## 🛸 Antigravity Module

The custom antigravity protocol simulates zero-G subsystem metrics and launches developer physics tools:

```python
# modules/antigravity_core.py
import time
import antigravity  # Python core easter egg


def toggle_antigravity(voice_engine):
    voice_engine.speak(
        "Antigravity drives engaged. Stabilizing orbital altitude."
    )
    time.sleep(0.5)
    # Launches web comic / physics simulation hook
    antigravity.geohash(37.421542, -122.085589, b"2005-05-26-10458.68")
```

---

## 👤 Creator & Author

**Ayushmaan Shukla**  
- **Role:** Lead Architect & Developer  
- **Project:** FRIDAY — Custom AI Assistant

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.