@echo off
echo Running Enhanced Blender Test with GenAI Agent integration...
echo.

REM Set variables for paths
set PROJECT_DIR=%~dp0
set EXAMPLES_DIR=%PROJECT_DIR%examples
set SCRIPT_PATH=%EXAMPLES_DIR%\enhanced_blender_test.py

REM Check if examples directory exists
if not exist "%EXAMPLES_DIR%" (
    echo ERROR: Examples directory not found at: %EXAMPLES_DIR%
    exit /b 1
)

REM Check if the test script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Enhanced Blender test script not found at: %SCRIPT_PATH%
    exit /b 1
)

echo Using script: %SCRIPT_PATH%

REM Check for Blender executable
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
if not exist %BLENDER_PATH% (
    REM Try Blender 4.0 instead
    set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
    
    if not exist %BLENDER_PATH% (
        REM Try blender in PATH
        echo WARNING: Blender not found at expected locations, trying "blender" command
        set BLENDER_PATH=blender
    )
)

echo Using Blender from: %BLENDER_PATH%

REM Ensure Ollama is running
echo Checking if Ollama is running...
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Ollama does not appear to be running. Starting it...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)

REM Check if Redis is running
echo Checking if Redis is running...
redis-cli ping >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Redis does not appear to be running. Starting it...
    start /B redis-server
    timeout /t 2 /nobreak >nul
)

REM Create output directory if it doesn't exist
set OUTPUT_DIR=%EXAMPLES_DIR%\output
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo Created output directory: %OUTPUT_DIR%
)

echo.
echo Starting enhanced Blender test...
echo.

REM Run the test script
%BLENDER_PATH% --python "%SCRIPT_PATH%"

echo.
echo Test completed. Check the examples/output directory for results.
echo.
echo Press any key to exit...
pause >nul
