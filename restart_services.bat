@echo off
echo ========================================================================
echo                Restart GenAI Agent 3D Services
echo ========================================================================
echo.
echo This script will restart all GenAI Agent 3D services.
echo.
echo Press any key to continue...
pause > nul

REM Activate the Python virtual environment
call .\genai_agent_project\venv\Scripts\activate.bat

REM Run manage_services.py to restart all services
python genai_agent_project/manage_services.py restart all

echo.
echo Press any key to exit...
pause > nul
