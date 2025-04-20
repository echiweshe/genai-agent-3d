@echo off
echo ==========================================================
echo GenAI Agent 3D - Blender Scripts Fix Utility
echo ==========================================================
echo.
echo This script will fix issues with the Blender script execution feature:
echo   1. Create all required directories
echo   2. Add example Blender scripts
echo   3. Ensure correct paths are configured
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Running fix_directories.py...
python fix_directories.py

echo.
echo ==========================================================
echo Fix completed! Next steps:
echo ==========================================================
echo 1. Restart your backend server
echo 2. Restart your frontend server
echo 3. Navigate to the Blender Scripts page
echo 4. You should now see example scripts in the models folder
echo.
echo If you still encounter issues, check the console logs and
echo use the "Debug Blender Integration" button in the UI.
echo ==========================================================
echo.
pause
