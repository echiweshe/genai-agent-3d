@echo off
echo ========================================================================
echo                Fix Claude API Key for GenAI Agent 3D
echo ========================================================================
echo.
echo This script will help you set up your Claude (Anthropic) API key.
echo You'll need a valid API key from Anthropic to use Claude in the application.
echo.
echo Press any key to continue...
pause > nul

REM Activate the Python virtual environment
call .\genai_agent_project\venv\Scripts\activate.bat

REM Run the Python script to fix the API key
python fix_claude_api_key.py

echo.
echo If the key was set successfully, you can now restart the application to use Claude.
echo To restart the application, use: python manage_services.py restart all
echo.
echo Press any key to exit...
pause > nul
