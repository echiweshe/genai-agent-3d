@echo off
setlocal enabledelayedexpansion

REM Professional Quality SVG to 3D Conversion Script
REM This script runs the clarity-preserving SVG to 3D conversion with professional quality settings

echo Professional Quality SVG to 3D Conversion
echo ---------------------------------------

REM Check for SVG file argument
if "%~1"=="" (
    echo Error: SVG file not specified
    echo Usage: professional_quality_convert.bat path\to\svg_file.svg [/open]
    exit /b 1
)

REM Get SVG file path
set SVG_FILE=%~1
if not exist "%SVG_FILE%" (
    echo Error: SVG file not found at %SVG_FILE%
    exit /b 1
)

REM Check for optional /open flag
set OPEN_IN_BLENDER=0
if "%~2"=="/open" set OPEN_IN_BLENDER=1
if "%~3"=="/open" set OPEN_IN_BLENDER=1

REM Get script directory
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%

REM Set paths
set CONFIG_FILE=%ROOT_DIR%genai_agent_project\config.yaml
set SCRIPTS_DIR=%ROOT_DIR%genai_agent_project\scripts
set SVG_TO_3D_SCRIPT=%SCRIPTS_DIR%\svg_to_3d_clarity.py
set OUTPUT_DIR=%ROOT_DIR%output\models

REM Generate output filename
for %%F in ("%SVG_FILE%") do set BASE_NAME=%%~nF
set OUTPUT_FILE=%OUTPUT_DIR%\%BASE_NAME%_professional.blend

REM Check if config file exists
if not exist "%CONFIG_FILE%" (
    echo Warning: Config file not found at %CONFIG_FILE%
    echo Trying to locate Blender directly...
)

REM Try to get Blender path from config
set BLENDER_PATH=
if exist "%CONFIG_FILE%" (
    for /f "tokens=1,2 delims=:" %%a in ('findstr /C:"blender_path" "%CONFIG_FILE%"') do (
        set BLENDER_PATH=%%b
        set BLENDER_PATH=!BLENDER_PATH:~1!
    )
)

REM If not found in config, try environment variable
if "%BLENDER_PATH%"=="" (
    if defined BLENDER_PATH (
        echo Using Blender from environment variable: %BLENDER_PATH%
    ) else (
        echo Blender path not found in config or environment variables
        echo Searching for Blender in common locations...
        
        REM Try to find Blender in common locations
        if exist "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" (
            set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe
        ) else if exist "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe" (
            set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.1\blender.exe
        ) else if exist "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" (
            set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe
        ) else if exist "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe" (
            set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 3.6\blender.exe
        ) else if exist "C:\Program Files\Blender Foundation\Blender 3.5\blender.exe" (
            set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 3.5\blender.exe
        ) else if exist "C:\Program Files\Blender Foundation\Blender\blender.exe" (
            set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender\blender.exe
        )
    )
)

REM Check if Blender path was found
if "%BLENDER_PATH%"=="" (
    echo Error: Could not find Blender executable.
    echo Please set BLENDER_PATH environment variable or update the config.yaml file.
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Check if the script exists
if not exist "%SVG_TO_3D_SCRIPT%" (
    echo Error: SVG to 3D script not found at %SVG_TO_3D_SCRIPT%
    exit /b 1
)

REM Prepare conversion options - updated extrusion depth to 0.0005
set OPTIONS={"extrude_depth": 0.0005, "style_preset": "professional", "preserve_clarity": true, "custom_elements": true, "debug": true}

REM Run the conversion
echo Converting SVG to 3D with professional quality settings...
echo SVG File: %SVG_FILE%
echo Output File: %OUTPUT_FILE%
echo Blender: %BLENDER_PATH%
echo Script: %SVG_TO_3D_SCRIPT%
echo Extrusion Depth: 0.0005 (Ultra-minimal for maximum clarity)

REM Execute Blender with the script
if %OPEN_IN_BLENDER%==1 (
    REM Run with UI
    echo Opening in Blender after conversion...
    "%BLENDER_PATH%" --python "%SVG_TO_3D_SCRIPT%" -- "%SVG_FILE%" "%OUTPUT_FILE%" "%OPTIONS%"
) else (
    REM Run in background
    "%BLENDER_PATH%" --background --python "%SVG_TO_3D_SCRIPT%" -- "%SVG_FILE%" "%OUTPUT_FILE%" "%OPTIONS%"
)

REM Check if conversion was successful
if %ERRORLEVEL% NEQ 0 (
    echo Error: SVG to 3D conversion failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo Conversion complete!
echo Output saved to: %OUTPUT_FILE%

REM Open in Blender if requested
if %OPEN_IN_BLENDER%==1 (
    echo Opening in Blender...
    start "" "%BLENDER_PATH%" "%OUTPUT_FILE%"
)

exit /b 0
