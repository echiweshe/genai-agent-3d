@echo off
REM Simple Clarity-Preserving SVG to 3D Conversion Script
REM For direct testing

echo Simple Clarity-Preserving SVG to 3D Converter
echo -------------------------------------------

REM Check if SVG file path is provided
if "%~1"=="" (
  echo ERROR: No SVG file specified.
  echo Usage: simple_clarity_convert.bat [path\to\svg_file.svg]
  exit /b 1
)

REM Settings
set SVG_FILE=%~1
set EXTRUDE_DEPTH=0.05
set STYLE_PRESET=technical
set DEBUG=true

REM Get base file name without extension
for %%F in ("%SVG_FILE%") do set BASE_NAME=%%~nF

REM Check if SVG file exists
if not exist "%SVG_FILE%" (
  echo ERROR: SVG file not found: %SVG_FILE%
  exit /b 1
)

REM Set output file path
set OUTPUT_DIR=output\models
set OUTPUT_FILE=%OUTPUT_DIR%\%BASE_NAME%_clarity.blend

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Create options JSON
set OPTIONS_JSON={"extrude_depth": %EXTRUDE_DEPTH%, "use_enhanced": true, "style_preset": "%STYLE_PRESET%", "preserve_clarity": true, "debug": %DEBUG%}

echo.
echo Converting SVG: %SVG_FILE%
echo Output: %OUTPUT_FILE%
echo Extrusion Depth: %EXTRUDE_DEPTH% (reduced for clarity)
echo.

REM Get Blender path
if exist "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe" (
  set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.6\blender.exe
) else if exist "C:\Program Files\Blender Foundation\Blender 3.5\blender.exe" (
  set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.5\blender.exe
) else if exist "C:\Program Files\Blender Foundation\Blender 3.4\blender.exe" (
  set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.4\blender.exe
) else if exist "C:\Program Files\Blender Foundation\Blender 3.3\blender.exe" (
  set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.3\blender.exe
) else (
  echo ERROR: Blender executable not found.
  exit /b 1
)

echo Using Blender: %BLENDER_EXE%
echo.

REM Find our script
set SCRIPT_FILE=svg_to_3d_clarity.py
set SCRIPT_PATH=

for /F "tokens=*" %%G in ('dir /s /b "%CD%\%SCRIPT_FILE%" 2^>nul') do (
  set SCRIPT_PATH=%%G
)

if "%SCRIPT_PATH%"=="" (
  echo ERROR: Could not find script: %SCRIPT_FILE%
  echo Make sure the script is in genai_agent_project\scripts\ directory
  exit /b 1
)

echo Found script: %SCRIPT_PATH%
echo.

REM Run Blender with the conversion script
echo Running conversion...
"%BLENDER_EXE%" -b -P "%SCRIPT_PATH%" -- "%SVG_FILE%" "%OUTPUT_FILE%" "%OPTIONS_JSON%"

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Conversion failed with error code %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

echo.
echo Conversion completed successfully!
echo 3D model saved to: %OUTPUT_FILE%

REM Open result in Blender
echo.
echo Opening result in Blender...
start "" "%BLENDER_EXE%" "%OUTPUT_FILE%"

exit /b 0
