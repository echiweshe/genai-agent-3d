@echo off
echo SVG to Video Pipeline - Update and Run
echo ===============================
echo.

echo This script will update, restart, and test the SVG to Video pipeline.
echo.
echo Steps:
echo 1. Run the complete integration
echo 2. Restart the backend service
echo 3. Run diagnostics to verify everything is working
echo 4. Test the full pipeline
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Step 1: Running complete integration...
call integrate_all.bat
echo.

echo Step 2: Running diagnostics...
call diagnose_svg_pipeline.bat
echo.

echo Step 3: Testing the full pipeline...
call test_full_pipeline.bat
echo.

echo All done!
echo If everything is working, you can now push changes to GitHub.
echo.
pause
