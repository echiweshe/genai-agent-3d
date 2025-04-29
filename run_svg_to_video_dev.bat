@echo off
echo Starting GenAI Agent 3D - SVG to Video Pipeline (Development)
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_svg_to_video.bat first.
    exit /b 1
)

REM Create outputs directory if it doesn't exist
if not exist outputs mkdir outputs

REM Load environment variables from .env file if it exists
if exist .env (
    echo Loading environment variables from .env...
    for /F "tokens=*" %%A in (.env) do (
        set %%A
    )
)

REM Start the backend server in a new window
start cmd /k "echo Starting backend server... & call venv\Scripts\activate & cd web\backend & python main.py"

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
echo SVG to Video Pipeline development servers are running.
