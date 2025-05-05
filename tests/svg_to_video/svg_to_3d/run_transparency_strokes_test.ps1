$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Transparency and Strokes Test..." -ForegroundColor Cyan
Write-Host "Using Blender: $blender" -ForegroundColor Green

# Close any running Blender instances first
Write-Host "`nClosing any existing Blender instances..." -ForegroundColor Cyan
Get-Process blender -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Run with GUI to see materials
Write-Host "Starting fresh Blender instance..." -ForegroundColor Cyan
& $blender --python test_stroke_fill_fixed.py

Write-Host "`nTest complete!" -ForegroundColor Green
