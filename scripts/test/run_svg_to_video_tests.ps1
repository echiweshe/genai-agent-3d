# PowerShell script to run SVG to Video tests

# Get the directory of this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)

# Python executable
$pythonPath = Join-Path $projectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    # Try system Python if venv not found
    $pythonPath = "python"
}

# Test script
$testScript = Join-Path $scriptPath "run_svg_to_video_tests.py"

# Parse command line arguments
param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("svg_generator", "svg_to_3d", "animation", "rendering", "pipeline")]
    [string]$Module
)

# Set up command
$cmd = "$pythonPath $testScript"
if ($Module) {
    $cmd += " --module $Module"
}

# Run the tests
Write-Host "Running SVG to Video tests..." -ForegroundColor Cyan
Write-Host "Command: $cmd" -ForegroundColor DarkGray
Write-Host

# Execute the command
Invoke-Expression $cmd

# Get the exit code
$exitCode = $LASTEXITCODE

# Display result
if ($exitCode -eq 0) {
    Write-Host "`nAll tests passed!" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed." -ForegroundColor Red
}

# Return the exit code
exit $exitCode
