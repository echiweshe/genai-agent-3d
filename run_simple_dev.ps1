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

# Start the simple backend server in a new window
Write-Host "Starting simple backend server..." -ForegroundColor Cyan
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Set-Location '$PWD'; & .\venv\Scripts\Activate.ps1; Set-Location web\backend; python simple_server.py }" -PassThru

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if Node.js is available
try {
    node --version
    $nodeAvailable = $true
} catch {
    $nodeAvailable = $false
    Write-Host "WARNING: Node.js is not installed or not in PATH." -ForegroundColor Yellow
    Write-Host "The frontend development server cannot be started." -ForegroundColor Yellow
    Write-Host "You can still access the backend API at http://localhost:8000" -ForegroundColor Cyan
    exit 0
}

# Start the frontend development server
if ($nodeAvailable) {
    Write-Host "Starting frontend development server..." -ForegroundColor Cyan
    Set-Location web\frontend
    npm start
}

Write-Host ""
Write-Host "Development environment is running." -ForegroundColor Green
