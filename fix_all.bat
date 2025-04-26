@echo off
echo ===============================================================================
echo                GenAI Agent 3D - Fix All Issues
echo ===============================================================================
echo.
echo This script will fix all known issues with the GenAI Agent 3D project.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

python fix_all_issues.py

echo.
echo If you chose not to restart services, you can do so now by running:
echo python genai_agent_project\manage_services.py restart all
echo.
echo Press any key to exit...
pause > nul
