# SceneX Animation System

## 1. Introduction

SceneX is a Python-based animation system designed for the GenAI Agent 3D project. Inspired by libraries like Manim and Three.js, SceneX provides a programmatic approach to creating complex 3D animations from SVG diagrams and other content. The system bridges the gap between static diagrams and dynamic 3D presentations.

## 2. System Architecture

### 2.1 Core Components

```
┌─────────────────────────────────────────────────────────┐
│                   SceneX Animation System               │
└───────────────────────────┬─────────────────────────────┘
                            │
           ┌───────────────┴──────────────┐
           │                              │
┌──────────▼─────────┐         ┌──────────▼─────────┐
│                    │         │                    │
│    Core Engine     │         │    Animation       │
│                    │         │    Primitives      │
│  - Scene           │         │                    │
│  - Camera          │         │  - Fade            │
│  - Timeline        │         │  - Move            │
│  - Renderer        │         │  - Scale           │
│  - Object Manager  │         │  - Rotate          │
│                    │         │  - Color           │
└──────────┬─────────┘         └──────────┬─────────┘
           │                              │
           └──────────────┬───────────────┘
                          │
           ┌──────────────┴───────────────┐
           │                              │
┌──────────▼─────────┐         ┌──────────▼─────────┐
│                    │         │                    │
│    Element Types   │         │    Export System   │
│                    │         │                    │
│  - ShapeElement    │         │  - Blender Exporter│
│  - TextElement     │         │  - Video Renderer  │
│  - GroupElement    │         │  - PowerPoint      │
│  - PathElement     │         │    Exporter        │
│  - ConnectorElement│         │  - Interactive     │
│                    │         │    Web Viewer      │
└────────────────────┘         └────────────────────┘
```

### 2.2 System Components

1. **Core Engine**: The foundation of the animation system
   - Scene: Manages the 3D environment and object hierarchy
   - Camera: Controls viewpoints and movements
   - Timeline: Manages animation sequencing and timing
   - Renderer: Handles visual output generation
   - Object Manager: Tracks and manipulates scene objects

2. **Animation Primitives**: Basic animation building blocks
   - Fade: Controls object opacity (fade in/out)
   - Move: Translates objects in 3D space
   - Scale: Changes object size
   - Rotate: Rotates objects around specified axes
   - Color: Animates color changes
   - Transform: Combines multiple transformations

3. **Element Types**: Specialized object types
   - ShapeElement: Basic 3D shapes (cube, sphere, etc.)
   - TextElement: 3D text with formatting options
   - GroupElement: Container for multiple elements
   - PathElement: Complex shapes defined by paths
   - ConnectorElement: Lines and arrows connecting elements

4. **Export System**: Output generation components
   - Blender Exporter: Creates Blender files with animations
   - Video Renderer: Generates video output
   - PowerPoint Exporter: Creates presentation slides
   - Interactive Web Viewer: Browser-based 3D viewer

## 3. Core Functionality

### 3.1 Scene Management

The Scene class is the central component that manages the 3D environment:

```python
class Scene:
    """Main scene container for 3D elements and animations."""
    
    def __init__(self, width=1920, height=1080, background_color=(0.9, 0.9, 0.9)):
        """Initialize a new scene with specified dimensions and background."""
        self.width = width
        self.height = height
        self.background_color = background_color
        self.objects = []
        self.camera = Camera()
        self.timeline = Timeline()
        
    def add(self, *objects):
        """Add objects to the scene."""
        for obj in objects:
            self.objects.append(obj)
            obj.scene = self
        return objects
    
    def remove(self, *objects):
        """Remove objects from the scene."""
        for obj in objects:
            if obj in self.objects:
                self.objects.remove(obj)
                obj.scene = None
        
    def play(self, *animations, duration=1.0, easing="linear"):
        """Add animations to the timeline and play them."""
        for anim in animations:
            anim.set_duration(duration)
            anim.set_easing(easing)
            self.timeline.add_animation(anim)
        
    def wait(self, duration=1.0):
        """Add a pause in the animation sequence."""
        self.timeline.add_pause(duration)
        
    def camera_move_to(self, position, duration=1.0, easing="ease_in_out"):
        """Move the camera to a new position."""
        self.timeline.add_animation(
            CameraAnimation(self.camera, "position", position, duration, easing)
        )
        
    def render(self, output_path, format="mp4", fps=30):
        """Render the scene to the specified output format."""
        renderer = Renderer(self, fps=fps)
        renderer.render(output_path, format)
```

### 3.2 Animation Primitives

Animation primitives form the building blocks of all animations:

```python
class Animation:
    """Base class for all animations."""
    
    def __init__(self, target, duration=1.0, easing="linear"):
        self.target = target
        self.duration = duration
        self.easing = easing
        self.start_time = 0
        
    def set_duration(self, duration):
        """Set the animation duration."""
        self.duration = duration
        
    def set_easing(self, easing):
        """Set the easing function."""
        self.easing = easing
        
    def update(self, t):
        """Update the animation at time t (0 to 1)."""
        # Apply easing function
        progress = self.apply_easing(t)
        # Implement in subclasses
        self.apply_animation(progress)
        
    def apply_easing(self, t):
        """Apply the easing function to t."""
        if self.easing == "linear":
            return t
        elif self.easing == "ease_in":
            return t * t
        elif self.easing == "ease_out":
            return t * (2 - t)
        elif self.easing == "ease_in_out":
            return t * t * (3 - 2 * t)
        # Additional easing functions...
        
    def apply_animation(self, progress):
        """Apply the animation at the given progress (0 to 1)."""
        raise NotImplementedError("Subclasses must implement this method")
```

Example animation primitives:

```python
class FadeIn(Animation):
    """Fade in animation that increases opacity from 0 to 1."""
    
    def __init__(self, target, duration=1.0, easing="ease_out"):
        super().__init__(target, duration, easing)
        self.start_opacity = 0
        self.end_opacity = 1
        
    def apply_animation(self, progress):
        current_opacity = self.start_opacity + (self.end_opacity - self.start_opacity) * progress
        self.target.set_opacity(current_opacity)


class MoveTo(Animation):
    """Move animation that changes position."""
    
    def __init__(self, target, end_position, duration=1.0, easing="ease_in_out"):
        super().__init__(target, duration, easing)
        self.start_position = target.position
        self.end_position = end_position
        
    def apply_animation(self, progress):
        current_x = self.start_position[0] + (self.end_position[0] - self.start_position[0]) * progress
        current_y = self.start_position[1] + (self.end_position[1] - self.start_position[1]) * progress
        current_z = self.start_position[2] + (self.end_position[2] - self.start_position[2]) * progress
        self.target.set_position((current_x, current_y, current_z))
```

### 3.3 Timeline Management

The Timeline manages the sequencing and timing of animations:

```python
class Timeline:
    """Manages animation sequences and timing."""
    
    def __init__(self):
        self.animations = []  # (start_time, animation) tuples
        self.current_time = 0
        self.duration = 0
        
    def add_animation(self, animation, start_time=None):
        """Add an animation to the timeline."""
        if start_time is None:
            start_time = self.current_time
            
        animation.start_time = start_time
        self.animations.append((start_time, animation))
        self.current_time = start_time + animation.duration
        self.duration = max(self.duration, self.current_time)
        
    def add_pause(self, duration):
        """Add a pause to the timeline."""
        self.current_time += duration
        self.duration = max(self.duration, self.current_time)
        
    def get_state_at(self, time):
        """Compute the scene state at the given time."""
        # Find all animations that are active at this time
        active_animations = []
        for start_time, animation in self.animations:
            end_time = start_time + animation.duration
            if start_time <= time < end_time:
                # Calculate progress within this animation
                local_progress = (time - start_time) / animation.duration
                active_animations.append((animation, local_progress))
                
        return active_animations
```

## 4. Element Types

### 4.1 Base Element Class

```python
class Element:
    """Base class for all 3D elements."""
    
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.opacity = 1.0
        self.color = (1, 1, 1)
        self.scene = None
        self.parent = None
        self.children = []
        
    def set_position(self, position):
        """Set the element's position."""
        self.position = position
        
    def set_rotation(self, rotation):
        """Set the element's rotation."""
        self.rotation = rotation
        
    def set_scale(self, scale):
        """Set the element's scale."""
        self.scale = scale
        
    def set_color(self, color):
        """Set the element's color."""
        self.color = color
        
    def set_opacity(self, opacity):
        """Set the element's opacity."""
        self.opacity = opacity
        
    def add(self, *children):
        """Add child elements."""
        for child in children:
            self.children.append(child)
            child.parent = self
            
    def remove(self, *children):
        """Remove child elements."""
        for child in children:
            if child in self.children:
                self.children.remove(child)
                child.parent = None
                
    def get_global_transform(self):
        """Get the global transformation matrix."""
        # Start with local transform
        transform = self.get_local_transform()
        
        # Apply parent transforms
        if self.parent:
            parent_transform = self.parent.get_global_transform()
            transform = multiply_matrices(parent_transform, transform)
            
        return transform
        
    def get_local_transform(self):
        """Get the local transformation matrix."""
        # Create transformation matrices for position, rotation, and scale
        translation_matrix = create_translation_matrix(self.position)
        rotation_matrix = create_rotation_matrix(self.rotation)
        scale_matrix = create_scale_matrix(self.scale)
        
        # Combine the matrices
        transform = multiply_matrices(translation_matrix, rotation_matrix)
        transform = multiply_matrices(transform, scale_matrix)
        
        return transform
```

### 4.2 Specialized Element Types

```python
class ShapeElement(Element):
    """Basic 3D shape element."""
    
    def __init__(self, shape_type="cube", size=1.0, **kwargs):
        super().__init__(**kwargs)
        self.shape_type = shape_type
        self.size = size
        
    def get_geometry(self):
        """Get the shape's geometry data."""
        if self.shape_type == "cube":
            return create_cube_geometry(self.size)
        elif self.shape_type == "sphere":
            return create_sphere_geometry(self.size)
        elif self.shape_type == "cylinder":
            return create_cylinder_geometry(self.size)
        # Handle other shape types...
        

class TextElement(Element):
    """3D text element."""
    
    def __init__(self, text="", font_size=1.0, font_name="Arial", depth=0.2, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.font_name = font_name
        self.depth = depth
        
    def get_geometry(self):
        """Get the text geometry."""
        return create_text_geometry(self.text, self.font_name, self.font_size, self.depth)
        

class PathElement(Element):
    """Element defined by an SVG path."""
    
    def __init__(self, path_data="", depth=0.2, **kwargs):
        super().__init__(**kwargs)
        self.path_data = path_data
        self.depth = depth
        
    def get_geometry(self):
        """Get the extruded path geometry."""
        return create_extruded_path_geometry(self.path_data, self.depth)
        

class ConnectorElement(Element):
    """Connection between elements."""
    
    def __init__(self, start_element=None, end_element=None, 
                 start_point=None, end_point=None, 
                 thickness=0.05, arrow_size=0.2, **kwargs):
        super().__init__(**kwargs)
        self.start_element = start_element
        self.end_element = end_element
        self.start_point = start_point
        self.end_point = end_point
        self.thickness = thickness
        self.arrow_size = arrow_size
        
    def update_positions(self):
        """Update the start and end positions based on connected elements."""
        if self.start_element:
            self.start_point = self.start_element.position
        if self.end_element:
            self.end_point = self.end_element.position
            
    def get_geometry(self):
        """Get the connector geometry."""
        self.update_positions()
        return create_connector_geometry(
            self.start_point, self.end_point, 
            self.thickness, self.arrow_size
        )
```

## 5. Blender Integration

SceneX integrates with Blender to leverage its powerful rendering capabilities:

### 5.1 Blender Exporter

```python
class BlenderExporter:
    """Exports SceneX scenes to Blender."""
    
    def __init__(self, scene):
        self.scene = scene
        
    def export(self, filepath):
        """Export the scene to a .blend file."""
        # Create a new Blender document
        doc = BlenderDocument()
        
        # Convert scene elements to Blender objects
        for element in self.scene.objects:
            self._convert_element(element, doc)
            
        # Convert animations to Blender keyframes
        self._convert_animations(doc)
        
        # Set up the camera
        self._setup_camera(doc)
        
        # Set up rendering settings
        self._setup_render_settings(doc)
        
        # Save the document
        doc.save(filepath)
        
    def _convert_element(self, element, doc):
        """Convert a SceneX element to a Blender object."""
        if isinstance(element, ShapeElement):
            obj = doc.create_mesh_object(element.shape_type, element.get_geometry())
        elif isinstance(element, TextElement):
            obj = doc.create_text_object(element.text, element.font_name, element.depth)
        elif isinstance(element, PathElement):
            obj = doc.create_mesh_object("path", element.get_geometry())
        elif isinstance(element, ConnectorElement):
            obj = doc.create_mesh_object("connector", element.get_geometry())
        else:
            obj = doc.create_empty_object()
            
        # Set transform
        obj.position = element.position
        obj.rotation = element.rotation
        obj.scale = element.scale
        
        # Set material
        material = doc.create_material(
            element.color, 
            opacity=element.opacity
        )
        obj.set_material(material)
        
        # Handle children
        for child in element.children:
            child_obj = self._convert_element(child, doc)
            child_obj.parent = obj
            
        return obj
        
    def _convert_animations(self, doc):
        """Convert SceneX animations to Blender keyframes."""
        # For each animation in the timeline
        for start_time, animation in self.scene.timeline.animations:
            # Find the corresponding Blender object
            target_obj = doc.find_object_by_name(animation.target.name)
            
            # Set keyframes based on animation type
            if isinstance(animation, FadeIn):
                doc.set_opacity_keyframes(
                    target_obj,
                    start_time,
                    animation.duration,
                    0.0,
                    1.0,
                    animation.easing
                )
            elif isinstance(animation, MoveTo):
                doc.set_position_keyframes(
                    target_obj,
                    start_time,
                    animation.duration,
                    animation.start_position,
                    animation.end_position,
                    animation.easing
                )
            # Handle other animation types...
            
    def _setup_camera(self, doc):
        """Set up the Blender camera based on SceneX camera."""
        camera = doc.create_camera()
        camera.position = self.scene.camera.position
        camera.rotation = self.scene.camera.rotation
        camera.lens = self.scene.camera.focal_length
        
        # Add camera animations
        for start_time, animation in self.scene.timeline.animations:
            if isinstance(animation, CameraAnimation):
                if animation.property == "position":
                    doc.set_position_keyframes(
                        camera,
                        start_time,
                        animation.duration,
                        animation.start_value,
                        animation.end_value,
                        animation.easing
                    )
                elif animation.property == "rotation":
                    doc.set_rotation_keyframes(
                        camera,
                        start_time,
                        animation.duration,
                        animation.start_value,
                        animation.end_value,
                        animation.easing
                    )
                # Handle other camera properties...
                
    def _setup_render_settings(self, doc):
        """Set up Blender render settings."""
        doc.set_render_resolution(self.scene.width, self.scene.height)
        doc.set_render_engine("CYCLES")
        doc.set_samples(128)
        doc.set_background_color(self.scene.background_color)
```
