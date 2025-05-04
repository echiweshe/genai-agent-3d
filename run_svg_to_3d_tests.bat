@echo off
REM Batch file to run SVG to 3D tests

echo SVG to 3D Converter Test Runner
echo ==============================
echo.

cd tests\svg_to_video\svg_to_3d

echo What would you like to do?
echo 1. Run quick test
echo 2. Run full test suite
echo 3. Run visual test (opens Blender UI)
echo 4. Run debug test
echo 5. Check imports only
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running quick test...
    python run_quick_test.py
) else if "%choice%"=="2" (
    echo.
    echo Running full test suite...
    python test_suite.py
) else if "%choice%"=="3" (
    echo.
    echo Running visual test...
    python run_tests.py --test visual --no-background
) else if "%choice%"=="4" (
    echo.
    echo Running debug test...
    python run_tests.py --test debug
) else if "%choice%"=="5" (
    echo.
    echo Checking imports...
    python check_imports.py
) else (
    echo Invalid choice!
)

cd ..\..\..

echo.
echo Test complete!
pause
