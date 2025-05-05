"""
Animation System for SVG to Video Pipeline

This module handles the application of animations to 3D models generated from SVG diagrams.
It analyzes the diagram structure and applies appropriate animations based on the content.
"""

import os
import asyncio
import logging
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class AnimationSystem:
    """
    System for adding animations to 3D models generated from SVG diagrams.
    Integrates with Blender for animation creation.
    """
    
    def __init__(self, debug=False):
        """
        Initialize the Animation System.
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        
        # Get Blender path from environment
        self.blender_path = os.environ.get("BLENDER_PATH", "blender")
        
        # Animation script paths
        self.scripts_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
        self.animation_script = os.path.join(self.scripts_dir, "animate_model.py")
        
        # Create scripts directory if it doesn't exist
        os.makedirs(self.scripts_dir, exist_ok=True)
        
        if self.debug:
            logger.info("Animation System initialized")
            logger.info(f"Blender path: {self.blender_path}")
            logger.info(f"Animation script: {self.animation_script}")
    
    async def animate_model(
        self,
        model_path: str,
        output_path: str,
        animation_type: str = "standard",
        duration: int = 10
    ) -> bool:
        """
        Animate a 3D model using Blender.
        
        Args:
            model_path: Path to input 3D model file (.blend)
            output_path: Path to save animated model file
            animation_type: Type of animation to apply (standard, flowchart, network)
            duration: Animation duration in seconds
            
        Returns:
            True if animation was successful, False otherwise
        """
        try:
            if self.debug:
                logger.info(f"Animating model: {model_path}")
                logger.info(f"Animation type: {animation_type}")
                logger.info(f"Duration: {duration} seconds")
            
            # Create animation script if it doesn't exist
            await self._ensure_animation_script_exists()
            
            # Build Blender command
            cmd = [
                self.blender_path,
                "--background",
                model_path,
                "--python",
                self.animation_script,
                "--",
                "--output", output_path,
                "--type", animation_type,
                "--duration", str(duration)
            ]
            
            # Run Blender process
            if self.debug:
                logger.info(f"Running command: {' '.join(cmd)}")
            
            # Create log files
            log_dir = os.path.dirname(output_path)
            log_base = os.path.splitext(os.path.basename(output_path))[0]
            log_file = os.path.join(log_dir, f"{log_base}.log")
            err_file = os.path.join(log_dir, f"{log_base}.err")
            
            # Run process
            with open(log_file, "w") as log, open(err_file, "w") as err:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=log,
                    stderr=err
                )
                await process.wait()
            
            # Check if process was successful
            if process.returncode != 0:
                logger.error(f"Animation failed with code {process.returncode}")
                return False
            
            # Check if output file was created
            if not os.path.exists(output_path):
                logger.error("Animation file was not created")
                return False
            
            logger.info(f"Animation completed successfully: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error in animate_model: {str(e)}")
            return False
    
    async def _ensure_animation_script_exists(self) -> bool:
        """
        Ensure the animation script exists. Create it if it doesn't.
        
        Returns:
            True if script exists or was created, False otherwise
        """
        if os.path.exists(self.animation_script):
            return True
        
        try:
            # Create scripts directory if it doesn't exist
            os.makedirs(os.path.dirname(self.animation_script), exist_ok=True)
            
            # Create animation script
            script_content = """
import bpy
import argparse
import sys
import os
import math
import random

def parse_args():
    \"\"\"Parse command line arguments.\"\"\"
    parser = argparse.ArgumentParser(description='Animate 3D model from command line')
    
    # Add the arguments
    parser.add_argument('--output', type=str, required=True, help='Output file path')
    parser.add_argument('--type', type=str, default='standard', help='Animation type (standard, flowchart, network)')
    parser.add_argument('--duration', type=int, default=10, help='Animation duration in seconds')
    
    # Extract arguments after '--'
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    return args

def setup_animation(duration):
    \"\"\"Set up the animation parameters.\"\"\"
    # Set the frame range
    fps = 30
    frames = duration * fps
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    bpy.context.scene.render.fps = fps
    
    # Clear any existing animation
    for obj in bpy.data.objects:
        if obj.animation_data:
            obj.animation_data_clear()
    
    return frames

def animate_standard(frames):
    \"\"\"Apply standard animation to all objects.\"\"\"
    # Get all mesh and curve objects
    objects = [obj for obj in bpy.data.objects if obj.type in ['MESH', 'CURVE', 'FONT']]
    
    if not objects:
        print("No objects found to animate")
        return
    
    # Sort objects by size (to animate smaller objects first)
    objects.sort(key=lambda obj: obj.dimensions.x * obj.dimensions.y)
    
    # Set up animation parameters
    delay_per_object = frames / (len(objects) + 1)
    
    # Animate each object
    for i, obj in enumerate(objects):
        # Calculate start and end frames for this object
        start_frame = 1 + int(i * delay_per_object)
        mid_frame = start_frame + int(frames / (len(objects) * 2))
        end_frame = frames
        
        # Initialize object properties at start
        obj.scale = (0, 0, 0)
        obj.keyframe_insert(data_path="scale", frame=1)
        
        # Scale up animation
        obj.scale = (1, 1, 1)
        obj.keyframe_insert(data_path="scale", frame=start_frame + 10)
        
        # Add slight rotation for interest
        if random.random() > 0.5:  # 50% chance of rotation
            obj.rotation_euler = (0, 0, 0)
            obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)
            
            obj.rotation_euler = (0, 0, math.radians(5))  # Small rotation for subtlety
            obj.keyframe_insert(data_path="rotation_euler", frame=mid_frame)
            
            obj.rotation_euler = (0, 0, 0)
            obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    
    # Animate camera
    camera = None
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            camera = obj
            break
    
    if camera:
        # Start camera animation
        camera.location = camera.location
        camera.keyframe_insert(data_path="location", frame=1)
        
        # Slightly move camera for interest
        original_loc = camera.location.copy()
        camera.location = (original_loc.x * 1.1, original_loc.y * 1.1, original_loc.z)
        camera.keyframe_insert(data_path="location", frame=frames // 2)
        
        # Return to original position
        camera.location = original_loc
        camera.keyframe_insert(data_path="location", frame=frames)

def animate_flowchart(frames):
    \"\"\"Apply flowchart-specific animation.\"\"\"
    # Get all mesh and curve objects
    objects = [obj for obj in bpy.data.objects if obj.type in ['MESH', 'CURVE', 'FONT']]
    
    if not objects:
        print("No objects found to animate")
        return
    
    # Try to identify flowchart elements by location and type
    # Typically rectangles are process steps, diamonds are decisions, lines are connectors
    
    # Group objects by their Y position to identify rows
    row_tolerance = 0.2  # Tolerance for considering objects in the same row
    rows = {}
    
    for obj in objects:
        y_pos = obj.location.y
        
        # Find the appropriate row
        row_key = None
        for key in rows.keys():
            if abs(key - y_pos) < row_tolerance:
                row_key = key
                break
        
        if row_key is None:
            row_key = y_pos
            rows[row_key] = []
        
        rows[row_key].append(obj)
    
    # Sort rows by Y position (top to bottom)
    sorted_rows = sorted(rows.items(), key=lambda x: -x[0])
    
    # Calculate frames per row
    frames_per_row = frames / (len(sorted_rows) + 1)
    
    # Animate each row sequentially
    for i, (y_pos, row_objects) in enumerate(sorted_rows):
        start_frame = 1 + int(i * frames_per_row)
        
        # Sort objects in row by X position (left to right)
        row_objects.sort(key=lambda obj: obj.location.x)
        
        # Calculate frames per object
        frames_per_object = frames_per_row / (len(row_objects) + 1)
        
        # Animate each object in the row
        for j, obj in enumerate(row_objects):
            obj_start_frame = start_frame + int(j * frames_per_object)
            
            # Initial state (invisible)
            obj.scale = (0, 0, 0)
            obj.keyframe_insert(data_path="scale", frame=1)
            
            # Appear animation
            obj.scale = (1, 1, 1)
            obj.keyframe_insert(data_path="scale", frame=obj_start_frame)
            
            # For each object, add a highlight animation
            if obj.data.materials:
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.node_tree:
                        # Try to find Principled BSDF node
                        for node in mat_slot.material.node_tree.nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                # Create a copy of the original color
                                original_color = node.inputs['Base Color'].default_value[:]
                                
                                # Set keyframe for original color
                                node.inputs['Base Color'].default_value = original_color
                                node.inputs['Base Color'].keyframe_insert('default_value', frame=obj_start_frame)
                                
                                # Set highlight color (slightly brighter)
                                highlight_color = (
                                    min(original_color[0] * 1.5, 1.0),
                                    min(original_color[1] * 1.5, 1.0),
                                    min(original_color[2] * 1.5, 1.0),
                                    original_color[3]
                                )
                                node.inputs['Base Color'].default_value = highlight_color
                                node.inputs['Base Color'].keyframe_insert('default_value', frame=obj_start_frame + 15)
                                
                                # Return to original color
                                node.inputs['Base Color'].default_value = original_color
                                node.inputs['Base Color'].keyframe_insert('default_value', frame=obj_start_frame + 30)
                                break

def animate_network(frames):
    \"\"\"Apply network diagram-specific animation.\"\"\"
    # Get all mesh and curve objects
    objects = [obj for obj in bpy.data.objects if obj.type in ['MESH', 'CURVE', 'FONT']]
    
    if not objects:
        print("No objects found to animate")
        return
    
    # Identify potential nodes (circles/ellipses) and connections (lines/paths)
    nodes = []
    connections = []
    
    for obj in objects:
        # Rough heuristic: nodes are typically more square-like in bounding box
        dimensions = obj.dimensions
        aspect_ratio = max(dimensions.x, dimensions.y) / max(0.001, min(dimensions.x, dimensions.y))
        
        if aspect_ratio < 3 and obj.type == 'MESH':  # Likely a node
            nodes.append(obj)
        elif aspect_ratio >= 3 or obj.type == 'CURVE':  # Likely a connection
            connections.append(obj)
    
    # If no clear separation is found, use a fallback approach
    if not nodes or not connections:
        # Assume larger objects are nodes and smaller ones are connections
        all_objects = sorted(objects, key=lambda obj: obj.dimensions.x * obj.dimensions.y, reverse=True)
        split_point = max(1, len(all_objects) // 3)
        nodes = all_objects[:split_point]
        connections = all_objects[split_point:]
    
    # Start with nodes animation
    node_frames = frames // 2
    frames_per_node = node_frames / (len(nodes) + 1)
    
    for i, node in enumerate(nodes):
        start_frame = 1 + int(i * frames_per_node)
        
        # Initial state (invisible)
        node.scale = (0, 0, 0)
        node.keyframe_insert(data_path="scale", frame=1)
        
        # Appear animation with slight bounce
        node.scale = (1.2, 1.2, 1.2)  # Overshoot
        node.keyframe_insert(data_path="scale", frame=start_frame)
        
        node.scale = (1, 1, 1)  # Settle
        node.keyframe_insert(data_path="scale", frame=start_frame + 10)
    
    # Then connections animation
    connection_start = node_frames
    frames_per_connection = (frames - connection_start) / (len(connections) + 1)
    
    for i, connection in enumerate(connections):
        start_frame = connection_start + int(i * frames_per_connection)
        
        # For curves, animate growth
        if connection.type == 'CURVE':
            # Set initial state
            connection.data.bevel_factor_end = 0
            connection.keyframe_insert(data_path="data.bevel_factor_end", frame=1)
            
            # Animate growth along curve
            connection.data.bevel_factor_end = 1
            connection.keyframe_insert(data_path="data.bevel_factor_end", frame=start_frame + 20)
        else:
            # For other objects, use scale animation
            connection.scale = (0, 0, 0)
            connection.keyframe_insert(data_path="scale", frame=1)
            
            connection.scale = (1, 1, 1)
            connection.keyframe_insert(data_path="scale", frame=start_frame + 20)
    
    # Add pulse effect to nodes
    for node in nodes:
        if node.data.materials:
            for mat_slot in node.material_slots:
                if mat_slot.material and mat_slot.material.node_tree:
                    # Try to find Principled BSDF node
                    for node_tree_node in mat_slot.material.node_tree.nodes:
                        if node_tree_node.type == 'BSDF_PRINCIPLED':
                            # Add pulse effect to emission
                            if 'Emission Strength' in node_tree_node.inputs:
                                # Initial state
                                node_tree_node.inputs['Emission Strength'].default_value = 0
                                node_tree_node.inputs['Emission Strength'].keyframe_insert('default_value', frame=1)
                                
                                # Pulse intervals
                                for pulse in range(3):
                                    pulse_frame = frames // 4 * (pulse + 1)
                                    
                                    # Pulse on
                                    node_tree_node.inputs['Emission Strength'].default_value = 1
                                    node_tree_node.inputs['Emission Strength'].keyframe_insert('default_value', frame=pulse_frame)
                                    
                                    # Pulse off
                                    node_tree_node.inputs['Emission Strength'].default_value = 0
                                    node_tree_node.inputs['Emission Strength'].keyframe_insert('default_value', frame=pulse_frame + 15)

def animate_sequence(frames):
    \"\"\"Apply sequence diagram-specific animation.\"\"\"
    # Get all mesh and curve objects
    objects = [obj for obj in bpy.data.objects if obj.type in ['MESH', 'CURVE', 'FONT']]
    
    if not objects:
        print("No objects found to animate")
        return
    
    # In sequence diagrams, we often have:
    # 1. Actors/lifelines (vertical objects at the top)
    # 2. Messages (horizontal arrows)
    # 3. Activations (vertical rectangles on lifelines)
    
    # Sort objects by Y position (top to bottom)
    objects.sort(key=lambda obj: -obj.location.y)
    
    # First tier objects are likely the actors
    actors = []
    messages = []
    activations = []
    
    # Simple heuristic: top row of objects are actors
    y_pos_first = objects[0].location.y
    tolerance = 0.5
    
    for obj in objects:
        if abs(obj.location.y - y_pos_first) < tolerance:
            actors.append(obj)
        elif abs(obj.dimensions.x / max(0.001, obj.dimensions.y)) > 3:
            # Horizontal elements are likely messages
            messages.append(obj)
        else:
            # Other elements might be activations or other components
            activations.append(obj)
    
    # Sort messages by Y position (top to bottom) - they should be animated in sequence
    messages.sort(key=lambda obj: -obj.location.y)
    
    # Animate actors first
    actor_frames = frames // 5
    frames_per_actor = actor_frames / (len(actors) + 1)
    
    for i, actor in enumerate(actors):
        start_frame = 1 + int(i * frames_per_actor)
        
        # Initial state (invisible)
        actor.scale = (0, 0, 0)
        actor.keyframe_insert(data_path="scale", frame=1)
        
        # Appear animation
        actor.scale = (1, 1, 1)
        actor.keyframe_insert(data_path="scale", frame=start_frame)
    
    # Then animate messages in sequence
    message_start = actor_frames
    message_frames = (frames - message_start) * 3 // 4
    frames_per_message = message_frames / (len(messages) + 1)
    
    for i, message in enumerate(messages):
        start_frame = message_start + int(i * frames_per_message)
        
        # For curves, animate growth
        if message.type == 'CURVE':
            # Set initial state
            message.data.bevel_factor_end = 0
            message.keyframe_insert(data_path="data.bevel_factor_end", frame=1)
            
            # Animate growth along curve
            message.data.bevel_factor_end = 1
            message.keyframe_insert(data_path="data.bevel_factor_end", frame=start_frame + 15)
        else:
            # For other objects, use scale animation
            message.scale = (0, 1, 1)  # Start with zero width
            message.keyframe_insert(data_path="scale", frame=1)
            
            message.scale = (1, 1, 1)
            message.keyframe_insert(data_path="scale", frame=start_frame + 15)
        
        # Find activation that might be triggered by this message
        for activation in activations:
            # If activation is near the message endpoint
            if abs(activation.location.x - message.location.x) < tolerance and activation.location.y < message.location.y:
                # Animate the activation appearing
                activation.scale = (0, 0, 0)
                activation.keyframe_insert(data_path="scale", frame=1)
                
                activation.scale = (1, 1, 1)
                activation.keyframe_insert(data_path="scale", frame=start_frame + 20)

def save_blender_file(output_path):
    \"\"\"Save the Blender file.\"\"\"
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the Blender file
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"Saved animated file to: {output_path}")

def main():
    # Parse command line arguments
    args = parse_args()
    
    print(f"Animation type: {args.type}")
    print(f"Duration: {args.duration} seconds")
    print(f"Output path: {args.output}")
    
    # Setup animation parameters
    frames = setup_animation(args.duration)
    
    # Apply appropriate animation based on type
    if args.type == "flowchart":
        animate_flowchart(frames)
    elif args.type == "network":
        animate_network(frames)
    elif args.type == "sequence":
        animate_sequence(frames)
    else:
        animate_standard(frames)
    
    # Save the file
    save_blender_file(args.output)
    print("Animation complete!")

if __name__ == "__main__":
    main()
            """
            
            # Write the script to file
            with open(self.animation_script, "w") as f:
                f.write(script_content)
            
            logger.info(f"Created animation script at {self.animation_script}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating animation script: {str(e)}")
            return False
