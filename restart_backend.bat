@echo off
echo Restarting backend service
echo ========================
echo.

cd genai_agent_project
call venv\Scripts\activate
python manage_services.py restart backend
echo.

echo Backend restart complete!
pause
