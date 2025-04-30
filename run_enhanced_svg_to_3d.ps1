# PowerShell script to run the enhanced SVG to 3D converter
# Save this as run_enhanced_svg_to_3d.ps1

param (
    [Parameter(Mandatory=$true)]
    [string]$SvgPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "",
    
    [Parameter(Mandatory=$false)]
    [float]$ExtrudeDepth = 0.1,
    
    [Parameter(Mandatory=$false)]
    [float]$ScaleFactor = 0.01,
    
    [Parameter(Mandatory=$false)]
    [switch]$Debug
)

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
                Write-Host "Loaded env variable: $name" -ForegroundColor DarkGray
            }
        }
    }
    else {
        Write-Host "Warning: .env file not found at $envPath" -ForegroundColor Yellow
    }
}

# Function to find Blender executable
function Find-BlenderPath {
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
    
    return $blenderPath
}

# Find Blender
$blenderPath = Find-BlenderPath
if (-not $blenderPath) {
    Write-Host "❌ Blender not found. Please install Blender or set BLENDER_PATH in your .env file." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found Blender at: $blenderPath" -ForegroundColor Green

# Handle path with spaces
if ($blenderPath -match '\s') {
    Write-Host "Note: Blender path contains spaces. Ensuring proper quoting." -ForegroundColor Yellow
}

# Set default output path if not provided
if (-not $OutputPath) {
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($SvgPath)
    $OutputPath = "./outputs/enhanced_svg_test/${fileName}.blend"
}

# Create output directory if it doesn't exist
$outputDir = Split-Path -Parent $OutputPath
if ($outputDir -and -not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Prepare debug flag
$debugFlag = ""
if ($Debug) {
    $debugFlag = "--debug"
}

# Path to the enhanced SVG to 3D script
$scriptPath = "./genai_agent/scripts/enhanced_svg_to_3d_blender.py"

# Run Blender with the enhanced script
Write-Host "Converting SVG to 3D:" -ForegroundColor Cyan
Write-Host "  SVG path: $SvgPath" -ForegroundColor Cyan
Write-Host "  Output path: $OutputPath" -ForegroundColor Cyan
Write-Host "  Extrude depth: $ExtrudeDepth" -ForegroundColor Cyan
Write-Host "  Scale factor: $ScaleFactor" -ForegroundColor Cyan

$command = "& `"$blenderPath`" --background --python `"$scriptPath`" -- --svg `"$SvgPath`" --output `"$OutputPath`" --extrude $ExtrudeDepth --scale $ScaleFactor $debugFlag"

Write-Host "Executing command:" -ForegroundColor Yellow
Write-Host $command -ForegroundColor Yellow
Write-Host ""

try {
    Invoke-Expression $command
    
    if (Test-Path $OutputPath) {
        Write-Host "✅ Successfully converted SVG to 3D model: $OutputPath" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create 3D model" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error running enhanced SVG to 3D script: $_" -ForegroundColor Red
    exit 1
}
