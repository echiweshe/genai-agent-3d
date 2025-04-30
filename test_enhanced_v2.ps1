# PowerShell script to test the enhanced SVG to 3D v2 converter
# Save as test_enhanced_v2.ps1

function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Read Blender path directly from .env file
$blenderPath = $null
if (Test-Path ".env") {
    $content = Get-Content ".env"
    foreach ($line in $content) {
        if ($line -match "BLENDER_PATH=(.*)") {
            $blenderPath = $matches[1].Trim('"').Trim("'")
            break
        }
    }
}

# If not found, use the path we discovered earlier
if (-not $blenderPath -or -not (Test-Path $blenderPath)) {
    $blenderPath = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
}

Write-ColorMessage "Using Blender at: $blenderPath" "Green"

# Create test directory
$testDir = "./outputs/enhanced_test_v2"
if (-not (Test-Path $testDir)) {
    New-Item -ItemType Directory -Path $testDir -Force | Out-Null
}

# Run the enhanced script on each of our test SVGs
$svgFiles = @(
    "./outputs/minimal_test/simple_test.svg", 
    "./outputs/enhanced_svg_test/simple_test.svg",
    "./outputs/enhanced_svg_test/complex_test.svg"
)

foreach ($svgPath in $svgFiles) {
    if (Test-Path $svgPath) {
        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($svgPath)
        $outputPath = "$testDir/$fileName.blend"
        
        Write-ColorMessage "`nTesting with SVG: $svgPath" "Cyan"
        Write-ColorMessage "Output to: $outputPath" "Cyan"
        
        $script = "./genai_agent/scripts/enhanced_svg_to_3d_v2.py"
        
        # Run the command
        $process = Start-Process -FilePath $blenderPath -ArgumentList "--background", "--python", $script, "--", $svgPath, $outputPath, "0.1", "0.01" -Wait -NoNewWindow -PassThru -RedirectStandardOutput "$testDir/$fileName.log" -RedirectStandardError "$testDir/$fileName.err"
        
        if ($process.ExitCode -eq 0) {
            Write-ColorMessage "✅ Successfully converted $fileName (Exit code: 0)" "Green"
        } else {
            Write-ColorMessage "❌ Failed to convert $fileName (Exit code: $($process.ExitCode))" "Red"
        }
        
        # Show log tail
        if (Test-Path "$testDir/$fileName.log") {
            Write-ColorMessage "`nLast few log lines:" "Yellow"
            Get-Content "$testDir/$fileName.log" -Tail 10 | ForEach-Object {
                if ($_ -match "error|exception|failed" -and $_ -notmatch "TBBmalloc") {
                    Write-ColorMessage $_ "Red"
                } elseif ($_ -match "\[SVG2-3D\]") {
                    Write-ColorMessage $_ "Green"
                } else {
                    Write-ColorMessage $_ "Gray"
                }
            }
        }
    } else {
        Write-ColorMessage "SVG file not found: $svgPath" "Red"
    }
}

# Check if any files were successfully created
$createdFiles = Get-ChildItem "$testDir/*.blend" -ErrorAction SilentlyContinue
if ($createdFiles) {
    Write-ColorMessage "`n✅ Created Blender files:" "Green"
    foreach ($file in $createdFiles) {
        Write-ColorMessage "  - $($file.Name)" "Green"
    }
} else {
    Write-ColorMessage "`n❌ No Blender files were created" "Red"
}

Write-ColorMessage "`nAll tests completed! Results are in: $testDir" "Yellow"
