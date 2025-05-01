# PowerShell script to test TCP handshake SVG conversion
# Save as test_tcp_handshake.ps1

function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Find Blender executable
function Find-Blender {
    # Read from .env file if it exists
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

    # If not found, try common installation locations
    if (-not $blenderPath -or -not (Test-Path $blenderPath)) {
        $defaultPaths = @(
            "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
        )
        
        foreach ($path in $defaultPaths) {
            if (Test-Path $path) {
                $blenderPath = $path
                break
            }
        }
    }

    return $blenderPath
}

# Run the enhanced script on the TCP handshake SVG
function Test-TCPHandshakeSVG {
    param (
        [string]$BlenderPath,
        [string]$SVGPath,
        [string]$OutputPath,
        [float]$ExtrudeDepth = 0.2,  # Increased extrusion for better visibility
        [float]$ScaleFactor = 0.03,  # Increased scale factor
        [switch]$Debug
    )
    
    Write-ColorMessage "`nTesting TCP Handshake SVG to 3D conversion" "Cyan"
    Write-ColorMessage "Input SVG: $SVGPath" "Yellow"
    Write-ColorMessage "Output Blend: $OutputPath" "Yellow"
    
    # Ensure the converter script exists
    $scriptPath = "./genai_agent/scripts/enhanced_svg_to_3d_v3.py"
    if (-not (Test-Path $scriptPath)) {
        Write-ColorMessage "❌ Enhanced SVG to 3D v3 script not found at: $scriptPath" "Red"
        $scriptPath = "./enhanced_svg_to_3d_v3.py"
        
        if (-not (Test-Path $scriptPath)) {
            Write-ColorMessage "❌ Enhanced SVG to 3D v3 script not found in current directory either!" "Red"
            return $false
        }
        
        Write-ColorMessage "✅ Using converter script from current directory: $scriptPath" "Green"
    }
    
    # Create output directory if needed
    $outputDir = Split-Path -Parent $OutputPath
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
        Write-ColorMessage "Created output directory: $outputDir" "Gray"
    }
    
    # Prepare debug flag
    $debugFlag = ""
    if ($Debug) {
        $debugFlag = "debug"
    }
    
    # Detailed logging options
    $logFile = "$OutputPath.log"
    $errorFile = "$OutputPath.err"
    
    Write-ColorMessage "Running Blender with options:" "Cyan"
    Write-ColorMessage "  - Extrusion depth: $ExtrudeDepth" "Gray"
    Write-ColorMessage "  - Scale factor: $ScaleFactor" "Gray"
    Write-ColorMessage "  - Debug mode: $($Debug.IsPresent)" "Gray"
    Write-ColorMessage "  - Log file: $logFile" "Gray"
    
    # Run Blender with the enhanced script
    $process = Start-Process -FilePath $BlenderPath -ArgumentList "--background", "--python", $scriptPath, "--", $SVGPath, $OutputPath, $ExtrudeDepth, $ScaleFactor, $debugFlag -Wait -NoNewWindow -PassThru -RedirectStandardOutput $logFile -RedirectStandardError $errorFile
    
    if ($process.ExitCode -eq 0) {
        Write-ColorMessage "✅ Successfully converted SVG to 3D model (Exit code: 0)" "Green"
        
        # Display log summary
        if (Test-Path $logFile) {
            Write-ColorMessage "`nLog File Summary:" "Yellow"
            $logContent = Get-Content $logFile
            
            # Find element count
            $elementLine = $logContent | Where-Object { $_ -match "Parsed elements:" }
            if ($elementLine) {
                Write-ColorMessage $elementLine "Green"
            }
            
            # Find created objects
            $objectLine = $logContent | Where-Object { $_ -match "Created \d+ 3D objects" }
            if ($objectLine) {
                Write-ColorMessage $objectLine "Green"
            }
            
            # Check for specific elements
            $rectangles = $logContent | Where-Object { $_ -match "Rect_" }
            $texts = $logContent | Where-Object { $_ -match "Text_" }
            $paths = $logContent | Where-Object { $_ -match "Path_" }
            
            Write-ColorMessage "Object counts:" "Yellow"
            Write-ColorMessage "  - Rectangles: $($rectangles.Count)" "Cyan"
            Write-ColorMessage "  - Texts: $($texts.Count)" "Cyan"
            Write-ColorMessage "  - Paths: $($paths.Count)" "Cyan"
        }
        
        Write-ColorMessage "`nBlender file created: $OutputPath" "Green"
        return $true
    } else {
        Write-ColorMessage "❌ Failed to convert SVG to 3D model (Exit code: $($process.ExitCode))" "Red"
        
        # Show error details
        if (Test-Path $errorFile -and (Get-Item $errorFile).Length -gt 0) {
            Write-ColorMessage "`nError details:" "Red"
            Get-Content $errorFile | ForEach-Object {
                Write-ColorMessage "  $_" "Red"
            }
        }
        
        # Show log tail if available
        if (Test-Path $logFile) {
            Write-ColorMessage "`nLast 20 log lines:" "Yellow"
            Get-Content $logFile -Tail 20 | ForEach-Object {
                if ($_ -match "error|exception|failed" -and $_ -notmatch "TBBmalloc") {
                    Write-ColorMessage $_ "Red"
                } elseif ($_ -match "\[SVG2-3D\]") {
                    Write-ColorMessage $_ "Green"
                } else {
                    Write-ColorMessage $_ "Gray"
                }
            }
        }
        
        return $false
    }
}

# Main execution
$svgPath = "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\outputs\tcp-3-way-handshake.svg"
$outputPath = "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\outputs\tcp-3-way-handshake.blend"

# Verify the SVG file exists
if (-not (Test-Path $svgPath)) {
    Write-ColorMessage "❌ SVG file not found: $svgPath" "Red"
    exit 1
}

# Find Blender
$blenderPath = Find-Blender
if (-not $blenderPath) {
    Write-ColorMessage "❌ Blender executable not found. Please install Blender or set BLENDER_PATH in your .env file." "Red"
    exit 1
}

Write-ColorMessage "✅ Using Blender: $blenderPath" "Green"

# Run the test
$result = Test-TCPHandshakeSVG -BlenderPath $blenderPath -SVGPath $svgPath -OutputPath $outputPath -ExtrudeDepth 0.2 -ScaleFactor 0.03 -Debug

if ($result) {
    Write-ColorMessage "`n✅ TCP Handshake SVG conversion successful!" "Green"
    Write-ColorMessage "Open the generated .blend file in Blender to inspect the results: $outputPath" "Yellow"
} else {
    Write-ColorMessage "`n❌ TCP Handshake SVG conversion failed" "Red"
}