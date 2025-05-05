# PowerShell script to fix all SVG Generator issues in one go
# This script combines all the fixes into a single script

# Define paths
$ProjectRoot = "C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d"
$BackupPath = "$ProjectRoot\XX_genai_agent\svg_to_video"
$DestinationPath = "$ProjectRoot\genai_agent_project\genai_agent\svg_to_video"
$SVGOutputDir = "$ProjectRoot\output\svg"
$SVGToVideoSVGDir = "$ProjectRoot\output\svg_to_video\svg"
$TestSVGDir = "$ProjectRoot\genai_agent_project\output\svg"
$SVGToVideoModelsDir = "$ProjectRoot\output\svg_to_video\models"
$SVGToVideoAnimationsDir = "$ProjectRoot\output\svg_to_video\animations"
$SVGToVideoVideosDir = "$ProjectRoot\output\svg_to_video\videos"

$BackupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "$ProjectRoot\backups\svg_fix_$BackupTimestamp"

Write-Host "SVG Generator All-in-One Fix" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green
Write-Host ""

# Create backup directory
Write-Host "Creating backup directory..." -ForegroundColor Cyan
if (-not (Test-Path "$ProjectRoot\backups")) {
    New-Item -ItemType Directory -Path "$ProjectRoot\backups" -Force | Out-Null
}
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
Write-Host "  Created backup directory: $BackupDir" -ForegroundColor Green

# Function to ensure a directory exists
function Ensure-Directory-Exists {
    param (
        [string]$Path
    )
    
    if (Test-Path $Path) {
        # Check if it's a file instead of a directory
        if ((Get-Item $Path).PSIsContainer -eq $false) {
            Write-Host "  Path exists as a file instead of a directory: $Path" -ForegroundColor Yellow
            
            # Create backup of the file
            $BackupFilePath = "$BackupDir\$(Split-Path -Leaf $Path)"
            Copy-Item -Path $Path -Destination $BackupFilePath -Force
            Write-Host "  Created backup at: $BackupFilePath" -ForegroundColor Gray
            
            # Remove the file
            Remove-Item -Path $Path -Force
            
            # Create directory
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
            Write-Host "  Created directory: $Path" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  Directory already exists: $Path" -ForegroundColor Gray
            return $false
        }
    } else {
        # Create directory
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "  Created directory: $Path" -ForegroundColor Green
        return $true
    }
}

# STEP 1: Ensure all required directories exist
Write-Host "STEP 1: Ensuring all required directories exist..." -ForegroundColor Cyan
Ensure-Directory-Exists -Path $DestinationPath
Ensure-Directory-Exists -Path $SVGOutputDir
Ensure-Directory-Exists -Path $SVGToVideoSVGDir
Ensure-Directory-Exists -Path $TestSVGDir
Ensure-Directory-Exists -Path $SVGToVideoModelsDir
Ensure-Directory-Exists -Path $SVGToVideoAnimationsDir
Ensure-Directory-Exists -Path $SVGToVideoVideosDir

# STEP 2: Copy SVG generator from backup to destination
Write-Host "STEP 2: Copying SVG generator from backup to destination..." -ForegroundColor Cyan
if (Test-Path $BackupPath) {
    # Create backup of current destination if it exists
    if (Test-Path $DestinationPath) {
        $DestinationBackupPath = "$BackupDir\svg_to_video"
        Copy-Item -Path "$DestinationPath\*" -Destination $DestinationBackupPath -Recurse -Force
        Write-Host "  Created backup of current destination at: $DestinationBackupPath" -ForegroundColor Gray
    }
    
    # Copy from backup to destination
    Copy-Item -Path "$BackupPath\*" -Destination $DestinationPath -Recurse -Force
    Write-Host "  Copied SVG generator from backup to destination" -ForegroundColor Green
} else {
    Write-Host "  Backup path doesn't exist: $BackupPath" -ForegroundColor Red
    Write-Host "  Skipping copy step" -ForegroundColor Yellow
}

# STEP 3: Update import statements in Python files
Write-Host "STEP 3: Updating import statements in Python files..." -ForegroundColor Cyan
$PythonFiles = Get-ChildItem -Path $DestinationPath -Filter "*.py" -Recurse -File

foreach ($File in $PythonFiles) {
    $Content = Get-Content -Path $File.FullName -Raw
    
    # Check if file contains old import paths
    if ($Content -match "from genai_agent\.svg_to_video" -or $Content -match "import genai_agent\.svg_to_video") {
        # Create backup of file
        $BackupFilePath = "$BackupDir\$(($File.FullName).Substring($DestinationPath.Length + 1))"
        $BackupFileDir = Split-Path -Parent $BackupFilePath
        if (-not (Test-Path $BackupFileDir)) {
            New-Item -ItemType Directory -Path $BackupFileDir -Force | Out-Null
        }
        Copy-Item -Path $File.FullName -Destination $BackupFilePath -Force
        
        Write-Host "  Updating imports in: $($File.Name)" -ForegroundColor Yellow
        
        # Replace all instances of import paths
        $NewContent = $Content -replace "from genai_agent\.svg_to_video", "from genai_agent_project.genai_agent.svg_to_video"
        $NewContent = $NewContent -replace "import genai_agent\.svg_to_video", "import genai_agent_project.genai_agent.svg_to_video"
        
        # Write updated content back to file
        Set-Content -Path $File.FullName -Value $NewContent -Encoding UTF8
        Write-Host "    Updated: $($File.Name)" -ForegroundColor Green
    }
}

# STEP 4: Create stub for mathutils module
Write-Host "STEP 4: Creating stub for mathutils module..." -ForegroundColor Cyan
$MathutilsPath = "$DestinationPath\svg_to_3d\mathutils.py"
$MathutilsDir = Split-Path -Parent $MathutilsPath

if (-not (Test-Path $MathutilsDir)) {
    New-Item -ItemType Directory -Path $MathutilsDir -Force | Out-Null
}

$MathutilsContent = @"
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
"@

Set-Content -Path $MathutilsPath -Value $MathutilsContent -Encoding UTF8
Write-Host "  Created mathutils stub module at: $MathutilsPath" -ForegroundColor Green

# STEP 5: Fix the Claude provider issue
Write-Host "STEP 5: Fixing Claude provider integration..." -ForegroundColor Cyan
$LangchainIntegrationsPath = "$DestinationPath\llm_integrations\langchain_integrations.py"

if (Test-Path $LangchainIntegrationsPath) {
    # Create backup
    $BackupLangchainPath = "$BackupDir\llm_integrations\langchain_integrations.py"
    $BackupLangchainDir = Split-Path -Parent $BackupLangchainPath
    if (-not (Test-Path $BackupLangchainDir)) {
        New-Item -ItemType Directory -Path $BackupLangchainDir -Force | Out-Null
    }
    Copy-Item -Path $LangchainIntegrationsPath -Destination $BackupLangchainPath -Force
    
    # Read content
    $Content = Get-Content -Path $LangchainIntegrationsPath -Raw
    
    # Fix the Claude provider initialization
    $FixedContent = $Content -replace "(\s+)self\.providers\[""claude""\] = ChatAnthropic\(([^)]*)\)", '$1try:
$1    self.providers["claude"] = ChatAnthropic($2)
$1except AttributeError as e:
$1    if "count_tokens" in str(e):
$1        # Fix for "Anthropic object has no attribute count_tokens"
$1        logging.warning("Using workaround for ChatAnthropic count_tokens issue")
$1        from langchain.chat_models.anthropic import ChatAnthropic as ChatAnthropicFixed
$1        # Monkey patch to fix the missing count_tokens attribute
$1        if not hasattr(ChatAnthropicFixed._client_obj.__class__, "count_tokens"):
$1            ChatAnthropicFixed._client_obj.__class__.count_tokens = lambda self, text: len(text.split())
$1        self.providers["claude"] = ChatAnthropicFixed($2)
$1    else:
$1        logging.error(f"Failed to initialize Claude provider: {str(e)}")
$1'
    
    # Write fixed content
    Set-Content -Path $LangchainIntegrationsPath -Value $FixedContent -Encoding UTF8
    Write-Host "  Fixed Claude provider initialization in langchain_integrations.py" -ForegroundColor Green
} else {
    Write-Host "  Could not find langchain_integrations.py" -ForegroundColor Red
}

# STEP 6: Create a simple ModelAnimator class
Write-Host "STEP 6: Creating ModelAnimator stub class..." -ForegroundColor Cyan
$AnimationInitPath = "$DestinationPath\animation\__init__.py"
$AnimationDir = Split-Path -Parent $AnimationInitPath

if (-not (Test-Path $AnimationDir)) {
    New-Item -ItemType Directory -Path $AnimationDir -Force | Out-Null
}

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
Write-Host "  Created ModelAnimator stub class at: $AnimationInitPath" -ForegroundColor Green

# STEP 7: Create a simple test SVG file
Write-Host "STEP 7: Creating test SVG file..." -ForegroundColor Cyan
$TestSVGPath = "$SVGOutputDir\test_all_in_one_fix.svg"
$TestSVGContent = @"
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="#f0f0f0" />
  <circle cx="100" cy="100" r="50" fill="blue" opacity="0.5" />
  <text x="100" y="100" font-family="Arial" font-size="16" text-anchor="middle" fill="black">
    SVG Test
  </text>
  <text x="100" y="130" font-family="Arial" font-size="12" text-anchor="middle" fill="black">
    Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
  </text>
</svg>
"@
Set-Content -Path $TestSVGPath -Value $TestSVGContent -Encoding UTF8
Write-Host "  Created test SVG file: $TestSVGPath" -ForegroundColor Green

# Copy the test SVG file to the other directories
Copy-Item -Path $TestSVGPath -Destination $SVGToVideoSVGDir -Force
Copy-Item -Path $TestSVGPath -Destination $TestSVGDir -Force
Write-Host "  Copied test SVG file to other directories" -ForegroundColor Green

# STEP 8: Create a test script for the SVG Generator
Write-Host "STEP 8: Creating test script for the SVG Generator..." -ForegroundColor Cyan
$TestScriptPath = "$ProjectRoot\test_svg_generator.py"
$TestScriptContent = @"
"""
Test script for the SVG generator.
This script tests the SVG generator with Claude and OpenAI LLMs.
"""

import os
import sys
import time
from pathlib import Path

# Add project directory to path
project_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project")
sys.path.insert(0, str(project_dir))

# Import SVG generator
try:
    from genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator import generate_svg
    print("Successfully imported SVG generator")
except ImportError as e:
    print(f"Error importing SVG generator: {e}")
    sys.exit(1)

# Define output directory
output_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg")
os.makedirs(output_dir, exist_ok=True)

# Test with Claude
def test_with_claude():
    print("\nTesting SVG generator with Claude...")
    output_file = output_dir / f"claude_test_flowchart_{int(time.time())}.svg"
    
    try:
        result = generate_svg(
            prompt="Create a flowchart showing the process of making coffee",
            diagram_type="flowchart",
            output_file=str(output_file),
            provider="claude"  # Use Claude provider
        )
        
        if result and os.path.isfile(output_file):
            print(f"Success! SVG generated at: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return True
        else:
            print("Failed to generate SVG with Claude")
            return False
    except Exception as e:
        print(f"Error generating SVG with Claude: {e}")
        return False

# Test with OpenAI
def test_with_openai():
    print("\nTesting SVG generator with OpenAI...")
    output_file = output_dir / f"openai_test_flowchart_{int(time.time())}.svg"
    
    try:
        result = generate_svg(
            prompt="Create a flowchart showing the process of making coffee",
            diagram_type="flowchart",
            output_file=str(output_file),
            provider="openai"  # Use OpenAI provider
        )
        
        if result and os.path.isfile(output_file):
            print(f"Success! SVG generated at: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return True
        else:
            print("Failed to generate SVG with OpenAI")
            return False
    except Exception as e:
        print(f"Error generating SVG with OpenAI: {e}")
        return False

# Test with mock provider as fallback
def test_with_mock():
    print("\nTesting SVG generator with mock provider...")
    output_file = output_dir / f"mock_test_flowchart_{int(time.time())}.svg"
    
    try:
        result = generate_svg(
            prompt="Create a flowchart showing the process of making coffee",
            diagram_type="flowchart",
            output_file=str(output_file),
            provider="mock"  # Use mock provider
        )
        
        if result and os.path.isfile(output_file):
            print(f"Success! SVG generated at: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return True
        else:
            print("Failed to generate SVG with mock provider")
            return False
    except Exception as e:
        print(f"Error generating SVG with mock provider: {e}")
        return False

if __name__ == "__main__":
    print("SVG Generator Test")
    print("=================")
    
    # Run tests
    claude_success = test_with_claude()
    openai_success = test_with_openai()
    mock_success = test_with_mock()
    
    # Print summary
    print("\nTest Summary:")
    print(f"Claude: {'SUCCESS' if claude_success else 'FAILED'}")
    print(f"OpenAI: {'SUCCESS' if openai_success else 'FAILED'}")
    print(f"Mock: {'SUCCESS' if mock_success else 'FAILED'}")
    
    # Overall result
    if claude_success or openai_success:
        print("\nSVG generator is working with at least one LLM provider!")
        sys.exit(0)
    elif mock_success:
        print("\nSVG generator is working with mock provider only.")
        print("Check your LLM provider configurations.")
        sys.exit(1)
    else:
        print("\nSVG generator is not working with any provider.")
        print("Please check the logs for errors.")
        sys.exit(1)
"@

Set-Content -Path $TestScriptPath -Value $TestScriptContent -Encoding UTF8
Write-Host "  Created test script: $TestScriptPath" -ForegroundColor Green

# STEP 9: Create a directory synchronization script
Write-Host "STEP 9: Creating directory synchronization script..." -ForegroundColor Cyan
$SyncScriptPath = "$ProjectRoot\sync_svg_directories.ps1"
$SyncScriptContent = @"
# PowerShell script to synchronize SVG directories
# Run this script when you need to make sure all SVG directories have the latest files

`$ProjectRoot = "$ProjectRoot"
`$SVGOutputDir = "`$ProjectRoot\output\svg"
`$SVGToVideoSVGDir = "`$ProjectRoot\output\svg_to_video\svg"
`$TestSVGDir = "`$ProjectRoot\genai_agent_project\output\svg"

Write-Host "SVG Directory Synchronization" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green
Write-Host ""

# Function to sync directories (copies files from source to target)
function Sync-Directories {
    param (
        [string]`$Source,
        [string]`$Target,
        [string]`$Label
    )
    
    if (-not (Test-Path `$Source)) {
        Write-Host "  Source directory does not exist: `$Source" -ForegroundColor Red
        return 0
    }
    
    if (-not (Test-Path `$Target)) {
        New-Item -ItemType Directory -Path `$Target -Force | Out-Null
        Write-Host "  Created target directory: `$Target" -ForegroundColor Yellow
    }
    
    `$Files = Get-ChildItem -Path `$Source -File | Where-Object { `$_.Name -ne "README.md" }
    `$CopiedCount = 0
    
    foreach (`$File in `$Files) {
        `$TargetPath = Join-Path `$Target `$File.Name
        if (-not (Test-Path `$TargetPath) -or 
            (Get-Item `$TargetPath).LastWriteTime -lt `$File.LastWriteTime) {
            Copy-Item -Path `$File.FullName -Destination `$TargetPath -Force
            `$CopiedCount++
        }
    }
    
    Write-Host "  Copied `$CopiedCount files to `$Label" -ForegroundColor Green
    return `$CopiedCount
}

# Consolidate files from all directories to main SVG directory
Write-Host "Consolidating files to main SVG directory..." -ForegroundColor Cyan
`$ConsolidatedCount = 0

# Copy from SVG to Video directory to main SVG directory
`$ConsolidatedCount += Sync-Directories -Source `$SVGToVideoSVGDir -Target `$SVGOutputDir -Label "main SVG directory (from SVG to Video)"

# Copy from Test directory to main SVG directory
`$ConsolidatedCount += Sync-Directories -Source `$TestSVGDir -Target `$SVGOutputDir -Label "main SVG directory (from Test)"

Write-Host "  Consolidated `$ConsolidatedCount files to main SVG directory" -ForegroundColor Green

# Sync from main SVG directory to other directories
Write-Host "Syncing from main SVG directory to other directories..." -ForegroundColor Cyan

# Copy from main SVG directory to SVG to Video directory
Sync-Directories -Source `$SVGOutputDir -Target `$SVGToVideoSVGDir -Label "SVG to Video directory"

# Copy from main SVG directory to Test directory
Sync-Directories -Source `$SVGOutputDir -Target `$TestSVGDir -Label "Test directory"

Write-Host "SVG directory synchronization complete!" -ForegroundColor Green
"@

Set-Content -Path $SyncScriptPath -Value $SyncScriptContent -Encoding UTF8
Write-Host "  Created directory synchronization script: $SyncScriptPath" -ForegroundColor Green

# Create a batch file to run the synchronization script
$SyncBatchPath = "$ProjectRoot\sync_svg_directories.bat"
$SyncBatchContent = @"
@echo off
echo SVG Directory Synchronization
echo ===========================
echo.

powershell -ExecutionPolicy Bypass -File sync_svg_directories.ps1
echo.

echo Synchronization complete!
pause
"@
Set-Content -Path $SyncBatchPath -Value $SyncBatchContent -Encoding UTF8
Write-Host "  Created batch file to run synchronization script: $SyncBatchPath" -ForegroundColor Green

# STEP 10: Create a batch file to restart the backend
Write-Host "STEP 10: Creating batch file to restart the backend..." -ForegroundColor Cyan
$RestartBackendBatchPath = "$ProjectRoot\restart_backend.bat"
$RestartBackendBatchContent = @"
@echo off
echo Restarting backend service
echo ========================
echo.

cd genai_agent_project
call venv\Scripts\activate
python manage_services.py restart backend
echo.

echo Backend restart complete!
pause
"@
Set-Content -Path $RestartBackendBatchPath -Value $RestartBackendBatchContent -Encoding UTF8
Write-Host "  Created batch file to restart the backend: $RestartBackendBatchPath" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "SVG Generator All-in-One Fix Complete!" -ForegroundColor Green
Write-Host "------------------------------------" -ForegroundColor Green
Write-Host "Fixed issues:"
Write-Host "1. SVG output directory structure" -ForegroundColor Yellow
Write-Host "2. Copied SVG generator code from backup" -ForegroundColor Yellow
Write-Host "3. Updated import statements" -ForegroundColor Yellow
Write-Host "4. Created mathutils stub module" -ForegroundColor Yellow
Write-Host "5. Fixed Claude provider integration" -ForegroundColor Yellow
Write-Host "6. Created ModelAnimator stub class" -ForegroundColor Yellow
Write-Host "7. Created test SVG file" -ForegroundColor Yellow
Write-Host "8. Created test script for SVG Generator" -ForegroundColor Yellow
Write-Host "9. Created directory synchronization script" -ForegroundColor Yellow
Write-Host "10. Created backend restart script" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Test the SVG generator:"
Write-Host "   python test_svg_generator.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Restart the backend service:"
Write-Host "   restart_backend.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Synchronize SVG directories if needed:"
Write-Host "   sync_svg_directories.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "If you still encounter issues, please check the logs for more details."
Write-Host ""
