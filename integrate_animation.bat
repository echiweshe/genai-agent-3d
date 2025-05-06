@echo off
echo Animation Module Integration
echo =========================
echo.

echo Running integration script...
powershell -ExecutionPolicy Bypass -File integrate_animation.ps1
echo.

echo Integration complete!
echo Please restart the backend to apply changes:
echo restart_backend.bat
echo.
pause
