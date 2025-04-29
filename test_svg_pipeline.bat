@echo off
:: SVG to Video Pipeline Test Script
:: This script tests the SVG to Video pipeline components

:: Set the project root directory
set PROJECT_ROOT=%~dp0

:: Check if virtual environment exists
if not exist "%PROJECT_ROOT%venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating new virtual environment...
    python -m venv "%PROJECT_ROOT%venv"
    
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Please install Python 3.9+ and try again.
        exit /b 1
    )
    
    :: Install dependencies
    call "%PROJECT_ROOT%venv\Scripts\activate.bat"
    pip install -r "%PROJECT_ROOT%web\backend\requirements.txt"
    
    if %errorlevel% neq 0 (
        echo Failed to install dependencies. Please check your pip installation.
        exit /b 1
    )
) else (
    :: Activate the virtual environment
    call "%PROJECT_ROOT%venv\Scripts\activate.bat"
)

echo ==============================================
echo          SVG to Video Pipeline Test
echo ==============================================

:: Test outputs directory
if not exist "%PROJECT_ROOT%outputs" (
    mkdir "%PROJECT_ROOT%outputs"
    echo Created outputs directory.
)

:: Test SVG Generator
echo.
echo Testing SVG Generator...
python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('__file__')))
try:
    from genai_agent.svg_to_video.llm_integrations.llm_factory import LLMFactory
    factory = LLMFactory()
    providers = factory.get_providers()
    print('Available LLM Providers:')
    for provider in providers:
        status = 'Available' if provider.get('available', False) else 'Not Available'
        print(f'{provider[\"name\"]}: {status}')
    print('SVG Generator test passed.')
except Exception as e:
    print(f'SVG Generator test failed: {e}')
    sys.exit(1)
"

if %errorlevel% neq 0 (
    echo SVG Generator test failed.
    exit /b 1
)

:: Test Blender installation
echo.
echo Testing Blender installation...
set BLENDER_PATH=%BLENDER_PATH%

if "%BLENDER_PATH%"=="" (
    where blender >nul 2>&1
    if %errorlevel% neq 0 (
        echo Blender not found in PATH. Please install Blender or set BLENDER_PATH in the .env file.
        echo You can continue but the SVG to 3D conversion will not work.
    ) else (
        echo Blender found in PATH.
    )
) else (
    if not exist "%BLENDER_PATH%" (
        echo Blender not found at specified path: %BLENDER_PATH%
        echo Please check the BLENDER_PATH in the .env file.
        echo You can continue but the SVG to 3D conversion will not work.
    ) else (
        echo Blender found at: %BLENDER_PATH%
    )
)

:: Test Pipeline module
echo.
echo Testing Pipeline module...
python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('__file__')))
try:
    from genai_agent.svg_to_video.pipeline import SVGToVideoPipeline
    pipeline = SVGToVideoPipeline()
    print('Pipeline module loaded successfully.')
    print('Pipeline test passed.')
except Exception as e:
    print(f'Pipeline test failed: {e}')
    sys.exit(1)
"

if %errorlevel% neq 0 (
    echo Pipeline test failed.
    exit /b 1
)

echo.
echo All tests completed.
echo ==============================================
echo          SVG to Video Pipeline Test Passed
echo ==============================================

:: Deactivate the virtual environment
deactivate
