# PowerShell script to test the enhanced SVG to 3D v3 converter
# Save as test_enhanced_v3.ps1

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
            "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
            "C:\Program Files\Blender Foundation\Blender 3.3\blender.exe"
        )
        
        foreach ($path in $defaultPaths) {
            if (Test-Path $path) {
                $blenderPath = $path
                break
            }
        }
    }

    # Try to find Blender in PATH as a last resort
    if (-not $blenderPath) {
        try {
            $blenderPath = (Get-Command "blender" -ErrorAction SilentlyContinue).Source
        } catch {
            $blenderPath = $null
        }
    }

    return $blenderPath
}

# Create test SVG files
function Create-TestSVG {
    param (
        [string]$OutputPath,
        [string]$SvgType
    )
    
    Write-ColorMessage "Creating test SVG: $SvgType" "Yellow"
    
    # Create output directory if it doesn't exist
    $outputDir = Split-Path -Parent $OutputPath
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    $svgContent = ""
    
    switch ($SvgType) {
        "basic" {
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
        
        "paths" {
            $svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <!-- Cubic Bezier -->
  <path d="M50,50 C100,25 150,75 200,50" stroke="blue" stroke-width="3" fill="none" />
  
  <!-- Multiple path segments with different commands -->
  <path d="M100,100 L150,100 Q200,50 250,100 T300,100 C350,50 400,150 450,100 Z" fill="lightgreen" stroke="green" stroke-width="2" />
  
  <!-- Arc command -->
  <path d="M200,300 A100,50 0 0 1 400,300" fill="none" stroke="red" stroke-width="3" />
  
  <!-- Closed shape with mixed commands -->
  <path d="M250,200 L300,150 Q350,150 350,200 L350,250 C320,280 280,280 250,250 Z" fill="orange" />
</svg>
"@
        }
        
        "transforms" {
            $svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <!-- Translate -->
  <rect x="50" y="50" width="50" height="50" fill="red" transform="translate(20, 30)" />
  
  <!-- Scale -->
  <circle cx="200" cy="100" r="30" fill="blue" transform="scale(1.5)" />
  
  <!-- Rotate -->
  <rect x="300" y="50" width="80" height="30" fill="green" transform="rotate(45)" />
  
  <!-- Combined transforms -->
  <polygon points="100,300 150,250 200,300" fill="purple" transform="translate(50,50) rotate(30) scale(0.8)" />
  
  <!-- Matrix transform -->
  <ellipse cx="350" cy="350" rx="60" ry="30" fill="orange" transform="matrix(1, 0.5, -0.5, 1, 10, 10)" />
  
  <!-- Nested transforms -->
  <g transform="translate(250, 180)">
    <g transform="rotate(15)">
      <rect x="-25" y="-25" width="50" height="50" fill="cyan" />
    </g>
  </g>
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

# Run the enhanced script on the test SVG
function Test-EnhancedSVGTo3D {
    param (
        [string]$BlenderPath,
        [string]$SVGPath,
        [string]$OutputPath,
        [float]$ExtrudeDepth = 0.1,
        [float]$ScaleFactor = 0.01,
        [switch]$Debug
    )
    
    Write-ColorMessage "`nTesting enhanced SVG to 3D conversion for: $SVGPath" "Cyan"
    Write-ColorMessage "Output to: $OutputPath" "Cyan"
    
    # Ensure the converter script exists
    $scriptPath = "./genai_agent/scripts/enhanced_svg_to_3d_v3.py"
    if (-not (Test-Path $scriptPath)) {
        Write-ColorMessage "❌ Enhanced SVG to 3D v3 script not found: $scriptPath" "Red"
        Write-ColorMessage "Creating a placeholder..." "Yellow"
        
        # Create the directory if it doesn't exist
        $scriptDir = Split-Path -Parent $scriptPath
        if (-not (Test-Path $scriptDir)) {
            New-Item -ItemType Directory -Path $scriptDir -Force | Out-Null
        }
        
        # Copy our enhanced script to the expected location
        $enhancedScript = Get-Content "enhanced_svg_to_3d_v3.py" -ErrorAction SilentlyContinue
        if ($enhancedScript) {
            $enhancedScript | Out-File -FilePath $scriptPath -Encoding utf8
            Write-ColorMessage "✅ Enhanced script copied to: $scriptPath" "Green"
        } else {
            Write-ColorMessage "❌ Could not find enhanced_svg_to_3d_v3.py in current directory" "Red"
            return $false
        }
    }
    
    # Prepare debug flag
    $debugFlag = ""
    if ($Debug) {
        $debugFlag = "debug"
    }
    
    # Run Blender with the enhanced script
    $process = Start-Process -FilePath $BlenderPath -ArgumentList "--background", "--python", $scriptPath, "--", $SVGPath, $OutputPath, $ExtrudeDepth, $ScaleFactor, $debugFlag -Wait -NoNewWindow -PassThru -RedirectStandardOutput "$OutputPath.log" -RedirectStandardError "$OutputPath.err"
    
    if ($process.ExitCode -eq 0) {
        Write-ColorMessage "✅ Successfully converted SVG to 3D model (Exit code: 0)" "Green"
        return $true
    } else {
        Write-ColorMessage "❌ Failed to convert SVG to 3D model (Exit code: $($process.ExitCode))" "Red"
        
        # Show log tail if available
        if (Test-Path "$OutputPath.log") {
            Write-ColorMessage "`nLast few log lines:" "Yellow"
            Get-Content "$OutputPath.log" -Tail 10 | ForEach-Object {
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

# Main function to run all tests
function Run-Tests {
    Write-ColorMessage "=============================================" "Cyan"
    Write-ColorMessage "     Testing Enhanced SVG to 3D v3 Converter " "Cyan"
    Write-ColorMessage "=============================================" "Cyan"
    
    # Step 1: Verify Blender installation
    $blenderPath = Find-Blender
    if (-not $blenderPath) {
        Write-ColorMessage "❌ Blender not found. Please install Blender or set BLENDER_PATH in your .env file." "Red"
        return
    }
    
    Write-ColorMessage "✅ Using Blender: $blenderPath" "Green"
    
    # Create output directory
    $outputDir = "./outputs/enhanced_svg_test_v3"
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # Step 2: Create test SVG files
    $testFiles = @(
        @{Type = "basic"; Path = "$outputDir/basic_test.svg"},
        @{Type = "complex"; Path = "$outputDir/complex_test.svg"},
        @{Type = "paths"; Path = "$outputDir/paths_test.svg"},
        @{Type = "transforms"; Path = "$outputDir/transforms_test.svg"},
        @{Type = "flowchart"; Path = "$outputDir/flowchart_test.svg"}
    )
    
    # Create and test each SVG file
    $successCount = 0
    $totalTests = $testFiles.Count
    
    foreach ($testFile in $testFiles) {
        $svgPath = Create-TestSVG -OutputPath $testFile.Path -SvgType $testFile.Type
        if ($svgPath) {
            $outputBlend = [System.IO.Path]::ChangeExtension($svgPath, "blend")
            $success = Test-EnhancedSVGTo3D -BlenderPath $blenderPath -SVGPath $svgPath -OutputPath $outputBlend -Debug
            if ($success) {
                $successCount++
            }
        }
    }
    
    # Step 3: Report results
    Write-ColorMessage "`n=============================================" "Cyan"
    Write-ColorMessage "     Test Results: $successCount/$totalTests passed" "Cyan"
    Write-ColorMessage "=============================================" "Cyan"
    
    # Check if any files were successfully created
    $createdFiles = Get-ChildItem "$outputDir/*.blend" -ErrorAction SilentlyContinue
    if ($createdFiles) {
        Write-ColorMessage "`n✅ Created Blender files:" "Green"
        foreach ($file in $createdFiles) {
            Write-ColorMessage "  - $($file.Name)" "Green"
        }
    } else {
        Write-ColorMessage "`n❌ No Blender files were created" "Red"
    }
    
    Write-ColorMessage "`nAll tests completed! Results are in: $outputDir" "Yellow"
    Write-ColorMessage "You can open the generated .blend files in Blender to inspect the results" "Yellow"
}

# Run the tests
Run-Tests