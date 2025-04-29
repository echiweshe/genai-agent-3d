# Port Configuration for GenAI Agent 3D

This document outlines the port configuration for the different services in the GenAI Agent 3D project.

## Service Port Assignments

The following ports are assigned to each service to ensure they can all run simultaneously without conflicts:

| Service | Port | Description |
|---------|------|-------------|
| Main Backend | 8000 | The original main GenAI Agent backend service |
| SVG to Video Backend | 8001 | The SVG to Video pipeline backend service |
| Web Backend | 8002 | The web interface backend service |
| Web Frontend | 3000 | The main web frontend |
| SVG to Video Frontend | 3001 | The SVG to Video frontend (if running separately) |

These port assignments are defined in the `config/ports.json` file.

## Running Multiple Services

When running multiple services simultaneously, ensure that:

1. You use the `kill_servers.ps1` script before starting new servers to clean up any running processes
2. Each service uses its assigned port
3. The frontend proxy settings point to the correct backend port

## Updating Port Configuration

If you need to change the port assignments, edit the `config/ports.json` file. The updated configuration will be used automatically by the scripts.

## Checking for Running Services

To see which services are currently running, you can use:

```powershell
Get-NetTCPConnection -LocalPort 8000,8001,8002,3000,3001 | 
  Format-Table LocalPort,OwningProcess,@{Name="ProcessName";Expression={(Get-Process -Id $_.OwningProcess).ProcessName}}
```

## Troubleshooting Port Conflicts

If you encounter port conflicts:

1. Run `kill_servers.ps1` to clean up all running servers
2. Check for any remaining processes using the ports:
   ```powershell
   Get-NetTCPConnection -LocalPort 8000,8001,8002,3000,3001
   ```
3. Manually kill any processes still using the ports:
   ```powershell
   Stop-Process -Id <process_id> -Force
   ```
4. If a port is persistently blocked, consider changing the port assignment in `config/ports.json`

## Default Server URLs

- Main GenAI Agent: http://localhost:8000
- SVG to Video Backend API: http://localhost:8001
- Web Backend API: http://localhost:8002
- Web Frontend: http://localhost:3000
- SVG to Video Frontend (if separate): http://localhost:3001
