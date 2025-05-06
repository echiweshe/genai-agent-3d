"""
Integrated SVG to Video Pipeline.

This module provides an integrated pipeline that combines all steps of
the SVG to Video process: SVG generation, 3D conversion, animation,
and rendering.
"""

import os
import sys
import logging
import tempfile
import subprocess
from pathlib import Path

# Import pipeline components
from .svg_generator import SVGGenerator
from .svg_to_3d import SVGTo3DConverter
from .animation.model_animator import ModelAnimator
from .rendering.video_renderer import VideoRenderer

# Configure logging
logger = logging.getLogger(__name__)

class SVGToVideoPipeline:
    """
    Integrated pipeline for SVG to Video conversion.
    
    This class orchestrates the entire pipeline from SVG generation to
    video rendering, providing a seamless way to generate videos from
    text descriptions.
    """
    
    def __init__(self, blender_path=None, output_dir=None):
        """
        Initialize the SVG to Video pipeline.
        
        Args:
            blender_path (str, optional): Path to the Blender executable.
                If not provided, it will try to get it from the environment.
            output_dir (str, optional): Directory for output files.
                If not provided, it will use the default output directory.
        """
        # Get Blender path
        self.blender_path = blender_path
        
        if not self.blender_path:
            # Try to get from environment
            self.blender_path = os.environ.get("BLENDER_PATH")
        
        # Set output directory
        self.output_dir = output_dir
        
        if not self.output_dir:
            # Use default output directory
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.output_dir = os.path.join(base_dir, "output", "svg_to_video")
            
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize pipeline components
        self.svg_generator = SVGGenerator()
        self.svg_to_3d_converter = SVGTo3DConverter(blender_path=self.blender_path)
        self.model_animator = ModelAnimator(blender_path=self.blender_path)
        self.video_renderer = VideoRenderer(blender_path=self.blender_path)
        
        # Set up output subdirectories
        self.svg_dir = os.path.join(self.output_dir, "svg")
        self.models_dir = os.path.join(self.output_dir, "models")
        self.animations_dir = os.path.join(self.output_dir, "animations")
        self.videos_dir = os.path.join(self.output_dir, "videos")
        
        # Create subdirectories if they don't exist
        for directory in [self.svg_dir, self.models_dir, self.animations_dir, self.videos_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def generate_video(self, description, diagram_type="flowchart", name=None, provider=None, 
                      animation_type="simple", video_quality="medium", 
                      duration=10.0, video_format="MP4", **kwargs):
        """
        Generate a video from a text description.
        
        This method orchestrates the entire pipeline:
        1. Generate SVG from description
        2. Convert SVG to 3D model
        3. Animate the 3D model
        4. Render the animation to video
        
        Args:
            description (str): Text description of the diagram
            diagram_type (str, optional): Type of diagram to generate
            name (str, optional): Name for the generated files
            provider (str, optional): LLM provider for SVG generation
            animation_type (str, optional): Type of animation
            video_quality (str, optional): Quality of video rendering
            duration (float, optional): Duration of the video in seconds
            video_format (str, optional): Format of the output video
            **kwargs: Additional parameters for each step
        
        Returns:
            dict: Dictionary with paths to all generated files and status
        """
        result = {
            "status": "in_progress",
            "steps": {
                "svg_generation": {"status": "pending"},
                "svg_to_3d": {"status": "pending"},
                "animation": {"status": "pending"},
                "rendering": {"status": "pending"}
            },
            "files": {},
            "error": None
        }
        
        try:
            # Step 1: Generate SVG
            logger.info(f"Generating SVG from description: {description[:50]}...")
            svg_result = self.svg_generator.generate_svg(
                description, 
                diagram_type=diagram_type,
                name=name,
                provider=provider,
                **kwargs.get("svg_options", {})
            )
            
            if not svg_result or svg_result.get("status") != "success":
                error_msg = "SVG generation failed"
                if svg_result and svg_result.get("error"):
                    error_msg += f": {svg_result['error']}"
                
                result["status"] = "error"
                result["error"] = error_msg
                result["steps"]["svg_generation"]["status"] = "error"
                result["steps"]["svg_generation"]["error"] = error_msg
                return result
            
            # Update result with SVG information
            result["steps"]["svg_generation"]["status"] = "success"
            result["files"]["svg_path"] = svg_result["file_path"]
            result["files"]["svg_code"] = svg_result["code"]
            
            svg_path = svg_result["file_path"]
            
            # Step 2: Convert SVG to 3D
            logger.info(f"Converting SVG to 3D: {svg_path}...")
            
            # Generate output path for 3D model
            svg_name = os.path.basename(svg_path)
            model_name = f"{os.path.splitext(svg_name)[0]}_3d.obj"
            model_path = os.path.join(self.models_dir, model_name)
            
            # Convert SVG to 3D
            model_path = self.svg_to_3d_converter.convert_svg_to_3d(
                svg_path, 
                output_file=model_path,
                **kwargs.get("model_options", {})
            )
            
            if not model_path:
                error_msg = "SVG to 3D conversion failed"
                result["status"] = "error"
                result["error"] = error_msg
                result["steps"]["svg_to_3d"]["status"] = "error"
                result["steps"]["svg_to_3d"]["error"] = error_msg
                return result
            
            # Update result with 3D model information
            result["steps"]["svg_to_3d"]["status"] = "success"
            result["files"]["model_path"] = model_path
            
            # Step 3: Animate the 3D model
            logger.info(f"Animating 3D model: {model_path}...")
            
            # Generate output path for animated model
            animated_model_name = f"{os.path.splitext(svg_name)[0]}_animated.blend"
            animated_model_path = os.path.join(self.animations_dir, animated_model_name)
            
            # Animate the model
            animated_model_path = self.model_animator.animate_model(
                model_path,
                output_path=animated_model_path,
                animation_type=animation_type,
                duration=duration,
                **kwargs.get("animation_options", {})
            )
            
            if not animated_model_path:
                error_msg = "Model animation failed"
                result["status"] = "error"
                result["error"] = error_msg
                result["steps"]["animation"]["status"] = "error"
                result["steps"]["animation"]["error"] = error_msg
                return result
            
            # Update result with animated model information
            result["steps"]["animation"]["status"] = "success"
            result["files"]["animated_model_path"] = animated_model_path
            
            # Step 4: Render the animation to video
            logger.info(f"Rendering animation to video: {animated_model_path}...")
            
            # Generate output path for video
            video_name = f"{os.path.splitext(svg_name)[0]}_video.{video_format.lower()}"
            video_path = os.path.join(self.videos_dir, video_name)
            
            # Render the video
            video_path = self.video_renderer.render_video(
                animated_model_path,
                output_path=video_path,
                quality=video_quality,
                duration=duration,
                output_format=video_format,
                **kwargs.get("render_options", {})
            )
            
            if not video_path:
                error_msg = "Video rendering failed"
                result["status"] = "error"
                result["error"] = error_msg
                result["steps"]["rendering"]["status"] = "error"
                result["steps"]["rendering"]["error"] = error_msg
                return result
            
            # Update result with video information
            result["steps"]["rendering"]["status"] = "success"
            result["files"]["video_path"] = video_path
            
            # Successfully completed all steps
            result["status"] = "success"
            
            # Add final output information
            result["output"] = {
                "video_path": video_path,
                "video_name": video_name,
                "duration": duration,
                "format": video_format
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error in SVG to Video pipeline: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
            return result
    
    def generate_svg_only(self, description, diagram_type="flowchart", name=None, provider=None, **kwargs):
        """
        Generate an SVG from a text description.
        
        This method runs only the SVG generation step of the pipeline.
        
        Args:
            description (str): Text description of the diagram
            diagram_type (str, optional): Type of diagram to generate
            name (str, optional): Name for the generated files
            provider (str, optional): LLM provider for SVG generation
            **kwargs: Additional parameters for SVG generation
        
        Returns:
            dict: Result of SVG generation
        """
        try:
            # Generate SVG
            svg_result = self.svg_generator.generate_svg(
                description, 
                diagram_type=diagram_type,
                name=name,
                provider=provider,
                **kwargs
            )
            
            return svg_result
        
        except Exception as e:
            logger.error(f"Error in SVG generation: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def convert_svg_to_3d_only(self, svg_path, output_path=None, **kwargs):
        """
        Convert an SVG to a 3D model.
        
        This method runs only the SVG to 3D conversion step of the pipeline.
        
        Args:
            svg_path (str): Path to the input SVG file
            output_path (str, optional): Path to save the output 3D model
            **kwargs: Additional parameters for SVG to 3D conversion
        
        Returns:
            dict: Result of SVG to 3D conversion
        """
        try:
            # If output path is not provided, generate one
            if not output_path:
                svg_name = os.path.basename(svg_path)
                model_name = f"{os.path.splitext(svg_name)[0]}_3d.obj"
                output_path = os.path.join(self.models_dir, model_name)
            
            # Convert SVG to 3D
            model_path = self.svg_to_3d_converter.convert_svg_to_3d(
                svg_path, 
                output_file=output_path,
                **kwargs
            )
            
            if not model_path:
                return {
                    "status": "error",
                    "error": "SVG to 3D conversion failed"
                }
            
            return {
                "status": "success",
                "model_path": model_path,
                "message": "SVG converted to 3D model successfully"
            }
        
        except Exception as e:
            logger.error(f"Error in SVG to 3D conversion: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def animate_model_only(self, model_path, output_path=None, animation_type="simple", duration=10.0, **kwargs):
        """
        Animate a 3D model.
        
        This method runs only the animation step of the pipeline.
        
        Args:
            model_path (str): Path to the input 3D model file
            output_path (str, optional): Path to save the animated model
            animation_type (str, optional): Type of animation
            duration (float, optional): Duration of the animation in seconds
            **kwargs: Additional parameters for animation
        
        Returns:
            dict: Result of model animation
        """
        try:
            # If output path is not provided, generate one
            if not output_path:
                model_name = os.path.basename(model_path)
                animated_model_name = f"{os.path.splitext(model_name)[0]}_animated.blend"
                output_path = os.path.join(self.animations_dir, animated_model_name)
            
            # Animate the model
            animated_model_path = self.model_animator.animate_model(
                model_path,
                output_path=output_path,
                animation_type=animation_type,
                duration=duration,
                **kwargs
            )
            
            if not animated_model_path:
                return {
                    "status": "error",
                    "error": "Model animation failed"
                }
            
            return {
                "status": "success",
                "animated_model_path": animated_model_path,
                "message": "3D model animated successfully"
            }
        
        except Exception as e:
            logger.error(f"Error in model animation: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def render_video_only(self, animated_model_path, output_path=None, quality="medium", duration=10.0, video_format="MP4", **kwargs):
        """
        Render an animated model to video.
        
        This method runs only the rendering step of the pipeline.
        
        Args:
            animated_model_path (str): Path to the input animated model file
            output_path (str, optional): Path to save the output video
            quality (str, optional): Quality of video rendering
            duration (float, optional): Duration of the video in seconds
            video_format (str, optional): Format of the output video
            **kwargs: Additional parameters for rendering
        
        Returns:
            dict: Result of video rendering
        """
        try:
            # If output path is not provided, generate one
            if not output_path:
                model_name = os.path.basename(animated_model_path)
                video_name = f"{os.path.splitext(model_name)[0]}_video.{video_format.lower()}"
                output_path = os.path.join(self.videos_dir, video_name)
            
            # Render the video
            video_path = self.video_renderer.render_video(
                animated_model_path,
                output_path=output_path,
                quality=quality,
                duration=duration,
                output_format=video_format,
                **kwargs
            )
            
            if not video_path:
                return {
                    "status": "error",
                    "error": "Video rendering failed"
                }
            
            return {
                "status": "success",
                "video_path": video_path,
                "message": "Animation rendered to video successfully"
            }
        
        except Exception as e:
            logger.error(f"Error in video rendering: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_pipeline_status(self):
        """
        Get status information about the SVG to Video pipeline.
        
        Returns:
            dict: Status information including available components
        """
        # Check if Blender is available
        blender_available = False
        if self.blender_path and os.path.exists(self.blender_path):
            blender_available = True
        
        # Check output directories
        directories_status = {
            "svg_dir": os.path.exists(self.svg_dir) and os.path.isdir(self.svg_dir),
            "models_dir": os.path.exists(self.models_dir) and os.path.isdir(self.models_dir),
            "animations_dir": os.path.exists(self.animations_dir) and os.path.isdir(self.animations_dir),
            "videos_dir": os.path.exists(self.videos_dir) and os.path.isdir(self.videos_dir)
        }
        
        # Check if all pipeline components are available
        svg_generator_available = hasattr(self, 'svg_generator')
        svg_to_3d_available = hasattr(self, 'svg_to_3d_converter') and blender_available
        animation_available = hasattr(self, 'model_animator') and blender_available
        rendering_available = hasattr(self, 'video_renderer') and blender_available
        
        return {
            "status": "available" if all([svg_generator_available, svg_to_3d_available, animation_available, rendering_available]) else "partial",
            "components": {
                "svg_generator": svg_generator_available,
                "svg_to_3d": svg_to_3d_available,
                "model_animator": animation_available,
                "video_renderer": rendering_available
            },
            "blender": {
                "available": blender_available,
                "path": self.blender_path if blender_available else None
            },
            "directories": directories_status,
            "output_dir": self.output_dir
        }
