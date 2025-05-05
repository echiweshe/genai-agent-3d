@echo off
echo Verifying output directory paths...
cd %~dp0
python verify_output_paths.py
pause
