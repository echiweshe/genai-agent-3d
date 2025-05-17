@echo off
REM Enhanced SVG to 3D Conversion Script
REM Converts SVG to professional-grade 3D model with improved materials, geometry, and scene setup

echo Enhanced SVG to 3D Converter
echo ----------------------------

REM Check if SVG file path is provided
if "%~1"=="" (
  echo ERROR: No SVG file specified.
  echo Usage: enhanced_convert_svg_to_3d.bat [path\to\svg_file.svg] [options]
  echo Options:
  echo   /extrude:N     - Set extrusion depth (default: 0.1)
  echo   /style:NAME    - Set style preset (technical, organic, glossy, metal)
  echo   /open          - Open the result in Blender after conversion
  echo   /debug         - Enable debug output
  exit /b 1
)

REM Default settings
set SVG_FILE=%~1
set EXTRUDE_DEPTH=0.1
set STYLE_PRESET=technical
set OPEN_RESULT=false
set DEBUG=false

REM Parse additional arguments
:parse_args
if "%~2"=="" goto :end_parse_args

if /i "%~2"=="/extrude" (
  set EXTRUDE_DEPTH=%~3
  shift
  shift
  goto :parse_args
)

if /i "%~2:~0,9%"=="/extrude:" (
  set EXTRUDE_DEPTH=%~2:~9%
  shift
  goto :parse_args
)

if /i "%~2"=="/style" (
  set STYLE_PRESET=%~3
  shift
  shift
  goto :parse_args
)

if /i "%~2:~0,7%"=="/style:" (
  set STYLE_PRESET=%~2:~7%
  shift
  goto :parse_args
)

if /i "%~2"=="/open" (
  set OPEN_RESULT=true
  shift
  goto :parse_args
)

if /i "%~2"=="/debug" (
  set DEBUG=true
  shift
  goto :parse_args
)

REM Unknown argument - ignore and continue
shift
goto :parse_args

:end_parse_args

REM Get base file name without extension
for %%F in ("%SVG_FILE%") do set BASE_NAME=%%~nF

REM Check if SVG file exists
if not exist "%SVG_FILE%" (
  echo ERROR: SVG file not found: %SVG_FILE%
  exit /b 1
)

REM Set output file path
set OUTPUT_DIR=output\models
set OUTPUT_FILE=%OUTPUT_DIR%\%BASE_NAME%_enhanced.blend

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Create options JSON
set OPTIONS_JSON={"extrude_depth": %EXTRUDE_DEPTH%, "use_enhanced": true, "style_preset": "%STYLE_PRESET%", "debug": %DEBUG%}

echo.
echo Converting SVG: %SVG_FILE%
echo Output: %OUTPUT_FILE%
echo Extrusion Depth: %EXTRUDE_DEPTH%
echo Style Preset: %STYLE_PRESET%
echo.

REM Get Blender path
if defined BLENDER_PATH (
  set BLENDER_EXE=%BLENDER_PATH%
) else (
  REM Try to find Blender in common locations
  if exist "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe" (
    set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.6\blender.exe
  ) else if exist "C:\Program Files\Blender Foundation\Blender 3.5\blender.exe" (
    set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.5\blender.exe
  ) else if exist "C:\Program Files\Blender Foundation\Blender 3.4\blender.exe" (
    set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.4\blender.exe
  ) else if exist "C:\Program Files\Blender Foundation\Blender 3.3\blender.exe" (
    set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 3.3\blender.exe
  ) else (
    echo ERROR: Blender executable not found. Please set the BLENDER_PATH environment variable.
    exit /b 1
  )
)

echo Using Blender: %BLENDER_EXE%
echo.

REM Get script path
set SCRIPT_PATH=genai_agent_project\scripts\svg_to_3d_blender_enhanced.py

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
echo Enhanced 3D model saved to: %OUTPUT_FILE%

REM Open result in Blender if requested
if /i "%OPEN_RESULT%"=="true" (
  echo.
  echo Opening result in Blender...
  start "" "%BLENDER_EXE%" "%OUTPUT_FILE%"
)

exit /b 0
