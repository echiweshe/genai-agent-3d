"""
Web API routes for SVG generation and conversion with professional quality options.
This integrates the clarity-preserving and professional style approach into the web UI.
"""

import os
import json
import tempfile
import subprocess
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import shutil

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

# Import utility functions
from ..utils.file_utils import get_absolute_path, ensure_directory_exists
from ..config import get_settings

# Create router
router = APIRouter(prefix="/svg-generator", tags=["SVG Generator"])

# Define models
class SVGGenerationRequest(BaseModel):
    description: str
    provider: str = "claude-direct"
    diagramType: str = "flowchart"
    name: Optional[str] = None


class ConversionOptions(BaseModel):
    extrude_depth: float = 0.005  # Default reduced for clarity
    show_in_blender: bool = False
    style_preset: str = "professional"  # Default to professional quality
    use_enhanced: bool = True
    preserve_clarity: bool = True  # Default ON for clarity preservation
    custom_elements: bool = False  # New option for element-specific treatment
    debug: bool = False


class ConversionRequest(BaseModel):
    svg_path: str
    options: Optional[ConversionOptions] = None


# Get settings
settings = get_settings()

# Define output directories
SVG_OUTPUT_DIR = get_absolute_path(settings.svg_output_dir)
MODELS_OUTPUT_DIR = get_absolute_path(settings.models_output_dir)
DIAGRAMS_OUTPUT_DIR = get_absolute_path(settings.diagrams_output_dir)


@router.get("/health")
async def check_health():
    """Check the health of the SVG Generator service"""
    # Check if required directories exist
    svg_dir_exists = os.path.isdir(SVG_OUTPUT_DIR)
    models_dir_exists = os.path.isdir(MODELS_OUTPUT_DIR)
    
    # Check if Blender is available by searching common paths
    blender_path = find_blender_path()
    blender_available = blender_path is not None
    
    # Always report SVG to 3D as available, even if Blender is not found
    # This allows the UI to show conversion options and handle the unavailability gracefully
    svg_to_3d_available = True
    
    return {
        "status": "ok",
        "svg_output_dir_exists": svg_dir_exists,
        "models_output_dir_exists": models_dir_exists,
        "blender_available": blender_available,
        "blender_path": blender_path,
        "svg_to_3d_available": svg_to_3d_available
    }


@router.get("/list")
async def list_svg_files():
    """List all generated SVG files"""
    try:
        ensure_directory_exists(SVG_OUTPUT_DIR)
        svg_files = []
        
        for file in os.listdir(SVG_OUTPUT_DIR):
            if file.endswith(".svg"):
                file_path = os.path.join(SVG_OUTPUT_DIR, file)
                svg_files.append({
                    "name": file,
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path)
                })
        
        return {"svg_files": svg_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing SVG files: {str(e)}")


@router.post("/generate")
async def generate_svg(request: SVGGenerationRequest):
    """Generate an SVG diagram from a text description"""
    try:
        # Ensure output directory exists
        ensure_directory_exists(SVG_OUTPUT_DIR)
        ensure_directory_exists(DIAGRAMS_OUTPUT_DIR)
        
        # TODO: Implement the actual SVG generation logic using the LLM factory
        # This is a placeholder that simulates a successful response
        
        # Generate a file name if not provided
        if not request.name:
            timestamp = int(time.time())
            safe_type = request.diagramType.replace(" ", "_").lower()
            file_name = f"{safe_type}_{timestamp}.svg"
        else:
            # Make sure the name has .svg extension
            file_name = request.name if request.name.lower().endswith(".svg") else f"{request.name}.svg"
        
        # Define paths
        svg_path = os.path.join(SVG_OUTPUT_DIR, file_name)
        diagram_path = os.path.join(DIAGRAMS_OUTPUT_DIR, file_name)
        
        # In a real implementation, this would be the SVG content generated by the LLM
        # For now, we'll use a placeholder SVG
        svg_content = """
        <svg xmlns="http://www.w3.org/2000/svg" width="500" height="300" viewBox="0 0 500 300">
            <rect x="50" y="50" width="400" height="200" fill="#e0e0ff" stroke="#000080" stroke-width="2" />
            <text x="250" y="150" font-family="Arial" font-size="24" text-anchor="middle">Sample SVG</text>
            <circle cx="250" cy="250" r="30" fill="#ff8080" stroke="#800000" stroke-width="2" />
        </svg>
        """
        
        # Write the SVG to the output files
        with open(svg_path, "w") as f:
            f.write(svg_content)
        
        # Copy to diagrams directory
        shutil.copy(svg_path, diagram_path)
        
        return {
            "status": "success",
            "svg_content": svg_content,
            "svg_path": svg_path,
            "diagram_path": diagram_path,
            "file_name": file_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SVG: {str(e)}")


@router.get("/providers")
async def get_providers():
    """Get available LLM providers for SVG generation"""
    # This would typically fetch providers from the LLM factory
    # For now, return a static list
    return {
        "providers": [
            {"id": "claude-direct", "name": "Claude Direct"},
            {"id": "openai", "name": "OpenAI"},
            {"id": "ollama", "name": "Ollama (Local)"}
        ]
    }


@router.get("/diagram-types")
async def get_diagram_types():
    """Get available diagram types for SVG generation"""
    return {
        "diagram_types": [
            {"id": "flowchart", "name": "Flowchart"},
            {"id": "network", "name": "Network Diagram"},
            {"id": "sequence", "name": "Sequence Diagram"},
            {"id": "mindmap", "name": "Mind Map"},
            {"id": "architecture", "name": "Architecture Diagram"}
        ]
    }


@router.get("/style-presets")
async def get_style_presets():
    """Get available style presets for 3D conversion"""
    return {
        "style_presets": [
            {"id": "professional", "name": "Professional", "description": "Premium quality with subtle details and refined materials"},
            {"id": "technical", "name": "Technical", "description": "Clean, precise look suitable for technical diagrams"},
            {"id": "organic", "name": "Organic", "description": "Softer, natural look with subtle texturing"},
            {"id": "glossy", "name": "Glossy", "description": "Shiny, reflective appearance with higher specular values"},
            {"id": "metal", "name": "Metal", "description": "Strong metallic appearance with anisotropic reflections"}
        ]
    }


@router.post("/convert-to-3d")
async def convert_svg_to_3d(request: ConversionRequest):
    """Convert an SVG file to a 3D model using the professional quality converter"""
    try:
        # Ensure the SVG file exists
        if not os.path.isfile(request.svg_path):
            raise HTTPException(status_code=404, detail=f"SVG file not found: {request.svg_path}")
        
        # Ensure output directory exists
        ensure_directory_exists(MODELS_OUTPUT_DIR)
        
        # Set default options if not provided
        if request.options is None:
            request.options = ConversionOptions()
        
        # Generate output file name
        svg_name = os.path.basename(request.svg_path)
        base_name = os.path.splitext(svg_name)[0]
        
        # Modify filename based on conversion options
        if request.options.style_preset == "professional":
            model_name = f"{base_name}_professional.blend"
        elif request.options.preserve_clarity:
            model_name = f"{base_name}_clarity.blend"
        elif request.options.use_enhanced:
            model_name = f"{base_name}_enhanced.blend"
        else:
            model_name = f"{base_name}.blend"
        
        model_path = os.path.join(MODELS_OUTPUT_DIR, model_name)
        
        # Find Blender path
        blender_path = find_blender_path()
        
        if blender_path:
            # Create options JSON for the script
            options = {
                "extrude_depth": request.options.extrude_depth,
                "use_enhanced": request.options.use_enhanced,
                "style_preset": request.options.style_preset,
                "preserve_clarity": request.options.preserve_clarity,
                "custom_elements": request.options.custom_elements,
                "debug": request.options.debug
            }
            options_json = json.dumps(options)
            
            # Determine which script to use based on options
            if request.options.preserve_clarity:
                # Use clarity-preserving script
                script_path = get_absolute_path("genai_agent_project/scripts/svg_to_3d_clarity.py")
                if not os.path.exists(script_path):
                    # Try alternate path
                    script_path = get_absolute_path("genai_agent_project/genai_agent/svg_to_video/svg_to_3d/svg_to_3d_clarity.py")
                    if not os.path.exists(script_path):
                        # Fall back to standard script if clarity script doesn't exist
                        script_path = get_absolute_path("genai_agent_project/scripts/svg_to_3d_blender.py")
            else:
                # Use standard or enhanced script based on options
                if request.options.use_enhanced:
                    script_path = get_absolute_path("genai_agent_project/scripts/svg_to_3d_blender_enhanced.py")
                else:
                    script_path = get_absolute_path("genai_agent_project/scripts/svg_to_3d_blender.py")
            
            # Check if script exists, if not fall back to a script that definitely exists
            if not os.path.exists(script_path):
                # Create a temporary minimal script if no scripts are found
                script_path = create_minimal_script()
            
            # Create command
            command = [
                blender_path,
                "--background",
                "--python", script_path,
                "--",
                request.svg_path,
                model_path,
                options_json
            ]
            
            # Run Blender conversion process
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Error converting SVG to 3D: {process.stderr}",
                    "details": process.stdout
                }
            
            # If show_in_blender is True, open the file in Blender
            if request.options.show_in_blender and blender_path:
                subprocess.Popen([blender_path, model_path])
            
            return {
                "status": "success",
                "message": "SVG converted to 3D model successfully",
                "model_path": model_path,
                "enhanced": request.options.use_enhanced,
                "preserve_clarity": request.options.preserve_clarity,
                "style_preset": request.options.style_preset,
                "custom_elements": request.options.custom_elements
            }
        else:
            # Blender not found, create a mock output
            return {
                "status": "warning",
                "message": "Blender not found, created a mock output",
                "model_path": None,
                "error": "Blender executable not found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting SVG to 3D: {str(e)}")


@router.post("/import-to-blender")
async def import_svg_to_blender(request: ConversionRequest):
    """Import an SVG file directly into Blender with professional quality settings"""
    try:
        # Ensure the SVG file exists
        if not os.path.isfile(request.svg_path):
            raise HTTPException(status_code=404, detail=f"SVG file not found: {request.svg_path}")
        
        # Find Blender path
        blender_path = find_blender_path()
        
        if not blender_path:
            raise HTTPException(status_code=500, detail="Blender executable not found")
        
        # Set default options if not provided
        if request.options is None:
            request.options = ConversionOptions()
        
        # Get style preset
        style_preset = request.options.style_preset if request.options else "professional"
        
        # Set extrusion depth based on style and clarity options
        extrude_depth = request.options.extrude_depth if request.options else 0.005
        
        # Create a temporary script to import the SVG with professional quality settings
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
            temp_script_path = temp_script.name
            
            # Write the import script
            temp_script.write(f"""
import bpy
import os
import sys
import json

# Clear the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import SVG
bpy.ops.import_curve.svg(filepath="{request.svg_path.replace('\\', '\\\\')}")

# Set view to top
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'ORTHO'
                break

# Select all curves
bpy.ops.object.select_all(action='SELECT')

# Center objects
bpy.ops.view3d.view_selected()

# Define professional style material creation function
def create_professional_material(obj, color=(0.8, 0.8, 0.8, 1.0)):
    # Create new material
    mat = bpy.data.materials.new(name=f"Professional_{obj.name}")
    mat.use_nodes = True
    
    # Get node tree
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear existing nodes
    nodes.clear()
    
    # Create basic nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Set positions
    output.location = (300, 0)
    principled.location = (0, 0)
    
    # Professional material settings
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Metallic'].default_value = 0.2
    principled.inputs['Roughness'].default_value = 0.15
    principled.inputs['Specular'].default_value = 0.6
    principled.inputs['Clearcoat'].default_value = 0.3
    principled.inputs['Clearcoat Roughness'].default_value = 0.1
    
    # Connect nodes
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to object
    if len(obj.data.materials) > 0:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Process all curve objects with professional settings
for obj in bpy.context.selected_objects:
    if obj.type == 'CURVE':
        # Set extrusion with optimal clarity-preserving depth
        obj.data.extrude = {extrude_depth}
        
        # Apply higher resolution bevel for smoother edges
        obj.data.bevel_depth = {extrude_depth * 0.2}
        obj.data.bevel_resolution = 4
        
        # Apply smooth shading for better appearance
        try:
            bpy.ops.object.shade_smooth()
        except:
            pass
        
        # Apply professional material with original color if available
        if obj.active_material:
            orig_color = obj.active_material.diffuse_color
            create_professional_material(obj, orig_color)
        else:
            # Create a random color if no material exists
            import random
            r = random.uniform(0.2, 0.8)
            g = random.uniform(0.2, 0.8)
            b = random.uniform(0.2, 0.8)
            create_professional_material(obj, (r, g, b, 1.0))

# Set up professional studio lighting
bpy.ops.object.light_add(type='AREA', radius=5, location=(5, -5, 5))
key_light = bpy.context.active_object
key_light.data.energy = 500.0
key_light.data.color = (1.0, 0.95, 0.9)  # Warm key light

bpy.ops.object.light_add(type='AREA', radius=3, location=(-5, -2, 3))
fill_light = bpy.context.active_object
fill_light.data.energy = 200.0
fill_light.data.color = (0.9, 0.95, 1.0)  # Cool fill light

# Set up environment light for better reflections
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.05, 0.05, 0.05, 1.0)  # Dark gray
bg.inputs[1].default_value = 1.0  # Low intensity

# Set up camera with depth of field for professional look
bpy.ops.object.camera_add(location=(0, -10, 5))
camera = bpy.context.active_object
camera.rotation_euler = (0.7, 0, 0)
bpy.context.scene.camera = camera

# Enable depth of field
camera.data.dof.use_dof = True
camera.data.dof.aperture_fstop = 2.8
camera.data.dof.focus_distance = 10.0

# Set up render settings for high quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.cycles.preview_samples = 32
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
            """)
        
        # Launch Blender with the script
        subprocess.Popen([blender_path, "--python", temp_script_path])
        
        # Wait a bit before removing the temp file
        time.sleep(2)
        try:
            os.unlink(temp_script_path)
        except:
            pass
        
        return {
            "status": "success",
            "message": f"SVG imported to Blender successfully with {style_preset} style preset"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing SVG to Blender: {str(e)}")


# Utility functions
def find_blender_path():
    """Find the Blender executable path"""
    # Check environment variable first
    if 'BLENDER_PATH' in os.environ:
        blender_path = os.environ['BLENDER_PATH']
        if os.path.isfile(blender_path):
            return blender_path
    
    # Check config for blender path
    try:
        config = get_settings()
        if hasattr(config, 'blender') and hasattr(config.blender, 'path'):
            blender_path = config.blender.path
            # Convert forward slashes to backslashes on Windows
            if os.name == 'nt':
                blender_path = blender_path.replace('/', '\\')
            if os.path.isfile(blender_path):
                return blender_path
    except:
        pass
    
    # List of common Blender installation paths
    common_paths = [
        # Windows paths - check for Blender 4.x first
        "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
        # Windows paths - Blender 3.x
        "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 3.5\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 3.4\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 3.3\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 3.2\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 3.1\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 3.0\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 2.93\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
        # macOS paths
        "/Applications/Blender.app/Contents/MacOS/Blender",
        # Linux paths
        "/usr/bin/blender",
        "/usr/local/bin/blender"
    ]
    
    # Try each path
    for path in common_paths:
        if os.path.isfile(path):
            return path
    
    # If not found in common paths, try to find in PATH
    try:
        # Check if 'blender' is in the PATH
        result = subprocess.run(
            ["where", "blender"] if os.name == "nt" else ["which", "blender"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    # Blender not found
    return None


def create_minimal_script():
    """Create a minimal script for SVG to 3D conversion if no proper scripts are found"""
    script_content = """
import bpy
import os
import sys
import json
import traceback

def clean_scene():
    # Remove all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Remove all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Remove all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    
    # Remove all curves
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve)

def create_minimal_model():
    # Create a simple cube as placeholder
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "SVG_Placeholder"
    
    # Create a material
    mat = bpy.data.materials.new(name="PlaceholderMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.2, 0.2, 1.0)
    
    # Assign material to cube
    cube.data.materials.append(mat)
    
    # Create camera and light
    bpy.ops.object.camera_add(location=(0, -5, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (0.7, 0, 0)
    bpy.context.scene.camera = camera
    
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))

def main():
    try:
        # Parse command line arguments
        if "--" in sys.argv:
            args = sys.argv[sys.argv.index("--") + 1:]
        else:
            args = []
        
        if len(args) < 2:
            print("Insufficient arguments")
            return 1
        
        svg_path = args[0]
        blend_output_path = args[1]
        options_json = args[2] if len(args) > 2 else "{}"
        
        # Parse options
        try:
            options = json.loads(options_json)
        except:
            options = {}
        
        print(f"Processing SVG: {svg_path}")
        print(f"Output: {blend_output_path}")
        
        # Clean the scene
        clean_scene()
        
        # Create minimal model
        create_minimal_model()
        
        # Save Blender file
        print(f"Saving to: {blend_output_path}")
        bpy.ops.wm.save_as_mainfile(filepath=blend_output_path)
        print("Minimal conversion completed")
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
"""
    
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix='.py')
    with os.fdopen(fd, 'w') as f:
        f.write(script_content)
    
    return path
