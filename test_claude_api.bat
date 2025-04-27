@echo off
echo =============================================
echo Claude API Integration Test for GenAI Agent 3D
echo =============================================
echo.
echo This script will test the Claude API integration.
echo It will send a simple request to the Claude API and check if the response is valid.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

python test_claude_api.py

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo An error occurred during execution.
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo Test completed. Press any key to exit...
pause > nul
