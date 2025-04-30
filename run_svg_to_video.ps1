# A simplified and robust SVG to Video run script
# This script will kill existing processes, then start either development or production mode

param (
    [switch]$Production,
    [switch]$Dev,
    [switch]$Simple
)

# Set script path
$scriptPath = $PSScriptRoot

# Function for colorful output
function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Define default ports
$backendPort = 8001
$frontendPort = 3001

# Display header
Write-ColorMessage "=============================================" "Cyan"
if ($Production) {
    Write-ColorMessage "      Starting SVG to Video in PRODUCTION mode  " "Cyan"
} elseif ($Simple) {
    Write-ColorMessage "      Starting SVG to Video in SIMPLE mode      " "Cyan"
} else {
    # Default to dev mode
    $Dev = $true
    Write-ColorMessage "      Starting SVG to Video in DEVELOPMENT mode " "Cyan"
}
Write-ColorMessage "=============================================" "Cyan"

# Kill existing server processes
Write-ColorMessage "Killing any existing server processes..." "Yellow"
& "$scriptPath\kill_servers.ps1"

# Ensure outputs directory exists
$outputsDir = Join-Path -Path $scriptPath -ChildPath "outputs"
if (-not (Test-Path $outputsDir)) {
    New-Item -ItemType Directory -Path $outputsDir | Out-Null
    Write-ColorMessage "Created outputs directory" "Green"
}

# Ensure virtual environment exists
$venvPath = Join-Path -Path $scriptPath -ChildPath "venv"
$venvActivateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvActivateScript)) {
    Write-ColorMessage "Creating virtual environment..." "Yellow"
    try {
        python -m venv $venvPath
        & $venvActivateScript
        
        # Install requirements if available
        $requirementsPath = Join-Path -Path $scriptPath -ChildPath "web\backend\requirements.txt"
        if (Test-Path $requirementsPath) {
            Write-ColorMessage "Installing requirements..." "Yellow"
            pip install -r $requirementsPath
        }
    } catch {
        Write-ColorMessage "Failed to create virtual environment: $($_.Exception.Message)" "Red"
        exit 1
    }
}

# Run the appropriate script based on mode
try {
    if ($Production) {
        # Production mode - build frontend and run server
        Write-ColorMessage "Starting server in PRODUCTION mode..." "Green"
        
        # Backend with built frontend
        $backendDir = Join-Path -Path $scriptPath -ChildPath "web\backend"
        $backendCmd = "& '$venvActivateScript'; Set-Location '$backendDir'; python main.py --port $backendPort --prod"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal
        
        Write-ColorMessage "Production server started on http://localhost:$backendPort" "Green"
    } 
    elseif ($Simple) {
        # Simple mode - use simple_server.py
        Write-ColorMessage "Starting server in SIMPLE mode..." "Green"
        
        # Simple backend server
        $backendDir = Join-Path -Path $scriptPath -ChildPath "web\backend"
        $backendCmd = "& '$venvActivateScript'; Set-Location '$backendDir'; python simple_server.py"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal
        
        Write-ColorMessage "Simple server started on http://localhost:$backendPort" "Green"
    }
    else {
        # Development mode - separate backend and frontend
        Write-ColorMessage "Starting servers in DEVELOPMENT mode..." "Green"
        
        # Start backend
        $backendDir = Join-Path -Path $scriptPath -ChildPath "web\backend"
        $backendCmd = "& '$venvActivateScript'; Set-Location '$backendDir'; python main.py --port $backendPort"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal
        
        # Wait a bit for backend to start
        Start-Sleep -Seconds 3
        
        # Update the frontend proxy configuration
        $packageJsonPath = Join-Path -Path $scriptPath -ChildPath "web\frontend\package.json"
        if (Test-Path $packageJsonPath) {
            try {
                $packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
                $packageJson.proxy = "http://localhost:$backendPort"
                $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
                Write-ColorMessage "Updated frontend proxy configuration to point to port $backendPort" "Green"
            } catch {
                Write-ColorMessage "Failed to update frontend proxy: $($_.Exception.Message)" "Yellow"
            }
        }
        
        # Start frontend if Node.js is available
        try {
            $nodeVersion = node -v
            Write-ColorMessage "Node.js version: $nodeVersion" "Green"
            
            $frontendDir = Join-Path -Path $scriptPath -ChildPath "web\frontend"
            Set-Location $frontendDir
            
            # Set environment variable for frontend port
            $env:PORT = $frontendPort
            
            # Start frontend server in a new window
            $frontendCmd = "Set-Location '$frontendDir'; $env:PORT=$frontendPort; npm start"
            Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal
            
            Write-ColorMessage "Frontend server starting on http://localhost:$frontendPort" "Green"
        } catch {
            Write-ColorMessage "Node.js not found. Cannot start frontend server." "Red"
            Write-ColorMessage "If you need the frontend, please install Node.js and try again." "Yellow"
        }
    }
    
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "          Server(s) started successfully      " "Cyan"
    if ($Production -or $Simple) {
        Write-ColorMessage "          http://localhost:$backendPort         " "Green"
    } else {
        Write-ColorMessage "  Backend: http://localhost:$backendPort         " "Green"
        Write-ColorMessage "  Frontend: http://localhost:$frontendPort       " "Green"
    }
    Write-ColorMessage "=============================================" "Cyan"
    
} catch {
    Write-ColorMessage "Error starting servers: $($_.Exception.Message)" "Red"
    exit 1
}
