@echo off
echo Testing SVG Generator with Claude Direct...
python scripts\test_svg_generator.py --provider claude-direct --diagram-type flowchart --description "A flowchart showing the process of user registration and login in a web application, including email verification and password recovery" --output-dir output\svg
pause
