@echo off
echo ========================================================================
echo             Ensuring SVG to 3D Output Paths Exist
echo ========================================================================
echo.

echo Creating all necessary output directories...

REM Main output directories
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\diagrams 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\models 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\animations 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\videos 2>nul

REM SVG to Video specific directories
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg_to_video 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg_to_video\svg 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg_to_video\models 2>nul

REM Other output directories
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\blendergpt 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\hunyuan 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\scenes 2>nul
mkdir C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\trellis 2>nul

echo All output directories have been created.
echo.
echo ========================================================================
echo.

REM Check Blender path in config.yaml
echo Checking Blender path in configuration...
echo.
echo Current Blender path (from config.yaml):
findstr /C:"path:" C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\config.yaml | findstr /C:"blender.exe"
echo.
echo If the above path is incorrect, please update it in config.yaml
echo.
echo Checking status of SVG to 3D integration...
echo.
echo Press any key to restart services and test the integration...
pause > nul

REM Restart services
call C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\restart_services.bat
