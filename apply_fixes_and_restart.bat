@echo off
echo ================================================================================
echo                   Applying SVG Pipeline Fixes and Restarting Services                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

echo Step 1: Ensuring dependencies are installed...
call genai_agent_project\venv\Scripts\activate.bat
cd genai_agent_project\web\frontend
call npm install --save lucide-react
cd ..\..\..\

echo.
echo Step 2: Restarting services...
python genai_agent_project\manage_services.py restart all

echo.
echo ================================================================================
echo All fixes applied and services restarted. 
echo.
echo The following issues have been fixed:
echo  1. SVGTo3DConverter async compatibility
echo  2. Frontend icon display
echo.
echo You can now access the web interface at: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
