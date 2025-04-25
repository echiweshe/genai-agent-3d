@echo off
echo ================================================================================
echo                       GenAI Agent 3D - LLM Error Fixes
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

:: Run the fix script
echo Running LLM error fix script...
python fix_llm_errors.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error encountered while running fix script. Please check the output above.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                              Fixes Applied!
echo ================================================================================
echo.
echo You can now restart the services with: python restart_services.py
echo Or by running: cd genai_agent_project
echo               python manage_services.py restart all
echo.
echo After restarting, access the web interface at: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
