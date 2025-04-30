# PowerShell script to run the debug version of SVG to 3D conversion
# Save this as run_debug_test.ps1

function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Function to read environment variables from .env file
function Read-EnvFile {
    param (
        [string]$envPath = ".env"
    )
    
    $envVars = @{}
    
    if (Test-Path $envPath) {
        $content = Get-Content $envPath -ErrorAction Stop
        foreach ($line in $content) {
            if ($line -match '^\s*([^#][^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                # Remove surrounding quotes if present
                if ($value -match '^[''"](.*)[''"]\s*$') {
                    $value = $matches[1]
                }
                $envVars[$name] = $value
            }
        }
    }
    else {
        Write-ColorMessage "Warning: .env file not found at $envPath" "Yellow"
    }
    
    return $envVars
}

# Read the Blender path from .env file directly
$envVars = Read-EnvFile
$blenderPath = $envVars["BLENDER_PATH"]

# If the path is not found or valid, try to find Blender in standard locations
if (-not $blenderPath -or -not (Test-Path $blenderPath)) {
    Write-ColorMessage "Blender path not found in .env file or invalid, trying to find Blender..." "Yellow"
    
    # Try to find Blender in the default installation location
    $defaultPaths = @(
        "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.3\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.2\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.1\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.0\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 2.93\blender.exe"
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

Write-ColorMessage "Using Blender at: $blenderPath" "Green"

# Create simple test SVG
$testDir = "./outputs/debug_test"
if (-not (Test-Path $testDir)) {
    New-Item -ItemType Directory -Path $testDir -Force | Out-Null
}

$svgPath = "$testDir/simple_square.svg"
$outputPath = "$testDir/simple_square.blend"

# Create a very simple SVG with just a rectangle
$svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <rect x="50" y="50" width="100" height="100" fill="red" />
</svg>
"@

Write-ColorMessage "Creating simple test SVG at: $svgPath" "Yellow"
$svgContent | Out-File -FilePath $svgPath -Encoding utf8

# Verify SVG was created
if (-not (Test-Path $svgPath)) {
    Write-ColorMessage "Error: Failed to create test SVG" "Red"
    exit 1
}

# Run debug script with detailed output
Write-ColorMessage "Running debug script with: $svgPath" "Cyan"
$debugScript = "./genai_agent/scripts/enhanced_svg_to_3d_blender_debug.py"

$command = "& `"$blenderPath`" --background --python `"$debugScript`" -- --svg `"$svgPath`" --output `"$outputPath`" --debug"
Write-ColorMessage "Command: $command" "Yellow"

try {
    # Use Start-Process to capture all output
    $tempStdout = "$testDir/stdout.txt"
    $tempStderr = "$testDir/stderr.txt"
    
    # Run the command
    $process = Start-Process -FilePath $blenderPath -ArgumentList "--background", "--python", $debugScript, "--", "--svg", $svgPath, "--output", $outputPath, "--debug" -Wait -NoNewWindow -PassThru -RedirectStandardOutput $tempStdout -RedirectStandardError $tempStderr
    
    # Check process exit code
    if ($process.ExitCode -eq 0) {
        Write-ColorMessage "✅ Process completed successfully with exit code 0" "Green"
    } else {
        Write-ColorMessage "❌ Process failed with exit code $($process.ExitCode)" "Red"
    }
    
    # Display output
    if (Test-Path $tempStdout) {
        Write-ColorMessage "`nSTANDARD OUTPUT:" "Cyan"
        Get-Content $tempStdout | ForEach-Object { Write-ColorMessage $_ "Gray" }
    } else {
        Write-ColorMessage "`nNo standard output captured" "Yellow"
    }
    
    if (Test-Path $tempStderr) {
        Write-ColorMessage "`nSTANDARD ERROR:" "Red"
        Get-Content $tempStderr | ForEach-Object { Write-ColorMessage $_ "Red" }
    } else {
        Write-ColorMessage "`nNo standard error captured" "Yellow"
    }
    
    # Check if output file was created
    if (Test-Path $outputPath) {
        Write-ColorMessage "`n✅ Successfully created Blender file: $outputPath" "Green"
    } else {
        Write-ColorMessage "`n❌ Failed to create Blender file: $outputPath" "Red"
    }
    
} catch {
    Write-ColorMessage "Error running Blender: $_" "Red"
}

Write-ColorMessage "`nDebug files saved to: $testDir" "Yellow"
