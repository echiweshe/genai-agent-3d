# PowerShell script to run fixed stroke and fill test

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Fixed Stroke and Fill Test..." -ForegroundColor Cyan
Write-Host "Using Blender: $blender" -ForegroundColor Green

# Run with GUI to see materials
Write-Host "Running with GUI..." -ForegroundColor Cyan
& $blender --python test_stroke_fill_fixed.py

Write-Host "`nTest complete!" -ForegroundColor Green
Write-Host "Output file: stroke_fill_output_fixed.blend" -ForegroundColor Yellow

Write-Host "`nThis test demonstrates:" -ForegroundColor Cyan
Write-Host "Row 1: Basic Fill and Stroke" -ForegroundColor White
Write-Host "  - Red rectangle with fill only" -ForegroundColor White
Write-Host "  - Green outline with stroke only" -ForegroundColor White
Write-Host "  - Blue rectangle with yellow stroke" -ForegroundColor White

Write-Host "`nRow 2: Transparency" -ForegroundColor White
Write-Host "  - Semi-transparent fill (50%)" -ForegroundColor White
Write-Host "  - Semi-transparent stroke (50%)" -ForegroundColor White
Write-Host "  - Different opacities for fill (70%) and stroke (30%)" -ForegroundColor White

Write-Host "`nRow 3: Complex Shapes" -ForegroundColor White
Write-Host "  - Triangle with fill and stroke" -ForegroundColor White
Write-Host "  - Curved path with stroke only" -ForegroundColor White
Write-Host "  - Star shape with fill and stroke" -ForegroundColor White
