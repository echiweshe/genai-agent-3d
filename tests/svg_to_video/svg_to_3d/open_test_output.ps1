# PowerShell script to open the test output in Blender

$blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
$outputFile = "test_output.blend"

if (-not (Test-Path $blender)) {
    Write-Host "Blender not found at: $blender" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $outputFile)) {
    Write-Host "Output file not found: $outputFile" -ForegroundColor Red
    Write-Host "Please run the test first to generate the output file." -ForegroundColor Yellow
    exit 1
}

Write-Host "Opening test output in Blender..." -ForegroundColor Cyan
& $blender $outputFile

Write-Host "Blender closed." -ForegroundColor Green
