"""
SceneX Animation Blender Script

This script is executed by Blender to apply animations to 3D objects.
It identifies different types of objects and applies appropriate animations.

Usage:
    blender --background --python scenex_animation.py -- input.blend output.blend [animation_type] [duration]
"""

import bpy
import sys
import os
import math
import random

class SceneXAnimation:
    """Apply animations to 3D objects in a Blender scene."""
    
    def __init__(self, blend_file, animation_type="standard", duration=250):
        """
        Initialize with a blend file path and animation settings.
        
        Args:
            blend_file: Path to the input Blender file
            animation_type: Type of animation (standard, flowchart, network)
            duration: Animation duration in frames
        """
        self.blend_file = blend_file
        self.animation_type = animation_type
        self.duration = int(duration)
        
        # Open the Blender file
        bpy.ops.wm.open_mainfile(filepath=blend_file)
        
        # Set up animation settings
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = self.duration
        bpy.context.scene.render.fps = 30
        
        # Get all objects in the scene
        self.objects = [obj for obj in bpy.context.scene.objects 
                       if obj.type in ('MESH', 'CURVE', 'FONT')]
        
        # Separate objects by type for animation
        self.nodes = [obj for obj in self.objects if self._is_node(obj)]
        self.connectors = [obj for obj in self.objects if self._is_connector(obj)]
        self.labels = [obj for obj in self.objects if self._is_label(obj)]
        
        print(f"Found {len(self.nodes)} nodes, {len(self.connectors)} connectors, and {len(self.labels)} labels")
    
    def _is_node(self, obj):
        """Determine if an object is a node (e.g., rectangle, circle)."""
        # Simple heuristic: nodes are usually wider than they are tall
        if obj.type == 'MESH':
            dims = obj.dimensions
            return dims.x > 0.1 and dims.y > 0.1 and dims.z < 0.2
        return False
    
    def _is_connector(self, obj):
        """Determine if an object is a connector (e.g., line, path)."""
        # Simple heuristic: connectors are usually long and thin
        if obj.type == 'MESH':
            dims = obj.dimensions
            return (dims.x > dims.y * 3 or dims.y > dims.x * 3) and dims.z < 0.1
        return False
    
    def _is_label(self, obj):
        """Determine if an object is a label (e.g., text)."""
        return obj.type == 'FONT'
    
    def create_animation(self):
        """Create an animation sequence based on the selected type."""
        if self.animation_type == "flowchart":
            self._create_flowchart_animation()
        elif self.animation_type == "network":
            self._create_network_animation()
        else:
            # Default to standard animation
            self._create_standard_animation()
    
    def _create_standard_animation(self):
        """Create a standard animation sequence for diagrams."""
        # Calculate timing based on total duration
        total_frames = self.duration
        intro_end = int(total_frames * 0.2)  # First 20% for intro
        nodes_end = int(total_frames * 0.5)  # Next 30% for nodes
        conn_end = int(total_frames * 0.7)   # Next 20% for connections
        labels_end = int(total_frames * 0.9) # Next 20% for labels
        # Last 10% for flow animation
        
        # 1. Introduction (camera movement)
        self._animate_camera_intro(1, intro_end)
        
        # 2. Node Introduction
        self._animate_node_intro(intro_end, nodes_end)
        
        # 3. Connection Building
        self._animate_connections(nodes_end, conn_end)
        
        # 4. Labeling
        self._animate_labels(conn_end, labels_end)
        
        # 5. Highlight Flow
        self._animate_flow(labels_end, total_frames)
    
    def _create_flowchart_animation(self):
        """Create a flowchart-specific animation sequence."""
        # Similar to standard but with sequential highlighting
        self._create_standard_animation()
        
        # Override the flow animation with sequential highlighting
        self._animate_sequential_flow(int(self.duration * 0.7), self.duration)
    
    def _create_network_animation(self):
        """Create a network diagram animation sequence."""
        # Similar to standard but with different node intro and connection style
        total_frames = self.duration
        intro_end = int(total_frames * 0.2)
        nodes_end = int(total_frames * 0.5)
        conn_end = int(total_frames * 0.8)
        
        # 1. Introduction (camera movement)
        self._animate_camera_intro(1, intro_end)
        
        # 2. Node Introduction (with slight bouncing)
        self._animate_node_intro_with_physics(intro_end, nodes_end)
        
        # 3. Connection Building (with pulse effect)
        self._animate_connections_with_pulse(nodes_end, conn_end)
        
        # 4. Network Activity
        self._animate_network_activity(conn_end, total_frames)
    
    def _animate_camera_intro(self, start_frame, end_frame):
        """Animate camera for introduction."""
        camera = bpy.context.scene.camera
        if not camera:
            print("No camera found in scene")
            return
            
        # Set keyframes for camera movement
        camera.location = (0, -10, 10)
        camera.keyframe_insert(data_path="location", frame=start_frame)
        
        camera.location = (0, -5, 5)
        camera.keyframe_insert(data_path="location", frame=end_frame)
        
        # Add easing
        for fc in camera.animation_data.action.fcurves:
            for kf in fc.keyframe_points:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = 'AUTO_CLAMPED'
                kf.handle_right_type = 'AUTO_CLAMPED'
    
    def _animate_node_intro(self, start_frame, end_frame):
        """Animate the introduction of nodes."""
        if not self.nodes:
            return
            
        # Calculate frames per node intro
        frame_step = (end_frame - start_frame) / (len(self.nodes) + 1)
        
        # For each node, animate scale from 0 to 1
        for i, obj in enumerate(self.nodes):
            # Save original scale
            original_scale = obj.scale.copy()
            
            # Set initial scale to 0
            obj.scale = (0, 0, 0)
            obj.keyframe_insert(data_path="scale", frame=start_frame + int(i * frame_step))
            
            # Animate to full scale
            obj.scale = original_scale
            obj.keyframe_insert(data_path="scale", frame=start_frame + int((i + 1) * frame_step))
            
            # Add easing
            self._add_easing(obj, "scale")
    
    def _animate_node_intro_with_physics(self, start_frame, end_frame):
        """Animate nodes with a slight bounce effect."""
        if not self.nodes:
            return
            
        # Calculate frames per node intro
        frame_step = (end_frame - start_frame) / (len(self.nodes) + 1)
        
        # For each node, animate with bounce
        for i, obj in enumerate(self.nodes):
            # Save original scale and location
            original_scale = obj.scale.copy()
            original_location = obj.location.copy()
            
            # Set initial scale to 0
            obj.scale = (0, 0, 0)
            obj.keyframe_insert(data_path="scale", frame=start_frame + int(i * frame_step))
            
            # Animate to slightly larger than full scale (bounce effect)
            bounce_scale = (original_scale.x * 1.2, original_scale.y * 1.2, original_scale.z * 1.2)
            obj.scale = bounce_scale
            obj.keyframe_insert(data_path="scale", frame=start_frame + int((i + 0.7) * frame_step))
            
            # Settle to original scale
            obj.scale = original_scale
            obj.keyframe_insert(data_path="scale", frame=start_frame + int((i + 1) * frame_step))
            
            # Add slight position bounce
            obj.location = (original_location.x, original_location.y, original_location.z + 0.2)
            obj.keyframe_insert(data_path="location", frame=start_frame + int((i + 0.7) * frame_step))
            
            obj.location = original_location
            obj.keyframe_insert(data_path="location", frame=start_frame + int((i + 1) * frame_step))
            
            # Add easing
            self._add_easing(obj, "scale")
            self._add_easing(obj, "location")
    
    def _animate_connections(self, start_frame, end_frame):
        """Animate the introduction of connections."""
        if not self.connectors:
            return
            
        # Calculate frames per connector intro
        frame_step = (end_frame - start_frame) / (len(self.connectors) + 1)
        
        for i, obj in enumerate(self.connectors):
            # Create a shape key for animation
            if obj.type == 'MESH':
                # Add shape key basis
                obj.shape_key_add(name='Basis')
                
                # Add shape key for animation
                key = obj.shape_key_add(name='Grow')
                key.value = 0
                
                # Create animation
                key.keyframe_insert(data_path="value", frame=start_frame + int(i * frame_step))
                key.value = 1
                key.keyframe_insert(data_path="value", frame=start_frame + int((i + 1) * frame_step))
                
                # Add easing
                self._add_easing(key, "value")
    
    def _animate_connections_with_pulse(self, start_frame, end_frame):
        """Animate connections with a pulse effect."""
        if not self.connectors:
            return
            
        # Calculate frames per connector intro
        frame_step = (end_frame - start_frame) / (len(self.connectors) + 1)
        
        for i, obj in enumerate(self.connectors):
            if obj.type == 'MESH' and obj.data.materials:
                mat = obj.data.materials[0]
                
                if mat and mat.use_nodes:
                    # Get principled BSDF node
                    nodes = mat.node_tree.nodes
                    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                    
                    if bsdf:
                        # Grow the connector first
                        obj.scale.z = 0  # Start with zero scale
                        obj.keyframe_insert(data_path="scale", frame=start_frame + int(i * frame_step))
                        
                        obj.scale.z = 1  # Full scale
                        obj.keyframe_insert(data_path="scale", frame=start_frame + int((i + 0.5) * frame_step))
                        
                        # Then add pulse effect with emission
                        # Get base color
                        base_color = bsdf.inputs["Base Color"].default_value
                        
                        # Start with no emission
                        bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                        bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", 
                                                              frame=start_frame + int((i + 0.5) * frame_step))
                        
                        # Pulse 1
                        bsdf.inputs["Emission"].default_value = (base_color[0], base_color[1], base_color[2], 1)
                        bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", 
                                                              frame=start_frame + int((i + 0.7) * frame_step))
                        
                        # Pulse 2
                        bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                        bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", 
                                                              frame=start_frame + int((i + 0.9) * frame_step))
                        
                        # Add easing
                        self._add_easing(obj, "scale")
                        for fc in mat.node_tree.animation_data.action.fcurves:
                            for kf in fc.keyframe_points:
                                kf.interpolation = 'BEZIER'
    
    def _animate_labels(self, start_frame, end_frame):
        """Animate the introduction of labels."""
        if not self.labels:
            return
            
        # Calculate frames per label intro
        frame_step = (end_frame - start_frame) / (len(self.labels) + 1)
        
        for i, obj in enumerate(self.labels):
            # Fade in labels (using material transparency)
            if obj.type == 'FONT':
                # Create material if not exists
                if not obj.data.materials:
                    mat = bpy.data.materials.new(name="LabelMaterial")
                    mat.use_nodes = True
                    obj.data.materials.append(mat)
                else:
                    mat = obj.data.materials[0]
                
                # Get principled BSDF node
                nodes = mat.node_tree.nodes
                bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                
                if bsdf:
                    # Set initial alpha to 0
                    bsdf.inputs["Alpha"].default_value = 0
                    bsdf.inputs["Alpha"].keyframe_insert(data_path="default_value", 
                                                      frame=start_frame + int(i * frame_step))
                    
                    # Animate to full opacity
                    bsdf.inputs["Alpha"].default_value = 1
                    bsdf.inputs["Alpha"].keyframe_insert(data_path="default_value", 
                                                      frame=start_frame + int((i + 1) * frame_step))
                    
                    # Add easing
                    for fc in mat.node_tree.animation_data.action.fcurves:
                        for kf in fc.keyframe_points:
                            kf.interpolation = 'BEZIER'
                            kf.handle_left_type = 'AUTO_CLAMPED'
                            kf.handle_right_type = 'AUTO_CLAMPED'
    
    def _animate_flow(self, start_frame, end_frame):
        """Animate flow through the diagram (e.g., data flow, process steps)."""
        if not self.nodes:
            return
            
        # For simplicity, just highlight nodes in sequence
        frame_step = (end_frame - start_frame) / len(self.nodes)
        
        for i, obj in enumerate(self.nodes):
            # Create emission animation for highlighting
            if obj.data.materials:
                mat = obj.data.materials[0]
                nodes = mat.node_tree.nodes
                
                # Get principled BSDF node
                bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                
                if bsdf:
                    # No emission at start
                    bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                    bsdf.inputs["Emission Strength"].default_value = 0
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=start_frame)
                    bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=start_frame)
                    
                    # Peak emission during this node's highlight time
                    highlight_frame = start_frame + int(i * frame_step)
                    bsdf.inputs["Emission"].default_value = (1, 1, 1, 1)
                    bsdf.inputs["Emission Strength"].default_value = 1.0
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=highlight_frame)
                    bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=highlight_frame)
                    
                    # Back to no emission
                    bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                    bsdf.inputs["Emission Strength"].default_value = 0
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=highlight_frame + int(frame_step * 0.8))
                    bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=highlight_frame + int(frame_step * 0.8))
                    
                    # Add easing
                    for fc in mat.node_tree.animation_data.action.fcurves:
                        for kf in fc.keyframe_points:
                            kf.interpolation = 'BEZIER'
    
    def _animate_sequential_flow(self, start_frame, end_frame):
        """Animate a sequential flow through nodes (for flowcharts)."""
        if not self.nodes or len(self.nodes) < 2:
            return
            
        # Sort nodes by Y position (assumes flowchart goes from top to bottom)
        sorted_nodes = sorted(self.nodes, key=lambda obj: -obj.location.y)
        
        # Calculate frames per node
        frame_step = (end_frame - start_frame) / len(sorted_nodes)
        
        for i, obj in enumerate(sorted_nodes):
            # Highlight node
            if obj.data.materials:
                mat = obj.data.materials[0]
                nodes = mat.node_tree.nodes
                bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                
                if bsdf:
                    # No highlight at start
                    bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                    bsdf.inputs["Emission Strength"].default_value = 0
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=start_frame)
                    bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=start_frame)
                    
                    # Highlight this node
                    highlight_frame = start_frame + int(i * frame_step)
                    bsdf.inputs["Emission"].default_value = (1, 1, 1, 1)
                    bsdf.inputs["Emission Strength"].default_value = 1.0
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=highlight_frame)
                    bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=highlight_frame)
                    
                    # Keep highlighted for a while
                    bsdf.inputs["Emission"].default_value = (1, 1, 1, 1)
                    bsdf.inputs["Emission Strength"].default_value = 1.0
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=highlight_frame + int(frame_step * 0.8))
                    bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=highlight_frame + int(frame_step * 0.8))
                    
                    # Back to normal
                    bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                    bsdf.inputs["Emission Strength"].default_value = 0
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=highlight_frame + int(frame_step * 0.9))
                    bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=highlight_frame + int(frame_step * 0.9))
    
    def _animate_network_activity(self, start_frame, end_frame):
        """Animate network activity with pulse effects on connections."""
        if not self.connectors:
            return
            
        # Number of pulses to send
        num_pulses = 3
        pulse_duration = (end_frame - start_frame) / (len(self.connectors) * num_pulses)
        
        # For each connector, send multiple pulses
        for i, obj in enumerate(self.connectors):
            if obj.data.materials:
                mat = obj.data.materials[0]
                nodes = mat.node_tree.nodes
                bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                
                if bsdf:
                    for pulse in range(num_pulses):
                        pulse_start = start_frame + (i * num_pulses + pulse) * pulse_duration
                        
                        # Start pulse
                        bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                        bsdf.inputs["Emission Strength"].default_value = 0
                        bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=pulse_start)
                        bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=pulse_start)
                        
                        # Peak pulse
                        pulse_peak = pulse_start + pulse_duration * 0.2
                        bsdf.inputs["Emission"].default_value = (1, 1, 1, 1)
                        bsdf.inputs["Emission Strength"].default_value = 2.0
                        bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=pulse_peak)
                        bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=pulse_peak)
                        
                        # End pulse
                        pulse_end = pulse_start + pulse_duration * 0.4
                        bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                        bsdf.inputs["Emission Strength"].default_value = 0
                        bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=pulse_end)
                        bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=pulse_end)
    
    def _add_easing(self, obj, data_path):
        """Add easing to animation curves."""
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                if fc.data_path == data_path or data_path in fc.data_path:
                    for kf in fc.keyframe_points:
                        kf.interpolation = 'BEZIER'
                        kf.handle_left_type = 'AUTO_CLAMPED'
                        kf.handle_right_type = 'AUTO_CLAMPED'
    
    def apply_animation(self, output_path):
        """Apply animations and save the result."""
        # Create the animation
        self.create_animation()
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save the animated file
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        
        print(f"Animation applied and saved to {output_path}")
        return output_path

# For command-line execution from Blender
if __name__ == "__main__":
    # Get args after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    if len(argv) >= 2:
        blend_file = argv[0]
        output_path = argv[1]
        
        # Get optional animation type and duration
        animation_type = "standard"
        if len(argv) >= 3:
            animation_type = argv[2]
            
        duration = 250
        if len(argv) >= 4:
            try:
                duration = int(argv[3])
            except ValueError:
                print(f"Invalid duration: {argv[3]}, using default: 250")
        
        animator = SceneXAnimation(blend_file, animation_type, duration)
        animator.apply_animation(output_path)
    else:
        print("Usage: blender --background --python scenex_animation.py -- input.blend output.blend [animation_type] [duration]")
        sys.exit(1)
