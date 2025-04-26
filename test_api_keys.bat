@echo off
echo ========================================================================
echo                Test API Keys for GenAI Agent 3D
echo ========================================================================
echo.
echo This script will test your API keys by making simple requests.
echo.
echo Press any key to continue...
pause > nul

REM Activate the Python virtual environment
call .\genai_agent_project\venv\Scripts\activate.bat

REM Run the Python script to test API keys
python test_api_keys.py

echo.
echo Press any key to exit...
pause > nul
