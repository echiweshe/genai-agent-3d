@echo off
echo ================================================================================
echo                 GenAI Agent 3D - LLMService Initialization Fix
echo ================================================================================
echo.

echo This batch file will run a targeted fix for the LLMService initialization error:
echo "LLMService.__init__() takes 1 positional argument but 2 were given"
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Running LLMService initialization fix...

python fix_llmservice_init.py

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
