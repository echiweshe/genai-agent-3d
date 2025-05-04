# PowerShell script to run simple materials test

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Simple Materials Test..." -ForegroundColor Cyan
Write-Host "Using Blender: $blender" -ForegroundColor Green

# Run with GUI to see materials
Write-Host "Running with GUI..." -ForegroundColor Cyan
& $blender --python test_simple_materials.py

Write-Host "`nTest complete!" -ForegroundColor Green
Write-Host "Output file: simple_materials_output.blend" -ForegroundColor Yellow
