# PowerShell script to test the Blender integration for SVG to 3D conversion
# Save this as test_blender_integration.ps1

# Function for colorful console output
function Write-ColorMessage {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Function to verify Blender installation
function Test-BlenderInstallation {
    # Try to get Blender path from environment
    $blenderPath = $env:BLENDER_PATH
    
    if (-not $blenderPath) {
        # Try to find Blender in the default installation location
        $defaultPaths = @(
            "C:\Program Files\Blender Foundation\Blender 3.3\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 3.2\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 3.1\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 3.0\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 2.93\blender.exe"
        )
        
        foreach ($path in $defaultPaths) {
            if (Test-Path $path) {
                $blenderPath = $path
                break
            }
        }
    }
    
    if (-not $blenderPath) {
        # Try to find Blender in PATH
        try {
            $blenderPath = (Get-Command "blender" -ErrorAction SilentlyContinue).Source
        } catch {
            $blenderPath = $null
        }
    }
    
    if ($blenderPath -and (Test-Path $blenderPath)) {
        Write-ColorMessage "✅ Blender found at: $blenderPath" "Green"
        return $blenderPath
    } else {
        Write-ColorMessage "❌ Blender not found. Please install Blender or set BLENDER_PATH in your .env file." "Red"
        return $null
    }
}

# Function to test SVG generation
function Test-SVGGeneration {
    param (
        [string]$Concept = "A simple flowchart with three steps",
        [string]$OutputPath = "outputs/test_diagram.svg"
    )
    
    Write-ColorMessage "Generating test SVG..." "Yellow"
    
    # Ensure outputs directory exists
    $outputDir = Split-Path -Parent $OutputPath
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir | Out-Null
    }
    
    # Use the CLI to generate an SVG
    $command = ".\run_svg_cli.bat svg `"$Concept`" `"$OutputPath`""
    Invoke-Expression $command
    
    if (Test-Path $OutputPath) {
        Write-ColorMessage "✅ SVG generated successfully: $OutputPath" "Green"
        return $OutputPath
    } else {
        Write-ColorMessage "❌ Failed to generate SVG" "Red"
        return $null
    }
}

# Function to test SVG to 3D conversion with Blender
function Test-SVGTo3DConversion {
    param (
        [string]$BlenderPath,
        [string]$SVGPath,
        [string]$OutputPath = "outputs/test_model.blend"
    )
    
    Write-ColorMessage "Testing SVG to 3D conversion..." "Yellow"
    
    # Ensure the scripts directory exists
    $scriptsDir = "./genai_agent/scripts"
    if (-not (Test-Path $scriptsDir)) {
        Write-ColorMessage "❌ Scripts directory not found: $scriptsDir" "Red"
        return $false
    }
    
    # Check if the Blender script exists
    $blenderScript = "$scriptsDir/svg_to_3d_blender.py"
    if (-not (Test-Path $blenderScript)) {
        Write-ColorMessage "❌ Blender script not found: $blenderScript" "Red"
        return $false
    }
    
    # Run Blender with the conversion script
    Write-ColorMessage "Running Blender script..." "Yellow"
    $command = "& `"$BlenderPath`" --background --python `"$blenderScript`" -- --svg `"$SVGPath`" --output `"$OutputPath`" --extrude 0.1 --scale 1.0"
    
    try {
        Invoke-Expression $command
        
        if (Test-Path $OutputPath) {
            Write-ColorMessage "✅ 3D model created successfully: $OutputPath" "Green"
            return $true
        } else {
            Write-ColorMessage "❌ Failed to create 3D model" "Red"
            return $false
        }
    } catch {
        Write-ColorMessage "❌ Error running Blender script: $_" "Red"
        return $false
    }
}

# Function to test animation
function Test-Animation {
    param (
        [string]$BlenderPath,
        [string]$ModelPath,
        [string]$OutputPath = "outputs/test_animated.blend",
        [string]$AnimationType = "standard"
    )
    
    Write-ColorMessage "Testing animation system..." "Yellow"
    
    # Check if the animation script exists
    $animationScript = "./genai_agent/scripts/scenex_animation.py"
    if (-not (Test-Path $animationScript)) {
        Write-ColorMessage "❌ Animation script not found: $animationScript" "Red"
        return $false
    }
    
    # Run Blender with the animation script
    Write-ColorMessage "Running animation script..." "Yellow"
    $command = "& `"$BlenderPath`" --background --python `"$animationScript`" -- --input `"$ModelPath`" --output `"$OutputPath`" --animation-type `"$AnimationType`" --duration 5.0"
    
    try {
        Invoke-Expression $command
        
        if (Test-Path $OutputPath) {
            Write-ColorMessage "✅ Animation created successfully: $OutputPath" "Green"
            return $true
        } else {
            Write-ColorMessage "❌ Failed to create animation" "Red"
            return $false
        }
    } catch {
        Write-ColorMessage "❌ Error running animation script: $_" "Red"
        return $false
    }
}

# Function to test video rendering
function Test-VideoRendering {
    param (
        [string]$BlenderPath,
        [string]$AnimatedModelPath,
        [string]$OutputPath = "outputs/test_video.mp4",
        [string]$Quality = "medium"
    )
    
    Write-ColorMessage "Testing video rendering..." "Yellow"
    
    # Check if the rendering script exists
    $renderingScript = "./genai_agent/scripts/video_renderer.py"
    if (-not (Test-Path $renderingScript)) {
        Write-ColorMessage "❌ Rendering script not found: $renderingScript" "Red"
        return $false
    }
    
    # Run Blender with the rendering script
    Write-ColorMessage "Running rendering script..." "Yellow"
    $command = "& `"$BlenderPath`" --background --python `"$renderingScript`" -- --input `"$AnimatedModelPath`" --output `"$OutputPath`" --quality `"$Quality`" --width 1280 --height 720"
    
    try {
        Invoke-Expression $command
        
        if (Test-Path $OutputPath) {
            Write-ColorMessage "✅ Video rendered successfully: $OutputPath" "Green"
            return $true
        } else {
            Write-ColorMessage "❌ Failed to render video" "Red"
            return $false
        }
    } catch {
        Write-ColorMessage "❌ Error running rendering script: $_" "Red"
        return $false
    }
}

# Main function to run all tests
function Test-BlenderIntegration {
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "    Testing SVG to Video Blender Integration " "Cyan"
    Write-ColorMessage "=============================================" "Cyan"
    
    # Step 1: Verify Blender installation
    $blenderPath = Test-BlenderInstallation
    if (-not $blenderPath) {
        return
    }
    
    # Step 2: Generate a test SVG
    $svgPath = Test-SVGGeneration
    if (-not $svgPath) {
        return
    }
    
    # Step 3: Test SVG to 3D conversion
    $modelPath = "outputs/test_model.blend"
    $conversionSuccess = Test-SVGTo3DConversion -BlenderPath $blenderPath -SVGPath $svgPath -OutputPath $modelPath
    if (-not $conversionSuccess) {
        return
    }
    
    # Step 4: Test animation
    $animatedModelPath = "outputs/test_animated.blend"
    $animationSuccess = Test-Animation -BlenderPath $blenderPath -ModelPath $modelPath -OutputPath $animatedModelPath
    if (-not $animationSuccess) {
        return
    }
    
    # Step 5: Test video rendering
    $videoPath = "outputs/test_video.mp4"
    $renderingSuccess = Test-VideoRendering -BlenderPath $blenderPath -AnimatedModelPath $animatedModelPath -OutputPath $videoPath
    if (-not $renderingSuccess) {
        return
    }
    
    # All tests passed
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "          All tests passed successfully      " "Cyan"
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "SVG Path: $svgPath" "Green"
    Write-ColorMessage "3D Model Path: $modelPath" "Green"
    Write-ColorMessage "Animated Model Path: $animatedModelPath" "Green"
    Write-ColorMessage "Video Path: $videoPath" "Green"
}

# Run the tests
Test-BlenderIntegration