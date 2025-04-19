@echo off
echo Installing Playwright and its dependencies...
npm install --save-dev @playwright/test
npx playwright install
echo Installation complete!
pause
