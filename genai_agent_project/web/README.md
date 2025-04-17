# GenAI Agent 3D Web UI

This is the web-based user interface for GenAI Agent 3D, providing a user-friendly way to interact with the system.

## Architecture

The web UI consists of two main components:

1. **Backend API (FastAPI)**: Provides REST and WebSocket endpoints for interacting with the GenAI Agent 3D system.
2. **Frontend (React)**: Single-page application for user interaction and visualization.

## Setup

### Backend

1. Navigate to the backend directory:

   ```bash
   cd web/backend
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:

   ```bash
   python run_server.py
   ```

   By default, the server runs on port 8000. You can specify a different port:

   ```bash
   python run_server.py --port 8080
   ```

### Frontend

1. Navigate to the frontend directory:

   ```bash
   cd web/frontend
   ```
2. Install dependencies:

   ```bash
   npm install
   ```
3. Start the development server:

   ```bash
   npm start
   ```

   The frontend will be accessible at http://localhost:3000

## Features

- **Dashboard**: Overview of system status and available tools
- **Instructions**: Send natural language instructions to the agent
- **Tools**: Access and execute individual tools
- **Models**: Create 3D models from text descriptions
- **Scenes**: Create and edit 3D scenes
- **Diagrams**: Generate diagrams from text descriptions
- **Settings**: Configure the system

## WebSocket API

The application uses WebSockets for real-time updates during long-running operations:

- **Instruction Processing**: Get real-time updates during instruction processing
- **Tool Execution**: Monitor tool execution progress
- **Status Updates**: Receive system status updates

## Deployment

For production deployment:

1. Build the frontend:

   ```bash
   cd web/frontend
   npm run build
   ```
2. Serve the static files from the backend:

   ```bash
   # Copy the build directory to the backend's static folder
   cp -r web/frontend/build web/backend/static
   ```
3. Run the backend with a production ASGI server:

   ```bash
   cd web/backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Docker Support

Docker support will be added in a future release.
