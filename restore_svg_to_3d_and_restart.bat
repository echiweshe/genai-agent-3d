@echo off
echo ================================================================================
echo                  RESTORE SVG TO 3D MODULES AND RESTART                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

echo Step 1: Restoring SVG to 3D modules from backup...
python restore_svg_to_3d_modules.py

echo.
echo Step 2: Restarting backend service...
call genai_agent_project\venv\Scripts\activate.bat
python genai_agent_project\manage_services.py restart backend

echo.
echo ================================================================================
echo SVG to 3D modules restored and backend restarted!
echo.
echo The following has been restored:
echo  1. Complete modular SVG to 3D converter system
echo  2. All converter modules (svg_parser.py, svg_converter_*.py, etc.)
echo  3. Necessary utility files and functions
echo  4. All imports have been adjusted to work in the new location
echo  5. Output directories have been created
echo.
echo You can now use the complete SVG to Video pipeline at: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
