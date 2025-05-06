@echo off
echo ========================================================================
echo             Test Blender Integration for SVG to 3D Viewer
echo ========================================================================
echo.

REM Activate the Python virtual environment
call .\genai_agent_project\venv\Scripts\activate.bat

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
