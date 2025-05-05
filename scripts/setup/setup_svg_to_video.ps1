# PowerShell Script to set up the SVG to Video Pipeline

Write-Host "Setting up GenAI Agent 3D - SVG to Video Pipeline" -ForegroundColor Green
Write-Host ""

# Check for Python
try {
    python --version
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.9+." -ForegroundColor Red
    exit 1
}

# Check for pip
try {
    python -m pip --version
} catch {
    Write-Host "pip is not installed. Please install pip." -ForegroundColor Red
    exit 1
}

# Check for Node.js
try {
    node --version
    $SKIP_FRONTEND = $false
} catch {
    Write-Host "WARNING: Node.js is not installed or not in PATH." -ForegroundColor Yellow
    Write-Host "The frontend setup will be skipped. Please install Node.js 14+ to run the frontend." -ForegroundColor Yellow
    $SKIP_FRONTEND = $true
}

# Create outputs directory if it doesn't exist
if (-not (Test-Path "outputs")) {
    New-Item -ItemType Directory -Path "outputs" | Out-Null
}

# Install dotenv package for Python first 
Write-Host "Installing python-dotenv..." -ForegroundColor Cyan
pip install python-dotenv

# Create Python virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path "venv")) {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment. Please install venv." -ForegroundColor Red
        Write-Host "You can install it with: pip install virtualenv" -ForegroundColor Yellow
        exit 1
    }
}

# Activate virtual environment and install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
pip install -r web\backend\requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install backend dependencies." -ForegroundColor Red
    exit 1
}
Write-Host "Backend dependencies installed successfully." -ForegroundColor Green

# Install frontend dependencies if Node.js is available
if (-not $SKIP_FRONTEND) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Push-Location web\frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install frontend dependencies." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
    Write-Host "Frontend dependencies installed successfully." -ForegroundColor Green
}

# Check for existing .env files
Write-Host "Checking for .env files..." -ForegroundColor Cyan
if (Test-Path "genai_agent_project\.env") {
    Write-Host "Found master .env file at genai_agent_project\.env" -ForegroundColor Green
    Write-Host "The application will use this file for API keys."
} else {
    Write-Host "Master .env file not found at genai_agent_project\.env" -ForegroundColor Yellow
    
    if (-not (Test-Path ".env")) {
        Write-Host "Creating local .env file..." -ForegroundColor Cyan
        if (Test-Path ".env.template") {
            Copy-Item ".env.template" ".env"
            Write-Host "Created .env file from template. Please edit it to add your API keys." -ForegroundColor Yellow
        } else {
            Set-Content -Path ".env" -Value "# API Keys for LLM Providers`n# Uncomment and add your keys`n# ANTHROPIC_API_KEY=your_anthropic_api_key`n# OPENAI_API_KEY=your_openai_api_key`n# BLENDER_PATH=path_to_blender_executable"
        }
        Write-Host "Note: You'll need to add your API keys to this file."
    } else {
        Write-Host "Found local .env file at the project root." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""

if ($SKIP_FRONTEND) {
    Write-Host "NOTE: The frontend setup was skipped. Please install Node.js to run the frontend." -ForegroundColor Yellow
}

Write-Host "To test the SVG generator component:"
Write-Host "  .\run_svg_generator_test.ps1"
Write-Host ""
Write-Host "To run the simplified development environment:"
Write-Host "  .\run_simple_dev.ps1"
Write-Host ""
Write-Host "To run the development servers:"
Write-Host "  .\run_svg_to_video_dev.ps1"
Write-Host ""
Write-Host "To run the production server:"
Write-Host "  .\run_svg_to_video_prod.ps1"

# Keep the virtual environment active
