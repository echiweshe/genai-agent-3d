# PowerShell script to check and fix Claude API key issues

Write-Host "Checking and fixing Claude API key issues" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup_svg_to_video.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment and run the fix
& .\venv\Scripts\Activate.ps1
python fix_claude_key.py

Write-Host ""
Write-Host "After fixing the key, try running: .\run_svg_generator_test.ps1" -ForegroundColor Cyan
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
