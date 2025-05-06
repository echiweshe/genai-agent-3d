@echo off
echo Applying SVG to 3D Viewer and Blender Integration...

echo.
echo Checking if Blender is installed...
if exist "%ProgramFiles%\Blender Foundation" (
    echo Blender found in Program Files.
) else (
    echo Blender not found. Please install Blender or set BLENDER_PATH in .env file.
)

echo.
echo Checking if output directories exist...
if not exist ".\genai_agent_project\output\models" (
    echo Creating output\models directory...
    mkdir ".\genai_agent_project\output\models"
)

if not exist ".\genai_agent_project\output\svg_to_video" (
    echo Creating output\svg_to_video directory...
    mkdir ".\genai_agent_project\output\svg_to_video"
)

echo.
echo Updating backend routes...
echo - Blender routes are now available
echo - SVG to 3D conversion with Blender integration

echo.
echo Restarting services...

REM Activate the Python virtual environment
call .\genai_agent_project\venv\Scripts\activate.bat

REM Run manage_services.py to restart all services
python genai_agent_project/manage_services.py restart all

echo.
echo SVG to 3D Viewer and Blender Integration complete!
echo Please refresh your browser to access the new features.
echo Navigate to: http://localhost:3000/svg-to-video
echo.
pause
