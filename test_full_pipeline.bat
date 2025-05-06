@echo off
echo SVG to Video Pipeline - Full Test
echo ============================
echo.

echo Activating virtual environment...
cd genai_agent_project
call venv\Scripts\activate
cd ..
echo.

echo Running full pipeline test...
python test_full_pipeline.py
echo.

echo Test complete!
pause
