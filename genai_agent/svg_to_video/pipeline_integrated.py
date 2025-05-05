"""
SVG to Video Pipeline Integrated

This module provides an integrated pipeline for converting text descriptions
to SVG diagrams, then to 3D models, and finally to animated videos.
It uses the project's shared services and configuration.
"""

import os
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from .svg_generator.svg_generator import SVGGenerator
from .svg_to_3d import SVGTo3DConverter
from .animation.animation_system import AnimationSystem
from .rendering.video_renderer import VideoRenderer

logger = logging.getLogger(__name__)

class SVGToVideoPipeline:
    """
    Pipeline for converting text descriptions to animated videos.
    Uses the project's integrated services and configuration.
    """
    
    def __init__(self, debug=False):
        """
        Initialize the SVG to Video pipeline.
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        
        # Initialize output directories from environment or use defaults
        base_output_dir = os.environ.get("OUTPUT_DIR", "output")
        self.svg_output_dir = os.path.join(base_output_dir, "svg")
        self.model_output_dir = os.path.join(base_output_dir, "models")
        self.animation_output_dir = os.path.join(base_output_dir, "animations")
        self.video_output_dir = os.path.join(base_output_dir, "videos")
        
        # Create output directories if they don't exist
        for directory in [self.svg_output_dir, self.model_output_dir, 
                         self.animation_output_dir, self.video_output_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize components
        self.svg_generator = SVGGenerator(debug=debug)
        self.svg_to_3d_converter = SVGTo3DConverter(debug=debug)
        self.animation_system = AnimationSystem(debug=debug)
        self.video_renderer = VideoRenderer(debug=debug)
        
        # Flag to track initialization
        self._initialized = False
        
        if self.debug:
            logger.info("SVG to Video pipeline initialized")
    
    async def initialize(self):
        """Initialize the pipeline components."""
        if self._initialized:
            return
        
        # Initialize the SVG Generator
        await self.svg_generator.initialize()
        
        # Set the flag
        self._initialized = True
        
        if self.debug:
            logger.info("SVG to Video pipeline fully initialized")
            providers = self.svg_generator.get_available_providers()
            logger.info(f"Available LLM providers: {providers}")
    
    async def generate_video_from_description(
        self, 
        description: str, 
        provider: str = None,
        diagram_type: str = None,
        animation_type: str = None,
        render_quality: str = "medium",
        duration: int = 10
    ) -> Dict[str, str]:
        """
        Generate a video from a text description.
        
        Args:
            description: Text description of the diagram/scene
            provider: LLM provider to use (claude, openai, ollama)
            diagram_type: Type of diagram (flowchart, network, etc.)
            animation_type: Type of animation to apply
            render_quality: Rendering quality (low, medium, high)
            duration: Animation duration in seconds
            
        Returns:
            Dictionary with paths to generated files:
            {
                "svg": path to SVG file,
                "model": path to 3D model file,
                "animation": path to animated model file,
                "video": path to rendered video file
            }
        """
        try:
            # Ensure the pipeline is initialized
            if not self._initialized:
                await self.initialize()
            
            # Step 1: Generate SVG
            logger.info(f"Generating SVG from description: {description[:50]}...")
            svg_content = await self.svg_generator.generate_svg(
                concept=description,
                provider=provider,
                diagram_type=diagram_type
            )
            
            # Generate a unique ID for this job
            job_id = str(uuid.uuid4())
            
            # Save SVG file
            svg_filename = f"{job_id}.svg"
            svg_path = os.path.join(self.svg_output_dir, svg_filename)
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            if self.debug:
                logger.info(f"SVG saved to {svg_path}")
            
            # Step 2: Convert SVG to 3D model
            logger.info("Converting SVG to 3D model...")
            model_filename = f"{job_id}.blend"
            model_path = os.path.join(self.model_output_dir, model_filename)
            
            conversion_result = await self.svg_to_3d_converter.convert_svg_to_3d(
                svg_path=svg_path,
                output_path=model_path
            )
            
            if not conversion_result:
                raise RuntimeError("Failed to convert SVG to 3D model")
            
            if self.debug:
                logger.info(f"3D model saved to {model_path}")
            
            # Step 3: Add animation to the 3D model
            logger.info("Adding animation to 3D model...")
            animation_filename = f"{job_id}_animated.blend"
            animation_path = os.path.join(self.animation_output_dir, animation_filename)
            
            animation_result = await self.animation_system.animate_model(
                model_path=model_path,
                output_path=animation_path,
                animation_type=animation_type or self._detect_animation_type(diagram_type),
                duration=duration
            )
            
            if not animation_result:
                raise RuntimeError("Failed to animate 3D model")
            
            if self.debug:
                logger.info(f"Animated model saved to {animation_path}")
            
            # Step 4: Render the animation to video
            logger.info("Rendering animation to video...")
            video_filename = f"{job_id}.mp4"
            video_path = os.path.join(self.video_output_dir, video_filename)
            
            render_result = await self.video_renderer.render_video(
                animation_path=animation_path,
                output_path=video_path,
                quality=render_quality,
                fps=30
            )
            
            if not render_result:
                raise RuntimeError("Failed to render video")
            
            logger.info(f"Video rendered to {video_path}")
            
            # Return paths to generated files
            return {
                "svg": svg_path,
                "model": model_path,
                "animation": animation_path,
                "video": video_path
            }
        
        except Exception as e:
            logger.error(f"Error in SVG to Video pipeline: {str(e)}")
            raise
    
    async def generate_svg_only(
        self,
        description: str,
        provider: str = None,
        diagram_type: str = None
    ) -> Tuple[str, str]:
        """
        Generate only an SVG diagram from a text description.
        
        Args:
            description: Text description of the diagram
            provider: LLM provider to use
            diagram_type: Type of diagram
            
        Returns:
            Tuple of (svg_content, svg_path)
        """
        try:
            # Ensure the pipeline is initialized
            if not self._initialized:
                await self.initialize()
            
            # Generate SVG
            svg_content = await self.svg_generator.generate_svg(
                concept=description,
                provider=provider,
                diagram_type=diagram_type
            )
            
            # Save SVG file
            svg_filename = f"{str(uuid.uuid4())}.svg"
            svg_path = os.path.join(self.svg_output_dir, svg_filename)
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            return svg_content, svg_path
        
        except Exception as e:
            logger.error(f"Error generating SVG: {str(e)}")
            raise
    
    async def convert_svg_to_video(
        self,
        svg_path: str,
        animation_type: str = None,
        render_quality: str = "medium",
        duration: int = 10
    ) -> Dict[str, str]:
        """
        Convert an existing SVG file to a video.
        
        Args:
            svg_path: Path to SVG file
            animation_type: Type of animation to apply
            render_quality: Rendering quality
            duration: Animation duration in seconds
            
        Returns:
            Dictionary with paths to generated files
        """
        try:
            # Ensure the pipeline is initialized
            if not self._initialized:
                await self.initialize()
            
            # Generate a unique ID for this job
            job_id = str(uuid.uuid4())
            
            # Step 1: Convert SVG to 3D model
            logger.info(f"Converting SVG to 3D model: {svg_path}")
            model_filename = f"{job_id}.blend"
            model_path = os.path.join(self.model_output_dir, model_filename)
            
            conversion_result = await self.svg_to_3d_converter.convert_svg_to_3d(
                svg_path=svg_path,
                output_path=model_path
            )
            
            if not conversion_result:
                raise RuntimeError("Failed to convert SVG to 3D model")
            
            # Step 2: Add animation to the 3D model
            logger.info("Adding animation to 3D model...")
            animation_filename = f"{job_id}_animated.blend"
            animation_path = os.path.join(self.animation_output_dir, animation_filename)
            
            # Detect animation type if not specified
            if not animation_type:
                animation_type = self._detect_animation_type_from_svg(svg_path)
            
            animation_result = await self.animation_system.animate_model(
                model_path=model_path,
                output_path=animation_path,
                animation_type=animation_type,
                duration=duration
            )
            
            if not animation_result:
                raise RuntimeError("Failed to animate 3D model")
            
            # Step 3: Render the animation to video
            logger.info("Rendering animation to video...")
            video_filename = f"{job_id}.mp4"
            video_path = os.path.join(self.video_output_dir, video_filename)
            
            render_result = await self.video_renderer.render_video(
                animation_path=animation_path,
                output_path=video_path,
                quality=render_quality,
                fps=30
            )
            
            if not render_result:
                raise RuntimeError("Failed to render video")
            
            # Return paths to generated files
            return {
                "svg": svg_path,
                "model": model_path,
                "animation": animation_path,
                "video": video_path
            }
        
        except Exception as e:
            logger.error(f"Error converting SVG to video: {str(e)}")
            raise
    
    def _detect_animation_type(self, diagram_type: Optional[str]) -> str:
        """
        Detect the appropriate animation type based on diagram type.
        
        Args:
            diagram_type: Type of diagram
            
        Returns:
            Animation type (standard, flowchart, network)
        """
        if not diagram_type:
            return "standard"
        
        diagram_type = diagram_type.lower()
        if diagram_type == "flowchart":
            return "flowchart"
        elif diagram_type == "network":
            return "network"
        elif diagram_type == "sequence":
            return "sequence"
        
        return "standard"
    
    def _detect_animation_type_from_svg(self, svg_path: str) -> str:
        """
        Analyze an SVG file to detect the appropriate animation type.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            Animation type (standard, flowchart, network)
        """
        try:
            # Read SVG file
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            
            # Simple heuristics for diagram type detection
            
            # Check for flowchart elements (rectangles, diamonds, arrows)
            rectangle_count = svg_content.count("<rect")
            diamond_pattern = svg_content.count("transform=\"rotate(45")
            arrow_count = svg_content.count("<marker")
            
            # Check for network elements (circles, lines)
            circle_count = svg_content.count("<circle")
            line_count = svg_content.count("<line")
            
            # Check for sequence diagram patterns
            sequence_patterns = [
                "->", "-->", "<-", "<--",  # Arrow patterns
                "actor", "participant",     # Common sequence diagram terms
                "lifeline"                  # Another sequence diagram term
            ]
            sequence_matches = sum(1 for pattern in sequence_patterns if pattern in svg_content.lower())
            
            # Determine diagram type based on element counts
            if (rectangle_count > 5 and arrow_count > 3) or diamond_pattern > 1:
                return "flowchart"
            elif circle_count > 5 and line_count > 5:
                return "network"
            elif sequence_matches > 2:
                return "sequence"
            
            # Default to standard animation
            return "standard"
        
        except Exception as e:
            logger.warning(f"Error detecting animation type: {str(e)}")
            return "standard"  # Default to standard animation on error
