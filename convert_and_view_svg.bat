@echo off
echo ================================================================================
echo                  Convert SVG to 3D and View in Blender                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

:: Get SVG file path from command line argument
set SVG_FILE=%1

if "%SVG_FILE%"=="" (
    echo Error: No SVG file specified.
    echo Usage: convert_and_view_svg.bat path\to\svg_file.svg
    goto :end
)

:: Activate virtual environment
call genai_agent_project\venv\Scripts\activate.bat

:: Run the Python script to convert SVG to 3D and open in Blender
python convert_and_view_svg.py "%SVG_FILE%"

:end
echo.
echo ================================================================================
echo Press any key to exit...
pause >nul
