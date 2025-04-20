@echo off
echo ========================================================
echo     GenAI Agent 3D - Fix Models Endpoint Mismatch
echo ========================================================
echo.
echo This script will fix the "Error loading: output/models/..." issue
echo by adding a direct handler for the /models endpoint.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Running fix_models_endpoint.py...
python fix_models_endpoint.py

echo.
echo ========================================================
echo                      NEXT STEPS
echo ========================================================
echo 1. Restart your backend server:
echo    cd genai_agent_project\web\backend
echo    python run_server.py
echo.
echo 2. In a new command prompt, restart your frontend:
echo    cd genai_agent_project\web\frontend
echo    npm start
echo.
echo 3. Test creating a new model or refreshing models page
echo.
pause
