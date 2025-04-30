# Kill Servers PowerShell Script
# This script stops all running servers for the GenAI Agent 3D project

# Set up a function to log messages
function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Display header
Write-ColorMessage "=============================================" "Cyan"
Write-ColorMessage "          Killing all server processes        " "Cyan"
Write-ColorMessage "=============================================" "Cyan"

# Define ports to check - hardcoded to ensure all ports are covered
$portsToCheck = @(8000, 8001, 8002, 3000, 3001, 8080)

# Kill processes by port number
foreach ($port in $portsToCheck) {
    Write-ColorMessage "Checking for processes on port $port..." "Yellow"
    
    # Find processes using the port using different methods to ensure we find them
    try {
        # Method 1: Using netstat (works on most Windows systems)
        $processesUsingPort = netstat -ano | Select-String ":$port " | ForEach-Object { 
            if ($_ -match ":$port\s+\S+\s+\S+\s+(\d+)") {
                return $Matches[1]
            }
        } | Sort-Object -Unique

        # Method 2: Using Get-NetTCPConnection (PowerShell 4.0+)
        if (-not $processesUsingPort) {
            try {
                $processesUsingPort = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
                                     Select-Object -ExpandProperty OwningProcess -Unique
            } catch {
                Write-ColorMessage "Get-NetTCPConnection not available or failed: $($_.Exception.Message)" "Yellow"
            }
        }
        
        if ($processesUsingPort) {
            foreach ($pid in $processesUsingPort) {
                try {
                    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($process) {
                        Write-ColorMessage "Killing process: $($process.ProcessName) (PID: $pid) on port $port" "Red"
                        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                        
                        # Verify the process was killed
                        Start-Sleep -Milliseconds 500
                        if (-not (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
                            Write-ColorMessage "Successfully terminated process with PID $pid" "Green"
                        } else {
                            Write-ColorMessage "Failed to terminate process with PID $pid, trying again with higher priority" "Yellow"
                            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                        }
                    }
                } catch {
                    $errorText = $_.Exception.Message
                    Write-ColorMessage "Failed to kill process with PID $pid`: $errorText" "Red"
                }
            }
        } else {
            Write-ColorMessage "No processes found using port $port" "Green"
        }
    } catch {
        $errorText = $_.Exception.Message
        Write-ColorMessage "Error checking port $port`: $errorText" "Red"
    }
}

# Find and kill any Python or Node.js processes related to our project
Write-ColorMessage "Looking for Python and Node.js processes..." "Yellow"

# Define keywords to identify our project's processes
$projectKeywords = @("svg", "video", "genai", "backend", "server", "blender", "agent-3d")

# Get all Python processes
$pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
foreach ($process in $pythonProcesses) {
    try {
        # Try to get the command line to see if it's related to our project
        $commandLine = (Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
        
        if ($commandLine -and ($projectKeywords | Where-Object { $commandLine -like "*$_*" })) {
            Write-ColorMessage "Killing Python process: $($process.Id) - $commandLine" "Red"
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # If we can't check command line, be safer and don't kill
        continue
    }
}

# Get all Node.js processes
$nodeProcesses = Get-Process -Name "node*" -ErrorAction SilentlyContinue
foreach ($process in $nodeProcesses) {
    try {
        # Try to get the command line to see if it's related to our project
        $commandLine = (Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
        
        if ($commandLine -and ($projectKeywords | Where-Object { $commandLine -like "*$_*" })) {
            Write-ColorMessage "Killing Node.js process: $($process.Id) - $commandLine" "Red"
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # If we can't check command line, be safer and don't kill
        continue
    }
}

Write-ColorMessage "=============================================" "Cyan"
Write-ColorMessage "      All server processes have been killed   " "Cyan"
Write-ColorMessage "=============================================" "Cyan"
