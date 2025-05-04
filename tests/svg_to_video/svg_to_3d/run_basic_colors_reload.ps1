# PowerShell script to run basic colors test with module reloading
# This ensures all changes are picked up

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Basic Colors Test (with module reloading)..." -ForegroundColor Cyan
Write-Host "Using Blender: $blender" -ForegroundColor Green
Write-Host "This test will reload all modules to ensure changes take effect." -ForegroundColor Yellow

# Close any running Blender instances first
Write-Host "`nClosing any existing Blender instances..." -ForegroundColor Cyan
Get-Process blender -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Run with GUI to see materials
Write-Host "Starting fresh Blender instance..." -ForegroundColor Cyan
& $blender --python test_basic_colors_reload.py

Write-Host "`nTest complete!" -ForegroundColor Green
