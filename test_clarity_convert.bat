@echo off
REM Test script for minimal SVG to 3D conversion

echo SVG to 3D Conversion Test
echo ------------------------

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
echo Running minimal test script...
echo.

REM Get Blender path with more extensive checks
echo Searching for Blender...

REM ============================================================
REM Add your Blender path here if it's in an unusual location
REM set BLENDER_EXE=C:\your\custom\path\to\blender.exe
REM goto blender_found
REM ============================================================

REM Check environment variable first
if defined BLENDER_PATH (
  echo Found BLENDER_PATH environment variable: %BLENDER_PATH%
  if exist "%BLENDER_PATH%" (
    set BLENDER_EXE=%BLENDER_PATH%
    goto blender_found
  ) else (
    echo - But this path doesn't exist: %BLENDER_PATH%
  )
)

REM Check standard paths
set STANDARD_PATHS=^
"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.3\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.2\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.1\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 3.0\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender 2.93\blender.exe" ^
"C:\Program Files\Blender Foundation\Blender\blender.exe"

for %%P in (%STANDARD_PATHS%) do (
  echo Checking: %%P
  if exist %%P (
    set BLENDER_EXE=%%P
    goto blender_found
  )
)

REM Check for common portable installation locations
set PORTABLE_PATHS=^
"%CD%\blender\blender.exe" ^
"%CD%\bin\blender\blender.exe" ^
"%CD%\..\blender\blender.exe" ^
"%CD%\..\..\blender\blender.exe" ^
"%USERPROFILE%\Desktop\blender\blender.exe" ^
"%USERPROFILE%\Downloads\blender\blender.exe" ^
"C:\blender\blender.exe" ^
"D:\blender\blender.exe"

for %%P in (%PORTABLE_PATHS%) do (
  echo Checking: %%P
  if exist %%P (
    set BLENDER_EXE=%%P
    goto blender_found
  )
)

REM Check for "blender.exe" in PATH
for %%I in (blender.exe) do set BLENDER_PATH=%%~$PATH:I
if not "%BLENDER_PATH%"=="" (
  set BLENDER_EXE=%BLENDER_PATH%
  goto blender_found
)

REM ============================================================
REM Add specific CUSTOM search locations for this user's environment
echo Checking special/custom paths for this environment...

REM AWS Specific locations
if exist "C:\aws\blender\blender.exe" (
  set BLENDER_EXE=C:\aws\blender\blender.exe
  goto blender_found
)

REM Path structure seen in your environment
if exist "C:\ZB_Share\Tools\Blender\blender.exe" (
  set BLENDER_EXE=C:\ZB_Share\Tools\Blender\blender.exe
  goto blender_found
)

if exist "C:\ZB_Share\Apps\Blender\blender.exe" (
  set BLENDER_EXE=C:\ZB_Share\Apps\Blender\blender.exe
  goto blender_found
)

REM If you have a non-standard installation, add more paths here
REM ============================================================

REM If we get here, Blender was not found
echo.
echo ERROR: Blender executable not found.
echo.
echo Please do one of the following:
echo 1. Install Blender from blender.org
echo 2. Set the BLENDER_PATH environment variable to point to your Blender executable
echo 3. Modify this script to include the correct path to your Blender installation
echo.
echo NOTE: Edit this script and add your Blender path at the "Add your Blender path here" 
echo       section at the top.
echo.

exit /b 1

:blender_found
echo.
echo Found Blender: %BLENDER_EXE%
echo.

REM Find our script
set SCRIPT_FILE=svg_to_3d_clarity_minimal.py
set SCRIPT_PATH=

for /F "tokens=*" %%G in ('dir /s /b "%CD%\%SCRIPT_FILE%" 2^>nul') do (
  set SCRIPT_PATH=%%G
)

if "%SCRIPT_PATH%"=="" (
  echo ERROR: Could not find script: %SCRIPT_FILE%
  echo Current directory: %CD%
  echo Listing scripts directory:
  dir /b "%CD%\genai_agent_project\scripts\" 2>nul
  exit /b 1
)

echo Found script: %SCRIPT_PATH%
echo.

REM Run Blender with the minimal test script
echo Running minimal test script...
"%BLENDER_EXE%" -b -P "%SCRIPT_PATH%" -- "%SVG_FILE%" "%OUTPUT_FILE%" "%OPTIONS_JSON%"

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Test script failed with error code %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

echo.
echo Test completed successfully!
echo Test output saved to: %OUTPUT_FILE%

REM Open the test output in Blender
echo.
echo Opening test output in Blender...
start "" "%BLENDER_EXE%" "%OUTPUT_FILE%"

exit /b 0
