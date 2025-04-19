#!/bin/bash
echo "Starting E2E tests..."

# Check if backend server is running on port 8000
echo "Checking if backend server is running..."
if ! lsof -i:8000 > /dev/null; then
    echo "Backend server is not running. Starting it..."
    (cd ../backend && python start_server.sh) &
    sleep 5
fi

# Check if frontend server is running on port 3000
echo "Checking if frontend server is running..."
if ! lsof -i:3000 > /dev/null; then
    echo "Frontend server is not running. Starting it..."
    (cd ../frontend && npm start) &
    sleep 10
fi

echo "Running E2E tests..."
npm test

echo "Tests completed!"
