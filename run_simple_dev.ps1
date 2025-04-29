# PowerShell script to run the simplified development environment

Write-Host "Starting simplified SVG to Video development environment" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup_svg_to_video.ps1 first." -ForegroundColor Red
    exit 1
}

# Create outputs directory if it doesn't exist
if (-not (Test-Path "outputs")) {
    New-Item -ItemType Directory -Path "outputs" | Out-Null
}

# Load port configuration if available
$portsConfigPath = "config\ports.json"
$svgBackendPort = 8001  # Default port
$webFrontendPort = 3000  # Default port

if (Test-Path $portsConfigPath) {
    try {
        $portConfig = Get-Content $portsConfigPath | ConvertFrom-Json
        $svgBackendPort = $portConfig.svg_to_video_backend
        $webFrontendPort = $portConfig.web_frontend
        Write-Host "Using configured ports: Backend=$svgBackendPort, Frontend=$webFrontendPort" -ForegroundColor Green
    } catch {
        Write-Host "Error loading port configuration: $_" -ForegroundColor Red
        Write-Host "Using default ports: Backend=$svgBackendPort, Frontend=$webFrontendPort" -ForegroundColor Yellow
    }
} else {
    Write-Host "Port configuration file not found. Using default ports: Backend=$svgBackendPort, Frontend=$webFrontendPort" -ForegroundColor Yellow
}

# Kill any existing processes on our ports
try {
    # First check if our kill script exists and run it
    if (Test-Path "kill_servers.ps1") {
        Write-Host "Running kill_servers.ps1 to cleanup any running servers..." -ForegroundColor Cyan
        & .\kill_servers.ps1
    } else {
        # Fallback: manually check for processes on our ports
        $processId = Get-NetTCPConnection -LocalPort $svgBackendPort -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
        if ($processId) {
            Write-Host "Killing existing process on port $svgBackendPort..." -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
        
        $processId = Get-NetTCPConnection -LocalPort $webFrontendPort -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
        if ($processId) {
            Write-Host "Killing existing process on port $webFrontendPort..." -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Give processes time to shut down
    Start-Sleep -Seconds 2
} catch {
    Write-Host "Error killing existing processes: $_" -ForegroundColor Red
    Write-Host "Continuing anyway..." -ForegroundColor Yellow
}

# Check for master .env file
if (Test-Path "genai_agent_project\.env") {
    Write-Host "Using master .env file from genai_agent_project directory." -ForegroundColor Green
} else {
    Write-Host "Warning: Master .env file not found at genai_agent_project\.env" -ForegroundColor Yellow
    Write-Host "Checking for local .env file..." -ForegroundColor Yellow
    
    if (Test-Path ".env") {
        Write-Host "Using local .env file." -ForegroundColor Green
    } else {
        Write-Host "No .env file found. API keys may not be available." -ForegroundColor Red
        Write-Host "The application may not work properly without API keys." -ForegroundColor Red
    }
}

# Modify the simple_server.py file to use the correct port
$serverPath = "web\backend\simple_server.py"
if (Test-Path $serverPath) {
    $serverContent = Get-Content $serverPath -Raw
    $serverContent = $serverContent -replace "port = \d+", "port = $svgBackendPort"
    Set-Content $serverPath -Value $serverContent
    Write-Host "Updated server port in simple_server.py to $svgBackendPort" -ForegroundColor Cyan
}

# Start the simple backend server in a new window
Write-Host "Starting SVG to Video backend server on port $svgBackendPort..." -ForegroundColor Cyan
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Set-Location '$PWD'; & .\venv\Scripts\Activate.ps1; Set-Location web\backend; python simple_server.py }" -PassThru

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Update the frontend proxy configuration to use the correct port
$packageJsonPath = "web\frontend\package.json"
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
    Write-Host "Starting frontend development server on port $webFrontendPort..." -ForegroundColor Cyan
    Set-Location web\frontend
    
    # Update the PORT environment variable for the React app
    $env:PORT = $webFrontendPort
    
    # Start the React app
    npm start
}

Write-Host ""
Write-Host "Development environment is running." -ForegroundColor Green
