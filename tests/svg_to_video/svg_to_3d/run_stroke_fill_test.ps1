# PowerShell script to run stroke and fill test

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

Write-Host "Running Stroke and Fill Test..." -ForegroundColor Cyan
Write-Host "Using Blender: $blender" -ForegroundColor Green

# Run with GUI to see materials
Write-Host "Running with GUI..." -ForegroundColor Cyan
& $blender --python test_stroke_fill.py

Write-Host "`nTest complete!" -ForegroundColor Green
Write-Host "Output file: stroke_fill_output.blend" -ForegroundColor Yellow
Write-Host "`nThis test demonstrates:" -ForegroundColor Cyan
Write-Host "- Fill-only objects" -ForegroundColor White
Write-Host "- Stroke-only objects" -ForegroundColor White
Write-Host "- Objects with both fill and stroke" -ForegroundColor White
Write-Host "- Semi-transparent fills and strokes" -ForegroundColor White
Write-Host "- Different stroke styles" -ForegroundColor White
