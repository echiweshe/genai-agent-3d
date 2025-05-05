# Animation System

## Overview

The Animation System adds animations to 3D models generated from SVG diagrams. It can automatically detect the appropriate animation type based on the content or apply a specified animation type.

## Features

- Multiple animation types (standard, flowchart, network, sequence)
- Automatic animation type detection
- Camera animations
- Element animations
- Configurable animation parameters
- Integration with Blender's animation system

## Architecture

The Animation System consists of these main components:

1. **Animation Type Detection**: Analyzes the 3D model to determine the appropriate animation type
2. **Animation Generators**: Specialized modules for different animation types
3. **Blender Integration**: Scripts for applying animations using Blender's Python API
4. **Configuration Management**: Handling of animation parameters

## Usage

```python
from genai_agent.svg_to_video.animation import AnimationSystem

# Initialize the animation system
animation_system = AnimationSystem(debug=True)

# Animate a 3D model
result = await animation_system.animate_model(
    model_path="input.blend",
    output_path="animated.blend",
    animation_type="flowchart",  # Optional, auto-detected if None
    duration=10  # Animation duration in seconds
)

# Check the result
if result:
    print("Animation successful!")
else:
    print("Animation failed!")
```

## Animation Types

The system supports the following animation types:

1. **Standard**: Generic animation for any diagram type
2. **Flowchart**: Specialized animation for flowcharts
3. **Network**: Specialized animation for network diagrams
4. **Sequence**: Specialized animation for sequence diagrams

Each animation type implements different techniques:

### Standard Animation

- Sequential element appearance
- Simple rotation and scale effects
- Basic camera movements

### Flowchart Animation

- Sequential flow following the diagram structure
- Highlighting of active steps
- Path following for connections
- Focus and zoom for decision points

### Network Animation

- Node appearance followed by connections
- Pulsing effects for nodes
- Data flow animations along connections
- Node highlighting to show relationships

### Sequence Animation

- Timeline-based animation following sequence order
- Message flow animations
- Activation/deactivation animations
- Lifeline animations

## Animation Script

The animation system generates a Blender Python script that:

1. Analyzes the 3D scene to identify objects and their relationships
2. Determines the animation sequence based on the diagram type
3. Creates keyframes for each object at appropriate times
4. Configures camera animations to follow the flow
5. Adds visual effects like highlighting and focus changes
6. Sets up render parameters for the animation

## Extending

To add a new animation type:

1. Create a new animation generation function in `animate_model.py`
2. Add detection logic in `_detect_animation_type` method
3. Update the animation script to handle the new type

## Dependencies

- `bpy`: Blender Python API
- `asyncio`: For asynchronous operations
- `os`, `pathlib`: For file operations
- `subprocess`: For running Blender as a subprocess
