@echo off
echo ================================================================================
echo                   Restarting Frontend Service                        
echo ================================================================================
echo.

:: Activate virtual environment if it exists
if exist "genai_agent_project\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "genai_agent_project\venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found.
)

:: Run the restart script
echo Restarting frontend service...
python genai_agent_project\manage_services.py restart frontend

echo.
echo ================================================================================
echo Frontend service restarted successfully. Press any key to exit...
pause >nul
