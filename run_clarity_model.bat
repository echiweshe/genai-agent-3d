@echo off
REM Very simple batch script that uses a pre-created Python script

echo Simple Clarity Model Generator
echo ----------------------------

if "%~1"=="" (
  echo ERROR: No SVG file specified.
  echo Usage: run_clarity_model.bat [path\to\svg_file.svg]
  exit /b 1
)

REM Get file paths
set SVG_FILE=%~1
for %%F in ("%SVG_FILE%") do set BASE_NAME=%%~nF
set OUTPUT_DIR=output\models
set OUTPUT_FILE=%OUTPUT_DIR%\%BASE_NAME%_clarity.blend

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Use known working Blender path
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

REM Verify Blender path
if not exist "%BLENDER_EXE%" (
  echo ERROR: Blender executable not found at: %BLENDER_EXE%
  exit /b 1
)

REM Check script exists
set SCRIPT_FILE=%CD%\genai_agent_project\scripts\simple_clarity_model.py
if not exist "%SCRIPT_FILE%" (
  echo ERROR: Script not found: %SCRIPT_FILE%
  exit /b 1
)

echo Using Blender: %BLENDER_EXE%
echo Using script: %SCRIPT_FILE%
echo Converting: %SVG_FILE% 
echo Output to: %OUTPUT_FILE%
echo.

echo Running Blender...
"%BLENDER_EXE%" -b -P "%SCRIPT_FILE%" -- "%SVG_FILE%" "%OUTPUT_FILE%"

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Conversion failed with error code %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

echo.
echo Conversion completed successfully!
echo 3D model saved to: %OUTPUT_FILE%

echo.
echo Opening result in Blender...
start "" "%BLENDER_EXE%" "%OUTPUT_FILE%"

exit /b 0
