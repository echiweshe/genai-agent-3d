@echo off
echo ========================================================================
echo             Restart Services After SVG to 3D Viewer Integration
echo ========================================================================
echo.
echo This script will restart all GenAI Agent 3D services.
echo.

REM Activate the Python virtual environment
call .\genai_agent_project\venv\Scripts\activate.bat

echo.
echo Restarting services...
python genai_agent_project/manage_services.py restart all

echo.
echo Services restarted! Now testing Blender integration...
timeout /t 5 /nobreak > nul

echo.
echo Testing Blender availability...
curl -s http://localhost:8000/blender/health

echo.
echo.
echo If you see "status": "available" above, Blender integration is working!
echo If you see "status": "unavailable", please check your Blender installation.
echo.
echo You can now try the SVG to 3D Viewer at http://localhost:3000/svg-to-video
echo.
pause
