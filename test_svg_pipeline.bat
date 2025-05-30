@echo off
echo ================================================================================
echo                   Testing SVG to Video Pipeline                        
echo ================================================================================
echo.

:: Activate virtual environment if it exists
if exist "genai_agent_project\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "genai_agent_project\venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found.
)

:: Run the test script
echo Running SVG to Video pipeline test...
python genai_agent_project\genai_agent\svg_to_video\test_pipeline.py

echo.
echo ================================================================================
echo Test completed. Check the output for any errors. Press any key to exit...
pause >nul
