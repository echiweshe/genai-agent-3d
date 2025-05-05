@echo off
echo SVG Generator All-in-One Fix and Test
echo ==================================
echo.

echo Step 1: Running all-in-one fix script...
powershell -ExecutionPolicy Bypass -File fix_svg_generator_all_in_one.ps1
echo.

echo Step 2: Testing SVG Generator with real LLMs...
python test_svg_generator.py
echo.

echo Step 3: Restarting backend service...
call restart_backend.bat
echo.

echo Process complete!
echo You can now test the SVG Generator through the web UI.
echo.
pause
