@echo off
echo SVG Pipeline Consolidation
echo ========================
echo.
echo Step 1: Verifying SVG Pipeline...
python svg_pipeline_verification.py
echo.
echo Step 2: Consolidating SVG Pipeline...
python consolidate_svg_pipeline.py
echo.
echo Consolidation complete! Please check the logs for details.
echo If any issues were encountered, you can restore from the backups.
echo.
pause
