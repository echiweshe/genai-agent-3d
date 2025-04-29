# PowerShell script to run the simplified development environment

Write-Host "Starting simplified SVG to Video development environment" -ForegroundColor Green
Write-Host ""

# Get the script path
$scriptPath = $PSScriptRoot

# Check if virtual environment exists
if (-not (Test-Path (Join-Path -Path $scriptPath -ChildPath "venv"))) {
    Write-Host "Virtual environment not found. Please run setup_svg_to_video.ps1 first." -ForegroundColor Red
    exit 1
}

# Create outputs directory if it doesn't exist
$outputsDir = Join-Path -Path $scriptPath -ChildPath "outputs"
if (-not (Test-Path $outputsDir)) {
    New-Item -ItemType Directory -Path $outputsDir | Out-Null
    Write-Host "Created outputs directory" -ForegroundColor Green
}

# Load port configuration if available
$portsConfigPath = Join-Path -Path $scriptPath -ChildPath "config\ports.json"
$svgBackendPort = 8001  # Default port
$svgFrontendPort = 3001  # Default SVG to Video frontend port

if (Test-Path $portsConfigPath) {
    try {
        $portConfig = Get-Content $portsConfigPath | ConvertFrom-Json
        if ($portConfig.services -and $portConfig.services.PSObject.Properties.Name -contains "svg_to_video_backend") {
            $svgBackendPort = $portConfig.services.svg_to_video_backend
        }
        if ($portConfig.services -and $portConfig.services.PSObject.Properties.Name -contains "svg_to_video_frontend") {
            $svgFrontendPort = $portConfig.services.svg_to_video_frontend
        }
        Write-Host "Using configured ports: Backend=$svgBackendPort, Frontend=$svgFrontendPort" -ForegroundColor Green
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Host "Error loading port configuration: $errorMsg" -ForegroundColor Red
        Write-Host "Using default ports: Backend=$svgBackendPort, Frontend=$svgFrontendPort" -ForegroundColor Yellow
    }
} else {
    Write-Host "Port configuration file not found. Using default ports: Backend=$svgBackendPort, Frontend=$svgFrontendPort" -ForegroundColor Yellow
}

# Kill any existing processes on our ports
try {
    # First check if our kill script exists and run it
    $killScriptPath = Join-Path -Path $scriptPath -ChildPath "kill_servers.ps1"
    if (Test-Path $killScriptPath) {
        Write-Host "Running kill_servers.ps1 to cleanup any running servers..." -ForegroundColor Cyan
        & $killScriptPath
    } else {
        # Fallback: manually check for processes on our ports
        try {
            $processId = Get-NetTCPConnection -LocalPort $svgBackendPort -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
            if ($processId) {
                Write-Host "Killing existing process on port $svgBackendPort..." -ForegroundColor Yellow
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        } catch {
            $errorText = $_.Exception.Message
            Write-Host "Error checking port $svgBackendPort - $errorText" -ForegroundColor Yellow
        }
        
        try {
            $processId = Get-NetTCPConnection -LocalPort $svgFrontendPort -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
            if ($processId) {
                Write-Host "Killing existing process on port $svgFrontendPort..." -ForegroundColor Yellow
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        } catch {
            $errorText = $_.Exception.Message
            Write-Host "Error checking port $svgFrontendPort - $errorText" -ForegroundColor Yellow
        }
    }
    
    # Give processes time to shut down
    Start-Sleep -Seconds 2
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Error killing existing processes: $errorMsg" -ForegroundColor Red
    Write-Host "Continuing anyway..." -ForegroundColor Yellow
}

# Check for master .env file
$masterEnvPath = Join-Path -Path $scriptPath -ChildPath "genai_agent_project\.env"
if (Test-Path $masterEnvPath) {
    Write-Host "Using master .env file from genai_agent_project directory." -ForegroundColor Green
} else {
    Write-Host "Warning: Master .env file not found at genai_agent_project\.env" -ForegroundColor Yellow
    Write-Host "Checking for local .env file..." -ForegroundColor Yellow
    
    $localEnvPath = Join-Path -Path $scriptPath -ChildPath ".env"
    if (Test-Path $localEnvPath) {
        Write-Host "Using local .env file." -ForegroundColor Green
    } else {
        Write-Host "No .env file found. API keys may not be available." -ForegroundColor Red
        Write-Host "The application may not work properly without API keys." -ForegroundColor Red
    }
}

# Modify the simple_server.py file to use the correct port
$serverPath = Join-Path -Path $scriptPath -ChildPath "web\backend\simple_server.py"
if (Test-Path $serverPath) {
    $serverContent = Get-Content $serverPath -Raw
    $serverContent = $serverContent -replace "port = \d+", "port = $svgBackendPort"
    Set-Content $serverPath -Value $serverContent
    Write-Host "Updated server port in simple_server.py to $svgBackendPort" -ForegroundColor Cyan
}

# Start the simple backend server in a new window
Write-Host "Starting SVG to Video backend server on port $svgBackendPort..." -ForegroundColor Cyan
$venvActivateScript = Join-Path -Path $scriptPath -ChildPath "venv\Scripts\Activate.ps1"
$backendDir = Join-Path -Path $scriptPath -ChildPath "web\backend"
$backendCmd = "& { Set-Location '$scriptPath'; & '$venvActivateScript'; Set-Location '$backendDir'; python simple_server.py }"
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -PassThru

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Update the frontend proxy configuration to use the correct port
$packageJsonPath = Join-Path -Path $scriptPath -ChildPath "web\frontend\package.json"
if (Test-Path $packageJsonPath) {
    Write-Host "Updating frontend proxy configuration..." -ForegroundColor Cyan
    $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    $packageJson.proxy = "http://localhost:$svgBackendPort"
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content $packageJsonPath
}

# Check if Node.js is available
try {
    node --version
    $nodeAvailable = $true
} catch {
    $nodeAvailable = $false
    Write-Host "WARNING: Node.js is not installed or not in PATH." -ForegroundColor Yellow
    Write-Host "The frontend development server cannot be started." -ForegroundColor Yellow
    Write-Host "You can still access the backend API at http://localhost:$svgBackendPort" -ForegroundColor Cyan
    exit 0
}

# Start the frontend development server
if ($nodeAvailable) {
    Write-Host "Starting frontend development server on port $svgFrontendPort..." -ForegroundColor Cyan
    $frontendDir = Join-Path -Path $scriptPath -ChildPath "web\frontend"
    Set-Location $frontendDir
    
    # Update the PORT environment variable for the React app
    $env:PORT = $svgFrontendPort
    
    # Start the React app
    npm start
}

Write-Host ""
Write-Host "Development environment is running." -ForegroundColor Green
Write-Host "Backend API: http://localhost:$svgBackendPort" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:$svgFrontendPort" -ForegroundColor Cyan
