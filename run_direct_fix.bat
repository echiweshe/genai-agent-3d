@echo off
echo ========================================================
echo     GenAI Agent 3D - Direct Fix for Blender Scripts
echo ========================================================
echo.
echo This script will:
echo  1. Create all possible output directories
echo  2. Add example Blender scripts
echo  3. Fix API path issues
echo  4. Add direct API endpoints
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Running direct_fix.py...
python direct_fix.py

echo.
echo ========================================================
echo                  MANUAL FIX STEPS
echo ========================================================
echo If the issue persists, try the following:
echo.
echo 1. Start your backend server and access:
echo    http://localhost:8000/direct/fix-directories
echo.
echo 2. Check for any error messages in the browser console
echo    by pressing F12 and looking at the Network tab
echo.
echo 3. Make sure your API URL is correct:
echo    - Frontend should use: http://localhost:8000
echo    - NOT: http://localhost:8000/api
echo.
echo ========================================================
echo.
pause
