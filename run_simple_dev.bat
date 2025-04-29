@echo off
echo Starting simplified SVG to Video development environment
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_svg_to_video.bat first.
    exit /b 1
)

REM Create outputs directory if it doesn't exist
if not exist outputs mkdir outputs

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
        echo The application may not work properly without API keys.
    )
)

REM Start the simple backend server in a new window
start cmd /k "echo Starting simple backend server... & call venv\Scripts\activate & cd web\backend & python simple_server.py"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if Node.js is available
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo WARNING: Node.js is not installed or not in PATH.
    echo The frontend development server cannot be started.
    echo You can still access the backend API at http://localhost:8000
    exit /b 0
)

REM Start the frontend development server
echo Starting frontend development server...
cd web\frontend
npm start

echo.
echo Development environment is running.
