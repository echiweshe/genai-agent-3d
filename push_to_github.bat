@echo off
echo SVG to Video Pipeline - Push to GitHub
echo ===================================
echo.

echo Step 1: Add all modified files to git...
git add .
echo.

echo Step 2: Commit changes with message...
git commit -F COMMIT_MESSAGE.txt
echo.

echo Step 3: Push changes to GitHub...
git push
echo.

echo Process complete!
echo Changes have been pushed to GitHub repository.
echo.
pause
