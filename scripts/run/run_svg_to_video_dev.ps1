# Run SVG to Video Development Servers PowerShell Script
# This script starts the backend and frontend servers for the SVG to Video pipeline

# Import port configurations
$scriptPath = $PSScriptRoot
$configPath = Join-Path -Path $scriptPath -ChildPath "config\ports.json"

function Get-PortsFromConfig {
    try {
        if (Test-Path -Path $configPath) {
            $config = Get-Content -Path $configPath -Raw | ConvertFrom-Json
            return $config.services
        } else {
            Write-Warning "Config file not found at: $configPath"
            # Return default ports
            return @{
                svg_to_video_backend = 8001
                svg_to_video_frontend = 3001
            }
        }
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Warning "Could not load port configuration: $errorMsg"
        # Return default ports
        return @{
            svg_to_video_backend = 8001
            svg_to_video_frontend = 3001
        }
    }
}

# Get ports from configuration
$ports = Get-PortsFromConfig

# Make sure we have valid port numbers
if ($ports -is [System.Collections.IDictionary]) {
    if ($ports.ContainsKey("svg_to_video_backend")) {
        $backendPort = $ports.svg_to_video_backend
    } else {
        $backendPort = 8001  # Default port
        Write-Warning "Using default backend port: $backendPort"
    }
    
    if ($ports.ContainsKey("svg_to_video_frontend")) {
        $frontendPort = $ports.svg_to_video_frontend
    } else {
        $frontendPort = 3001  # Default port
        Write-Warning "Using default frontend port: $frontendPort"
    }
} else {
    $backendPort = 8001
    $frontendPort = 3001
    Write-Warning "Using default ports: Backend=$backendPort, Frontend=$frontendPort"
}

# Display header
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "        Starting SVG to Video Dev Servers     " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Check if the ports are already in use
function Test-PortInUse {
    param(
        [int]$Port
    )
    
    $connections = netstat -ano | Select-String ":$Port "
    return $connections.Count -gt 0
}

# Kill process using a specific port
function Kill-ProcessOnPort {
    param(
        [int]$Port
    )
    
    $processesUsingPort = netstat -ano | Select-String ":$Port " | ForEach-Object { ($_ -split '\s+')[5] } | Sort-Object -Unique
    
    if ($processesUsingPort) {
        foreach ($pid in $processesUsingPort) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Killing process: $($process.ProcessName) (PID: $pid) on port $Port" -ForegroundColor Red
                    Stop-Process -Id $pid -Force
                }
            } catch {
                $errorMsg = $_.Exception.Message
                Write-Warning "Failed to kill process with PID $pid`: $errorMsg"
            }
        }
    }
}

# Check and update frontend proxy configuration
function Update-FrontendProxy {
    $packageJsonPath = Join-Path -Path $scriptPath -ChildPath "web\frontend\package.json"
    
    if (Test-Path $packageJsonPath) {
        try {
            $packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
            
            # Check if proxy is set correctly
            $currentProxy = $packageJson.proxy
            $requiredProxy = "http://localhost:$backendPort"
            
            if ($currentProxy -ne $requiredProxy) {
                Write-Host "Updating frontend proxy configuration to point to backend on port $backendPort" -ForegroundColor Yellow
                
                # Update the proxy in package.json
                $packageJson.proxy = $requiredProxy
                $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
                
                Write-Host "Frontend proxy configuration updated successfully" -ForegroundColor Green
            } else {
                Write-Host "Frontend proxy configuration is already set correctly" -ForegroundColor Green
            }
        } catch {
            $errorMsg = $_.Exception.Message
            Write-Warning "Failed to update frontend proxy configuration: $errorMsg"
        }
    } else {
        Write-Warning "Frontend package.json not found at $packageJsonPath"
    }
}

# Ensure necessary directories exist
$outputsDir = Join-Path -Path $scriptPath -ChildPath "outputs"
if (-not (Test-Path $outputsDir)) {
    New-Item -Path $outputsDir -ItemType Directory | Out-Null
    Write-Host "Created outputs directory" -ForegroundColor Green
}

# Check if virtual environment exists
$venvPath = Join-Path -Path $scriptPath -ChildPath "venv"
$venvActivateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvActivateScript)) {
    Write-Host "Virtual environment not found. Creating new virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    
    if (-not $?) {
        Write-Host "Failed to create virtual environment. Please install Python 3.9+ and try again." -ForegroundColor Red
        exit 1
    }
}

# Check if ports are in use and kill processes if necessary
if (Test-PortInUse -Port $backendPort) {
    Write-Host "Port $backendPort is already in use. Killing processes..." -ForegroundColor Yellow
    Kill-ProcessOnPort -Port $backendPort
}

if (Test-PortInUse -Port $frontendPort) {
    Write-Host "Port $frontendPort is already in use. Killing processes..." -ForegroundColor Yellow
    Kill-ProcessOnPort -Port $frontendPort
}

# Update frontend proxy configuration
Update-FrontendProxy

# Start backend server
Write-Host "Starting backend server on port $backendPort..." -ForegroundColor Green
$backendDir = Join-Path -Path $scriptPath -ChildPath "web\backend"
$backendCmd = "& '$venvActivateScript'; Set-Location '$backendDir'; python main.py --port $backendPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# Wait a bit for the backend to start
Write-Host "Waiting for backend server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend server
Write-Host "Starting frontend server on port $frontendPort..." -ForegroundColor Green
$frontendDir = Join-Path -Path $scriptPath -ChildPath "web\frontend"
$frontendCmd = "Set-Location '$frontendDir'; npm start -- --port $frontendPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  SVG to Video Dev Servers Started Successfully" -ForegroundColor Cyan
Write-Host "  Backend: http://localhost:$backendPort" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
