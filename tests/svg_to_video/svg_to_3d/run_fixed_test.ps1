# PowerShell script to run the fixed SVG to 3D test

Write-Host "Running Fixed SVG to 3D Test..." -ForegroundColor Cyan

# Find Blender
$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    Write-Host "Please update the path to your Blender installation." -ForegroundColor Yellow
    exit 1
}

# Run the test
Write-Host "Using Blender: $blender" -ForegroundColor Green
Write-Host "Running test..." -ForegroundColor Cyan

& $blender --background --python test_converter_fixed.py

Write-Host "`nTest complete!" -ForegroundColor Green
