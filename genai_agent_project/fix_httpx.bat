@echo off
echo ================================================================================
echo                 GenAI Agent 3D - Install Dependencies Fix
echo ================================================================================
echo.

:: Activate virtual environment if not already activated
if not defined VIRTUAL_ENV (
    if exist venv\Scripts\activate.bat (
        echo Activating virtual environment...
        call venv\Scripts\activate.bat
    ) else (
        echo Virtual environment not found!
        pause
        exit /b 1
    )
)

:: Install httpx directly
echo Installing httpx and other dependencies...
pip install httpx pydantic fastapi redis pyyaml requests uvicorn

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to install dependencies. Please check the output above.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                       Dependencies installed successfully!
echo ================================================================================
echo.
echo You can now start the application with: python manage_services.py restart all
echo.
pause
