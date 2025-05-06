@echo off
echo Fixing mathutils import issue
echo =========================
echo.

echo Running fix script...
python fix_mathutils_import.py
echo.

echo Fix complete!
echo Please restart the backend to apply changes.
echo.
pause
