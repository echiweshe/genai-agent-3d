# PowerShell script to fix SVG file paths in the GenAI Agent 3D project
# This script finds all Python files that reference the old SVG paths and updates them
# This version does NOT require administrator privileges as it uses file copies instead of symlinks

# Define paths
$ProjectRoot = "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d"
$OldWebUIPath = "output\svg_to_video\svg"
$OldTestPath = "genai_agent_project\output\svg"
$ConsolidatedPath = "output\svg"

# Create a backup timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $ProjectRoot "backups\$Timestamp"

Write-Host "SVG Path Fixer for GenAI Agent 3D (No Symlinks Version)" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Create backup directory
Write-Host "Creating backup directory... " -NoNewline
if (-not (Test-Path "$ProjectRoot\backups")) {
    New-Item -ItemType Directory -Path "$ProjectRoot\backups" -Force | Out-Null
}
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
Write-Host "Done." -ForegroundColor Green

# Function to backup a file before modifying it
function Backup-File {
    param (
        [string]$FilePath
    )
    
    $FileName = Split-Path $FilePath -Leaf
    $BackupPath = Join-Path $BackupDir $FileName
    
    # Create subdirectories in backup if needed
    $RelativePath = $FilePath.Substring($ProjectRoot.Length + 1)
    $BackupPath = Join-Path $BackupDir $RelativePath
    $BackupDir = Split-Path $BackupPath -Parent
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    Copy-Item -Path $FilePath -Destination $BackupPath -Force
    return $BackupPath
}

# Function to update paths in a file
function Update-Paths {
    param (
        [string]$FilePath
    )
    
    $Content = Get-Content -Path $FilePath -Raw
    $OriginalContent = $Content
    
    # Simplified patterns to avoid regex escape issues
    $Pattern1 = "output[/\\]svg_to_video[/\\]svg"
    $Pattern2 = "genai_agent_project[/\\]output[/\\]svg"
    
    # Replace patterns with consolidated path
    $NewContent = $Content -replace $Pattern1, $ConsolidatedPath
    $NewContent = $NewContent -replace $Pattern2, $ConsolidatedPath
    
    # Only update file if content changed
    if ($NewContent -ne $OriginalContent) {
        Backup-File -FilePath $FilePath | Out-Null
        Set-Content -Path $FilePath -Value $NewContent
        return $true
    }
    
    return $false
}

# Find all Python files in the project
Write-Host "Searching for Python files... " -NoNewline
$PythonFiles = Get-ChildItem -Path $ProjectRoot -Filter "*.py" -Recurse -File | 
               Where-Object { $_.FullName -notlike "*\backups\*" -and $_.FullName -notlike "*\venv\*" }
Write-Host "Found $($PythonFiles.Count) files." -ForegroundColor Green

# Check for SVG output path references and update them
Write-Host "Scanning files for SVG path references..."
$UpdatedFiles = 0

foreach ($File in $PythonFiles) {
    $Content = Get-Content -Path $File.FullName -Raw
    
    # Check if file contains references to the SVG output paths - using simplified pattern
    if ($Content -match "output[/\\]svg_to_video[/\\]svg" -or $Content -match "genai_agent_project[/\\]output[/\\]svg") {
        Write-Host "  Found SVG path references in: $($File.FullName)" -ForegroundColor Yellow
        
        $Updated = Update-Paths -FilePath $File.FullName
        if ($Updated) {
            Write-Host "    Updated file: $($File.FullName)" -ForegroundColor Green
            $UpdatedFiles++
        } else {
            Write-Host "    No changes needed in: $($File.FullName)" -ForegroundColor Gray
        }
    }
}

# Find and update JavaScript files in the web UI
$JsFiles = Get-ChildItem -Path "$ProjectRoot\genai_agent_project\web\frontend" -Filter "*.js" -Recurse -File | 
           Where-Object { $_.FullName -notlike "*\node_modules\*" }

foreach ($File in $JsFiles) {
    $Content = Get-Content -Path $File.FullName -Raw
    
    # Check if file contains references to the SVG output paths
    if ($Content -match "output/svg_to_video/svg" -or $Content -match "genai_agent_project/output/svg") {
        Write-Host "  Found SVG path references in JS file: $($File.FullName)" -ForegroundColor Yellow
        
        $Updated = Update-Paths -FilePath $File.FullName
        if ($Updated) {
            Write-Host "    Updated file: $($File.FullName)" -ForegroundColor Green
            $UpdatedFiles++
        } else {
            Write-Host "    No changes needed in: $($File.FullName)" -ForegroundColor Gray
        }
    }
}

# Create the consolidated SVG directory if it doesn't exist, or if it exists as a file
if (Test-Path "$ProjectRoot\$ConsolidatedPath") {
    if ((Get-Item "$ProjectRoot\$ConsolidatedPath").PSIsContainer -eq $false) {
        Write-Host "Consolidated path exists as a file! Backing up and recreating as directory..." -ForegroundColor Red
        $BackupPath = "$ProjectRoot\$ConsolidatedPath.backup_$Timestamp"
        Move-Item -Path "$ProjectRoot\$ConsolidatedPath" -Destination $BackupPath -Force
        New-Item -ItemType Directory -Path "$ProjectRoot\$ConsolidatedPath" -Force | Out-Null
        Write-Host "Done." -ForegroundColor Green
    } else {
        Write-Host "Consolidated SVG directory already exists." -ForegroundColor Green
    }
} else {
    Write-Host "Creating consolidated SVG directory... " -NoNewline
    New-Item -ItemType Directory -Path "$ProjectRoot\$ConsolidatedPath" -Force | Out-Null
    Write-Host "Done." -ForegroundColor Green
}

# Setup file synchronization instead of symlinks
Write-Host "Setting up file synchronization (instead of symlinks)..."

# Create the old SVG directories if they don't exist
if (-not (Test-Path "$ProjectRoot\$OldWebUIPath")) {
    Write-Host "  Creating Web UI SVG directory... " -NoNewline
    New-Item -ItemType Directory -Path "$ProjectRoot\$OldWebUIPath" -Force | Out-Null
    Write-Host "Done." -ForegroundColor Green
} else {
    Write-Host "  Web UI SVG directory already exists." -ForegroundColor Gray
}

if (-not (Test-Path "$ProjectRoot\$OldTestPath")) {
    Write-Host "  Creating Test SVG directory... " -NoNewline
    New-Item -ItemType Directory -Path "$ProjectRoot\$OldTestPath" -Force | Out-Null
    Write-Host "Done." -ForegroundColor Green
} else {
    Write-Host "  Test SVG directory already exists." -ForegroundColor Gray
}

# Synchronize files between the directories
Write-Host "Synchronizing files between directories..."

# Copy files from consolidated to old directories
$ConsolidatedFiles = Get-ChildItem -Path "$ProjectRoot\$ConsolidatedPath" -File
$CopiedToWebUI = 0
$CopiedToTest = 0

foreach ($File in $ConsolidatedFiles) {
    # Copy to Web UI path
    $TargetPath = Join-Path "$ProjectRoot\$OldWebUIPath" $File.Name
    if (-not (Test-Path $TargetPath) -or 
        (Get-Item $TargetPath).LastWriteTime -lt $File.LastWriteTime) {
        Copy-Item -Path $File.FullName -Destination $TargetPath -Force
        $CopiedToWebUI++
    }
    
    # Copy to Test path
    $TargetPath = Join-Path "$ProjectRoot\$OldTestPath" $File.Name
    if (-not (Test-Path $TargetPath) -or 
        (Get-Item $TargetPath).LastWriteTime -lt $File.LastWriteTime) {
        Copy-Item -Path $File.FullName -Destination $TargetPath -Force
        $CopiedToTest++
    }
}

Write-Host "  Copied $CopiedToWebUI files to Web UI directory" -ForegroundColor Green
Write-Host "  Copied $CopiedToTest files to Test directory" -ForegroundColor Green

# Copy files from old directories to consolidated directory
$WebUIFiles = Get-ChildItem -Path "$ProjectRoot\$OldWebUIPath" -File
$TestFiles = Get-ChildItem -Path "$ProjectRoot\$OldTestPath" -File
$CopiedFromWebUI = 0
$CopiedFromTest = 0

foreach ($File in $WebUIFiles) {
    $TargetPath = Join-Path "$ProjectRoot\$ConsolidatedPath" $File.Name
    if (-not (Test-Path $TargetPath) -or 
        (Get-Item $TargetPath).LastWriteTime -lt $File.LastWriteTime) {
        Copy-Item -Path $File.FullName -Destination $TargetPath -Force
        $CopiedFromWebUI++
    }
}

foreach ($File in $TestFiles) {
    $TargetPath = Join-Path "$ProjectRoot\$ConsolidatedPath" $File.Name
    if (-not (Test-Path $TargetPath) -or 
        (Get-Item $TargetPath).LastWriteTime -lt $File.LastWriteTime) {
        Copy-Item -Path $File.FullName -Destination $TargetPath -Force
        $CopiedFromTest++
    }
}

Write-Host "  Copied $CopiedFromWebUI files from Web UI directory" -ForegroundColor Green
Write-Host "  Copied $CopiedFromTest files from Test directory" -ForegroundColor Green

# Create a sync script that can be run periodically
$SyncScriptPath = "$ProjectRoot\sync_svg_directories.ps1"
$SyncScriptContent = @"
# PowerShell script to synchronize SVG directories
# Run this script when you need to make sure all SVG directories have the latest files

`$ProjectRoot = "$ProjectRoot"
`$ConsolidatedPath = "`$ProjectRoot\$ConsolidatedPath"
`$WebUIPath = "`$ProjectRoot\$OldWebUIPath"
`$TestPath = "`$ProjectRoot\$OldTestPath"

Write-Host "Synchronizing SVG Directories..."
Write-Host "================================"

# Function to sync two directories (source to target)
function Sync-Directories {
    param (
        [string]`$Source,
        [string]`$Target,
        [string]`$Label
    )
    
    `$Files = Get-ChildItem -Path `$Source -File
    `$CopiedCount = 0
    
    foreach (`$File in `$Files) {
        `$TargetPath = Join-Path `$Target `$File.Name
        if (-not (Test-Path `$TargetPath) -or 
            (Get-Item `$TargetPath).LastWriteTime -lt `$File.LastWriteTime) {
            Copy-Item -Path `$File.FullName -Destination `$TargetPath -Force
            `$CopiedCount++
        }
    }
    
    Write-Host "  Copied `$CopiedCount files to `$Label"
}

# Sync from consolidated to others
Sync-Directories -Source `$ConsolidatedPath -Target `$WebUIPath -Label "Web UI directory"
Sync-Directories -Source `$ConsolidatedPath -Target `$