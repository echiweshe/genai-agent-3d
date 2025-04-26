genai_agent_project/.env@echo off
echo ================================================================================
echo                   GenAI Agent 3D - Update and Run Script
echo ================================================================================
echo.

:: Check if Python is available
where python > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python 3.8 or higher.
    echo.
    pause
    exit /b 1
)

:: Run the update script
echo Running update script...
python 09_update_agent_llm.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Update script encountered an error. Please check the output above.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                 GenAI Agent 3D is now updated and running!
echo ================================================================================
echo.
echo You can access the web interface at: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
