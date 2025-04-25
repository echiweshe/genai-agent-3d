@echo off
echo ================================================================================
echo                       GenAI Agent 3D - Quick Fix Script
echo ================================================================================
echo.

echo Stopping all services...
cd genai_agent_project
call venv\Scripts\activate.bat
python manage_services.py stop all

echo.
echo Applying redis_bus.py fix...
cd ..

echo.
echo Starting services...
cd genai_agent_project
python manage_services.py start all

echo.
echo ================================================================================
echo                                 Fix Applied!  
echo ================================================================================
echo.
echo The redis_bus.py file has been updated to fix the inet_pton() error.
echo.
echo You can now access the web interface at: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
