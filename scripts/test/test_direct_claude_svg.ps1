# PowerShell script to run the direct Claude SVG generator

Write-Host "Direct Claude SVG Generator" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup_svg_to_video.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment and run the script
& .\venv\Scripts\Activate.ps1
python direct_claude_svg.py

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
