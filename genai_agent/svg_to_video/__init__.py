"""
SVG to Video Pipeline Module

This module provides functionality to convert SVG diagrams to animated 3D videos.
The pipeline consists of four main stages:
1. SVG Generation: Using LangChain to prompt LLMs to create SVG diagrams
2. 3D Model Conversion: Converting SVG elements to 3D objects in Blender
3. Animation: Adding animations and camera movements with SceneX
4. Video Rendering: Producing the final video output

"""

from .svg_generator import SVGGenerator
from .svg_to_3d_converter import SVGTo3DConverter
from .animation_system import AnimationSystem
from .video_renderer import VideoRenderer
from .pipeline import SVGToVideoPipeline

__all__ = [
    'SVGGenerator',
    'SVGTo3DConverter',
    'AnimationSystem',
    'VideoRenderer',
    'SVGToVideoPipeline',
]
