@echo off
echo ========================================================
echo  Starting F.R.I.D.A.Y. Backend Bridge + Vite Frontend
echo ========================================================

start "FRIDAY Chrome Bridge (Port 8000)" cmd /k ".\venv\Scripts\python.exe backend/app.py"
start "Avatar Chat Interface (Port 5173)" cmd /k "npm --prefix avatar-chat-interface run dev"

echo Both services launched in background windows.
echo - Backend:  http://localhost:8000
echo - Frontend: http://localhost:5173

