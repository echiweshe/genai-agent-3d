# PowerShell script to fix Claude integration issues

Write-Host "Fixing Claude API Integration" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup_svg_to_video.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

Write-Host "Uninstalling current anthropic and langchain packages..." -ForegroundColor Yellow
pip uninstall -y anthropic langchain

Write-Host "Installing specific versions known to work together..." -ForegroundColor Cyan
pip install anthropic==0.3.6 langchain==0.0.267

Write-Host "Installing direct anthropic client..." -ForegroundColor Cyan
pip install anthropic -U

Write-Host "Creating test script to verify Claude API integration..." -ForegroundColor Cyan

$testScriptContent = @"
# Test script to verify Claude API integration
import os
import asyncio
from anthropic import Anthropic
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "genai_agent_project" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from {env_path}")

# Get Claude API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not set in environment")
    sys.exit(1)

print(f"API key found: {api_key[:8]}...{api_key[-4:]}")

# Test direct API access
def test_direct_api():
    print("Testing direct Anthropic API access...")
    try:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Create a simple SVG circle."}]
        )
        print("API call successful!")
        print(f"Response: {message.content[0].text[:200]}...")
        return True
    except Exception as e:
        print(f"Error with direct API: {str(e)}")
        return False

# Run the tests
success = test_direct_api()

if success:
    print("\nClaude API is working correctly!")
    print("You should now be able to use the SVG generator with Claude.")
else:
    print("\nClaude API is still not working.")
    print("Please check your API key and environment setup.")
"@

Set-Content -Path "test_claude_api.py" -Value $testScriptContent

Write-Host "Running test script..." -ForegroundColor Cyan
python test_claude_api.py

Write-Host ""
Write-Host "Fix completed. If the test was successful, Claude should now be available as a provider." -ForegroundColor Green
Write-Host "Try running the application again: .\run_simple_dev.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
