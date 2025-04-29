    def _animate_connections(self):
        """Animate the introduction of connections."""
        for i, obj in enumerate(self.connectors):
            # Create a shape key for animation
            if obj.type == 'MESH':
                # Add shape key basis
                obj.shape_key_add(name='Basis')
                
                # Add shape key for animation
                key = obj.shape_key_add(name='Grow')
                key.value = 0
                
                # Create animation
                key.keyframe_insert(data_path="value", frame=120 + i*3)
                key.value = 1
                key.keyframe_insert(data_path="value", frame=150 + i*3)
                
                # Add easing
                self._add_easing(key, "value")
    
    def _animate_labels(self):
        """Animate the introduction of labels."""
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
                    bsdf.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=180 + i*2)
                    
                    # Animate to full opacity
                    bsdf.inputs["Alpha"].default_value = 1
                    bsdf.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=200 + i*2)
                    
                    # Add easing
                    for fc in mat.node_tree.animation_data.action.fcurves:
                        for kf in fc.keyframe_points:
                            kf.interpolation = 'BEZIER'
                            kf.handle_left_type = 'AUTO_CLAMPED'
                            kf.handle_right_type = 'AUTO_CLAMPED'
    
    def _animate_flow(self):
        """Animate flow through the diagram (e.g., data flow, process steps)."""
        # For simplicity, just highlight nodes in sequence
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
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=220)
                    
                    # Peak emission during this node's highlight time
                    highlight_frame = 220 + i*5
                    bsdf.inputs["Emission"].default_value = (1, 1, 1, 1)
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=highlight_frame)
                    
                    # Back to no emission
                    bsdf.inputs["Emission"].default_value = (0, 0, 0, 1)
                    bsdf.inputs["Emission"].keyframe_insert(data_path="default_value", frame=highlight_frame + 5)
                    
                    # Add easing
                    for fc in mat.node_tree.animation_data.action.fcurves:
                        for kf in fc.keyframe_points:
                            kf.interpolation = 'BEZIER'
    
    def _add_easing(self, obj, data_path):
        """Add easing to animation curves."""
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                if fc.data_path == data_path:
                    for kf in fc.keyframe_points:
                        kf.interpolation = 'BEZIER'
                        kf.handle_left_type = 'AUTO_CLAMPED'
                        kf.handle_right_type = 'AUTO_CLAMPED'
    
    def apply_animation(self, output_path):
        """Apply animations and save the result."""
        # Create the standard animation
        self.create_standard_animation()
        
        # Save the animated file
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        
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
        
        animator = SceneXAnimation(blend_file)
        animator.apply_animation(output_path)
```

## Advanced Animation Features

### Custom Animation Sequence Class

For more advanced animation control, we can extend our system with a customizable sequence class:

```python
# animation_sequence.py
import bpy

class AnimationSequence:
    """A customizable sequence of animations for diagram elements."""
    
    def __init__(self, scene_objects):
        """Initialize with objects from the scene."""
        self.objects = scene_objects
        self.steps = []
        self.current_frame = 1
    
    def add_step(self, duration, animation_fn, *args, **kwargs):
        """Add an animation step to the sequence."""
        self.steps.append({
            'start_frame': self.current_frame,
            'duration': duration,
            'animation_fn': animation_fn,
            'args': args,
            'kwargs': kwargs
        })
        self.current_frame += duration
        return self
    
    def set_frame_range(self, scene):
        """Set the frame range in the scene based on the sequence."""
        if not self.steps:
            return
        
        scene.frame_start = 1
        scene.frame_end = self.current_frame - 1
    
    def execute(self):
        """Execute all animation steps in the sequence."""
        for step in self.steps:
            step['animation_fn'](
                start_frame=step['start_frame'],
                duration=step['duration'],
                *step['args'],
                **step['kwargs']
            )
        return self
```

### Animation Templates

We can create predefined animation templates for common diagram types:

```python
# animation_templates.py
import bpy

class FlowchartAnimationTemplate:
    """Template for animating flowchart diagrams."""
    
    def __init__(self, scene_x):
        """Initialize with a SceneX instance."""
        self.scene_x = scene_x
    
    def apply(self):
        """Apply the flowchart animation template."""
        # 1. Fade in title (if any)
        self._animate_title()
        
        # 2. Introduce nodes in sequence
        self._introduce_nodes()
        
        # 3. Connect nodes with animated lines
        self._connect_nodes()
        
        # 4. Show the process flow
        self._animate_flow()
        
        # 5. Final camera movement
        self._final_camera_move()
    
    def _animate_title(self):
        """Animate the title (if present)."""
        # Implementation details...
    
    def _introduce_nodes(self):
        """Introduce nodes in sequence."""
        # Implementation details...
    
    def _connect_nodes(self):
        """Connect nodes with animated lines."""
        # Implementation details...
    
    def _animate_flow(self):
        """Show the process flow through the diagram."""
        # Implementation details...
    
    def _final_camera_move(self):
        """Final camera movement to show the complete diagram."""
        # Implementation details...

class NetworkDiagramTemplate:
    """Template for animating network diagrams."""
    
    def __init__(self, scene_x):
        """Initialize with a SceneX instance."""
        self.scene_x = scene_x
    
    def apply(self):
        """Apply the network diagram animation template."""
        # Implementation details...

# Add more templates as needed
```

## Command-Line Usage

To use the animation system from the command line:

```bash
blender --background --python scenex_animation.py -- input.blend output.blend
```

## Implementation Notes

### Animation Strategy

The animation system follows these principles:

1. **Progressive Disclosure**: Introduce elements gradually to help viewers understand the structure
2. **Logical Sequence**: Show elements in a logical order (nodes → connections → labels)
3. **Visual Hierarchy**: Emphasize important elements with stronger animations
4. **Smooth Transitions**: Use easing for professional-looking animations

### Object Classification

The system automatically classifies objects into three categories:

1. **Nodes**: Main structural elements (rectangles, circles, etc.)
2. **Connectors**: Elements connecting nodes (lines, arrows, etc.)
3. **Labels**: Text elements describing nodes or connections

This classification enables applying appropriate animations to each type.

### Animation Techniques

The system uses several animation techniques:

1. **Scale Animation**: Growing elements from 0 to full size
2. **Fade Animation**: Changing opacity/transparency
3. **Shape Keys**: For more complex deformations and growth
4. **Emission Animation**: For highlighting and flow effects
5. **Camera Animation**: For controlling viewer focus

### Material Animation

To animate material properties, the system:

1. Accesses the material node tree
2. Locates the Principled BSDF node
3. Animates properties like color, emission, or transparency
4. Adds proper easing to the animation curves

## Dependencies

- Blender 3.0+ with Python support
- Blender Python modules (`bpy`, included with Blender)

## Testing

### Manual Testing

1. Test with simple diagrams first
2. Check that animation timings look natural
3. Verify that object classification works as expected
4. Ensure camera movements frame the content appropriately

### Automated Testing

As with the conversion component, automated testing requires running Blender in headless mode:

```python
# test_animation_system.py
import subprocess
import os
import unittest

class TestAnimationSystem(unittest.TestCase):
    def test_animation(self):
        # Use a sample Blender file
        input_blend = "test_input.blend"
        output_blend = "test_output.blend"
        
        # Run the animation script
        result = subprocess.run([
            "blender", "--background", "--python", "scenex_animation.py", "--",
            input_blend, output_blend
        ], capture_output=True)
        
        # Check if the process succeeded
        self.assertEqual(result.returncode, 0)
        
        # Check if the output file exists
        self.assertTrue(os.path.exists(output_blend))
        
        # Clean up
        os.remove(output_blend)

if __name__ == "__main__":
    unittest.main()
```

## Known Limitations

1. Limited animation variety (currently focused on standard sequence)
2. Basic object classification might not work for all diagram types
3. No support for complex animation paths or custom timing functions
4. Limited camera control (basic movements only)

## Next Steps

1. Implement additional animation templates for different diagram types
2. Add support for more complex animation paths and timing functions
3. Enhance object classification with machine learning techniques
4. Improve camera control for more dynamic presentations
5. Add support for animated textures and effects
6. Integrate with the video rendering component