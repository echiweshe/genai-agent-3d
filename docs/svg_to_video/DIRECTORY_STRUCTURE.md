# SVG to Video Pipeline: Directory Structure

## Overview

The SVG to Video pipeline follows a modular directory structure that organizes code by component and function. This document explains the directory layout and the purpose of each file.

## Main Directory Structure

```
genai_agent/
└── svg_to_video/                  # Main pipeline package
    ├── svg_generator/             # SVG generation module
    ├── svg_to_3d/                 # SVG to 3D conversion module
    ├── animation/                 # Animation module
    ├── rendering/                 # Video rendering module
    ├── __init__.py                # Package initialization
    └── pipeline_integrated.py     # Integrated pipeline
```

## SVG Generator Module

```
svg_generator/
├── __init__.py                    # Module initialization
└── svg_generator.py               # SVG generation implementation
```

## SVG to 3D Conversion Module

```
svg_to_3d/
├── __init__.py                    # Module initialization
├── svg_parser.py                  # SVG file parsing
├── svg_parser_elements.py         # SVG element parsing
├── svg_parser_paths.py            # SVG path parsing
├── svg_converter.py               # Base converter class
├── svg_converter_create.py        # Object creation methods
├── svg_converter_group.py         # Group handling methods
├── svg_converter_materials.py     # Material creation methods
├── svg_converter_path.py          # Path conversion methods
├── svg_converter_scene.py         # Scene setup methods
├── svg_to_3d_converter_new.py     # Main converter class
└── svg_utils.py                   # Utility functions
```

## Animation Module

```
animation/
├── __init__.py                    # Module initialization
└── animation_system.py            # Animation system implementation
```

## Rendering Module

```
rendering/
├── __init__.py                    # Module initialization
└── video_renderer.py              # Video renderer implementation
```

## Test Directory Structure

```
tests/
└── svg_to_video/                  # SVG to Video tests
    ├── svg_generator/             # SVG Generator tests
    ├── svg_to_3d/                 # SVG to 3D Converter tests
    ├── animation/                 # Animation System tests
    ├── rendering/                 # Video Renderer tests
    └── pipeline/                  # Integrated Pipeline tests
```

## Documentation Directory Structure

```
docs/
└── svg_to_video/                  # SVG to Video documentation
    ├── API.md                     # API reference
    ├── ARCHITECTURE.md            # Architecture overview
    ├── DIRECTORY_STRUCTURE.md     # This file
    ├── svg_generator.md           # SVG Generator documentation
    ├── svg_to_3d.md               # SVG to 3D Converter documentation
    ├── animation.md               # Animation System documentation
    ├── rendering.md               # Video Renderer documentation
    └── pipeline.md                # Integrated Pipeline documentation
```

## Scripts Directory Structure

```
scripts/
└── svg_to_video/                  # SVG to Video scripts
    ├── run/                       # Run scripts
    │   ├── run_svg_to_video.ps1   # Main run script
    │   └── run_svg_video_demo.ps1 # Demo script
    ├── test/                      # Test scripts
    │   └── run_svg_to_video_tests.ps1 # Test runner
    └── utils/                     # Utility scripts
        └── fix_svg_to_video_imports.ps1 # Import fixer
```

## Output Directory Structure

```
output/
└── svg_to_video/                  # SVG to Video output
    ├── svg/                       # Generated SVG files
    ├── models/                    # 3D model files
    ├── animations/                # Animation files
    └── videos/                    # Rendered videos
```

## File Descriptions

### Main Pipeline Files

- **`__init__.py`**: Package initialization, exports main classes
- **`pipeline_integrated.py`**: Integrated pipeline implementation

### SVG Generator Files

- **`svg_generator/__init__.py`**: Exports SVGGenerator class
- **`svg_generator/svg_generator.py`**: SVG Generator implementation

### SVG to 3D Converter Files

- **`svg_to_3d/__init__.py`**: Exports SVGTo3DConverter class
- **`svg_to_3d/svg_parser.py`**: SVG file parsing
- **`svg_to_3d/svg_parser_elements.py`**: SVG element parsing functions
- **`svg_to_3d/svg_parser_paths.py`**: SVG path parsing functions
- **`svg_to_3d/svg_converter.py`**: Base converter class
- **`svg_to_3d/svg_converter_create.py`**: 3D object creation methods
- **`svg_to_3d/svg_converter_group.py`**: Group and transform methods
- **`svg_to_3d/svg_converter_materials.py`**: Material creation methods
- **`svg_to_3d/svg_converter_path.py`**: Path conversion methods
- **`svg_to_3d/svg_converter_scene.py`**: Scene setup methods
- **`svg_to_3d/svg_to_3d_converter_new.py`**: Main converter implementation
- **`svg_to_3d/svg_utils.py`**: Utility functions

### Animation Files

- **`animation/__init__.py`**: Exports AnimationSystem class
- **`animation/animation_system.py`**: Animation system implementation

### Rendering Files

- **`rendering/__init__.py`**: Exports VideoRenderer class
- **`rendering/video_renderer.py`**: Video renderer implementation

### Script Files

- **`scripts/run/run_svg_to_video.ps1`**: Main run script
- **`scripts/run/run_svg_video_demo.ps1`**: Demo script
- **`scripts/test/run_svg_to_video_tests.ps1`**: Test runner
- **`scripts/utils/fix_svg_to_video_imports.ps1`**: Import fixer

## Naming Conventions

The directory structure follows these naming conventions:

1. **Module Names**: Descriptive names in snake_case
2. **Class Names**: Descriptive names in PascalCase
3. **Function Names**: Descriptive names in snake_case
4. **Constants**: UPPERCASE with underscores
5. **Private Members**: Prefixed with underscore (_)

## Import Patterns

For importing modules, the following patterns are used:

1. **Relative Imports** for internal module imports:
   ```python
   from .svg_generator import SVGGenerator
   from .svg_to_3d import SVGTo3DConverter
   ```

2. **Absolute Imports** for external dependencies:
   ```python
   import os
   import asyncio
   import logging
   ```

3. **Component Imports** for module components:
   ```python
   from genai_agent.svg_to_video import SVGToVideoPipeline
   ```

## Dependency Structure

The modules have the following dependency relationships:

```
SVGToVideoPipeline
    ├── SVGGenerator
    │   └── LLMServiceManager
    ├── SVGTo3DConverter
    │   ├── SVGParser
    │   ├── SVGConverter
    │   └── SVGUtils
    ├── AnimationSystem
    └── VideoRenderer
```

Each module can be used independently, allowing for flexible usage of the pipeline components.
