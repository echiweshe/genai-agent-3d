@echo off
echo Checking and fixing Claude API key issues
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_svg_to_video.bat first.
    exit /b 1
)

REM Activate virtual environment and run the fix
call venv\Scripts\activate
python fix_claude_key.py

echo.
echo After fixing the key, try running: run_svg_generator_test.bat
pause
