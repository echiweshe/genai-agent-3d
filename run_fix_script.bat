@echo off
echo ========================================================
echo           GenAI Agent 3D - Directory Fix Script
echo ========================================================
echo.
echo This script will:
echo  - Create all necessary directories for Blender scripts
echo  - Add example scripts to these directories
echo  - Make sure your application can find them
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Running fix_directories.py...
python fix_directories.py

echo.
echo ========================================================
echo                      NEXT STEPS
echo ========================================================
echo 1. Restart your backend server (python run_server.py)
echo 2. Restart your frontend server (npm start)
echo 3. Refresh your browser page
echo.
echo If you still see "No scripts found", check the browser 
echo console (F12) for more detailed error messages.
echo ========================================================
echo.

pause
