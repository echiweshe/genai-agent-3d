# WebSocket Testing Guide for GenAI Agent 3D

This guide explains how to run WebSocket tests for the GenAI Agent 3D project.

## Prerequisites

- Python 3.10+ (Python 3.11 recommended)
- Required Python packages (installed via `pip install -r requirements.txt`)

## Testing Methods

There are two primary ways to test the WebSocket functionality:

### 1. Automated Tests

The automated tests use pytest and TestClient to verify WebSocket communication. Run these with:

```bash
cd genai_agent_project/web/backend
python run_tests.py --websocket
```

### 2. Manual WebSocket Testing

For direct WebSocket testing and observing the full communication flow, use the manual WebSocket test script:

```bash
# First, start the server in test mode (minimal dependencies)
cd genai_agent_project/web/backend
python run_server.py --test-mode

# In a separate terminal:
cd genai_agent_project/web/backend/tests
python manual_websocket_test.py
```

## Test Mode

The `--test-mode` flag does the following:

1. Sets environment variable `GENAI_TEST_MODE=true`
2. Uses mock objects instead of real connections (Redis, Agent, etc.)
3. Enables verbose logging
4. Allows testing without setting up the full infrastructure

This is useful for:
- CI/CD pipelines
- Testing on systems without dependencies
- Focusing on specific functionality

## What The Tests Verify

The WebSocket tests check:

1. Connection establishment
2. Ping/Pong communication
3. Instruction processing via WebSocket
4. Tool execution via WebSocket
5. Error handling for various scenarios

## Troubleshooting

If you encounter issues with the tests:

1. Ensure you're using the right Python version and virtual environment
2. Check that Redis is running (for non-test mode)
3. Verify the server is running on the expected port (default: 8000)
4. Look for detailed error messages in the logs

## Expected Output

When running the manual test, you should see a sequence of log messages showing:

1. Connection established
2. Ping sent, Pong received
3. Instruction sent, acknowledgement received
4. Status updates received
5. Results received
6. Tool execution sent, acknowledgement received
7. Tool execution results received

All with proper JSON formatting and timestamps.
