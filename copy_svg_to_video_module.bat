@echo off
echo Copying SVG to Video module...
python copy_svg_to_video_module.py
echo.
if %ERRORLEVEL% EQU 0 (
    echo SVG to Video module copied successfully.
    echo You can now restart the services with:
    echo python manage_services.py restart all
) else (
    echo Failed to copy SVG to Video module. Check the logs for details.
)
pause
