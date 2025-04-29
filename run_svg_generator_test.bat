@echo off
echo Testing SVG Generator Component
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_svg_to_video.bat first.
    exit /b 1
)

REM Check for master .env file
if exist genai_agent_project\.env (
    echo Using master .env file from genai_agent_project directory.
) else (
    echo Warning: Master .env file not found at genai_agent_project\.env
    echo Checking for local .env file...
    
    if exist .env (
        echo Using local .env file.
    ) else (
        echo No .env file found. API keys may not be available.
        echo The test may fail if no API keys are available.
    )
)

REM Activate virtual environment and run the test
call venv\Scripts\activate
python test_svg_generator.py

echo.
echo Test completed.
pause
