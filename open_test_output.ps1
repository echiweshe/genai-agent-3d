# PowerShell script to open the test output in Blender

# Check for different versions of Blender
$blenderPaths = @(
    "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe", 
    "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    "C:\Program Files\Blender Foundation\Blender\blender.exe"
)

$blender = $null
foreach ($path in $blenderPaths) {
    if (Test-Path $path) {
        $blender = $path
        break
    }
}

if ($null -eq $blender) {
    Write-Host "Blender not found in standard locations. Please enter the path to Blender:" -ForegroundColor Yellow
    $blender = Read-Host
    if (-not (Test-Path $blender)) {
        Write-Host "Invalid Blender path. Exiting." -ForegroundColor Red
        exit 1
    }
}

# Look for test output file in several possible locations
$testOutputLocations = @(
    ".\test_output.blend",
    ".\tests\svg_to_video\svg_to_3d\test_output.blend",
    "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\tests\svg_to_video\svg_to_3d\test_output.blend"
)

$outputFile = $null
foreach ($location in $testOutputLocations) {
    if (Test-Path $location) {
        $outputFile = $location
        break
    }
}

# If not found, search output directories for recent blend files
if ($null -eq $outputFile) {
    Write-Host "Test output not found in standard locations. Searching for recent Blender files..." -ForegroundColor Yellow
    
    $outputDirs = @(
        ".\output\models",
        ".\output\svg_to_video\models",
        "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\models",
        "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg_to_video\models"
    )
    
    $recentFiles = @()
    foreach ($dir in $outputDirs) {
        if (Test-Path $dir) {
            $recentFiles += Get-ChildItem -Path $dir -Filter "*.blend" | Sort-Object LastWriteTime -Descending
        }
    }
    
    if ($recentFiles.Count -gt 0) {
        $outputFile = $recentFiles[0].FullName
        Write-Host "Found recent Blender file: $outputFile" -ForegroundColor Green
    } else {
        # If still not found, look for obj files
        $recentFiles = @()
        foreach ($dir in $outputDirs) {
            if (Test-Path $dir) {
                $recentFiles += Get-ChildItem -Path $dir -Filter "*.obj" | Sort-Object LastWriteTime -Descending
            }
        }
        
        if ($recentFiles.Count -gt 0) {
            $outputFile = $recentFiles[0].FullName
            Write-Host "Found recent OBJ file: $outputFile" -ForegroundColor Green
        }
    }
}

if ($null -eq $outputFile) {
    Write-Host "No output file found. Please run the test first to generate the output file." -ForegroundColor Red
    exit 1
}

Write-Host "Using Blender: $blender" -ForegroundColor Cyan
Write-Host "Opening file: $outputFile" -ForegroundColor Cyan

# Open the file in Blender
& $blender $outputFile

Write-Host "Blender closed." -ForegroundColor Green
