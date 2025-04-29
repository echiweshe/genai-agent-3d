@echo off
echo Setting up GenAI Agent 3D - SVG to Video Pipeline
echo.

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.9+.
    exit /b 1
)

REM Check for pip
python -m pip --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo pip is not installed. Please install pip.
    exit /b 1
)

REM Check for Node.js
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo WARNING: Node.js is not installed or not in PATH.
    echo The frontend setup will be skipped. Please install Node.js 14+ to run the frontend.
    set SKIP_FRONTEND=1
) else (
    set SKIP_FRONTEND=0
)

REM Create outputs directory if it doesn't exist
if not exist outputs mkdir outputs

REM Install dotenv package for Python first 
echo Installing python-dotenv...
pip install python-dotenv

REM Create Python virtual environment
echo Creating Python virtual environment...
if not exist venv (
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment. Please install venv.
        echo You can install it with: pip install virtualenv
        exit /b 1
    )
)

REM Activate virtual environment and install backend dependencies
echo Installing backend dependencies...
call venv\Scripts\activate
pip install -r web\backend\requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install backend dependencies.
    exit /b 1
)
echo Backend dependencies installed successfully.

REM Install frontend dependencies if Node.js is available
if %SKIP_FRONTEND% == 0 (
    echo Installing frontend dependencies...
    cd web\frontend
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo Failed to install frontend dependencies.
        cd ..\..
        exit /b 1
    )
    cd ..\..
    echo Frontend dependencies installed successfully.
)

REM Check for existing .env files
echo Checking for .env files...
if exist genai_agent_project\.env (
    echo Found master .env file at genai_agent_project\.env
    echo The application will use this file for API keys.
) else (
    echo Master .env file not found at genai_agent_project\.env
    
    if not exist .env (
        echo Creating local .env file...
        if exist .env.template (
            copy .env.template .env
            echo Created .env file from template. Please edit it to add your API keys.
        ) else (
            echo # API Keys for LLM Providers > .env
            echo # Uncomment and add your keys > .env
            echo # ANTHROPIC_API_KEY=your_anthropic_api_key >> .env
            echo # OPENAI_API_KEY=your_openai_api_key >> .env
            echo # BLENDER_PATH=path_to_blender_executable >> .env
        )
        echo Note: You'll need to add your API keys to this file.
    else
        echo Found local .env file at the project root.
    )
)

echo.
echo Setup completed successfully!
echo.

if %SKIP_FRONTEND% == 1 (
    echo NOTE: The frontend setup was skipped. Please install Node.js to run the frontend.
)

echo To test the SVG generator component:
echo   run_svg_generator_test.bat
echo.
echo To run the simplified development environment:
echo   run_simple_dev.bat
echo.
echo To run the development servers:
echo   run_svg_to_video_dev.bat
echo.
echo To run the production server:
echo   run_svg_to_video_prod.bat
