@echo off
echo Verifying no mock implementations in the SVG to Video pipeline...
cd %~dp0
python verify_no_mocks.py
if %ERRORLEVEL% EQU 0 (
    echo All checks passed! No mock implementations found.
) else (
    echo Warning: Potential mock implementations found.
)
pause
