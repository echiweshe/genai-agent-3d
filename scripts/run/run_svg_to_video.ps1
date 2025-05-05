# PowerShell script to run the SVG to Video pipeline

# Get the directory of this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)

# Python executable
$pythonPath = Join-Path $projectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    # Try system Python if venv not found
    $pythonPath = "python"
}

# Pipeline script
$pipelineScript = Join-Path $scriptPath "svg_to_video.py"

# Parse command line arguments and forward them to the Python script
$arguments = $args

# Print header
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "SVG to Video Pipeline" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Project Root: $projectRoot" -ForegroundColor DarkGray
Write-Host "Python Path: $pythonPath" -ForegroundColor DarkGray
Write-Host "Script Path: $pipelineScript" -ForegroundColor DarkGray
Write-Host

# Build and run the command
$cmd = "$pythonPath $pipelineScript $arguments"
Write-Host "Running command:" -ForegroundColor Yellow
Write-Host "$cmd" -ForegroundColor DarkGray
Write-Host

# Execute the command
Invoke-Expression $cmd

# Get the exit code
$exitCode = $LASTEXITCODE

# Display result
if ($exitCode -eq 0) {
    Write-Host "`nCommand completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nCommand failed with exit code $exitCode." -ForegroundColor Red
}

# Return the exit code
exit $exitCode
