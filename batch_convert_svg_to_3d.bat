@echo off
echo ================================================================================
echo                  Batch Convert SVG to 3D Models                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

:: Get input directory from command line argument
set INPUT_DIR=%1

if "%INPUT_DIR%"=="" (
    set INPUT_DIR=output\svg
    echo No input directory specified, using default: %INPUT_DIR%
) else (
    echo Input directory: %INPUT_DIR%
)

:: Activate virtual environment
call genai_agent_project\venv\Scripts\activate.bat

:: Run the Python script to convert all SVG files to 3D models
python batch_convert_svg_to_3d.py "%INPUT_DIR%"

echo.
echo ================================================================================
echo Press any key to exit...
pause >nul
