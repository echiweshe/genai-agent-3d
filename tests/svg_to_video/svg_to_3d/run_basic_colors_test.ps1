# PowerShell script to run basic colors test

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Basic Colors Test..." -ForegroundColor Cyan
Write-Host "Using Blender: $blender" -ForegroundColor Green

# Run with GUI to see materials
Write-Host "Running with GUI..." -ForegroundColor Cyan
& $blender --python test_basic_colors.py

Write-Host "`nTest complete!" -ForegroundColor Green
Write-Host "Output file: basic_colors_output.blend" -ForegroundColor Yellow

Write-Host "`nExpected results:" -ForegroundColor Cyan
Write-Host "- Red rectangle (top left)" -ForegroundColor White
Write-Host "- Green rectangle (top center)" -ForegroundColor White  
Write-Host "- Blue rectangle (top right)" -ForegroundColor White
Write-Host "- Yellow circle (bottom left)" -ForegroundColor White
Write-Host "- Semi-transparent magenta circle (bottom center)" -ForegroundColor White
Write-Host "- Cyan circle with black stroke (bottom right)" -ForegroundColor White
