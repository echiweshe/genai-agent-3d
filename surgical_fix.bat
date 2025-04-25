@echo off
echo ================================================================================
echo                  GenAI Agent 3D - Surgical Redis Connection Fix
echo ================================================================================
echo.

echo This batch file will run a minimal, targeted fix for the Redis connection
echo error without making extensive changes to the codebase.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Running surgical fix...

python surgical_redis_fix.py

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
