@echo off
echo ================================================================================
echo                  GenAI Agent 3D - Fix All LLM Issues
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

:: Run the combined fix script
echo Running combined fix script for all LLM issues...
python fix_all_llm_issues.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error encountered while running fix script. Please check the output above.
    echo.
    pause
    exit /b 1
)

echo.
echo Press any key to exit...
pause > nul
