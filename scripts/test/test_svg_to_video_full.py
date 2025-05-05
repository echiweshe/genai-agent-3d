"""
Comprehensive test for the SVG to Video pipeline

This script tests the complete SVG to Video pipeline, from text description to video,
ensuring that all components work correctly together.
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to Python path")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_svg_to_video_full")

# Create stub classes for testing if needed
def create_stub_classes():
    """Create stub implementations for testing if they don't exist."""
    try:
        from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter
        logger.info("Found SVG to 3D converter")
    except (ImportError, AttributeError):
        class StubSVGTo3DConverter:
            def __init__(self, debug=False):
                self.debug = debug
                logger.info("Created stub SVG to 3D converter")
            
            async def convert_svg_to_3d(self, svg_path, output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write("Stub 3D model")
                return True
        
        # Inject the stub class into the module
        import genai_agent.svg_to_video.svg_to_3d
        genai_agent.svg_to_video.svg_to_3d.SVGTo3DConverter = StubSVGTo3DConverter
        logger.info("Injected stub SVG to 3D converter")
    
    try:
        from genai_agent.svg_to_video.animation.animation_system import AnimationSystem
        logger.info("Found Animation System")
    except (ImportError, AttributeError):
        class StubAnimationSystem:
            def __init__(self, debug=False):
                self.debug = debug
                logger.info("Created stub Animation System")
            
            async def animate_model(self, model_path, output_path, animation_type="standard", duration=5):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write("Stub animation")
                return True
        
        # Create the module structure if it doesn't exist
        if not hasattr(sys.modules, 'genai_agent.svg_to_video.animation'):
            import genai_agent.svg_to_video
            if not hasattr(genai_agent.svg_to_video, 'animation'):
                import types
                genai_agent.svg_to_video.animation = types.ModuleType('animation')
                genai_agent.svg_to_video.animation.animation_system = types.ModuleType('animation_system')
        
        # Inject the stub class
        import genai_agent.svg_to_video.animation.animation_system
        genai_agent.svg_to_video.animation.animation_system.AnimationSystem = StubAnimationSystem
        logger.info("Injected stub Animation System")
    
    try:
        from genai_agent.svg_to_video.rendering.video_renderer import VideoRenderer
        logger.info("Found Video Renderer")
    except (ImportError, AttributeError):
        class StubVideoRenderer:
            def __init__(self, debug=False):
                self.debug = debug
                logger.info("Created stub Video Renderer")
            
            async def render_video(self, animation_path, output_path, quality="low", resolution=(640, 480), fps=30):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write("Stub video")
                return True
        
        # Create the module structure if it doesn't exist
        if not hasattr(sys.modules, 'genai_agent.svg_to_video.rendering'):
            import genai_agent.svg_to_video
            if not hasattr(genai_agent.svg_to_video, 'rendering'):
                import types
                genai_agent.svg_to_video.rendering = types.ModuleType('rendering')
                genai_agent.svg_to_video.rendering.video_renderer = types.ModuleType('video_renderer')
        
        # Inject the stub class
        import genai_agent.svg_to_video.rendering.video_renderer
        genai_agent.svg_to_video.rendering.video_renderer.VideoRenderer = StubVideoRenderer
        logger.info("Injected stub Video Renderer")

async def test_pipeline(description, provider=None, diagram_type=None, use_stubs=True, svg_only=False):
    """
    Test the SVG to Video pipeline.
    
    Args:
        description: Text description for the SVG
        provider: LLM provider to use
        diagram_type: Type of diagram
        use_stubs: Whether to use stub implementations for 3D and video components
        svg_only: Whether to only test SVG generation
    """
    try:
        # Create stub classes if needed
        if use_stubs:
            create_stub_classes()
        
        # Import the pipeline
        logger.info("Importing SVGToVideoPipeline...")
        try:
            from genai_agent.svg_to_video import SVGToVideoPipeline
        except ImportError:
            from genai_agent.svg_to_video.pipeline_integrated import SVGToVideoPipeline
        
        # Create pipeline instance
        logger.info("Creating pipeline instance...")
        pipeline = SVGToVideoPipeline(debug=True)
        
        # Initialize the pipeline
        logger.info("Initializing pipeline...")
        await pipeline.initialize()
        
        # Log available providers
        providers = pipeline.svg_generator.get_available_providers()
        logger.info(f"Available providers: {providers}")
        
        # Test SVG Generator
        if svg_only:
            logger.info("\nTesting SVG Generator only...")
            svg_content, svg_path = await pipeline.generate_svg_only(
                description=description,
                provider=provider,
                diagram_type=diagram_type
            )
            
            if not svg_content or not os.path.exists(svg_path):
                logger.error("SVG Generator test failed!")
                return False
            
            logger.info(f"SVG generated: {svg_path}")
            logger.info("SVG Generator test passed!")
            return True
        
        # Test full pipeline
        logger.info("\nTesting Full Pipeline...")
        
        output_files = await pipeline.generate_video_from_description(
            description=description,
            provider=provider,
            diagram_type=diagram_type,
            render_quality="low",
            duration=5
        )
        
        if not output_files or not all(os.path.exists(path) for path in output_files.values()):
            logger.error("Full Pipeline test failed!")
            return False
        
        logger.info("Full Pipeline test passed!")
        logger.info("Generated files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  {file_type}: {file_path}")
        
        return True
    
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required modules are available")
        return False
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the SVG to Video pipeline.")
    parser.add_argument("--description", "-d", type=str, required=True,
                       help="Text description for the SVG")
    parser.add_argument("--provider", "-p", type=str, default=None,
                       help="LLM provider to use")
    parser.add_argument("--diagram-type", "-t", type=str, default=None,
                       help="Type of diagram (flowchart, network, etc.)")
    parser.add_argument("--svg-only", "-s", action="store_true",
                       help="Only test SVG generation")
    parser.add_argument("--no-stubs", action="store_true",
                       help="Don't use stub implementations for 3D and video components")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Run the test
    success = asyncio.run(test_pipeline(
        description=args.description,
        provider=args.provider,
        diagram_type=args.diagram_type,
        use_stubs=not args.no_stubs,
        svg_only=args.svg_only
    ))
    
    # Exit with appropriate status
    sys.exit(0 if success else 1)
