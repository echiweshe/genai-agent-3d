@echo off
echo ========================================================
echo     GenAI Agent 3D - Comprehensive Path Check and Fix
echo ========================================================
echo.
echo This script will:
echo  1. Analyze your project structure
echo  2. Check all possible paths for issues
echo  3. Create missing directories
echo  4. Fix API configuration issues
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Running direct_check.py...
python direct_check.py

echo.
echo ========================================================
echo                IMPORTANT INSTRUCTIONS
echo ========================================================
echo After running this check and fix utility:
echo.
echo 1. Make sure to restart your backend server:
echo    cd genai_agent_project\web\backend
echo    python run_server.py
echo.
echo 2. In a separate command prompt, restart frontend:
echo    cd genai_agent_project\web\frontend
echo    npm start
echo.
echo 3. If your Blender Scripts page works now, great!
echo.
echo 4. If not, run the direct_fix.py script for more fixes:
echo    python direct_fix.py
echo.
echo ========================================================
echo.
pause
