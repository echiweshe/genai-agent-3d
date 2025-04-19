#!/bin/bash
echo "Fixing Playwright dependencies..."

# Clean npm cache
npm cache clean --force

# Remove node_modules if it exists
if [ -d "node_modules" ]; then
    echo "Removing existing node_modules..."
    rm -rf node_modules
fi

# Remove package-lock.json if it exists
if [ -f "package-lock.json" ]; then
    echo "Removing package-lock.json..."
    rm package-lock.json
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Install playwright
echo "Installing Playwright..."
npx playwright install

echo "Dependencies fixed!"
