# Wrapper script to test SVG to Video pipeline
# This is a convenience script that redirects to various test implementations

param (
    [string]$TestType = "all"
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$testDir = Join-Path $scriptPath "scripts\test"

switch ($TestType) {
    "blender" {
        & (Join-Path $testDir "test_blender_integration.ps1") @args
    }
    "svg" {
        & (Join-Path $testDir "test_direct_claude_svg.ps1") @args
    }
    "3d" {
        & (Join-Path $testDir "test_enhanced_svg_to_3d.ps1") @args
    }
    "all" {
        Write-Host "Running all SVG to Video tests..." -ForegroundColor Cyan
        & (Join-Path $testDir "test_direct_claude_svg.ps1")
        & (Join-Path $testDir "test_enhanced_svg_to_3d.ps1")
        & (Join-Path $testDir "test_blender_integration.ps1")
    }
    default {
        Write-Host "Unknown test type: $TestType" -ForegroundColor Red
        Write-Host "Available test types: blender, svg, 3d, all" -ForegroundColor Yellow
    }
}
