@echo off
REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_svg_to_video.bat first.
    exit /b 1
)

REM Load environment variables from .env file if it exists
if exist .env (
    for /F "tokens=*" %%A in (.env) do (
        set %%A
    )
)

REM Activate virtual environment and run CLI
call venv\Scripts\activate
python cli\svg_video_cli.py %*
