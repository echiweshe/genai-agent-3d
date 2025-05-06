@echo off
echo SVG to Video Pipeline - Diagnostic Tool
echo ================================
echo.

echo Activating virtual environment...
cd genai_agent_project
call venv\Scripts\activate
cd ..
echo.

echo Running diagnostic tool...
python diagnose_svg_pipeline.py
echo.

echo Diagnostic complete!
echo Please review the results in svg_pipeline_diagnostic_results.json and svg_pipeline_diagnostic.log
echo.
pause
