# PowerShell script to update the required packages

Write-Host "Updating packages for SVG to Video Pipeline" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup_svg_to_video.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment and update packages
& .\venv\Scripts\Activate.ps1

Write-Host "Updating langchain and anthropic packages..." -ForegroundColor Cyan
pip install -U langchain==0.0.267 anthropic==0.3.11

if ($LASTEXITCODE -eq 0) {
    Write-Host "Packages updated successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to update packages." -ForegroundColor Red
}

Write-Host ""
Write-Host "Installing additional required packages..." -ForegroundColor Cyan
pip install -U python-dotenv requests fastapi uvicorn

if ($LASTEXITCODE -eq 0) {
    Write-Host "Additional packages installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to install additional packages." -ForegroundColor Red
}

Write-Host ""
Write-Host "Package update completed." -ForegroundColor Green
Write-Host "Now try running the simplified server: .\run_simple_dev.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
