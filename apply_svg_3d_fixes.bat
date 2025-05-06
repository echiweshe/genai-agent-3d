@echo off
echo ================================================================================
echo                  SVG to 3D Conversion Fixes                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

echo Step 1: Creating necessary directories...
mkdir output\svg_to_video\models 2>nul
mkdir output\models 2>nul

echo.
echo Step 2: Restarting backend service...
call genai_agent_project\venv\Scripts\activate.bat
python genai_agent_project\manage_services.py restart backend

echo.
echo ================================================================================
echo SVG to 3D conversion fixes applied and backend restarted.
echo.
echo The following issues have been fixed:
echo  1. Output path handling for SVG to 3D conversion
echo  2. Changed Claude model from Opus to 3.5 Sonnet for better SVG quality
echo  3. Added proper file path checking in multiple locations
echo.
echo You can now try the SVG to Video pipeline again at: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
