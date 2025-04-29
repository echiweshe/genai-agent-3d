# PowerShell script to test the SVG Generator component

Write-Host "Testing SVG Generator Component" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup_svg_to_video.ps1 first." -ForegroundColor Red
    exit 1
}

# Check for master .env file
if (Test-Path "genai_agent_project\.env") {
    Write-Host "Using master .env file from genai_agent_project directory." -ForegroundColor Green
} else {
    Write-Host "Warning: Master .env file not found at genai_agent_project\.env" -ForegroundColor Yellow
    Write-Host "Checking for local .env file..." -ForegroundColor Yellow
    
    if (Test-Path ".env") {
        Write-Host "Using local .env file." -ForegroundColor Green
    } else {
        Write-Host "No .env file found. API keys may not be available." -ForegroundColor Red
        Write-Host "The test may fail if no API keys are available." -ForegroundColor Red
    }
}

# Activate virtual environment and run the test
& .\venv\Scripts\Activate.ps1
python test_svg_generator.py

Write-Host ""
Write-Host "Test completed." -ForegroundColor Green
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
