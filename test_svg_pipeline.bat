@echo off
echo Testing SVG to Video Pipeline...
python scripts\test\test_svg_to_video_full.py --provider claude-direct --diagram-type network --description "A network diagram showing a secure cloud infrastructure with load balancers, web servers, application servers, database servers, and appropriate security measures" --svg-only
pause
