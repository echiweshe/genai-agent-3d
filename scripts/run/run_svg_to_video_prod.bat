@echo off
echo Starting GenAI Agent 3D - SVG to Video Pipeline (Production)
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

REM Check if frontend is built
if not exist web\frontend\build (
    echo Frontend is not built.
    
    REM Check if Node.js is available
    where node >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo WARNING: Node.js is not installed or not in PATH.
        echo The frontend cannot be built. The server will only provide API functionality.
    ) else (
        echo Building frontend...
        cd web\frontend
        call npm install
        call npm run build
        cd ..\..
    )
)

REM Start the backend server
echo Starting backend server...
call venv\Scripts\activate
cd web\backend
python main.py

echo.
echo SVG to Video Pipeline server has stopped.
