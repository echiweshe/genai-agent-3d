# Run SVG to Video Production Server PowerShell Script
# This script builds the frontend and starts the production server

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
            }
        }
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Warning "Could not load port configuration: $errorMsg"
        # Return default ports
        return @{
            svg_to_video_backend = 8001
        }
    }
}

# Get ports from configuration
$ports = Get-PortsFromConfig

# Make sure we have a valid port number
if ($ports -is [System.Collections.IDictionary] -and $ports.ContainsKey("svg_to_video_backend")) {
    $backendPort = $ports.svg_to_video_backend
} else {
    $backendPort = 8001  # Default port
    Write-Warning "Using default backend port: $backendPort"
}

# Display header
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "      Starting SVG to Video Production Server " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Check if the port is already in use
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

# Build frontend if it doesn't exist
function Build-Frontend {
    $frontendDir = Join-Path -Path $scriptPath -ChildPath "web\frontend"
    $buildDir = Join-Path -Path $frontendDir -ChildPath "build"
    
    if (-not (Test-Path $buildDir) -or (Get-ChildItem $buildDir | Measure-Object).Count -eq 0) {
        Write-Host "Frontend build not found. Building frontend..." -ForegroundColor Yellow
        
        # Check if Node.js is installed
        try {
            $nodeVersion = node -v
            Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green
        } catch {
            Write-Host "Node.js is not installed or not in PATH. Please install Node.js 14+ and try again." -ForegroundColor Red
            exit 1
        }
        
        # Build frontend
        Push-Location $frontendDir
        npm install
        if (-not $?) {
            Write-Host "Failed to install frontend dependencies. Please check your npm installation." -ForegroundColor Red
            Pop-Location
            exit 1
        }
        
        npm run build
        if (-not $?) {
            Write-Host "Failed to build frontend. Please check the error messages above." -ForegroundColor Red
            Pop-Location
            exit 1
        }
        
        Pop-Location
        
        Write-Host "Frontend built successfully" -ForegroundColor Green
    } else {
        Write-Host "Frontend build already exists" -ForegroundColor Green
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
    
    # Activate the virtual environment and install dependencies
    & $venvActivateScript
    $requirementsPath = Join-Path -Path $scriptPath -ChildPath "web\backend\requirements.txt"
    if (Test-Path $requirementsPath) {
        pip install -r $requirementsPath
        
        if (-not $?) {
            Write-Host "Failed to install backend dependencies. Please check your pip installation." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Warning "Requirements file not found at: $requirementsPath"
    }
}

# Check if port is in use and kill process if necessary
if (Test-PortInUse -Port $backendPort) {
    Write-Host "Port $backendPort is already in use. Killing processes..." -ForegroundColor Yellow
    Kill-ProcessOnPort -Port $backendPort
}

# Build frontend
Build-Frontend

# Start production server
Write-Host "Starting production server on port $backendPort..." -ForegroundColor Green
$backendDir = Join-Path -Path $scriptPath -ChildPath "web\backend"
$backendCmd = "& '$venvActivateScript'; Set-Location '$backendDir'; python main.py --port $backendPort --prod"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "SVG to Video Production Server Started Successfully" -ForegroundColor Cyan
Write-Host "Server running at: http://localhost:$backendPort" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
