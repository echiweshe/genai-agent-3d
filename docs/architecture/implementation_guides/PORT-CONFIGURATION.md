# Port Configuration Guide

## Overview

This document outlines the port configuration for all services in the GenAI Agent 3D project. Proper port allocation ensures that multiple services can run simultaneously without conflicts.

## Port Assignments

| Service | Port | Description |
|---------|------|-------------|
| Main Backend | 8000 | The primary backend API server |
| SVG to Video Backend | 8001 | Backend for the SVG to Video pipeline |
| Web Backend | 8002 | Backend for the web interface |
| Web Frontend | 3000 | Frontend development server for the main web interface |
| SVG to Video Frontend | 3001 | Frontend development server for the SVG to Video pipeline |

## Configuration File

All port assignments are stored in `config/ports.json`. This centralized configuration allows for easy updates and ensures consistency across the project.

## How Services Use Port Configuration

1. **Backend Services**: Read the port configuration at startup to determine which port to bind to
2. **Frontend Services**: Use the port configuration to:
   - Determine which port to start the development server on
   - Configure the proxy settings for API calls to the corresponding backend

## Updating Port Configuration

If you need to change a port assignment:

1. Update the `config/ports.json` file
2. Run the appropriate setup script to update proxy configurations in frontend code
3. Restart all affected services

## Troubleshooting Port Conflicts

If you encounter port conflicts:

1. Run the kill script to stop all services:
   ```powershell
   .\kill_servers.ps1
   ```

2. Check if any other applications are using the required ports:
   ```powershell
   netstat -ano | findstr "8001"
   ```

3. If necessary, change the port configuration in `config/ports.json`

4. Run the setup script to apply the new configuration:
   ```powershell
   .\setup_ports.ps1
   ```

## Additional Notes

- The kill script automatically references the port configuration to ensure all services are properly terminated
- When running in production mode, the frontend builds are served by the backend services, so only the backend ports are used
