@echo off
echo SVG Directory Synchronization
echo ===========================
echo.

powershell -ExecutionPolicy Bypass -File sync_svg_directories.ps1
echo.

echo Synchronization complete!
pause
