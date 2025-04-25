@echo off
echo ================================================================================
echo                  GenAI Agent 3D - Direct Redis Connection Fix
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

:: Run the direct fix script
echo Running direct Redis connection fix...
python direct_redis_fix.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error encountered while running the fix. Please check the output above.
    echo.
    pause
    exit /b 1
)

echo.
echo Press any key to exit...
pause > nul
