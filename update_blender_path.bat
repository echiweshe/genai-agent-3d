@echo off
echo ================================================================================
echo                   Blender Path Update Utility                        
echo ================================================================================
echo.

:: Activate virtual environment if it exists
if exist "genai_agent_project\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "genai_agent_project\venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found.
)

:: Run the update script
echo Running Blender path update script...
python update_blender_path.py

echo.
echo ================================================================================
echo Update completed. Press any key to exit...
pause >nul
