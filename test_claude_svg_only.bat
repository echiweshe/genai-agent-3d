@echo off
echo Testing SVG Generation with Claude Direct (Standalone)...
python test_svg_only.py --provider claude-direct --diagram-type flowchart --description "A flowchart showing the process of user registration and login in a web application, including email verification and password recovery" --output-dir output\svg
pause
