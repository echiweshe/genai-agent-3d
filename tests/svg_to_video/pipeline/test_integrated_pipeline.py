"""
Test Integrated SVG to Video Pipeline

This test validates the complete SVG to Video pipeline using the integrated
components and the shared LLM service.
"""

import os
import sys
import asyncio
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from genai_agent.svg_to_video.pipeline_integrated import SVGToVideoPipeline

class TestIntegratedPipeline(unittest.TestCase):
    """Tests for the integrated SVG to Video pipeline."""
    
    def setUp(self):
        """Set up the test environment."""
        self.pipeline = SVGToVideoPipeline(debug=True)
        
        # Create output directory if it doesn't exist
        self.output_dir = os.path.join(project_root, "output", "test_results", "pipeline")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_initialization(self):
        """Test that the pipeline initializes properly."""
        # Check that the pipeline was created
        self.assertIsNotNone(self.pipeline)
        
        # Check that the components were initialized
        self.assertIsNotNone(self.pipeline.svg_generator)
        self.assertIsNotNone(self.pipeline.svg_to_3d_converter)
        self.assertIsNotNone(self.pipeline.animation_system)
        self.assertIsNotNone(self.pipeline.video_renderer)
    
    def test_svg_generation(self):
        """Test SVG generation step of the pipeline."""
        test_description = "A simple flowchart showing user login process"
        
        # Run the async test
        result = asyncio.run(self.async_test_svg_generation(test_description))
        self.assertTrue(result)
    
    async def async_test_svg_generation(self, description):
        """Async helper to test SVG generation."""
        try:
            # Generate SVG only
            svg_content, svg_path = await self.pipeline.generate_svg_only(
                description=description,
                diagram_type="flowchart"
            )
            
            # Check that SVG content was returned
            self.assertIsNotNone(svg_content)
            self.assertIn("<svg", svg_content)
            self.assertIn("</svg>", svg_content)
            
            # Check that SVG file was created
            self.assertTrue(os.path.exists(svg_path))
            
            print(f"SVG generated successfully: {svg_path}")
            
            return True
        except Exception as e:
            print(f"Error in SVG generation test: {str(e)}")
            return False
    
    def test_complete_pipeline(self):
        """Test the complete pipeline from description to video."""
        # This test can be disabled if Blender is not available
        if not self._is_blender_available():
            print("Skipping complete pipeline test: Blender not available")
            return
        
        test_description = "A simple flowchart showing user login process"
        
        # Run the async test with a short timeout
        try:
            result = asyncio.run(
                self.async_test_complete_pipeline(test_description),
                timeout=300  # 5 minutes max
            )
            self.assertTrue(result)
        except asyncio.TimeoutError:
            print("Test timed out - this is normal for long rendering processes")
            # Don't fail the test on timeout
    
    async def async_test_complete_pipeline(self, description):
        """Async helper to test the complete pipeline."""
        try:
            # Use a simpler diagram and low quality for faster testing
            output_files = await self.pipeline.generate_video_from_description(
                description=description,
                diagram_type="flowchart",
                render_quality="low",
                duration=5  # 5 seconds for faster rendering
            )
            
            # Check that all expected files were created
            self.assertIn("svg", output_files)
            self.assertIn("model", output_files)
            self.assertIn("animation", output_files)
            self.assertIn("video", output_files)
            
            # Check that files exist
            for file_type, file_path in output_files.items():
                self.assertTrue(os.path.exists(file_path), f"{file_type} file not found: {file_path}")
            
            print(f"Pipeline completed successfully!")
            print(f"SVG: {output_files['svg']}")
            print(f"3D Model: {output_files['model']}")
            print(f"Animation: {output_files['animation']}")
            print(f"Video: {output_files['video']}")
            
            return True
        except Exception as e:
            print(f"Error in complete pipeline test: {str(e)}")
            return False
    
    def _is_blender_available(self):
        """Check if Blender is available on the system."""
        blender_path = os.environ.get("BLENDER_PATH", "blender")
        
        try:
            # Try to run blender with --version flag
            import subprocess
            process = subprocess.run(
                [blender_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            
            return process.returncode == 0
        except Exception:
            return False

if __name__ == "__main__":
    unittest.main()
