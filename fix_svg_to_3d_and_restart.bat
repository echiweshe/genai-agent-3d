@echo off
echo ================================================================================
echo                  FIX SVG TO 3D CONVERSION AND RESTART                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

echo Step 1: Applying SVG to 3D conversion fixes...
python fix_svg_to_3d_conversion.py

echo.
echo Step 2: Restarting backend service...
call genai_agent_project\venv\Scripts\activate.bat
python genai_agent_project\manage_services.py restart backend

echo.
echo ================================================================================
echo SVG to 3D conversion fixed and backend restarted!
echo.
echo The following improvements were made:
echo  1. Simplified SVG to 3D conversion process
echo  2. Improved Blender script for more reliable conversion
echo  3. Better error handling and logging
echo  4. Automatic copying of models to multiple output directories
echo.
echo You can now try the SVG to Video pipeline at: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
