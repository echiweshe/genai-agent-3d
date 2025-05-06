@echo off
echo Rendering Module Integration
echo ==========================
echo.

echo Running integration script...
powershell -ExecutionPolicy Bypass -File integrate_rendering.ps1
echo.

echo Integration complete!
echo Please restart the backend to apply changes:
echo restart_backend.bat
echo.
pause
