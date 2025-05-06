@echo off
echo ================================================================================
echo                   SVG to Video Pipeline Repair Script                        
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
echo Running SVG pipeline fix script...
python fix_svg_pipeline.py

echo.
echo ================================================================================
echo SVG to Video Pipeline repairs completed. Press any key to exit...
pause >nul
