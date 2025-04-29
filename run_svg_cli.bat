@echo off
:: SVG to Video CLI Runner
:: This script runs the SVG to Video CLI with the provided arguments

:: Set the project root directory
set PROJECT_ROOT=%~dp0

:: Check if virtual environment exists
if not exist "%PROJECT_ROOT%venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating new virtual environment...
    python -m venv "%PROJECT_ROOT%venv"
    
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Please install Python 3.9+ and try again.
        exit /b 1
    )
    
    :: Install dependencies
    call "%PROJECT_ROOT%venv\Scripts\activate.bat"
    pip install -r "%PROJECT_ROOT%web\backend\requirements.txt"
    
    if %errorlevel% neq 0 (
        echo Failed to install dependencies. Please check your pip installation.
        exit /b 1
    )
) else (
    :: Activate the virtual environment
    call "%PROJECT_ROOT%venv\Scripts\activate.bat"
)

:: Run the CLI
python "%PROJECT_ROOT%cli\svg_video_cli.py" %*

:: Deactivate the virtual environment
deactivate
