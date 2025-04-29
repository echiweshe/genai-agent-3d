# PowerShell script to kill servers running on our defined ports

Write-Host "Killing server processes..." -ForegroundColor Red
Write-Host ""

# Function to kill process on a specific port
function Kill-ProcessOnPort {
    param (
        [int]$Port,
        [string]$ServiceName
    )
    
    try {
        $processIds = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                      Select-Object -ExpandProperty OwningProcess -Unique
        
        if ($processIds -and $processIds.Count -gt 0) {
            foreach ($processId in $processIds) {
                $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Killing $ServiceName process $($process.Name) (ID: $processId) on port $Port" -ForegroundColor Yellow
                    Stop-Process -Id $processId -Force
                    return $true
                }
            }
        }
        return $false
    } catch {
        Write-Host "Error checking port $Port: $_" -ForegroundColor Red
        return $false
    }
}

# Load port configuration if available
$portsConfigPath = "config\ports.json"
$portConfig = $null

if (Test-Path $portsConfigPath) {
    try {
        $portConfig = Get-Content $portsConfigPath | ConvertFrom-Json
        Write-Host "Loaded port configuration from $portsConfigPath" -ForegroundColor Green
    } catch {
        Write-Host "Error loading port configuration: $_" -ForegroundColor Red
        $portConfig = $null
    }
}

# Define ports to check - either from config or defaults
$portsToCheck = @()

if ($portConfig) {
    # Get properties from the config object
    $portConfig.PSObject.Properties | ForEach-Object {
        $portsToCheck += @{
            Port = $_.Value
            Name = $_.Name
        }
    }
} else {
    # Default ports
    $portsToCheck = @(
        @{ Port = 8000; Name = "Main Backend" },
        @{ Port = 8001; Name = "SVG to Video Backend" },
        @{ Port = 8002; Name = "Web Backend" },
        @{ Port = 3000; Name = "Web Frontend" },
        @{ Port = 3001; Name = "SVG to Video Frontend" }
    )
}

$totalKilled = 0

foreach ($portInfo in $portsToCheck) {
    Write-Host "Checking for processes on port $($portInfo.Port) ($($portInfo.Name))..." -ForegroundColor Cyan
    if (Kill-ProcessOnPort -Port $portInfo.Port -ServiceName $portInfo.Name) {
        $totalKilled++
    }
}

if ($totalKilled -eq 0) {
    Write-Host "No running servers found on any of the checked ports." -ForegroundColor Green
} else {
    Write-Host "Successfully killed $totalKilled server process(es)." -ForegroundColor Green
}

Write-Host ""
Write-Host "Checking for python.exe and node.exe processes that might be servers..." -ForegroundColor Cyan

$serverProcesses = @("python", "node")
$killedExtra = 0

foreach ($procName in $serverProcesses) {
    $processes = Get-Process -Name $procName -ErrorAction SilentlyContinue | Where-Object {
        # Look for command line arguments that suggest it's a server
        $_.CommandLine -match "server|uvicorn|fastapi|react-scripts|start"
    }
    
    if ($processes) {
        foreach ($proc in $processes) {
            Write-Host "Killing $procName process (ID: $($proc.Id)) that appears to be a server" -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force
            $killedExtra++
        }
    }
}

if ($killedExtra -gt 0) {
    Write-Host "Killed $killedExtra additional server processes." -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! You can now start servers again." -ForegroundColor Green
