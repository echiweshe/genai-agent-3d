@echo off
echo SVG Pipeline Consolidation - Complete Process
echo ============================================
echo.

echo Step 1: Verifying the SVG Pipeline...
python svg_pipeline_verification.py
echo.

echo Step 2: Consolidating the SVG Pipeline...
python consolidate_svg_pipeline.py
echo.

echo Step 3: Fixing SVG Paths in Code...
powershell -ExecutionPolicy Bypass -File fix_svg_paths.ps1
echo.

echo Step 4: Testing the Consolidated SVG Pipeline...
python test_svg_pipeline.py
echo.

echo SVG Pipeline Consolidation Complete!
echo Please check the logs for any issues or warnings.
echo.
pause
