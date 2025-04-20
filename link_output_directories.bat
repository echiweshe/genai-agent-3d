@echo off
echo ========================================================
echo     GenAI Agent 3D - Link Output Directories
echo ========================================================
echo.
echo This script will create directory junctions to ensure both
echo the web frontend and backend/agent use the same output folders.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Step 1: Determining directories...
set SCRIPT_DIR=%~dp0
set FRONTEND_OUTPUT=%SCRIPT_DIR%genai_agent_project\web\backend\output
set AGENT_OUTPUT=%SCRIPT_DIR%genai_agent_project\output

echo Frontend output directory: %FRONTEND_OUTPUT%
echo Agent output directory: %AGENT_OUTPUT%

echo.
echo Step 2: Ensuring directories exist...
if not exist "%AGENT_OUTPUT%" (
    echo Creating agent output directory...
    mkdir "%AGENT_OUTPUT%"
)

if not exist "%FRONTEND_OUTPUT%" (
    echo Creating frontend output directory...
    mkdir "%FRONTEND_OUTPUT%"
)

echo.
echo Step 3: Creating directory junctions for subdirectories...

rem Models directory
echo Processing models directory...
if exist "%FRONTEND_OUTPUT%\models\" (
    echo - Backing up existing frontend models...
    if not exist "%FRONTEND_OUTPUT%\models_backup\" mkdir "%FRONTEND_OUTPUT%\models_backup\"
    xcopy /E /I /Y "%FRONTEND_OUTPUT%\models\*" "%FRONTEND_OUTPUT%\models_backup\"
    rmdir /S /Q "%FRONTEND_OUTPUT%\models\"
)
if not exist "%AGENT_OUTPUT%\models\" mkdir "%AGENT_OUTPUT%\models\"
mklink /J "%FRONTEND_OUTPUT%\models" "%AGENT_OUTPUT%\models"

rem Scenes directory
echo Processing scenes directory...
if exist "%FRONTEND_OUTPUT%\scenes\" (
    echo - Backing up existing frontend scenes...
    if not exist "%FRONTEND_OUTPUT%\scenes_backup\" mkdir "%FRONTEND_OUTPUT%\scenes_backup\"
    xcopy /E /I /Y "%FRONTEND_OUTPUT%\scenes\*" "%FRONTEND_OUTPUT%\scenes_backup\"
    rmdir /S /Q "%FRONTEND_OUTPUT%\scenes\"
)
if not exist "%AGENT_OUTPUT%\scenes\" mkdir "%AGENT_OUTPUT%\scenes\"
mklink /J "%FRONTEND_OUTPUT%\scenes" "%AGENT_OUTPUT%\scenes"

rem Diagrams directory
echo Processing diagrams directory...
if exist "%FRONTEND_OUTPUT%\diagrams\" (
    echo - Backing up existing frontend diagrams...
    if not exist "%FRONTEND_OUTPUT%\diagrams_backup\" mkdir "%FRONTEND_OUTPUT%\diagrams_backup\"
    xcopy /E /I /Y "%FRONTEND_OUTPUT%\diagrams\*" "%FRONTEND_OUTPUT%\diagrams_backup\"
    rmdir /S /Q "%FRONTEND_OUTPUT%\diagrams\"
)
if not exist "%AGENT_OUTPUT%\diagrams\" mkdir "%AGENT_OUTPUT%\diagrams\"
mklink /J "%FRONTEND_OUTPUT%\diagrams" "%AGENT_OUTPUT%\diagrams"

rem Tools directory
echo Processing tools directory...
if exist "%FRONTEND_OUTPUT%\tools\" (
    echo - Backing up existing frontend tools...
    if not exist "%FRONTEND_OUTPUT%\tools_backup\" mkdir "%FRONTEND_OUTPUT%\tools_backup\"
    xcopy /E /I /Y "%FRONTEND_OUTPUT%\tools\*" "%FRONTEND_OUTPUT%\tools_backup\"
    rmdir /S /Q "%FRONTEND_OUTPUT%\tools\"
)
if not exist "%AGENT_OUTPUT%\tools\" mkdir "%AGENT_OUTPUT%\tools\"
mklink /J "%FRONTEND_OUTPUT%\tools" "%AGENT_OUTPUT%\tools"

rem Temp directory
echo Processing temp directory...
if exist "%FRONTEND_OUTPUT%\temp\" (
    echo - Backing up existing frontend temp files...
    if not exist "%FRONTEND_OUTPUT%\temp_backup\" mkdir "%FRONTEND_OUTPUT%\temp_backup\"
    xcopy /E /I /Y "%FRONTEND_OUTPUT%\temp\*" "%FRONTEND_OUTPUT%\temp_backup\"
    rmdir /S /Q "%FRONTEND_OUTPUT%\temp\"
)
if not exist "%AGENT_OUTPUT%\temp\" mkdir "%AGENT_OUTPUT%\temp\"
mklink /J "%FRONTEND_OUTPUT%\temp" "%AGENT_OUTPUT%\temp"

echo.
echo Step 4: Moving existing model files...
echo Copying any files from web backend to agent output...
xcopy /E /I /Y "%FRONTEND_OUTPUT%\models_backup\*" "%AGENT_OUTPUT%\models\"
xcopy /E /I /Y "%FRONTEND_OUTPUT%\scenes_backup\*" "%AGENT_OUTPUT%\scenes\"
xcopy /E /I /Y "%FRONTEND_OUTPUT%\diagrams_backup\*" "%AGENT_OUTPUT%\diagrams\"
xcopy /E /I /Y "%FRONTEND_OUTPUT%\tools_backup\*" "%AGENT_OUTPUT%\tools\"
xcopy /E /I /Y "%FRONTEND_OUTPUT%\temp_backup\*" "%AGENT_OUTPUT%\temp\"

echo.
echo ========================================================
echo                  DIRECTORIES LINKED
echo ========================================================
echo Directory junctions have been created successfully.
echo.
echo Now both the web frontend and agent will access 
echo the same files in: %AGENT_OUTPUT%
echo.
echo Any existing files have been moved to the agent output directory.
echo Backups of the original web frontend files are in:
echo %FRONTEND_OUTPUT%\*_backup folders
echo.
echo Please restart your backend server for changes to take effect:
echo   python manage_services.py restart backend
echo ========================================================
echo.
pause
