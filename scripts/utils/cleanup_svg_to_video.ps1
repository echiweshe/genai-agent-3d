# PowerShell script to clean up SVG to Video module

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)
$pythonPath = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    # Try system Python if venv not found
    $pythonPath = "python"
}

$cleanupScript = Join-Path $scriptPath "cleanup_svg_to_video.py"

# Print header
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "SVG to Video Module Cleanup" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host

# Check if archive directory exists
$archiveDir = Join-Path $projectRoot "archive\svg_to_video"
if (-not (Test-Path $archiveDir)) {
    Write-Host "Creating archive directory..." -ForegroundColor Yellow
    New-Item -Path $archiveDir -ItemType Directory -Force | Out-Null
}

# Run the cleanup script
Write-Host "Running cleanup script..." -ForegroundColor Yellow
& $pythonPath $cleanupScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "Cleanup failed. See error messages above." -ForegroundColor Red
    exit 1
}

Write-Host "`nCleanup completed successfully!" -ForegroundColor Green
Write-Host "The SVG to Video module has been organized and deprecated files have been backed up to:" -ForegroundColor Green
Write-Host $archiveDir -ForegroundColor Yellow
Write-Host

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review the documentation in the docs/svg_to_video directory" -ForegroundColor White
Write-Host "2. Run the SVG to Video demo to verify everything works correctly:" -ForegroundColor White
Write-Host "   .\run_svg_video_demo.ps1" -ForegroundColor Yellow
Write-Host "3. Use the modular API in your code:" -ForegroundColor White
Write-Host "   from genai_agent.svg_to_video import SVGToVideoPipeline" -ForegroundColor Yellow
