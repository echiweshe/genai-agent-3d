@echo off
echo SVG to 3D Integration
echo ===================
echo.

echo Running integration script...
powershell -ExecutionPolicy Bypass -File integrate_svg_to_3d.ps1
echo.

echo Integration complete!
echo Please restart the backend to apply changes:
echo restart_backend.bat
echo.
pause
