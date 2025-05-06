@echo off
echo ================================================================================
echo                   SVG to Video Pipeline Status Check                        
echo ================================================================================
echo.

:: Activate virtual environment if it exists
if exist "genai_agent_project\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "genai_agent_project\venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found.
)

:: Run the status check script
echo Running SVG to Video pipeline status check...
python check_svg_pipeline_status.py

echo.
echo ================================================================================
echo Status check completed. Press any key to exit...
pause >nul
