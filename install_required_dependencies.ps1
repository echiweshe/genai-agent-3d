# PowerShell script to install required dependencies for SVG Generator
# This script checks for required Python packages and installs them if needed

# Define the project paths
$ProjectRoot = "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d"
$ProjectEnv = "$ProjectRoot\genai_agent_project\venv"

Write-Host "SVG Generator Dependency Installer" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "$ProjectEnv\Scripts\activate.ps1")) {
    Write-Host "Virtual environment not found at: $ProjectEnv" -ForegroundColor Red
    Write-Host "Please create the virtual environment first." -ForegroundColor Red
    exit 1
}

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "$ProjectEnv\Scripts\activate.ps1"

# Function to check if a package is installed
function Is-Package-Installed {
    param (
        [string]$Package
    )
    
    $Output = pip list | Select-String -Pattern "^$Package\s"
    return $null -ne $Output
}

# Function to install a package
function Install-Package {
    param (
        [string]$Package,
        [string]$Version = ""
    )
    
    if ($Version) {
        $PackageSpec = "$Package==$Version"
    } else {
        $PackageSpec = $Package
    }
    
    Write-Host "  Installing $PackageSpec..." -ForegroundColor Yellow
    pip install $PackageSpec
    
    if (Is-Package-Installed -Package $Package) {
        Write-Host "  ✅ $Package installed successfully" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ❌ Failed to install $Package" -ForegroundColor Red
        return $false
    }
}

# List of required packages with versions
$RequiredPackages = @(
    @{Name = "anthropic"; Version = "0.21.5" },
    @{Name = "langchain"; Version = "0.3.1" },
    @{Name = "langchain-openai"; Version = "0.0.2" },
    @{Name = "langchain-anthropic"; Version = "0.1.1" },
    @{Name = "langchain-community"; Version = "0.0.20" },
    @{Name = "langchain-ollama"; Version = "0.0.1" },
    @{Name = "svgwrite"; Version = "1.4.3" },
    @{Name = "svgpathtools"; Version = "1.6.1" },
    @{Name = "fastapi"; Version = "0.110.0" },
    @{Name = "uvicorn"; Version = "0.29.0" }
)

# Check and install required packages
Write-Host "Checking required packages..." -ForegroundColor Cyan
$AllPackagesInstalled = $true

foreach ($Package in $RequiredPackages) {
    if (Is-Package-Installed -Package $Package.Name) {
        Write-Host "  ✅ $($Package.Name) is already installed" -ForegroundColor Green
    } else {
        $Success = Install-Package -Package $Package.Name -Version $Package.Version
        if (-not $Success) {
            $AllPackagesInstalled = $false
        }
    }
}

# Create a stub package for mathutils to fix dependency issues
$MathutilsSetupPath = "$ProjectRoot\genai_agent_project\stub_mathutils"
$MathutilsInitPath = "$MathutilsSetupPath\mathutils\__init__.py"
$MathutilsSetupPyPath = "$MathutilsSetupPath\setup.py"

Write-Host "Creating stub package for mathutils..." -ForegroundColor Cyan

# Create directory structure
if (-not (Test-Path "$MathutilsSetupPath\mathutils")) {
    New-Item -ItemType Directory -Path "$MathutilsSetupPath\mathutils" -Force | Out-Null
}

# Create __init__.py
$MathutilsInitContent = @"
"""
Stub module for mathutils to prevent import errors.
This allows the code to run even without the actual Blender mathutils module.
"""

class Vector:
    """Stub Vector class that mimics Blender's Vector."""
    def __init__(self, coords=(0, 0, 0)):
        self.x = coords[0] if len(coords) > 0 else 0
        self.y = coords[1] if len(coords) > 1 else 0
        self.z = coords[2] if len(coords) > 2 else 0
        
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        
    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise IndexError("Vector index out of range")
            
    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Vector index out of range")
    
    def __len__(self):
        return 3
        
    def __repr__(self):
        return f"Vector(({self.x}, {self.y}, {self.z}))"
        
    def copy(self):
        return Vector((self.x, self.y, self.z))
        
    def normalize(self):
        length = (self.x**2 + self.y**2 + self.z**2)**0.5
        if length != 0:
            self.x /= length
            self.y /= length
            self.z /= length
        return self

class Matrix:
    """Stub Matrix class that mimics Blender's Matrix."""
    def __init__(self, rows=None):
        if rows is None:
            self.rows = [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ]
        else:
            self.rows = rows
            
    def __repr__(self):
        return f"Matrix({self.rows})"
        
    @classmethod
    def Identity(cls, size=4):
        matrix = cls()
        return matrix
        
    @classmethod
    def Translation(cls, vector):
        matrix = cls()
        matrix.rows[0][3] = vector[0]
        matrix.rows[1][3] = vector[1]
        matrix.rows[2][3] = vector[2]
        return matrix
        
    @classmethod
    def Rotation(cls, angle, size, axis):
        matrix = cls()
        # This is a simplified rotation matrix
        return matrix

# Add other classes and functions as needed
"@
Set-Content -Path $MathutilsInitPath -Value $MathutilsInitContent -Encoding UTF8

# Create setup.py
$MathutilsSetupPyContent = @"
from setuptools import setup, find_packages

setup(
    name="mathutils",
    version="0.1.0",
    description="Stub package for Blender's mathutils module",
    author="GenAI Agent 3D",
    packages=find_packages(),
)
"@
Set-Content -Path $MathutilsSetupPyPath -Value $MathutilsSetupPyContent -Encoding UTF8

# Install the stub package
Write-Host "Installing mathutils stub package..." -ForegroundColor Cyan
Push-Location $MathutilsSetupPath
pip install -e .
Pop-Location

if (Is-Package-Installed -Package "mathutils") {
    Write-Host "  ✅ mathutils stub package installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to install mathutils stub package" -ForegroundColor Red
    $AllPackagesInstalled = $false
}

# Fix the import error for ModelAnimator in the animation module
$AnimationInitPath = "$ProjectRoot\genai_agent_project\genai_agent\svg_to_video\animation\__init__.py"
$AnimationDir = Split-Path -Parent $AnimationInitPath

# Ensure the animation directory exists
if (-not (Test-Path $AnimationDir)) {
    New-Item -ItemType Directory -Path $AnimationDir -Force | Out-Null
}

# Create __init__.py with ModelAnimator class
$AnimationInitContent = @"
"""
Animation module for SVG to Video pipeline.
"""

class ModelAnimator:
    """Class for animating 3D models."""
    
    def __init__(self):
        """Initialize the ModelAnimator."""
        self.supported_animations = ["rotation", "translation", "scale"]
    
    def animate(self, model_path, output_path, animation_type="rotation", duration=5.0, **kwargs):
        """
        Animate a 3D model.
        
        Args:
            model_path (str): Path to the input 3D model.
            output_path (str): Path to save the animated model.
            animation_type (str): Type of animation (rotation, translation, scale).
            duration (float): Duration of the animation in seconds.
            **kwargs: Additional animation parameters.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # This is a stub implementation
        import os
        import shutil
        
        try:
            # Create the output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Simply copy the model file to the output path for now
            shutil.copy2(model_path, output_path)
            
            print(f"Stub animation created: {animation_type} for {duration}s")
            print(f"Model: {model_path} -> {output_path}")
            
            return True
        except Exception as e:
            print(f"Error animating model: {str(e)}")
            return False
    
    def get_supported_animations(self):
        """Get a list of supported animation types."""
        return self.supported_animations


def animate_model(model_path, output_file, animation_type="rotation", duration=5.0, **kwargs):
    """
    Animate a 3D model.
    
    Args:
        model_path (str): Path to the input 3D model.
        output_file (str): Path to save the animated model.
        animation_type (str): Type of animation.
        duration (float): Duration of the animation in seconds.
        **kwargs: Additional animation parameters.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    animator = ModelAnimator()
    return animator.animate(
        model_path=model_path,
        output_path=output_file,
        animation_type=animation_type,
        duration=duration,
        **kwargs
    )
"@
Set-Content -Path $AnimationInitPath -Value $AnimationInitContent -Encoding UTF8
Write-Host "  ✅ Created animation module with ModelAnimator class" -ForegroundColor Green

# Summary
Write-Host ""
if ($AllPackagesInstalled) {
    Write-Host "All required packages installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some packages could not be installed. Please check the logs." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Dependencies Installation Complete!" -ForegroundColor Green
Write-Host "------------------------------------" -ForegroundColor Green
Write-Host "Installed packages:"
foreach ($Package in $RequiredPackages) {
    Write-Host "- $($Package.Name) $($Package.Version)" -ForegroundColor Yellow
}
Write-Host "- mathutils (stub package)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Created animation module with ModelAnimator class"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Fix the SVG directory structure:"
Write-Host "   .\fix_svg_directory_structure.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Fix backend issues and restart the backend:"
Write-Host "   .\fix_and_restart_backend.bat" -ForegroundColor Yellow
Write-Host ""
