@echo off
echo Fixing Playwright dependencies...

rem Clean npm cache
npm cache clean --force

rem Remove node_modules if it exists
if exist node_modules (
    echo Removing existing node_modules...
    rmdir /s /q node_modules
)

rem Remove package-lock.json if it exists
if exist package-lock.json (
    echo Removing package-lock.json...
    del package-lock.json
)

rem Install dependencies
echo Installing dependencies...
npm install

rem Install playwright
echo Installing Playwright...
npx playwright install

echo Dependencies fixed!
pause
