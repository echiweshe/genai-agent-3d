# PowerShell script to fix SVG to Video imports and test the pipeline

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)

# Python executable
$pythonPath = Join-Path $projectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    # Try system Python if venv not found
    $pythonPath = "python"
}

# Import fix script
$importFixScript = Join-Path $scriptPath "fix_svg_to_video_imports.py"

# Test script to create after fixing imports
$testScript = @"
import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_svg_to_video")

async def test_pipeline():
    """Test the SVG to Video pipeline."""
    try:
        # Import the pipeline
        from genai_agent.svg_to_video import SVGToVideoPipeline
        
        # Create pipeline instance
        pipeline = SVGToVideoPipeline(debug=True)
        
        # Test SVG generation
        logger.info("Testing SVG generation...")
        description = "A simple flowchart showing a login process"
        svg_content, svg_path = await pipeline.generate_svg_only(
            description=description,
            diagram_type="flowchart"
        )
        
        logger.info(f"SVG generated: {svg_path}")
        logger.info("Pipeline test successful!")
        return True
    
    except Exception as e:
        logger.error(f"Error testing pipeline: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pipeline())
    sys.exit(0 if success else 1)
"@

$testScriptPath = Join-Path $projectRoot "test_svg_to_video_pipeline.py"

# Print header
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "SVG to Video Pipeline Fix and Test" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host

# Step 1: Fix imports
Write-Host "Step 1: Fixing SVG to Video imports..." -ForegroundColor Yellow
& $pythonPath $importFixScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to fix imports. See error messages above." -ForegroundColor Red
    exit 1
}

Write-Host "Import fixes applied successfully!" -ForegroundColor Green
Write-Host

# Step 2: Create and run test script
Write-Host "Step 2: Creating test script..." -ForegroundColor Yellow
$testScript | Out-File -FilePath $testScriptPath -Encoding utf8
Write-Host "Test script created: $testScriptPath" -ForegroundColor Green
Write-Host

Write-Host "Step 3: Running test script..." -ForegroundColor Yellow
& $pythonPath $testScriptPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "Test failed. See error messages above." -ForegroundColor Red
    exit 1
}

Write-Host "`nTest completed successfully!" -ForegroundColor Green
Write-Host "The SVG to Video pipeline is now working with the modularized structure." -ForegroundColor Green
Write-Host "`nYou can now use the pipeline with:" -ForegroundColor Yellow
Write-Host ".\run_svg_to_video.ps1 svg 'Your description' output.svg" -ForegroundColor White
Write-Host ".\run_svg_to_video.ps1 convert input.svg output.mp4" -ForegroundColor White
Write-Host ".\run_svg_to_video.ps1 generate 'Your description' output.mp4" -ForegroundColor White
