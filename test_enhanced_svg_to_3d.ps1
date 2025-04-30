# PowerShell script to test the enhanced SVG to 3D Blender conversion
# Save this as test_enhanced_svg_to_3d.ps1

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
function Load-EnvFile {
    param (
        [string]$envPath = ".env"
    )
    
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
                [Environment]::SetEnvironmentVariable($name, $value)
                Write-ColorMessage "Loaded env variable: $name" "DarkGray"
            }
        }
    }
    else {
        Write-ColorMessage "Warning: .env file not found at $envPath" "Yellow"
    }
}

# Check for Blender installation
function Test-BlenderInstallation {
    # First load environment variables from .env
    Load-EnvFile
    
    # Try to get Blender path from environment
    $blenderPath = $env:BLENDER_PATH
    
    if (-not $blenderPath) {
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

# Function to generate simple test SVGs
function Create-TestSVG {
    param (
        [string]$OutputPath,
        [string]$SvgType
    )
    
    Write-ColorMessage "Creating test SVG: $SvgType" "Yellow"
    
    # Create output directory if it doesn't exist
    $outputDir = Split-Path -Parent $OutputPath
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir | Out-Null
    }
    
    $svgContent = ""
    
    switch ($SvgType) {
        "simple" {
            $svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <rect x="100" y="100" width="100" height="100" fill="red" />
  <circle cx="300" cy="150" r="50" fill="blue" />
  <ellipse cx="250" cy="300" rx="100" ry="50" fill="green" />
  <line x1="50" y1="400" x2="450" y2="400" stroke="black" stroke-width="5" />
  <text x="200" y="250" font-size="24" fill="purple">Test Text</text>
</svg>
"@
        }
        
        "complex" {
            $svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <g id="group1" transform="translate(50, 50)">
    <rect x="0" y="0" width="100" height="100" fill="red" rx="10" ry="10" />
    <circle cx="150" cy="50" r="30" fill="blue" />
  </g>
  <path d="M100,200 C150,100 250,100 300,200 S450,300 400,400" fill="none" stroke="green" stroke-width="5" />
  <polygon points="100,350 150,350 125,400" fill="orange" />
  <polyline points="200,300 250,350 300,300 350,350" fill="none" stroke="purple" stroke-width="3" />
  <text x="200" y="100" font-size="24" fill="black" transform="rotate(15, 200, 100)">Rotated Text</text>
</svg>
"@
        }
        
        "flowchart" {
            $svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <!-- Start node -->
  <rect x="250" y="50" width="100" height="50" rx="15" ry="15" fill="#4CAF50" />
  <text x="300" y="80" font-size="16" text-anchor="middle" fill="white">Start</text>
  
  <!-- Decision node -->
  <polygon points="300,150 350,200 300,250 250,200" fill="#2196F3" />
  <text x="300" y="205" font-size="14" text-anchor="middle" fill="white">Decision?</text>
  
  <!-- Yes path -->
  <rect x="150" y="300" width="100" height="50" fill="#FFC107" />
  <text x="200" y="330" font-size="16" text-anchor="middle" fill="black">Yes</text>
  
  <!-- No path -->
  <rect x="350" y="300" width="100" height="50" fill="#F44336" />
  <text x="400" y="330" font-size="16" text-anchor="middle" fill="white">No</text>
  
  <!-- Connectors -->
  <line x1="300" y1="100" x2="300" y2="150" stroke="black" stroke-width="2" />
  <line x1="250" y1="200" x2="200" y2="200" stroke="black" stroke-width="2" />
  <line x1="200" y1="200" x2="200" y2="300" stroke="black" stroke-width="2" />
  <line x1="350" y1="200" x2="400" y2="200" stroke="black" stroke-width="2" />
  <line x1="400" y1="200" x2="400" y2="300" stroke="black" stroke-width="2" />
</svg>
"@
        }
    }
    
    # Save the SVG file
    $svgContent | Out-File -FilePath $OutputPath -Encoding utf8
    
    if (Test-Path $OutputPath) {
        Write-ColorMessage "✅ Test SVG created: $OutputPath" "Green"
        return $OutputPath
    } else {
        Write-ColorMessage "❌ Failed to create test SVG" "Red"
        return $null
    }
}

# Function to run the enhanced SVG to 3D script
function Test-EnhancedSVGTo3D {
    param (
        [string]$BlenderPath,
        [string]$SVGPath,
        [string]$OutputPath,
        [float]$ExtrudeDepth = 0.1,
        [float]$ScaleFactor = 0.01,
        [switch]$Debug
    )
    
    Write-ColorMessage "Testing enhanced SVG to 3D conversion..." "Yellow"
    
    # Ensure the script exists
    $scriptPath = "./genai_agent/scripts/enhanced_svg_to_3d_blender.py"
    if (-not (Test-Path $scriptPath)) {
        Write-ColorMessage "❌ Enhanced SVG to 3D script not found: $scriptPath" "Red"
        return $false
    }
    
    # Prepare debug flag
    $debugFlag = ""
    if ($Debug) {
        $debugFlag = "--debug"
    }
    
    # Run Blender with the enhanced script
    $command = "& `"$BlenderPath`" --background --python `"$scriptPath`" -- --svg `"$SVGPath`" --output `"$OutputPath`" --extrude $ExtrudeDepth --scale $ScaleFactor $debugFlag"
    
    try {
        Write-ColorMessage "Running command: $command" "Yellow"
        Invoke-Expression $command
        
        if (Test-Path $OutputPath) {
            Write-ColorMessage "✅ Successfully converted SVG to 3D model: $OutputPath" "Green"
            return $true
        } else {
            Write-ColorMessage "❌ Failed to create 3D model" "Red"
            return $false
        }
    } catch {
        Write-ColorMessage "❌ Error running enhanced SVG to 3D script: $_" "Red"
        return $false
    }
}

# Main function to run all tests
function Run-Tests {
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "     Testing Enhanced SVG to 3D Conversion   " "Cyan"
    Write-ColorMessage "=============================================" "Cyan"
    
    # Step 1: Verify Blender installation
    $blenderPath = Test-BlenderInstallation
    if (-not $blenderPath) {
        return
    }
    
    # Create output directory
    $outputDir = "./outputs/enhanced_svg_test"
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir | Out-Null
    }
    
    # Step 2: Create and test simple SVG
    $simpleSVGPath = "$outputDir/simple_test.svg"
    $simple3DPath = "$outputDir/simple_test.blend"
    
    $svgPath = Create-TestSVG -OutputPath $simpleSVGPath -SvgType "simple"
    if ($svgPath) {
        Test-EnhancedSVGTo3D -BlenderPath $blenderPath -SVGPath $svgPath -OutputPath $simple3DPath -Debug
    }
    
    # Step 3: Create and test complex SVG
    $complexSVGPath = "$outputDir/complex_test.svg"
    $complex3DPath = "$outputDir/complex_test.blend"
    
    $svgPath = Create-TestSVG -OutputPath $complexSVGPath -SvgType "complex"
    if ($svgPath) {
        Test-EnhancedSVGTo3D -BlenderPath $blenderPath -SVGPath $svgPath -OutputPath $complex3DPath -Debug
    }
    
    # Step 4: Create and test flowchart SVG
    $flowchartSVGPath = "$outputDir/flowchart_test.svg"
    $flowchart3DPath = "$outputDir/flowchart_test.blend"
    
    $svgPath = Create-TestSVG -OutputPath $flowchartSVGPath -SvgType "flowchart"
    if ($svgPath) {
        Test-EnhancedSVGTo3D -BlenderPath $blenderPath -SVGPath $svgPath -OutputPath $flowchart3DPath -Debug
    }
    
    # All tests completed
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "     Enhanced SVG to 3D Testing Complete     " "Cyan"
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "Output directory: $outputDir" "Yellow"
    Write-ColorMessage "Check the generated .blend files in Blender to verify results" "Yellow"
}

# Run the tests
Run-Tests
