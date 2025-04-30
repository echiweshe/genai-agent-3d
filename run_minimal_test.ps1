# PowerShell script to run the minimal SVG to 3D converter
# This version is designed for maximum compatibility with Blender 4.2

function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Read the Blender path from .env file directly
$envPath = ".env"
$blenderPath = $null

if (Test-Path $envPath) {
    $content = Get-Content $envPath
    foreach ($line in $content) {
        if ($line -match "BLENDER_PATH=(.*)") {
            $blenderPath = $matches[1].Trim('"').Trim("'")
            Write-ColorMessage "Found Blender path in .env: $blenderPath" "Green"
        }
    }
}

# If the path is not found or valid, try to find Blender in standard locations
if (-not $blenderPath -or -not (Test-Path $blenderPath)) {
    Write-ColorMessage "Blender path not found in .env file or invalid, trying to find Blender..." "Yellow"
    
    # Try common Blender paths
    $defaultPaths = @(
        "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.3\blender.exe"
    )
    
    foreach ($path in $defaultPaths) {
        if (Test-Path $path) {
            $blenderPath = $path
            Write-ColorMessage "Found Blender at: $blenderPath" "Green"
            break
        }
    }
}

if (-not $blenderPath -or -not (Test-Path $blenderPath)) {
    Write-ColorMessage "Error: Blender not found. Please set BLENDER_PATH in your .env file." "Red"
    exit 1
}

# Create simple test SVG
$testDir = "./outputs/minimal_test"
if (-not (Test-Path $testDir)) {
    New-Item -ItemType Directory -Path $testDir -Force | Out-Null
}

$svgPath = "$testDir/simple_test.svg"
$outputPath = "$testDir/simple_test.blend"

# Create a test SVG file
$svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200">
  <rect x="50" y="50" width="100" height="50" fill="#FF5555" />
  <circle cx="200" cy="100" r="40" fill="#5555FF" />
</svg>
"@

Write-ColorMessage "Creating test SVG file at: $svgPath" "Yellow"
$svgContent | Out-File -FilePath $svgPath -Encoding utf8

# Run the minimal SVG to 3D converter
$script = "./genai_agent/scripts/minimal_svg_to_3d.py"

Write-ColorMessage "Running minimal converter with Blender..." "Cyan"
Write-ColorMessage "Script: $script" "Yellow"
Write-ColorMessage "SVG: $svgPath" "Yellow"
Write-ColorMessage "Output: $outputPath" "Yellow"

$command = "& `"$blenderPath`" --background --python `"$script`" -- `"$svgPath`" `"$outputPath`" 0.1 0.01"
Write-ColorMessage "Command: $command" "DarkGray"

try {
    # Execute the command and capture output
    $process = Start-Process -FilePath $blenderPath -ArgumentList "--background", "--python", $script, "--", $svgPath, $outputPath, "0.1", "0.01" -Wait -NoNewWindow -PassThru -RedirectStandardOutput "$testDir/output.log" -RedirectStandardError "$testDir/error.log"
    
    # Display results
    if ($process.ExitCode -eq 0) {
        Write-ColorMessage "✅ Blender process completed successfully (Exit code: 0)" "Green"
    } else {
        Write-ColorMessage "❌ Blender process failed (Exit code: $($process.ExitCode))" "Red"
    }
    
    # Display logs
    if (Test-Path "$testDir/output.log") {
        Write-ColorMessage "`nOutput log:" "Cyan"
        Get-Content "$testDir/output.log" | ForEach-Object {
            if ($_ -match "\[MINIMAL\]") {
                Write-ColorMessage $_ "Green"
            } elseif ($_ -match "error|exception|failed" -and $_ -notmatch "TBBmalloc") {
                Write-ColorMessage $_ "Red"
            } else {
                Write-ColorMessage $_ "Gray"
            }
        }
    }
    
    if (Test-Path "$testDir/error.log" -and (Get-Item "$testDir/error.log").Length -gt 0) {
        Write-ColorMessage "`nError log:" "Red"
        Get-Content "$testDir/error.log" | ForEach-Object { Write-ColorMessage $_ "Red" }
    }
    
    # Check if output file exists
    if (Test-Path $outputPath) {
        Write-ColorMessage "`n✅ 3D model created successfully: $outputPath" "Green"
    } else {
        Write-ColorMessage "`n❌ Failed to create 3D model: $outputPath" "Red"
    }
    
} catch {
    Write-ColorMessage "Error executing Blender: $_" "Red"
}

Write-ColorMessage "`nAll test files are in: $testDir" "Yellow"
