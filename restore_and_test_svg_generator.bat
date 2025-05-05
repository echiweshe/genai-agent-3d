@echo off
echo SVG Generator Restoration and Testing
echo ===================================
echo.

echo Step 1: Restoring SVG Generator from backup...
powershell -ExecutionPolicy Bypass -File restore_svg_generator.ps1
echo.

echo Step 2: Testing SVG Generator with real LLMs...
python test_svg_generator.py
echo.

echo Step 3: Integrating SVG Generator with Web UI...
python integrate_svg_to_web_ui.py
echo.

echo Process complete! 
echo Now you can restart the Web UI to see the SVG Generator in action.
echo.
pause
