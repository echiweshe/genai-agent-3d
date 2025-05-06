@echo off
echo ================================================================================
echo                    SVG Directory Synchronization Script                       
echo ================================================================================
echo.

:: Check for Administrator privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo This script should be run as Administrator to create symbolic links.
    echo Right-click on this batch file and select "Run as administrator".
    echo.
    echo Press any key to continue anyway (symbolic links may fail)...
    pause >nul
)

:: Activate virtual environment if it exists
if exist "genai_agent_project\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "genai_agent_project\venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found.
)

:: Run the Python script
echo Running SVG directory synchronization script...
python sync_svg_directories.py

echo.
echo ================================================================================
echo Synchronization completed. Press any key to exit...
pause >nul
