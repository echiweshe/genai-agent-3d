@echo off
REM Script to create directory junctions for GenAI Agent 3D
REM This enables shared access to output directories from different parts of the application

echo GenAI Agent 3D - Directory Junction Setup

REM Define the base paths
set BASE_DIR=C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d
set OUTPUT_DIR=%BASE_DIR%\output
set GENAI_PROJECT_DIR=%BASE_DIR%\genai_agent_project
set WEB_BACKEND_DIR=%GENAI_PROJECT_DIR%\web\backend
set WEB_FRONTEND_DIR=%GENAI_PROJECT_DIR%\web\frontend

echo Creating main output directory if it doesn't exist...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo Creating output subdirectories...
if not exist "%OUTPUT_DIR%\models" mkdir "%OUTPUT_DIR%\models"
if not exist "%OUTPUT_DIR%\scenes" mkdir "%OUTPUT_DIR%\scenes"
if not exist "%OUTPUT_DIR%\svg" mkdir "%OUTPUT_DIR%\svg"
if not exist "%OUTPUT_DIR%\diagrams" mkdir "%OUTPUT_DIR%\diagrams"
if not exist "%OUTPUT_DIR%\svg_to_video" mkdir "%OUTPUT_DIR%\svg_to_video"
if not exist "%OUTPUT_DIR%\svg_to_video\svg" mkdir "%OUTPUT_DIR%\svg_to_video\svg"
if not exist "%OUTPUT_DIR%\svg_to_video\models" mkdir "%OUTPUT_DIR%\svg_to_video\models"
if not exist "%OUTPUT_DIR%\blendergpt" mkdir "%OUTPUT_DIR%\blendergpt"
if not exist "%OUTPUT_DIR%\hunyuan" mkdir "%OUTPUT_DIR%\hunyuan"
if not exist "%OUTPUT_DIR%\trellis" mkdir "%OUTPUT_DIR%\trellis"

echo Setting up directory junctions for genai_agent_project\output...
REM Remove existing junction if it exists
if exist "%GENAI_PROJECT_DIR%\output" rmdir "%GENAI_PROJECT_DIR%\output"
REM Create junction
mklink /J "%GENAI_PROJECT_DIR%\output" "%OUTPUT_DIR%"
echo Junction created: %GENAI_PROJECT_DIR%\output -^> %OUTPUT_DIR%

echo Setting up directory junctions for web backend output...
REM Remove existing junction if it exists
if exist "%WEB_BACKEND_DIR%\output" rmdir "%WEB_BACKEND_DIR%\output"
REM Create junction
mklink /J "%WEB_BACKEND_DIR%\output" "%OUTPUT_DIR%"
echo Junction created: %WEB_BACKEND_DIR%\output -^> %OUTPUT_DIR%

echo Setting up directory junctions for web frontend output (if needed)...
REM Remove existing junction if it exists
if exist "%WEB_FRONTEND_DIR%\public\output" rmdir "%WEB_FRONTEND_DIR%\public\output"
REM Create directory if it doesn't exist
if not exist "%WEB_FRONTEND_DIR%\public" mkdir "%WEB_FRONTEND_DIR%\public"
REM Create junction
mklink /J "%WEB_FRONTEND_DIR%\public\output" "%OUTPUT_DIR%"
echo Junction created: %WEB_FRONTEND_DIR%\public\output -^> %OUTPUT_DIR%

echo.
echo Setup complete. All components now point to the same output directory.
echo.

pause
