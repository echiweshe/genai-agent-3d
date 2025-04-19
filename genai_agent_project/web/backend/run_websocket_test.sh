#!/bin/bash
# Bash script to run the WebSocket test

# Function to cleanup on exit
cleanup() {
  echo "Stopping server..."
  kill $SERVER_PID
  wait $SERVER_PID 2>/dev/null
  echo "Server stopped"
  exit $TEST_EXIT_CODE
}

# Start the server process in test mode in the background
echo "Starting server in test mode..."
python run_server.py --test-mode &
SERVER_PID=$!

# Set trap to ensure server is stopped on exit
trap cleanup EXIT INT TERM

# Wait a bit for the server to start
echo "Waiting for server to start..."
sleep 3

# Run the WebSocket test
echo "Running WebSocket test..."
python tests/manual_websocket_test.py
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "WebSocket test completed successfully!"
else
  echo "WebSocket test failed with exit code $TEST_EXIT_CODE"
fi

# Cleanup will be called automatically via the trap
