@echo off
echo Running Blender test script...
echo.

REM Set variables for paths
set PROJECT_DIR=%~dp0
set EXAMPLES_DIR=%PROJECT_DIR%examples

REM Check if examples directory exists
if not exist "%EXAMPLES_DIR%" (
    echo ERROR: Examples directory not found at: %EXAMPLES_DIR%
    exit /b 1
)

REM Check if the test script exists
if not exist "%EXAMPLES_DIR%\simple_blender_test.py" (
    echo ERROR: Test script not found at: %EXAMPLES_DIR%\simple_blender_test.py
    exit /b 1
)

echo Using examples directory: %EXAMPLES_DIR%

REM Check for Blender 4.2 first (newer version)
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
if not exist %BLENDER_PATH% (
    REM Try Blender 4.0 instead
    set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
    
    if not exist %BLENDER_PATH% (
        REM Try just "blender" and hope it's in the PATH
        echo WARNING: Blender not found at expected locations, trying "blender" command
        set BLENDER_PATH=blender
    )
)

echo Using Blender from: %BLENDER_PATH%
echo.

REM Run the test script
%BLENDER_PATH% --background --python "%EXAMPLES_DIR%\simple_blender_test.py"

echo.
echo Test completed. Press any key to exit...
pause > nul
