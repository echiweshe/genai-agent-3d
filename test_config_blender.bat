@echo off
setlocal enabledelayedexpansion

REM Test script that uses config.yaml to find Blender path

echo SVG to 3D Conversion Test (Config-based)
echo --------------------------------------

REM Check if SVG file path is provided
if "%~1"=="" (
  echo INFO: No SVG file specified, will run in test mode.
  set SVG_FILE=test.svg
  set OUTPUT_FILE=test_output.blend
) else (
  set SVG_FILE=%~1
  for %%F in ("%SVG_FILE%") do set BASE_NAME=%%~nF
  set OUTPUT_FILE=output\models\%BASE_NAME%_test.blend
)

REM Create output directory if it doesn't exist
set OUTPUT_DIR=output\models
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Create options JSON
set OPTIONS_JSON={"debug": true}

echo.
echo Looking for Blender path in config.yaml...
echo.

REM Path to config file
set CONFIG_PATH=%CD%\genai_agent_project\config.yaml

if not exist "%CONFIG_PATH%" (
  echo ERROR: Config file not found: %CONFIG_PATH%
  goto try_alternate_methods
)

REM Extract Blender path from config
echo Extracting Blender path from config...
for /F "tokens=* usebackq" %%L in (`findstr /C:"path:" "%CONFIG_PATH%"`) do (
  set CONFIG_LINE=%%L
  echo Found config line: %%L
)

REM Parse the path
for /F "tokens=2 delims=:" %%P in ("!CONFIG_LINE!") do (
  set BLENDER_PATH=%%P
  set BLENDER_PATH=!BLENDER_PATH: =!
)

REM Remove any quotes
set BLENDER_PATH=!BLENDER_PATH:"=!

REM Check if path is valid
if not defined BLENDER_PATH (
  echo ERROR: Could not extract Blender path from config.
  goto try_alternate_methods
)

echo Extracted Blender path: !BLENDER_PATH!

REM Convert forward slashes to backslashes
set BLENDER_PATH=!BLENDER_PATH:/=\!

echo Converted path: !BLENDER_PATH!

REM Check if the path exists
if exist "!BLENDER_PATH!" (
  set BLENDER_EXE=!BLENDER_PATH!
  goto blender_found
) else (
  echo ERROR: Blender path from config doesn't exist: !BLENDER_PATH!
)

:try_alternate_methods
echo Trying alternate methods to find Blender...
echo.

REM Check for Blender 4.2 (from config)
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
echo Checking: !BLENDER_PATH!
if exist "!BLENDER_PATH!" (
  set BLENDER_EXE=!BLENDER_PATH!
  goto blender_found
)

REM Check standard paths
set STANDARD_PATHS=^
"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender\blender.exe"

for %%P in (%STANDARD_PATHS%) do (
  echo Checking: %%P
  if exist %%P (
    set BLENDER_EXE=%%P
    goto blender_found
  )
)

REM Check for "blender.exe" in PATH
for %%I in (blender.exe) do set BLENDER_PATH=%%~$PATH:I
if not "!BLENDER_PATH!"=="" (
  set BLENDER_EXE=!BLENDER_PATH!
  goto blender_found
)

REM If we get here, Blender was not found
echo.
echo ERROR: Blender executable not found.
echo.
echo Please check that the path in config.yaml is correct:
echo Path in config: !BLENDER_PATH!
echo.
echo You can also run find_blender.bat to locate your Blender executable.
echo.

exit /b 1

:blender_found
echo.
echo Found Blender: !BLENDER_EXE!
echo.

REM Find our script
set SCRIPT_FILE=svg_to_3d_clarity_minimal.py
set SCRIPT_PATH=

for /F "tokens=*" %%G in ('dir /s /b "%CD%\%SCRIPT_FILE%" 2^>nul') do (
  set SCRIPT_PATH=%%G
)

if "!SCRIPT_PATH!"=="" (
  echo ERROR: Could not find script: %SCRIPT_FILE%
  echo Current directory: %CD%
  echo Listing scripts directory:
  dir /b "%CD%\genai_agent_project\scripts\" 2>nul
  exit /b 1
)

echo Found script: !SCRIPT_PATH!
echo.

REM Run Blender with the minimal test script
echo Running minimal test script...
"!BLENDER_EXE!" -b -P "!SCRIPT_PATH!" -- "!SVG_FILE!" "!OUTPUT_FILE!" "!OPTIONS_JSON!"

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Test script failed with error code %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

echo.
echo Test completed successfully!
echo Test output saved to: !OUTPUT_FILE!

REM Open the test output in Blender
echo.
echo Opening test output in Blender...
start "" "!BLENDER_EXE!" "!OUTPUT_FILE!"

exit /b 0
