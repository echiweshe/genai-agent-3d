@echo off
echo Starting the GenAI Agent 3D Web UI with SVG Generator Integration

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python not found! Please install Python and try again.
    pause
    exit /b 1
)

REM Set environment variables
set PYTHONPATH=%CD%
set OUTPUT_DIR=%CD%\output

REM Create necessary directories
mkdir output\svg 2>nul
mkdir output\diagrams 2>nul

echo Starting backend server...
start "" cmd /c "cd genai_agent_project\web\backend && python main.py"

REM Wait for the backend to start
timeout /t 3 /nobreak >nul

echo Server should be running at http://localhost:8000
echo Frontend should be accessible at http://localhost:3000
echo.
echo You can now use the SVG Generator functionality in the Diagrams page
echo.
echo Press any key to exit...
pause >nul
