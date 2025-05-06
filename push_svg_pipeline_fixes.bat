@echo off
echo ================================================================================
echo                   Pushing SVG Pipeline Fixes to GitHub                        
echo ================================================================================
echo.

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

echo Stage 1: Making sure we're on the right branch...
git branch
echo.

echo Stage 2: Adding all modified files to git...
git add genai_agent_project\genai_agent\svg_to_video\svg_to_3d\__init__.py
git add genai_agent_project\web\frontend\src\components\svg\BlenderIntegration.js
git add restart_backend.bat
git add restart_frontend.bat
git add check_svg_pipeline_status.bat
git add check_svg_pipeline_status.py
git add test_svg_pipeline.bat
git add genai_agent_project\genai_agent\svg_to_video\test_pipeline.py
git add SVG_PIPELINE_FIXES.md
git add install_frontend_deps.bat
git add COMMIT_MESSAGE.txt
git add push_svg_pipeline_fixes.bat
echo.

echo Stage 3: Committing changes with detailed message...
git commit -F COMMIT_MESSAGE.txt
echo.

echo Stage 4: Pushing changes to GitHub...
git push
echo.

echo ================================================================================
echo Process complete! SVG Pipeline fixes have been pushed to GitHub.
echo.
echo If you encountered any issues, please check:
echo - Git credentials may need to be entered if not cached
echo - You might need to pull first if there are upstream changes
echo ================================================================================
echo.
pause
