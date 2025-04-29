# Kill Servers PowerShell Script
# This script stops all running servers for the GenAI Agent 3D project

# Import port configurations
$scriptPath = $PSScriptRoot
$configPath = Join-Path $scriptPath "config" "ports.json"

function Get-PortsFromConfig {
    try {
        $config = Get-Content -Path $configPath -Raw | ConvertFrom-Json
        return $config.services
    } catch {
        Write-Warning "Could not load port configuration: $_"
        # Return default ports
        return @{
            main_backend = 8000
            svg_to_video_backend = 8001
            web_backend = 8002
            web_frontend = 3000
            svg_to_video_frontend = 3001
        }
    }
}

# Get ports from configuration
$ports = Get-PortsFromConfig

# Display header
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "          Killing all server processes        " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Kill processes by port
foreach ($service in $ports.PSObject.Properties) {
    $port = $service.Value
    $serviceName = $service.Name
    
    Write-Host "Checking for processes on port $port ($serviceName)..." -ForegroundColor Yellow
    
    # Find processes using the port
    $processesUsingPort = netstat -ano | Select-String ":$port " | ForEach-Object { ($_ -split '\s+')[5] } | Sort-Object -Unique
    
    if ($processesUsingPort) {
        foreach ($pid in $processesUsingPort) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Killing process: $($process.ProcessName) (PID: $pid) on port $port" -ForegroundColor Red
                    Stop-Process -Id $pid -Force
                }
            } catch {
                Write-Warning "Failed to kill process with PID $pid: $_"
            }
        }
    } else {
        Write-Host "No processes found using port $port" -ForegroundColor Green
    }
}

# Also check for Python and Node processes that might be related to our project
Write-Host "Checking for remaining Python and Node.js processes..." -ForegroundColor Yellow

# Find all python processes running scripts from our project directory
$projectDir = $scriptPath
$pythonProcesses = Get-WmiObject Win32_Process | Where-Object { 
    $_.CommandLine -like "*python*" -and $_.CommandLine -like "*$projectDir*" 
}

foreach ($process in $pythonProcesses) {
    Write-Host "Killing Python process: PID $($process.ProcessId)" -ForegroundColor Red
    try {
        Stop-Process -Id $process.ProcessId -Force
    } catch {
        Write-Warning "Failed to kill Python process with PID $($process.ProcessId): $_"
    }
}

# Find all node processes running scripts from our project directory
$nodeProcesses = Get-WmiObject Win32_Process | Where-Object { 
    $_.CommandLine -like "*node*" -and $_.CommandLine -like "*$projectDir*" 
}

foreach ($process in $nodeProcesses) {
    Write-Host "Killing Node.js process: PID $($process.ProcessId)" -ForegroundColor Red
    try {
        Stop-Process -Id $process.ProcessId -Force
    } catch {
        Write-Warning "Failed to kill Node.js process with PID $($process.ProcessId): $_"
    }
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "      All server processes have been killed   " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
