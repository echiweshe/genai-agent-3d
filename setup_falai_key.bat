@echo off
echo ========================================================================
echo                Setup fal.ai API Key for Hunyuan3D
echo ========================================================================
echo.
echo This script will help you set up your fal.ai API key for Hunyuan3D integration.
echo.
echo Press any key to continue...
pause > nul

REM Activate the Python virtual environment
call .\genai_agent_project\venv\Scripts\activate.bat

REM Run the Python script to set up the API key
python setup_falai_key.py

echo.
echo Press any key to exit...
pause > nul
