@echo off
echo ================================================================================
echo                      GenAI Agent 3D - Redis Connection Fix
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
echo Running Redis connection fix script...
python fix_redis_connection.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error encountered while running fix script. Please check the output above.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                                 Fix Applied!
echo ================================================================================
echo.
echo You can access the web interface at: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
