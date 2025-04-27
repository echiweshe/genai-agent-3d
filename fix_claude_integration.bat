@echo off
echo =============================================
echo Claude API Integration Fix for GenAI Agent 3D
echo =============================================
echo.
echo This script will fix the Claude API integration issues.
echo It will update the LLM service to correctly handle Claude API requests and responses.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

python fix_claude_integration.py

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo An error occurred during execution.
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo Fix completed. Press any key to exit...
pause > nul
