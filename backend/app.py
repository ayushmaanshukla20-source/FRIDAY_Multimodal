"""
FRIDAY Multimodal Voice Assistant
Author: Ayushmaan Shukla
Roll / Enrollment No.: 202510101240164
Department: Computer Science & Engineering (AI & ML)
Institution: Shri Ramswaroop Memorial University
Notice: This project is strictly for academic evaluation. 
        Unauthorized reproduction or submission is a violation of academic integrity.
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uvicorn
from backend.main import app

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 8080))
    print(f"[F.R.I.D.A.Y. Backend Bridge] Starting on http://127.0.0.1:{port} (CORS enabled for http://localhost:5173)...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=False)


