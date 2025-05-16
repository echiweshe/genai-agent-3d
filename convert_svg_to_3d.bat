@echo off
REM SVG to 3D Conversion Script
REM This batch file runs the SVG to 3D conversion script

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Set up Python environment
cd %SCRIPT_DIR%
call ..\..\..\venv\Scripts\activate.bat

REM Run the conversion script
python genai_agent_project\genai_agent\svg_to_video\svg_to_3d\convert_svg_to_3d.py %*

REM Deactivate Python environment
call deactivate
