# WebSocket Testing Guide for GenAI Agent 3D

This guide explains how to run WebSocket tests for the GenAI Agent 3D project to verify the real-time communication functionality.

## Overview

WebSocket functionality is crucial for the GenAI Agent 3D project as it enables real-time communication between the frontend and backend. This includes:

1. **Status updates** during long-running operations
2. **Instruction processing** notifications
3. **Tool execution** results
4. **Error handling** for failed operations

## Testing Options

We provide several ways to test the WebSocket functionality, depending on your needs:

### 1. Quick Test with Convenience Script

The simplest way to run WebSocket tests is to use the provided convenience script:

**Windows:**
```cmd
run_websocket_test.bat
```

**Linux/macOS:**
```bash
./run_websocket_test.sh
```

This automatically starts a server in test mode, runs the tests, and shuts down the server.

### 2. Manual Testing with Custom Options

For more control, you can use the following commands:

```bash
cd web
python run_all_tests.py --manual-websocket --verbose
```

Additional options:
- `--port 8080` - Use a specific port (default: 8000)
- `--verbose` - Show detailed output
- `--test-mode` - Use mock services instead of real ones (recommended)

### 3. Automated Tests via Test Runner

If you want to run WebSocket tests as part of your existing test suite:

```bash
cd web/backend
python run_tests.py --websocket
```

### 4. Separate Server and Test Process

To run the server and test process separately (useful for debugging):

**Terminal 1:**
```bash
cd web/backend
python run_server.py --test-mode
```

**Terminal 2:**
```bash
cd web/backend/tests
python manual_websocket_test.py
```

## What the Tests Verify

The WebSocket tests check:

1. **Connection** - Can establish a WebSocket connection
2. **Ping/Pong** - Basic communication is working
3. **Instruction Processing** - Can send instructions and receive updates/results
4. **Tool Execution** - Can execute tools and receive updates/results
5. **Error Handling** - Properly handles unknown commands and errors

## Test Mode

Running in test mode (`--test-mode`) uses mock implementations instead of real services, which is faster and doesn't require external dependencies like Redis or Blender.

## Troubleshooting

If you encounter issues:

1. **Port already in use**
   - Change the port with `--port 8080` (or another free port)

2. **Connection refused**
   - Make sure the server is running and on the expected port
   - Check for firewall issues

3. **Timeouts**
   - The server might be busy or slow to respond
   - Try increasing the timeout with `--timeout 20`

4. **"ImportError" or missing dependencies**
   - Make sure you've installed all requirements:
     ```bash
     pip install -r web/backend/requirements.txt
     ```

## WebSocket API

The GenAI Agent 3D WebSocket API uses JSON messages with the following structure:

### Client-to-Server Messages:

```json
{
  "type": "ping"
}
```

```json
{
  "type": "instruction",
  "instruction": "Create a scene with a cube",
  "context": {}
}
```

```json
{
  "type": "tool",
  "tool_name": "scene_generator",
  "parameters": {
    "description": "A simple scene with a cube"
  }
}
```

### Server-to-Client Messages:

```json
{
  "type": "pong"
}
```

```json
{
  "type": "ack",
  "message": "Instruction received"
}
```

```json
{
  "type": "status",
  "status": "processing",
  "message": "Processing instruction"
}
```

```json
{
  "type": "result",
  "result": {
    "status": "success",
    "message": "Instruction processed successfully",
    "data": { ... }
  }
}
```

```json
{
  "type": "error",
  "message": "Error message here"
}
```

## WebSocket Implementation Details

The WebSocket functionality is implemented in the following files:

- **Backend**: `web/backend/main.py` - WebSocket endpoint and handler
- **Backend**: `web/backend/websocket_manager.py` - Connection and message management
- **Frontend**: `web/frontend/src/services/websocket.js` - Client-side WebSocket service

## Example WebSocket Client Usage

Here is a simple example of how to connect to the WebSocket endpoint from JavaScript:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket server');
  
  // Send a ping message
  ws.send(JSON.stringify({ type: 'ping' }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received message:', message);
  
  // Handle different message types
  switch (message.type) {
    case 'pong':
      console.log('Received pong response');
      break;
    case 'ack':
      console.log('Received acknowledgment:', message.message);
      break;
    case 'status':
      console.log('Status update:', message.status, message.message);
      break;
    case 'result':
      console.log('Result received:', message.result);
      break;
    case 'error':
      console.error('Error:', message.message);
      break;
    default:
      console.warn('Unknown message type:', message.type);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from WebSocket server');
};

// Example: Send an instruction
function sendInstruction(instruction, context = {}) {
  ws.send(JSON.stringify({
    type: 'instruction',
    instruction,
    context
  }));
}

// Example: Execute a tool
function executeTool(toolName, parameters = {}) {
  ws.send(JSON.stringify({
    type: 'tool',
    tool_name: toolName,
    parameters
  }));
}
```

## Integration with Frontend

The WebSocket functionality is integrated with the frontend React application to provide real-time updates to the user. This includes:

1. Showing progress indicators during long-running operations
2. Displaying status updates in real-time
3. Updating the UI when results are available
4. Showing error messages when something goes wrong

## Conclusion

The WebSocket functionality is a critical component of the GenAI Agent 3D project, enabling real-time communication between the frontend and backend. This guide has shown you how to test this functionality to ensure it works correctly.
