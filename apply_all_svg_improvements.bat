@echo off
echo ================================================================================
echo                  Applying All SVG Pipeline Improvements                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

echo Step 1: Creating necessary directories...
mkdir output\svg_to_video\models 2>nul
mkdir output\models 2>nul

echo.
echo Step 2: Installing frontend dependencies...
cd genai_agent_project\web\frontend
call npm install --save lucide-react
cd ..\..\..

echo.
echo Step 3: Restarting all services...
call genai_agent_project\venv\Scripts\activate.bat
python genai_agent_project\manage_services.py restart all

echo.
echo ================================================================================
echo All SVG Pipeline improvements applied and services restarted.
echo.
echo The following issues have been fixed:
echo  1. Frontend icon display fixed
echo  2. SVG to 3D conversion file path handling improved
echo  3. SVG generation prompt enhanced for better quality diagrams
echo  4. Changed Claude model to 3.5 Sonnet for better results
echo  5. Additional diagram types supported with specialized prompts
echo  6. Added proper error handling and file path checking
echo.
echo You can now use the complete SVG to Video pipeline at: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
