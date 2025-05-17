@echo off
setlocal enabledelayedexpansion

echo Simple Blender Test Script
echo -----------------------

REM EDIT THIS LINE TO POINT TO YOUR BLENDER EXECUTABLE
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

echo Checking the Blender path: !BLENDER_EXE!

if not exist "!BLENDER_EXE!" (
  echo ERROR: Blender not found at the specified path.
  echo Please edit this script and set BLENDER_EXE to your Blender executable path.
  exit /b 1
)

echo Blender found at: !BLENDER_EXE!
echo.

REM Create a simple Python script for Blender
set SCRIPT_FILE=%TEMP%\simple_test.py
echo Creating test script: !SCRIPT_FILE!

(
echo import bpy
echo import os
echo import sys
echo.
echo # Clean the scene
echo bpy.ops.object.select_all(action='SELECT'^)
echo bpy.ops.object.delete(^)
echo.
echo # Create a simple cube
echo bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0^)^)
echo cube = bpy.context.active_object
echo cube.name = "TestCube"
echo.
echo # Create a simple material
echo mat = bpy.data.materials.new(name="TestMaterial"^)
echo mat.use_nodes = True
echo nodes = mat.node_tree.nodes
echo nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.2, 0.2, 1.0^)
echo.
echo # Assign material to cube
echo cube.data.materials.append(mat^)
echo.
echo # Set up camera and lighting
echo bpy.ops.object.camera_add(location=(0, -7, 3^)^)
echo camera = bpy.context.active_object
echo camera.rotation_euler = (1.0, 0, 0^)
echo bpy.context.scene.camera = camera
echo.
echo bpy.ops.object.light_add(type='SUN', location=(5, -5, 10^)^)
echo.
echo # Save the file
echo output_path = os.path.join(os.path.dirname(os.path.realpath(__file__^)^), "simple_test_output.blend"^)
echo print(f"Saving test file to: {output_path}"^)
echo bpy.ops.wm.save_as_mainfile(filepath=output_path^)
echo.
echo print("Test script completed successfully"^)
) > "!SCRIPT_FILE!"

echo Script created.
echo.

REM Run Blender with the test script
echo Running Blender with test script...
"!BLENDER_EXE!" -b -P "!SCRIPT_FILE!"

if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Blender script failed with error code %ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

echo.
echo Test completed successfully!
echo Output saved to: %TEMP%\simple_test_output.blend
echo.

REM Open the output file
echo Opening file in Blender...
start "" "!BLENDER_EXE!" "%TEMP%\simple_test_output.blend"

exit /b 0
