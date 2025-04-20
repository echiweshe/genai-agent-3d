@echo off
echo ========================================================
echo     GenAI Agent 3D - Running Direct Backend Server
echo ========================================================
echo.
echo This will start the backend with direct API routes
echo to fix the "No scripts found" issue.
echo.
echo Press Ctrl+C to stop the server when done.
echo.
echo Starting server on http://localhost:8000
echo.
cd genai_agent_project\web\backend
python main_direct.py
