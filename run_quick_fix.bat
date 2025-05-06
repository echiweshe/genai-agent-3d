@echo off
echo ================================================================================
echo                   SVG to Video Pipeline Quick Fix                        
echo ================================================================================
echo.

:: Activate virtual environment if it exists
if exist "genai_agent_project\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "genai_agent_project\venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found.
)

:: Run the fix script
echo Running quick fix...
python run_quick_fix.py

echo.
echo ================================================================================
echo Quick fix applied. Press any key to exit...
pause >nul
