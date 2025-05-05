# PowerShell script to run the SVG to Video Pipeline Demo

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $scriptPath "venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    # Try system Python if venv not found
    $pythonPath = "python"
}

$demoScript = Join-Path $scriptPath "run_svg_video_demo.py"

# Get the arguments passed to this script
$arguments = $args

# First, check if we need to fix imports
$fixImportsScript = Join-Path $scriptPath "scripts\utils\fix_svg_to_video_imports.py"
if (Test-Path $fixImportsScript) {
    Write-Host "Checking SVG to Video imports..." -ForegroundColor Yellow
    & $pythonPath $fixImportsScript | Out-Null
}

# Print header
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "SVG to Video Pipeline Demo" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host

# Run the demo script
Write-Host "Running demo..." -ForegroundColor Yellow
$cmd = "$pythonPath $demoScript $arguments"
Write-Host "Executing: $cmd" -ForegroundColor DarkGray
Write-Host

Invoke-Expression $cmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "Demo failed. See error messages above." -ForegroundColor Red
    exit 1
}

Write-Host "`nDemo completed successfully!" -ForegroundColor Green
Write-Host "`nFor more options, run: $pythonPath $demoScript --help" -ForegroundColor Yellow
