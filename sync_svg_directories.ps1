# PowerShell script to synchronize SVG directories
# Run this script when you need to make sure all SVG directories have the latest files

$ProjectRoot = "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d"
$SVGOutputDir = "$ProjectRoot\output\svg"
$SVGToVideoSVGDir = "$ProjectRoot\output\svg_to_video\svg"
$TestSVGDir = "$ProjectRoot\genai_agent_project\output\svg"

Write-Host "SVG Directory Synchronization" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green
Write-Host ""

# Function to sync directories (copies files from source to target)
function Sync-Directories {
    param (
        [string]$Source,
        [string]$Target,
        [string]$Label
    )
    
    if (-not (Test-Path $Source)) {
        Write-Host "  Source directory does not exist: $Source" -ForegroundColor Red
        return 0
    }
    
    if (-not (Test-Path $Target)) {
        New-Item -ItemType Directory -Path $Target -Force | Out-Null
        Write-Host "  Created target directory: $Target" -ForegroundColor Yellow
    }
    
    $Files = Get-ChildItem -Path $Source -File | Where-Object { $_.Name -ne "README.md" }
    $CopiedCount = 0
    
    foreach ($File in $Files) {
        $TargetPath = Join-Path $Target $File.Name
        if (-not (Test-Path $TargetPath) -or 
            (Get-Item $TargetPath).LastWriteTime -lt $File.LastWriteTime) {
            Copy-Item -Path $File.FullName -Destination $TargetPath -Force
            $CopiedCount++
        }
    }
    
    Write-Host "  Copied $CopiedCount files to $Label" -ForegroundColor Green
    return $CopiedCount
}

# Consolidate files from all directories to main SVG directory
Write-Host "Consolidating files to main SVG directory..." -ForegroundColor Cyan
$ConsolidatedCount = 0

# Copy from SVG to Video directory to main SVG directory
$ConsolidatedCount += Sync-Directories -Source $SVGToVideoSVGDir -Target $SVGOutputDir -Label "main SVG directory (from SVG to Video)"

# Copy from Test directory to main SVG directory
$ConsolidatedCount += Sync-Directories -Source $TestSVGDir -Target $SVGOutputDir -Label "main SVG directory (from Test)"

Write-Host "  Consolidated $ConsolidatedCount files to main SVG directory" -ForegroundColor Green

# Sync from main SVG directory to other directories
Write-Host "Syncing from main SVG directory to other directories..." -ForegroundColor Cyan

# Copy from main SVG directory to SVG to Video directory
Sync-Directories -Source $SVGOutputDir -Target $SVGToVideoSVGDir -Label "SVG to Video directory"

# Copy from main SVG directory to Test directory
Sync-Directories -Source $SVGOutputDir -Target $TestSVGDir -Label "Test directory"

Write-Host "SVG directory synchronization complete!" -ForegroundColor Green
