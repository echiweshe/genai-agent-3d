@echo off
echo SVG to Video Pipeline - Complete Integration
echo =====================================
echo.

echo This script will run all integration steps in sequence.
echo.
echo Steps:
echo 1. Fix SVG directory structure
echo 2. Integrate SVG to 3D conversion
echo 3. Integrate animation module
echo 4. Integrate rendering module
echo 5. Test full pipeline
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Step 1: Fixing SVG directory structure...
powershell -ExecutionPolicy Bypass -File fix_svg_directory_structure.ps1
echo.

echo Step 2: Integrating SVG to 3D conversion...
powershell -ExecutionPolicy Bypass -File integrate_svg_to_3d.ps1
echo.

echo Step 3: Integrating animation module...
powershell -ExecutionPolicy Bypass -File integrate_animation.ps1
echo.

echo Step 4: Integrating rendering module...
powershell -ExecutionPolicy Bypass -File integrate_rendering.ps1
echo.

echo Step 5: Restarting backend service...
call restart_backend.bat
echo.

echo Integration complete!
echo.
echo To test the full pipeline, run:
echo test_full_pipeline.bat
echo.
pause
