@echo off
:: SVG to Video Setup Script
:: This script sets up the SVG to Video pipeline

:: Set the project root directory
set PROJECT_ROOT=%~dp0

echo ==============================================
echo        SVG to Video Pipeline Setup
echo ==============================================

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.9+ and try again.
    exit /b 1
)

:: Create virtual environment
echo Creating Python virtual environment...
if not exist "%PROJECT_ROOT%venv" (
    python -m venv "%PROJECT_ROOT%venv"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        echo Please ensure Python 3.9+ is installed and venv module is available.
        exit /b 1
    )
)

:: Activate virtual environment and install backend dependencies
echo Installing backend dependencies...
call "%PROJECT_ROOT%venv\Scripts\activate.bat"

:: Ensure pip is up to date
python -m pip install --upgrade pip

:: Create requirements.txt if it doesn't exist
if not exist "%PROJECT_ROOT%web\backend\requirements.txt" (
    echo Creating requirements.txt...
    mkdir "%PROJECT_ROOT%web\backend" 2>nul
    (
        echo fastapi==0.95.0
        echo uvicorn==0.21.1
        echo python-multipart==0.0.6
        echo requests==2.28.2
        echo python-dotenv==1.0.0
        echo jinja2==3.1.2
        echo aiofiles==23.1.0
        echo pydantic==1.10.7
    ) > "%PROJECT_ROOT%web\backend\requirements.txt"
)

:: Install backend dependencies
pip install -r "%PROJECT_ROOT%web\backend\requirements.txt"
if %errorlevel% neq 0 (
    echo Failed to install backend dependencies.
    exit /b 1
)

:: Create outputs directory
echo Creating outputs directory...
mkdir "%PROJECT_ROOT%outputs" 2>nul

:: Create .env template if it doesn't exist
if not exist "%PROJECT_ROOT%.env" (
    echo Creating .env template...
    (
        echo # API Keys for LLM Providers
        echo ANTHROPIC_API_KEY=your_anthropic_api_key
        echo OPENAI_API_KEY=your_openai_api_key
        echo # Optional, if Blender is not in PATH
        echo BLENDER_PATH=path_to_blender_executable
    ) > "%PROJECT_ROOT%.env"
)

:: Check if Node.js is installed and set up frontend if available
node --version > nul 2>&1
if %errorlevel% equ 0 (
    echo Node.js detected, setting up frontend...
    
    :: Create frontend directory if it doesn't exist
    if not exist "%PROJECT_ROOT%web\frontend" (
        mkdir "%PROJECT_ROOT%web\frontend" 2>nul
    )
    
    :: Create base package.json if it doesn't exist
    if not exist "%PROJECT_ROOT%web\frontend\package.json" (
        echo Creating basic package.json...
        (
            echo {
            echo   "name": "svg-to-video-frontend",
            echo   "version": "0.1.0",
            echo   "private": true,
            echo   "dependencies": {
            echo     "@testing-library/jest-dom": "^5.16.5",
            echo     "@testing-library/react": "^13.4.0",
            echo     "@testing-library/user-event": "^13.5.0",
            echo     "react": "^18.2.0",
            echo     "react-dom": "^18.2.0",
            echo     "react-scripts": "5.0.1",
            echo     "axios": "^1.3.4",
            echo     "web-vitals": "^2.1.4"
            echo   },
            echo   "scripts": {
            echo     "start": "react-scripts start",
            echo     "build": "react-scripts build",
            echo     "test": "react-scripts test",
            echo     "eject": "react-scripts eject"
            echo   },
            echo   "eslintConfig": {
            echo     "extends": [
            echo       "react-app",
            echo       "react-app/jest"
            echo     ]
            echo   },
            echo   "browserslist": {
            echo     "production": [
            echo       "^>0.2%%",
            echo       "not dead",
            echo       "not op_mini all"
            echo     ],
            echo     "development": [
            echo       "last 1 chrome version",
            echo       "last 1 firefox version",
            echo       "last 1 safari version"
            echo     ]
            echo   },
            echo   "proxy": "http://localhost:8001"
            echo }
        ) > "%PROJECT_ROOT%web\frontend\package.json"
    )
    
    :: Install frontend dependencies if directory exists and has package.json
    if exist "%PROJECT_ROOT%web\frontend\package.json" (
        cd "%PROJECT_ROOT%web\frontend"
        echo Installing frontend dependencies...
        call npm install
        if %errorlevel% neq 0 (
            echo Warning: Failed to install frontend dependencies.
            echo You can install them manually later.
        )
        cd "%PROJECT_ROOT%"
    )
) else (
    echo Node.js not detected, skipping frontend setup.
    echo To set up the frontend, please install Node.js 14+ and run this script again.
)

:: Update the port configuration in the frontend proxy setting
echo Updating port configuration...
python -c "
import json
import os

# Load port configuration
config_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'config', 'ports.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    backend_port = config.get('services', {}).get('svg_to_video_backend', 8001)
    
    # Update package.json proxy
    package_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'web', 'frontend', 'package.json')
    if os.path.exists(package_path):
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        package_data['proxy'] = f'http://localhost:{backend_port}'
        
        with open(package_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        print(f'Updated frontend proxy to use port {backend_port}')
except Exception as e:
    print(f'Warning: Failed to update port configuration: {e}')
"

echo.
echo ==============================================
echo   SVG to Video Pipeline Setup Complete
echo ==============================================
echo.
echo Please edit the .env file to add your API keys.
echo.
echo To start the development servers:
echo   run_svg_to_video_dev.bat
echo.
echo To start the production server:
echo   run_svg_to_video_prod.bat
echo.
echo To use the CLI:
echo   run_svg_cli.bat [command] [arguments]
echo.
echo To test the installation:
echo   test_svg_pipeline.bat
echo.
echo ==============================================

:: Deactivate virtual environment
call "%PROJECT_ROOT%venv\Scripts\deactivate.bat"
