# PowerShell script to run comprehensive test with fresh Blender instance

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Comprehensive Feature Test..." -ForegroundColor Cyan
Write-Host "This test demonstrates all working features" -ForegroundColor Green

# Close any running Blender instances first
Write-Host "`nClosing any existing Blender instances..." -ForegroundColor Cyan
Get-Process blender -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Run with GUI to see results
Write-Host "Starting fresh Blender instance..." -ForegroundColor Cyan
& $blender --python test_all_working.py

Write-Host "`nTest complete!" -ForegroundColor Green
Write-Host "Output file: comprehensive_output.blend" -ForegroundColor Yellow

Write-Host "`nFeatures demonstrated:" -ForegroundColor Cyan
Write-Host "- Basic shapes with colors (rectangles, circles, ellipses)" -ForegroundColor White
Write-Host "- Rounded rectangles" -ForegroundColor White
Write-Host "- Stroke only, fill only, and combined" -ForegroundColor White
Write-Host "- Transparency (opacity, fill-opacity, stroke-opacity)" -ForegroundColor White
Write-Host "- Complex shapes (polygons, paths, polylines)" -ForegroundColor White
Write-Host "- Text elements" -ForegroundColor White
