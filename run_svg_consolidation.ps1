Write-Host "SVG Pipeline Consolidation" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Verifying SVG Pipeline..." -ForegroundColor Cyan
python svg_pipeline_verification.py
Write-Host ""

Write-Host "Step 2: Consolidating SVG Pipeline..." -ForegroundColor Cyan
python consolidate_svg_pipeline.py
Write-Host ""

Write-Host "Consolidation complete! Please check the logs for details." -ForegroundColor Green
Write-Host "If any issues were encountered, you can restore from the backups." -ForegroundColor Yellow
Write-Host ""

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
