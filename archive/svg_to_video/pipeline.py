"""
SVG to Video Pipeline

This module orchestrates the entire SVG to Video pipeline, from SVG generation
to video rendering. It coordinates the various components and handles the flow
of data between them.
"""

import os
import uuid
import asyncio
import logging
import tempfile
import shutil
from typing import Dict, Any, Optional, List, Union

from .svg_generator import SVGGenerator
# Import our new modularized converter
from .svg_to_3d.svg_parser import SVGParser
from .svg_to_3d.svg_converter import SVGTo3DConverter as ModularSVGTo3DConverter
from .svg_to_3d_converter import SVGTo3DConverter as OldSVGTo3DConverter
from .animation_system import AnimationSystem
from .video_renderer import VideoRenderer

logger = logging.getLogger(__name__)

class SVGToVideoPipeline:
    """Orchestrate the SVG to Video pipeline."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SVG to Video Pipeline.
        
        Args:
            config: Configuration dictionary with settings for all components
        """
        self.config = config or {}
        self.temp_dir = self.config.get("temp_dir", os.path.join(tempfile.gettempdir(), "svg_pipeline"))
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize components
        self.svg_generator = SVGGenerator()
        # Use the new modular converter by default
        self.svg_to_3d_converter = ModularSVGTo3DConverter()
        # Keep old converter for fallback
        self.old_svg_to_3d_converter = OldSVGTo3DConverter(self.config)
        self.animation_system = AnimationSystem(self.config)
        self.video_renderer = VideoRenderer(self.config)
    
    async def process(self, concept: str, output_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a concept through the pipeline to create a video.
        
        Args:
            concept: Text description of the diagram to generate
            output_path: Path to save the output video file
            options: Additional options for the pipeline
            
        Returns:
            Dictionary with status and output information
        """
        options = options or {}
        
        # Create unique job ID and working directory
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(self.temp_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        try:
            logger.info(f"Starting pipeline for concept: {concept[:50]}...")
            
            # Step 1: Generate SVG
            provider = options.get("provider", "claude")
            svg_content = await self.svg_generator.generate_svg(concept, provider=provider)
            
            svg_path = os.path.join(job_dir, "diagram.svg")
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            logger.info(f"Generated SVG saved to {svg_path}")
            
            # Step 2: Convert SVG to 3D model
            model_path = os.path.join(job_dir, "model.blend")
            try:
                # First try new modular converter
                parser = SVGParser(svg_path)
                elements, width, height = parser.parse()
                
                if not elements:
                    logger.warning("No elements found in SVG, falling back to old converter")
                    model_path = await self.old_svg_to_3d_converter.convert(svg_path, model_path)
                else:
                    svg_data = {
                        'elements': elements,
                        'width': width,
                        'height': height
                    }
                    result = self.svg_to_3d_converter.convert(svg_data)
                    if result:
                        # Save the Blender file
                        import bpy
                        bpy.ops.wm.save_as_mainfile(filepath=model_path)
                    else:
                        logger.warning("Modular converter failed, falling back to old converter")
                        model_path = await self.old_svg_to_3d_converter.convert(svg_path, model_path)
            except Exception as e:
                logger.warning(f"Error with modular converter: {e}, falling back to old converter")
                model_path = await self.old_svg_to_3d_converter.convert(svg_path, model_path)
            
            logger.info(f"Converted 3D model saved to {model_path}")
            
            # Step 3: Apply animations
            animated_path = os.path.join(job_dir, "animated.blend")
            
            # Set animation options if provided
            if "animation_type" in options:
                self.animation_system.set_animation_type(options["animation_type"])
            if "animation_duration" in options:
                self.animation_system.set_animation_duration(options["animation_duration"])
                
            animated_path = await self.animation_system.animate(model_path, animated_path)
            
            logger.info(f"Animated scene saved to {animated_path}")
            
            # Step 4: Render video
            # Set rendering options if provided
            if "render_quality" in options:
                self.video_renderer.set_quality(options["render_quality"])
            if "resolution" in options:
                self.video_renderer.set_resolution(*options["resolution"])
            if "fps" in options:
                self.video_renderer.set_fps(options["fps"])
                
            output_path = await self.video_renderer.render(animated_path, output_path)
            
            logger.info(f"Video rendered to {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "job_id": job_id,
                "svg_path": svg_path,
                "model_path": model_path,
                "animated_path": animated_path
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "job_id": job_id
            }
        finally:
            # Cleanup temporary files if needed
            if self.config.get("cleanup_temp", True):
                shutil.rmtree(job_dir)
    
    async def generate_svg_only(self, concept: str, output_path: Optional[str] = None, 
                              provider: str = "claude") -> Dict[str, Any]:
        """
        Generate an SVG diagram only (without further processing).
        
        Args:
            concept: Text description of the diagram to generate
            output_path: Path to save the SVG file (optional)
            provider: LLM provider to use
            
        Returns:
            Dictionary with status and SVG information
        """
        try:
            svg_content = await self.svg_generator.generate_svg(concept, provider=provider)
            
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                logger.info(f"SVG saved to {output_path}")
            
            return {
                "status": "success",
                "svg_content": svg_content,
                "output_path": output_path
            }
        
        except Exception as e:
            logger.error(f"SVG generation error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def convert_existing_svg(self, svg_path: str, output_path: str, 
                                 options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an existing SVG through the pipeline to create a video.
        
        Args:
            svg_path: Path to the input SVG file
            output_path: Path to save the output video file
            options: Additional options for the pipeline
            
        Returns:
            Dictionary with status and output information
        """
        options = options or {}
        
        # Create unique job ID and working directory
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(self.temp_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        try:
            logger.info(f"Starting pipeline for existing SVG: {svg_path}")
            
            # Step 1: Convert SVG to 3D model
            model_path = os.path.join(job_dir, "model.blend")
            try:
                # First try new modular converter
                parser = SVGParser(svg_path)
                elements, width, height = parser.parse()
                
                if not elements:
                    logger.warning("No elements found in SVG, falling back to old converter")
                    model_path = await self.old_svg_to_3d_converter.convert(svg_path, model_path)
                else:
                    svg_data = {
                        'elements': elements,
                        'width': width,
                        'height': height
                    }
                    result = self.svg_to_3d_converter.convert(svg_data)
                    if result:
                        # Save the Blender file
                        import bpy
                        bpy.ops.wm.save_as_mainfile(filepath=model_path)
                    else:
                        logger.warning("Modular converter failed, falling back to old converter")
                        model_path = await self.old_svg_to_3d_converter.convert(svg_path, model_path)
            except Exception as e:
                logger.warning(f"Error with modular converter: {e}, falling back to old converter")
                model_path = await self.old_svg_to_3d_converter.convert(svg_path, model_path)
            
            logger.info(f"Converted 3D model saved to {model_path}")
            
            # Step 2: Apply animations
            animated_path = os.path.join(job_dir, "animated.blend")
            
            # Set animation options if provided
            if "animation_type" in options:
                self.animation_system.set_animation_type(options["animation_type"])
            if "animation_duration" in options:
                self.animation_system.set_animation_duration(options["animation_duration"])
                
            animated_path = await self.animation_system.animate(model_path, animated_path)
            
            logger.info(f"Animated scene saved to {animated_path}")
            
            # Step 3: Render video
            # Set rendering options if provided
            if "render_quality" in options:
                self.video_renderer.set_quality(options["render_quality"])
            if "resolution" in options:
                self.video_renderer.set_resolution(*options["resolution"])
            if "fps" in options:
                self.video_renderer.set_fps(options["fps"])
                
            output_path = await self.video_renderer.render(animated_path, output_path)
            
            logger.info(f"Video rendered to {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "job_id": job_id,
                "model_path": model_path,
                "animated_path": animated_path
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "job_id": job_id
            }
        finally:
            # Cleanup temporary files if needed
            if self.config.get("cleanup_temp", True):
                shutil.rmtree(job_dir)
    
    async def convert_svg_to_3d_only(self, svg_path: str, output_path: str) -> Dict[str, Any]:
        """
        Convert an SVG to a 3D model only.
        
        Args:
            svg_path: Path to the input SVG file
            output_path: Path to save the output Blender file
            
        Returns:
            Dictionary with status and output information
        """
        try:
            # Try new modular converter first
            parser = SVGParser(svg_path)
            elements, width, height = parser.parse()
            
            if not elements:
                logger.warning("No elements found in SVG, falling back to old converter")
                model_path = await self.old_svg_to_3d_converter.convert(svg_path, output_path)
            else:
                svg_data = {
                    'elements': elements,
                    'width': width,
                    'height': height
                }
                result = self.svg_to_3d_converter.convert(svg_data)
                if result:
                    # Save the Blender file
                    import bpy
                    bpy.ops.wm.save_as_mainfile(filepath=output_path)
                    model_path = output_path
                else:
                    logger.warning("Modular converter failed, falling back to old converter")
                    model_path = await self.old_svg_to_3d_converter.convert(svg_path, output_path)
            
            return {
                "status": "success",
                "output_path": model_path
            }
        
        except Exception as e:
            logger.error(f"SVG to 3D conversion error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of provider names
        """
        return self.svg_generator.get_available_providers()
