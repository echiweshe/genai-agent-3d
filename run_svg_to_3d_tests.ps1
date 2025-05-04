# PowerShell script to run SVG to 3D tests
# This script helps you run the tests with Blender

$ErrorActionPreference = "Stop"

Write-Host "SVG to 3D Converter Test Runner" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Navigate to the test directory
$testDir = "tests\svg_to_video\svg_to_3d"
if (-not (Test-Path $testDir)) {
    Write-Host "Error: Test directory not found!" -ForegroundColor Red
    exit 1
}

Push-Location $testDir

try {
    Write-Host "`nWhat would you like to do?" -ForegroundColor Yellow
    Write-Host "1. Run quick test" -ForegroundColor White
    Write-Host "2. Run full test suite" -ForegroundColor White
    Write-Host "3. Run visual test (opens Blender UI)" -ForegroundColor White
    Write-Host "4. Run debug test" -ForegroundColor White
    Write-Host "5. Check imports only" -ForegroundColor White
    
    $choice = Read-Host "`nEnter your choice (1-5)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nRunning quick test..." -ForegroundColor Cyan
            python run_quick_test.py
        }
        "2" {
            Write-Host "`nRunning full test suite..." -ForegroundColor Cyan
            python test_suite.py
        }
        "3" {
            Write-Host "`nRunning visual test..." -ForegroundColor Cyan
            python run_tests.py --test visual --no-background
        }
        "4" {
            Write-Host "`nRunning debug test..." -ForegroundColor Cyan
            python run_tests.py --test debug
        }
        "5" {
            Write-Host "`nChecking imports..." -ForegroundColor Cyan
            python check_imports.py
        }
        default {
            Write-Host "Invalid choice!" -ForegroundColor Red
        }
    }
}
finally {
    Pop-Location
}

Write-Host "`nTest complete!" -ForegroundColor Green
