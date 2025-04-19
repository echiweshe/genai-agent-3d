@echo off
echo Running all web tests for GenAI Agent 3D...
echo.

cd genai_agent_project\web

:: Run with the correct arguments based on the usage output
python run_all_tests.py --backend --frontend --e2e --start-backend --verbose

echo.
echo Test execution complete.
pause
