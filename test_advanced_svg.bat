@echo off
echo Testing Advanced SVG Generation with Claude Direct...
python test_svg_only.py --provider claude-direct --diagram-type flowchart --description "A detailed system architecture diagram showing microservices communication in a cloud environment, including API gateway, authentication service, user service, notification service, and database layer with proper connections and data flow" --output-dir output\svg
echo.
echo SVG file generated in output\svg\claude_direct_flowchart_test.svg
echo.
pause
