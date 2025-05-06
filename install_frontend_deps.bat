@echo off
echo ================================================================================
echo                   Installing Frontend Dependencies                        
echo ================================================================================
echo.

:: Navigate to the frontend directory
cd genai_agent_project\web\frontend

:: Install the missing lucide-react package
echo Installing lucide-react package...
call npm install --save lucide-react

echo.
echo ================================================================================
echo Frontend dependencies installed. Now restarting frontend service...

:: Go back to the project root
cd ..\..\..

:: Restart the frontend service
call genai_agent_project\manage_services.py restart frontend

echo.
echo ================================================================================
echo Frontend restarted. Access the web UI at http://localhost:3000
echo Press any key to exit...
pause >nul
