# PowerShell script to fix SVG file paths in the GenAI Agent 3D project
# This script finds all Python files that reference the old SVG paths and updates them

# Define paths
$ProjectRoot = "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d"
$OldWebUIPath = "output\svg_to_video\svg"
$OldTestPath = "genai_agent_project\output\svg"
$ConsolidatedPath = "output\svg"

# Create a backup timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $ProjectRoot "backups\$Timestamp"

Write-Host "SVG Path Fixer for GenAI Agent 3D" -ForegroundColor Green
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
    
    # Patterns to look for - make sure to escape backslashes for regex
    $Pattern1 = "output[\\\/]svg_to_video[\\\/]svg"
    $Pattern2 = "genai_agent_project[\\\/]output[\\\/]svg"
    
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
    
    # Check if file contains references to the SVG output paths
    if ($Content -match "output[\\\/]svg_to_video[\\\/]svg" -or $Content -match "genai_agent_project[\\\/]output[\\\/]svg") {
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

# Create the consolidated SVG directory if it doesn't exist
if (-not (Test-Path "$ProjectRoot\$ConsolidatedPath")) {
    Write-Host "Creating consolidated SVG directory... " -NoNewline
    New-Item -ItemType Directory -Path "$ProjectRoot\$ConsolidatedPath" -Force | Out-Null
    Write-Host "Done." -ForegroundColor Green
}

# Check if symlinks need to be created and create them
Write-Host "Checking symlinks..."

# Test output path symlink
$TestOutputDir = "$ProjectRoot\$OldTestPath"
if (Test-Path $TestOutputDir) {
    if ((Get-Item $TestOutputDir).LinkType -ne "SymbolicLink") {
        Write-Host "  Creating symlink for test output path... " -NoNewline
        
        # Backup the directory if it exists and isn't a symlink
        $BackupPath = "$TestOutputDir.backup_$Timestamp"
        Copy-Item -Path $TestOutputDir -Destination $BackupPath -Recurse -Force
        Remove-Item -Path $TestOutputDir -Recurse -Force
        
        # Create the parent directory if it doesn't exist
        $ParentDir = Split-Path $TestOutputDir -Parent
        if (-not (Test-Path $ParentDir)) {
            New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
        }
        
        # Create symlink using cmd.exe since PowerShell requires admin privileges
        cmd /c mklink /d "$TestOutputDir" "$ProjectRoot\$ConsolidatedPath"
        Write-Host "Done." -ForegroundColor Green
    } else {
        Write-Host "  Test output path is already a symlink." -ForegroundColor Gray
    }
} else {
    Write-Host "  Creating symlink for test output path... " -NoNewline
    
    # Create the parent directory if it doesn't exist
    $ParentDir = Split-Path $TestOutputDir -Parent
    if (-not (Test-Path $ParentDir)) {
        New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
    }
    
    # Create symlink using cmd.exe since PowerShell requires admin privileges
    cmd /c mklink /d "$TestOutputDir" "$ProjectRoot\$ConsolidatedPath"
    Write-Host "Done." -ForegroundColor Green
}

# Web UI output path symlink
$WebUIOutputDir = "$ProjectRoot\$OldWebUIPath"
if (Test-Path $WebUIOutputDir) {
    if ((Get-Item $WebUIOutputDir).LinkType -ne "SymbolicLink") {
        Write-Host "  Creating symlink for Web UI output path... " -NoNewline
        
        # Backup the directory if it exists and isn't a symlink
        $BackupPath = "$WebUIOutputDir.backup_$Timestamp"
        Copy-Item -Path $WebUIOutputDir -Destination $BackupPath -Recurse -Force
        Remove-Item -Path $WebUIOutputDir -Recurse -Force
        
        # Create the parent directory if it doesn't exist
        $ParentDir = Split-Path $WebUIOutputDir -Parent
        if (-not (Test-Path $ParentDir)) {
            New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
        }
        
        # Create symlink using cmd.exe since PowerShell requires admin privileges
        cmd /c mklink /d "$WebUIOutputDir" "$ProjectRoot\$ConsolidatedPath"
        Write-Host "Done." -ForegroundColor Green
    } else {
        Write-Host "  Web UI output path is already a symlink." -ForegroundColor Gray
    }
} else {
    Write-Host "  Creating symlink for Web UI output path... " -NoNewline
    
    # Create the parent directory if it doesn't exist
    $ParentDir = Split-Path $WebUIOutputDir -Parent
    if (-not (Test-Path $ParentDir)) {
        New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
    }
    
    # Create symlink using cmd.exe since PowerShell requires admin privileges
    cmd /c mklink /d "$WebUIOutputDir" "$ProjectRoot\$ConsolidatedPath"
    Write-Host "Done." -ForegroundColor Green
}

# Copy files from backup directories to consolidated directory if they don't exist
$BackupDirs = @(
    (Join-Path $ProjectRoot "$OldWebUIPath.backup_$Timestamp"),
    (Join-Path $ProjectRoot "$OldTestPath.backup_$Timestamp")
)

foreach ($BackupDir in $BackupDirs) {
    if (Test-Path $BackupDir) {
        Write-Host "Copying files from backup directory to consolidated directory... " -NoNewline
        $Files = Get-ChildItem -Path $BackupDir -File
        $CopiedCount = 0
        
        foreach ($File in $Files) {
            $TargetPath = Join-Path "$ProjectRoot\$ConsolidatedPath" $File.Name
            if (-not (Test-Path $TargetPath)) {
                Copy-Item -Path $File.FullName -Destination $TargetPath -Force
                $CopiedCount++
            }
        }
        
        Write-Host "Copied $CopiedCount files." -ForegroundColor Green
    }
}

# Check for duplicate SVG pipeline code directory
$MainCodeDir = "$ProjectRoot\genai_agent\svg_to_video"
if (Test-Path $MainCodeDir) {
    Write-Host "Found duplicate SVG pipeline code directory."
    Write-Host "  Backing up and removing: $MainCodeDir"
    
    $BackupPath = "$MainCodeDir.backup_$Timestamp"
    Copy-Item -Path $MainCodeDir -Destination $BackupPath -Recurse -Force
    Remove-Item -Path $MainCodeDir -Recurse -Force
    
    Write-Host "  Duplicate code directory removed." -ForegroundColor Green
} else {
    Write-Host "No duplicate SVG pipeline code directory found." -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "SVG Path Fix Summary:" -ForegroundColor Green
Write-Host "--------------------" -ForegroundColor Green
Write-Host "Files scanned: $($PythonFiles.Count + $JsFiles.Count)"
Write-Host "Files updated: $UpdatedFiles"
Write-Host "Backup created at: $BackupDir"
Write-Host "Consolidated SVG directory: $ProjectRoot\$ConsolidatedPath"
Write-Host ""
Write-Host "You should now restart your development environment to ensure changes take effect." -ForegroundColor Yellow
Write-Host "If you encounter any issues, you can restore files from the backup directory." -ForegroundColor Yellow
Write-Host ""
