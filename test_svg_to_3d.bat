@echo off
echo SVG to 3D Conversion Test
echo =======================
echo.

echo Activating virtual environment...
cd genai_agent_project
call venv\Scripts\activate
cd ..
echo.

echo Running test script...
python test_svg_to_3d.py
echo.

echo Test complete!
pause
