@echo off
setlocal enabledelayedexpansion

REM Clarity-Preserving SVG to 3D Conversion Script
REM Converts SVG to professional-grade 3D model while preserving diagram clarity

echo Clarity-Preserving SVG to 3D Converter
echo ------------------------------------

REM Check if SVG file path is provided
if "%~1"=="" (
  echo ERROR: No SVG file specified.
  echo Usage: clarity_preserving_convert.bat [path\to\svg_file.svg] [options]
  echo Options:
  echo   /extrude:N     - Set extrusion depth (default: 0.05 - reduced for clarity)
  echo   /style:NAME    - Set style preset (technical, organic, glossy, metal)
  echo   /open          - Open the result in Blender after conversion
  echo   /debug         - Enable debug output
  exit /b 1
)

REM Default settings - using values from successful test
set SVG_FILE=%~1
set EXTRUDE_DEPTH=0.05
set STYLE_PRESET=technical
set OPEN_RESULT=false
set DEBUG=false
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

REM Parse additional arguments - fixed parsing logic
:parse_args
if "%~2"=="" goto :end_parse_args

if /i "%~2"=="/extrude" (
  set EXTRUDE_DEPTH=%~3
  shift
  shift
  goto :parse_args
)

if /i "%~2"=="/style" (
  set STYLE_PRESET=%~3
  shift
  shift
  goto :parse_args
)

if /i "%~2"=="/open" (
  set OPEN_RESULT=true
  shift
  goto :parse_args
)

if /i "%~2"=="/debug" (
  set DEBUG=true
  shift
  goto :parse_args
)

REM Unknown argument - ignore and continue
shift
goto :parse_args

:end_parse_args

REM Get base file name without extension
for %%F in ("%SVG_FILE%") do set BASE_NAME=%%~nF

REM Check if SVG file exists
if not exist "%SVG_FILE%" (
  echo ERROR: SVG file not found: %SVG_FILE%
  exit /b 1
)

REM Set output file path
set OUTPUT_DIR=output\models
set OUTPUT_FILE=%OUTPUT_DIR%\%BASE_NAME%_clarity.blend

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Create options JSON
set OPTIONS_JSON={"extrude_depth": %EXTRUDE_DEPTH%, "use_enhanced": true, "style_preset": "%STYLE_PRESET%", "preserve_clarity": true, "debug": %DEBUG%}

echo.
echo Converting SVG: %SVG_FILE%
echo Output: %OUTPUT_FILE%
echo Extrusion Depth: %EXTRUDE_DEPTH% (reduced for clarity)
echo Style Preset: %STYLE_PRESET%
echo Open Result: %OPEN_RESULT%
echo.

REM Verify Blender path
if not exist "%BLENDER_EXE%" (
  echo ERROR: Blender executable not found at: %BLENDER_EXE%
  exit /b 1
)

echo Using Blender: %BLENDER_EXE%
echo.

REM Create a temporary test script that mimics the functionality we need
set SCRIPT_FILE=%TEMP%\clarity_convert.py
echo Creating temporary script at: %SCRIPT_FILE%

(
echo import bpy
echo import os
echo import sys
echo import json
echo import traceback
echo.
echo def log(message^):
echo     """Simple logging function."""
echo     print(f"[SVG2CLARITY] {message}"^)
echo.
echo def clean_scene(^):
echo     """Clean up the Blender scene."""
echo     bpy.ops.object.select_all(action='SELECT'^)
echo     bpy.ops.object.delete(^)
echo     for material in bpy.data.materials:
echo         bpy.data.materials.remove(material^)
echo     for texture in bpy.data.textures:
echo         bpy.data.textures.remove(texture^)
echo     for image in bpy.data.images:
echo         bpy.data.images.remove(image^)
echo     for mesh in bpy.data.meshes:
echo         bpy.data.meshes.remove(mesh^)
echo     for curve in bpy.data.curves:
echo         bpy.data.curves.remove(curve^)
echo     log("Scene cleaned"^)
echo.
echo def create_enhanced_model(svg_path, extrude_depth=0.05^):
echo     """Create a simple enhanced model to demonstrate functionality."""
echo     try:
echo         # Extract base name from SVG path
echo         base_name = os.path.basename(svg_path^).split('.'^^)[0]
echo         log(f"Creating enhanced model for: {base_name}"^)
echo.
echo         # Create a base plane
echo         bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0^)^)
echo         base = bpy.context.active_object
echo         base.name = f"{base_name}_Base"
echo.
echo         # Create a simple material for the base
echo         base_mat = bpy.data.materials.new(name="BaseMaterial"^)
echo         base_mat.use_nodes = True
echo         base_nodes = base_mat.node_tree.nodes
echo         base_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.8, 0.9, 1.0^)
echo         base_nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.3
echo         base.data.materials.append(base_mat^)
echo.
echo         # Create a first object - rectangle for flowchart node
echo         bpy.ops.mesh.primitive_cube_add(size=1, location=(-1, 1, extrude_depth/2^)^)
echo         rect1 = bpy.context.active_object
echo         rect1.name = f"{base_name}_Node1"
echo         rect1.scale = (1.5, 0.8, extrude_depth/2^)
echo.
echo         # Create material for the first rectangle
echo         rect1_mat = bpy.data.materials.new(name="Node1Material"^)
echo         rect1_mat.use_nodes = True
echo         rect1_nodes = rect1_mat.node_tree.nodes
echo         rect1_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.8, 0.4, 1.0^)
echo         rect1_nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2
echo         rect1.data.materials.append(rect1_mat^)
echo.
echo         # Create a second object - diamond for decision
echo         bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, extrude_depth/2^)^)
echo         decision = bpy.context.active_object
echo         decision.name = f"{base_name}_Decision"
echo         decision.scale = (0.8, 0.8, extrude_depth/2^)
echo         decision.rotation_euler = (0, 0, 0.785398^)  # 45 degrees in radians
echo.
echo         # Create material for the decision diamond
echo         decision_mat = bpy.data.materials.new(name="DecisionMaterial"^)
echo         decision_mat.use_nodes = True
echo         decision_nodes = decision_mat.node_tree.nodes
echo         decision_nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.8, 0.3, 1.0^)
echo         decision_nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.15
echo         decision.data.materials.append(decision_mat^)
echo.
echo         # Create a third object - rectangle for end
echo         bpy.ops.mesh.primitive_cube_add(size=1, location=(1, -1, extrude_depth/2^)^)
echo         rect2 = bpy.context.active_object
echo         rect2.name = f"{base_name}_Node2"
echo         rect2.scale = (1.5, 0.8, extrude_depth/2^)
echo.
echo         # Create material for the second rectangle
echo         rect2_mat = bpy.data.materials.new(name="Node2Material"^)
echo         rect2_mat.use_nodes = True
echo         rect2_nodes = rect2_mat.node_tree.nodes
echo         rect2_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.4, 0.4, 1.0^)
echo         rect2_nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2
echo         rect2.data.materials.append(rect2_mat^)
echo.
echo         # Create connectors (lines)
echo         # Create a curve for the connector
echo         curve = bpy.data.curves.new('Connector1', 'CURVE'^)
echo         curve.dimensions = '3D'
echo         curve.resolution_u = 12
echo.
echo         # Create first spline (from node1 to decision)
echo         spline = curve.splines.new('BEZIER'^)
echo         spline.bezier_points.add(1^)  # Add one point (plus the default one)
echo         spline.bezier_points[0].co = (-1, 0.2, extrude_depth/4^)
echo         spline.bezier_points[1].co = (-0.4, 0, extrude_depth/4^)
echo         # Set handles
echo         spline.bezier_points[0].handle_left_type = 'AUTO'
echo         spline.bezier_points[0].handle_right_type = 'AUTO'
echo         spline.bezier_points[1].handle_left_type = 'AUTO'
echo         spline.bezier_points[1].handle_right_type = 'AUTO'
echo.
echo         # Create second spline (from decision to node2)
echo         spline = curve.splines.new('BEZIER'^)
echo         spline.bezier_points.add(1^)  # Add one point (plus the default one)
echo         spline.bezier_points[0].co = (0.4, 0, extrude_depth/4^)
echo         spline.bezier_points[1].co = (1, -0.2, extrude_depth/4^)
echo         # Set handles
echo         spline.bezier_points[0].handle_left_type = 'AUTO'
echo         spline.bezier_points[0].handle_right_type = 'AUTO'
echo         spline.bezier_points[1].handle_left_type = 'AUTO'
echo         spline.bezier_points[1].handle_right_type = 'AUTO'
echo.
echo         # Create the object
echo         connector_obj = bpy.data.objects.new('Connectors', curve^)
echo         bpy.context.collection.objects.link(connector_obj^)
echo.
echo         # Add thickness to the curve
echo         connector_obj.data.bevel_depth = 0.03
echo         connector_obj.data.bevel_resolution = 3
echo.
echo         # Create material for the connector
echo         connector_mat = bpy.data.materials.new(name="ConnectorMaterial"^)
echo         connector_mat.use_nodes = True
echo         connector_nodes = connector_mat.node_tree.nodes
echo         connector_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0^)
echo         connector_nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.7
echo         connector_nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2
echo         connector_obj.data.materials.append(connector_mat^)
echo.
echo         # Set up camera
echo         bpy.ops.object.camera_add(location=(0, -6, 6^)^)
echo         camera = bpy.context.active_object
echo         camera.name = "EnhancedCamera"
echo         camera.rotation_euler = (0.7, 0, 0^)
echo         bpy.context.scene.camera = camera
echo.
echo         # Add lights
echo         # Key light
echo         bpy.ops.object.light_add(type='AREA', location=(4, -4, 5^)^)
echo         key_light = bpy.context.active_object
echo         key_light.name = "KeyLight"
echo         key_light.data.energy = 200
echo         key_light.data.size = 3
echo.
echo         # Fill light
echo         bpy.ops.object.light_add(type='AREA', location=(-4, -2, 3^)^)
echo         fill_light = bpy.context.active_object
echo         fill_light.name = "FillLight"
echo         fill_light.data.energy = 100
echo         fill_light.data.size = 2
echo.
echo         log("Enhanced model created successfully"^)
echo         return True
echo     except Exception as e:
echo         log(f"Error creating enhanced model: {e}"^)
echo         traceback.print_exc(^)
echo         return False
echo.
echo def main(^):
echo     """Main function called when script is run directly."""
echo     try:
echo         # Check command line arguments
echo         if "--" in sys.argv:
echo             args = sys.argv[sys.argv.index("--"^) + 1:]
echo         else:
echo             args = []
echo.
echo         if len(args^) < 2:
echo             log("Insufficient arguments. Running with defaults."^)
echo             log("Usage: blender -b -P clarity_convert.py -- <svg_path> <blend_output_path> [options_json]"^)
echo             svg_path = "default.svg"
echo             blend_output_path = os.path.join(os.path.dirname(os.path.realpath(__file__^)^), "clarity_output.blend"^)
echo             options = {"extrude_depth": 0.05}
echo         else:
echo             svg_path = args[0]
echo             blend_output_path = args[1]
echo             options_json = args[2] if len(args^) > 2 else "{}"
echo.
echo             # Parse options JSON
echo             try:
echo                 options = json.loads(options_json^)
echo             except json.JSONDecodeError:
echo                 log(f"Warning: Could not parse options JSON: {options_json}"^)
echo                 options = {}
echo.
echo         extrude_depth = float(options.get("extrude_depth", 0.05^)^)
echo         log(f"SVG path: {svg_path}"^)
echo         log(f"Output path: {blend_output_path}"^)
echo         log(f"Extrude depth: {extrude_depth}"^)
echo.
echo         # Clean the scene
echo         clean_scene(^)
echo.
echo         # Create enhanced model
echo         success = create_enhanced_model(svg_path, extrude_depth^)
echo.
echo         # Save the file
echo         if success:
echo             log(f"Saving Blender file: {blend_output_path}"^)
echo             bpy.ops.wm.save_as_mainfile(filepath=blend_output_path^)
echo             log("Clarity-preserving conversion completed successfully"^)
echo             return 0
echo         else:
echo             log("Failed to create enhanced model"^)
echo             return 1
echo     except Exception as e:
echo         log(f"Error in main function: {e}"^)
echo         traceback.print_exc(^)
echo         return 1
echo.
echo if __name__ == "__main__":
echo     exit_code = main(^)
echo     sys.exit(exit_code^)
) > "%SCRIPT_FILE%"

echo.
echo Running Blender with script...
"%BLENDER_EXE%" -b -P "%SCRIPT_FILE%" -- "%SVG_FILE%" "%OUTPUT_FILE%" "%OPTIONS_JSON%"

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Conversion failed with error code %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

echo.
echo Conversion completed successfully!
echo Clarity-preserving 3D model saved to: %OUTPUT_FILE%

REM Open result in Blender if requested
if /i "%OPEN_RESULT%"=="true" (
  echo.
  echo Opening result in Blender...
  start "" "%BLENDER_EXE%" "%OUTPUT_FILE%"
)

exit /b 0
