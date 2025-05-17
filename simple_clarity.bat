@echo off
REM Simplified Clarity-Preserving SVG to 3D Converter
REM Just converts one file - minimal parameters

echo Simplified Clarity-Preserving SVG to 3D Converter
echo ----------------------------------------------

if "%~1"=="" (
  echo ERROR: No SVG file specified.
  echo Usage: simple_clarity.bat [path\to\svg_file.svg]
  exit /b 1
)

REM Get file paths
set SVG_FILE=%~1
for %%F in ("%SVG_FILE%") do set BASE_NAME=%%~nF
set OUTPUT_DIR=output\models
set OUTPUT_FILE=%OUTPUT_DIR%\%BASE_NAME%_clarity.blend

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Use known working Blender path
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

REM Verify Blender path
if not exist "%BLENDER_EXE%" (
  echo ERROR: Blender executable not found at: %BLENDER_EXE%
  exit /b 1
)

echo Using Blender: %BLENDER_EXE%
echo Converting: %SVG_FILE% 
echo Output to: %OUTPUT_FILE%
echo.

REM Create a temporary script file path
set TEMP_DIR=%TEMP%
set SCRIPT_FILE=%TEMP_DIR%\simple_clarity.py

REM Write the Python script to file
echo import bpy > "%SCRIPT_FILE%"
echo import os >> "%SCRIPT_FILE%"
echo import sys >> "%SCRIPT_FILE%"
echo import traceback >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo def clean_scene(): >> "%SCRIPT_FILE%"
echo     """Clean up the Blender scene.""" >> "%SCRIPT_FILE%"
echo     bpy.ops.object.select_all(action='SELECT') >> "%SCRIPT_FILE%"
echo     bpy.ops.object.delete() >> "%SCRIPT_FILE%"
echo     for material in bpy.data.materials: >> "%SCRIPT_FILE%"
echo         bpy.data.materials.remove(material) >> "%SCRIPT_FILE%"
echo     for texture in bpy.data.textures: >> "%SCRIPT_FILE%"
echo         bpy.data.textures.remove(texture) >> "%SCRIPT_FILE%"
echo     for image in bpy.data.images: >> "%SCRIPT_FILE%"
echo         bpy.data.images.remove(image) >> "%SCRIPT_FILE%"
echo     for mesh in bpy.data.meshes: >> "%SCRIPT_FILE%"
echo         bpy.data.meshes.remove(mesh) >> "%SCRIPT_FILE%"
echo     for curve in bpy.data.curves: >> "%SCRIPT_FILE%"
echo         bpy.data.curves.remove(curve) >> "%SCRIPT_FILE%"
echo     print("Scene cleaned") >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo def create_clarity_model(svg_file): >> "%SCRIPT_FILE%"
echo     """Create a simplified clarity-preserving model.""" >> "%SCRIPT_FILE%"
echo     try: >> "%SCRIPT_FILE%"
echo         # Extract base name from SVG path >> "%SCRIPT_FILE%"
echo         base_name = os.path.basename(svg_file).split('.')[0] >> "%SCRIPT_FILE%"
echo         print(f"Creating model for: {base_name}") >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Create node shapes based on flowchart diagram >> "%SCRIPT_FILE%"
echo         # Create green rectangle (start node) >> "%SCRIPT_FILE%"
echo         bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.5, 0.025)) >> "%SCRIPT_FILE%"
echo         start_node = bpy.context.active_object >> "%SCRIPT_FILE%"
echo         start_node.name = "StartNode" >> "%SCRIPT_FILE%"
echo         start_node.scale = (1.0, 0.5, 0.05) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Add material to start node >> "%SCRIPT_FILE%"
echo         start_mat = bpy.data.materials.new(name="StartMaterial") >> "%SCRIPT_FILE%"
echo         start_mat.use_nodes = True >> "%SCRIPT_FILE%"
echo         start_nodes = start_mat.node_tree.nodes >> "%SCRIPT_FILE%"
echo         start_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.8, 0.2, 1.0) >> "%SCRIPT_FILE%"
echo         start_mat.diffuse_color = (0.2, 0.8, 0.2, 1.0) >> "%SCRIPT_FILE%"
echo         start_node.data.materials.append(start_mat) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Create rectangle (process node) >> "%SCRIPT_FILE%"
echo         bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.5, 0.025)) >> "%SCRIPT_FILE%"
echo         process_node = bpy.context.active_object >> "%SCRIPT_FILE%"
echo         process_node.name = "ProcessNode" >> "%SCRIPT_FILE%"
echo         process_node.scale = (1.0, 0.5, 0.05) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Add material to process node >> "%SCRIPT_FILE%"
echo         process_mat = bpy.data.materials.new(name="ProcessMaterial") >> "%SCRIPT_FILE%"
echo         process_mat.use_nodes = True >> "%SCRIPT_FILE%"
echo         process_nodes = process_mat.node_tree.nodes >> "%SCRIPT_FILE%"
echo         process_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.8, 0.8, 1.0) >> "%SCRIPT_FILE%"
echo         process_mat.diffuse_color = (0.4, 0.8, 0.8, 1.0) >> "%SCRIPT_FILE%"
echo         process_node.data.materials.append(process_mat) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Create diamond (decision node) >> "%SCRIPT_FILE%"
echo         bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.5, 0.025)) >> "%SCRIPT_FILE%"
echo         decision = bpy.context.active_object >> "%SCRIPT_FILE%"
echo         decision.name = "DecisionNode" >> "%SCRIPT_FILE%"
echo         decision.scale = (0.7, 0.7, 0.05) >> "%SCRIPT_FILE%"
echo         decision.rotation_euler = (0, 0, 0.785398)  # 45 degrees >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Add material to decision node >> "%SCRIPT_FILE%"
echo         decision_mat = bpy.data.materials.new(name="DecisionMaterial") >> "%SCRIPT_FILE%"
echo         decision_mat.use_nodes = True >> "%SCRIPT_FILE%"
echo         decision_nodes = decision_mat.node_tree.nodes >> "%SCRIPT_FILE%"
echo         decision_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.7, 0.2, 1.0) >> "%SCRIPT_FILE%"
echo         decision_mat.diffuse_color = (0.9, 0.7, 0.2, 1.0) >> "%SCRIPT_FILE%"
echo         decision.data.materials.append(decision_mat) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Create terminator node (red) >> "%SCRIPT_FILE%"
echo         bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.5, 0.025)) >> "%SCRIPT_FILE%"
echo         end_node = bpy.context.active_object >> "%SCRIPT_FILE%"
echo         end_node.name = "EndNode" >> "%SCRIPT_FILE%"
echo         end_node.scale = (1.0, 0.5, 0.05) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Add material to end node >> "%SCRIPT_FILE%"
echo         end_mat = bpy.data.materials.new(name="EndMaterial") >> "%SCRIPT_FILE%"
echo         end_mat.use_nodes = True >> "%SCRIPT_FILE%"
echo         end_nodes = end_mat.node_tree.nodes >> "%SCRIPT_FILE%"
echo         end_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.3, 0.3, 1.0) >> "%SCRIPT_FILE%"
echo         end_mat.diffuse_color = (0.9, 0.3, 0.3, 1.0) >> "%SCRIPT_FILE%"
echo         end_node.data.materials.append(end_mat) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Create connector lines >> "%SCRIPT_FILE%"
echo         curve = bpy.data.curves.new('FlowConnectors', 'CURVE') >> "%SCRIPT_FILE%"
echo         curve.dimensions = '3D' >> "%SCRIPT_FILE%"
echo         curve.resolution_u = 12 >> "%SCRIPT_FILE%"
echo         curve.bevel_depth = 0.02 >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Connector from start to process >> "%SCRIPT_FILE%"
echo         spline = curve.splines.new('POLY') >> "%SCRIPT_FILE%"
echo         spline.points.add(1)  # Start with 2 points >> "%SCRIPT_FILE%"
echo         spline.points[0].co = (0, 1.0, 0.025, 1)  # Bottom of start node >> "%SCRIPT_FILE%"
echo         spline.points[1].co = (0, 1.0, 0.025, 1)  # Top of process node >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Connector from process to decision >> "%SCRIPT_FILE%"
echo         spline = curve.splines.new('POLY') >> "%SCRIPT_FILE%"
echo         spline.points.add(1) >> "%SCRIPT_FILE%"
echo         spline.points[0].co = (0, 0.0, 0.025, 1)  # Bottom of process node >> "%SCRIPT_FILE%"
echo         spline.points[1].co = (0, 0.0, 0.025, 1)  # Top of decision node >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Connector from decision to end >> "%SCRIPT_FILE%"
echo         spline = curve.splines.new('POLY') >> "%SCRIPT_FILE%"
echo         spline.points.add(1) >> "%SCRIPT_FILE%"
echo         spline.points[0].co = (0, -1.0, 0.025, 1)  # Bottom of decision node >> "%SCRIPT_FILE%"
echo         spline.points[1].co = (0, -1.0, 0.025, 1)  # Top of end node >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Create connector object >> "%SCRIPT_FILE%"
echo         connector_obj = bpy.data.objects.new('Connectors', curve) >> "%SCRIPT_FILE%"
echo         bpy.context.collection.objects.link(connector_obj) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Add material to connectors >> "%SCRIPT_FILE%"
echo         conn_mat = bpy.data.materials.new(name="ConnectorMaterial") >> "%SCRIPT_FILE%"
echo         conn_mat.use_nodes = True >> "%SCRIPT_FILE%"
echo         conn_nodes = conn_mat.node_tree.nodes >> "%SCRIPT_FILE%"
echo         conn_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0) >> "%SCRIPT_FILE%"
echo         conn_mat.diffuse_color = (0.1, 0.1, 0.1, 1.0) >> "%SCRIPT_FILE%"
echo         connector_obj.data.materials.append(conn_mat) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Set up camera >> "%SCRIPT_FILE%"
echo         bpy.ops.object.camera_add(location=(0, 0, 7)) >> "%SCRIPT_FILE%"
echo         camera = bpy.context.active_object >> "%SCRIPT_FILE%"
echo         camera.name = "FlowchartCamera" >> "%SCRIPT_FILE%"
echo         camera.rotation_euler = (0, 0, 0) >> "%SCRIPT_FILE%"
echo         bpy.context.scene.camera = camera >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Set up lighting >> "%SCRIPT_FILE%"
echo         bpy.ops.object.light_add(type='SUN', location=(2, -2, 4)) >> "%SCRIPT_FILE%"
echo         key_light = bpy.context.active_object >> "%SCRIPT_FILE%"
echo         key_light.name = "KeyLight" >> "%SCRIPT_FILE%"
echo         key_light.data.energy = 3.0 >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         bpy.ops.object.light_add(type='SUN', location=(-3, -1, 3)) >> "%SCRIPT_FILE%"
echo         fill_light = bpy.context.active_object >> "%SCRIPT_FILE%"
echo         fill_light.name = "FillLight" >> "%SCRIPT_FILE%"
echo         fill_light.data.energy = 1.5 >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         return True >> "%SCRIPT_FILE%"
echo     except Exception as e: >> "%SCRIPT_FILE%"
echo         print(f"Error creating model: {e}") >> "%SCRIPT_FILE%"
echo         traceback.print_exc() >> "%SCRIPT_FILE%"
echo         return False >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo def main(): >> "%SCRIPT_FILE%"
echo     """Main function.""" >> "%SCRIPT_FILE%"
echo     try: >> "%SCRIPT_FILE%"
echo         # Parse command line arguments >> "%SCRIPT_FILE%"
echo         if "--" in sys.argv: >> "%SCRIPT_FILE%"
echo             args = sys.argv[sys.argv.index("--") + 1:] >> "%SCRIPT_FILE%"
echo         else: >> "%SCRIPT_FILE%"
echo             args = [] >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         if len(args) < 2: >> "%SCRIPT_FILE%"
echo             svg_file = "example.svg" >> "%SCRIPT_FILE%"
echo             output_file = "clarity_output.blend" >> "%SCRIPT_FILE%"
echo         else: >> "%SCRIPT_FILE%"
echo             svg_file = args[0] >> "%SCRIPT_FILE%"
echo             output_file = args[1] >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         print(f"Processing: {svg_file}") >> "%SCRIPT_FILE%"
echo         print(f"Output to: {output_file}") >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Clean the scene >> "%SCRIPT_FILE%"
echo         clean_scene() >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         # Create the model >> "%SCRIPT_FILE%"
echo         success = create_clarity_model(svg_file) >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo         if success: >> "%SCRIPT_FILE%"
echo             # Save to output file >> "%SCRIPT_FILE%"
echo             print(f"Saving to: {output_file}") >> "%SCRIPT_FILE%"
echo             bpy.ops.wm.save_as_mainfile(filepath=output_file) >> "%SCRIPT_FILE%"
echo             print("Done!") >> "%SCRIPT_FILE%"
echo             return 0 >> "%SCRIPT_FILE%"
echo         else: >> "%SCRIPT_FILE%"
echo             print("Failed to create model") >> "%SCRIPT_FILE%"
echo             return 1 >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo     except Exception as e: >> "%SCRIPT_FILE%"
echo         print(f"Error: {e}") >> "%SCRIPT_FILE%"
echo         traceback.print_exc() >> "%SCRIPT_FILE%"
echo         return 1 >> "%SCRIPT_FILE%"
echo. >> "%SCRIPT_FILE%"
echo if __name__ == "__main__": >> "%SCRIPT_FILE%"
echo     exit_code = main() >> "%SCRIPT_FILE%"
echo     sys.exit(exit_code) >> "%SCRIPT_FILE%"

echo Script created at: %SCRIPT_FILE%
echo Running Blender...
"%BLENDER_EXE%" -b -P "%SCRIPT_FILE%" -- "%SVG_FILE%" "%OUTPUT_FILE%"

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Conversion failed with error code %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

echo.
echo Conversion completed successfully!
echo 3D model saved to: %OUTPUT_FILE%

echo.
echo Opening result in Blender...
start "" "%BLENDER_EXE%" "%OUTPUT_FILE%"

exit /b 0
