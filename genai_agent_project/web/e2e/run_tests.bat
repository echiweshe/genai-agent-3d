@echo off
echo Starting E2E tests...

rem Check if backend server is running on port 8000
echo Checking if backend server is running...
netstat -ano | findstr :8000 > nul
if %errorlevel% neq 0 (
    echo Backend server is not running. Starting it...
    start cmd /c "cd ..\backend && python start_server.bat"
    timeout /t 5
)

rem Check if frontend server is running on port 3000
echo Checking if frontend server is running...
netstat -ano | findstr :3000 > nul
if %errorlevel% neq 0 (
    echo Frontend server is not running. Starting it...
    start cmd /c "cd ..\frontend && npm start"
    timeout /t 10
)

echo Running E2E tests...
npm test

echo Tests completed!
pause
