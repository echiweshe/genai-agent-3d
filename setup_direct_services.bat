@echo off
REM Setup Direct Services Architecture
REM This script applies all the necessary configurations for direct services

echo =============================================================
echo Setting up direct services architecture...
echo =============================================================

echo.
echo Step 1: Ensuring output directories are properly linked...
python ensure_output_directories.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to set up output directories
    exit /b 1
)

echo.
echo Step 2: Applying direct services integration...
python apply_direct_services.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to apply direct services integration
    exit /b 1
)

echo.
echo =============================================================
echo Direct services setup completed successfully!
echo =============================================================
echo.
echo You can now run the agent with direct services using:
echo   genai_agent_project\run_direct.bat
echo.
echo This implementation:
echo  - Initializes critical services directly without Redis discovery
echo  - Maintains extensibility of the microservices architecture
echo  - Provides reliable access to LLM and Blender functionality
echo  - Standardizes output directories to avoid path confusion
echo.

pause
