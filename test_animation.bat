@echo off
echo 3D Model Animation Test
echo ====================
echo.

echo Activating virtual environment...
cd genai_agent_project
call venv\Scripts\activate
cd ..
echo.

echo Running test script...
python test_animation.py
echo.

echo Test complete!
pause
