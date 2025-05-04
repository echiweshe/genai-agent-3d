# PowerShell script to run comprehensive test

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Comprehensive SVG to 3D Test..." -ForegroundColor Cyan
Write-Host "Using Blender: $blender" -ForegroundColor Green

# Run with GUI
$choice = Read-Host "Run with GUI? (y/n)"

if ($choice -eq "y") {
    Write-Host "Running with GUI..." -ForegroundColor Cyan
    & $blender --python test_all_elements.py
} else {
    Write-Host "Running in background..." -ForegroundColor Cyan
    & $blender --background --python test_all_elements.py
}

Write-Host "`nTest complete!" -ForegroundColor Green
Write-Host "Output file: comprehensive_output.blend" -ForegroundColor Yellow
