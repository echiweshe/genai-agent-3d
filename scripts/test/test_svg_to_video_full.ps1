# PowerShell script to run comprehensive SVG to Video test

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)
$pythonPath = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    # Try system Python if venv not found
    $pythonPath = "python"
}

$testScript = Join-Path $scriptPath "test_svg_to_video_full.py"

# Print header
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "SVG to Video Pipeline Comprehensive Test" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host

# Check if cleanup should be run first
$cleanupScript = Join-Path $projectRoot "scripts\utils\cleanup_svg_to_video.ps1"
$runCleanup = $false

if (Test-Path $cleanupScript) {
    Write-Host "Do you want to run the cleanup script first? (y/n): " -ForegroundColor Yellow -NoNewline
    $choice = Read-Host
    if ($choice -eq "y") {
        $runCleanup = $true
    }
}

if ($runCleanup) {
    Write-Host "`nRunning cleanup script first..." -ForegroundColor Yellow
    & $cleanupScript
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Cleanup failed. See error messages above." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Cleanup completed successfully!" -ForegroundColor Green
    Write-Host
}

# Run the test script
Write-Host "Running comprehensive test..." -ForegroundColor Yellow
& $pythonPath $testScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nTest failed. See error messages above." -ForegroundColor Red
    exit 1
}

Write-Host "`nTest completed successfully!" -ForegroundColor Green
Write-Host "The SVG to Video pipeline is working correctly with the modularized structure." -ForegroundColor Green

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Explore the documentation in docs/svg_to_video/" -ForegroundColor White
Write-Host "2. Try out the SVG to Video demo: .\run_svg_video_demo.ps1" -ForegroundColor White
Write-Host "3. Contribute to the development by addressing known issues and implementing enhancements" -ForegroundColor White
