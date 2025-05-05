@echo off
echo Testing SVG generation with Claude Direct...
cd %~dp0
python test_svg_generation.py
if %ERRORLEVEL% EQU 0 (
    echo Test passed!
) else (
    echo Test failed!
)
pause
