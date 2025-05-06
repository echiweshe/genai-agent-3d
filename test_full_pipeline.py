"""
Test script for the full SVG to Video pipeline.
This script tests the entire pipeline from SVG generation to video rendering.
"""

import os
import sys
import time
from pathlib import Path

# Add project directory to path
project_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project")
sys.path.insert(0, str(project_dir))

# Import modules
try:
    # Import SVG generator
    from genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator import generate_svg
    print("Successfully imported SVG generator")
    
    # Import SVG to 3D converter
    from genai_agent_project.genai_agent.svg_to_video.svg_to_3d import convert_svg_to_3d
    print("Successfully imported SVG to 3D converter")
    
    # Import animation module
    from genai_agent_project.genai_agent.svg_to_video.animation import animate_model
    print("Successfully imported animation module")
    
    # Import rendering module
    from genai_agent_project.genai_agent.svg_to_video.rendering import render_video
    print("Successfully imported rendering module")
except ImportError as e:
    print(f"Error importing pipeline modules: {e}")
    sys.exit(1)

# Define paths
project_root = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d")
svg_dir = project_root / "output" / "svg"
models_dir = project_root / "output" / "svg_to_video" / "models"
animations_dir = project_root / "output" / "svg_to_video" / "animations"
videos_dir = project_root / "output" / "svg_to_video" / "videos"

def ensure_directories():
    """Ensure all output directories exist."""
    os.makedirs(svg_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(animations_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)

def test_svg_generation(prompt, provider="claude-direct"):
    """Test SVG generation."""
    print(f"\n=== STAGE 1: SVG Generation ===")
    print(f"Generating SVG with prompt: '{prompt}'")
    print(f"Provider: {provider}")
    
    # Generate a unique filename with timestamp
    timestamp = int(time.time())
    filename = f"pipeline_test_{timestamp}.svg"
    output_file = svg_dir / filename
    
    try:
        # Generate the SVG
        result = generate_svg(
            prompt=prompt,
            diagram_type="flowchart",
            output_file=str(output_file),
            provider=provider
        )
        
        if result and os.path.isfile(output_file):
            print(f"✅ SVG generation successful")
            print(f"📄 Output file: {output_file}")
            print(f"📊 File size: {os.path.getsize(output_file)} bytes")
            return output_file
        else:
            print(f"❌ SVG generation failed")
            return None
    except Exception as e:
        print(f"❌ Error generating SVG: {e}")
        return None

def test_svg_to_3d_conversion(svg_path):
    """Test SVG to 3D conversion."""
    if not svg_path:
        print("⚠️ Skipping 3D conversion due to failed SVG generation")
        return None
    
    print(f"\n=== STAGE 2: SVG to 3D Conversion ===")
    print(f"Converting SVG to 3D: {svg_path}")
    
    # Generate output file path
    output_file = models_dir / f"{svg_path.stem}.obj"
    
    try:
        # Convert SVG to 3D
        result = convert_svg_to_3d(
            svg_path=str(svg_path),
            output_file=str(output_file),
            extrude_height=10.0,
            scale_factor=1.0
        )
        
        if result and os.path.isfile(result):
            print(f"✅ SVG to 3D conversion successful")
            print(f"📄 Output file: {result}")
            print(f"📊 File size: {os.path.getsize(result)} bytes")
            return result
        else:
            print(f"❌ SVG to 3D conversion failed")
            return None
    except Exception as e:
        print(f"❌ Error converting SVG to 3D: {e}")
        return None

def test_animation(model_path):
    """Test animation."""
    if not model_path:
        print("⚠️ Skipping animation due to failed 3D conversion")
        return None
    
    print(f"\n=== STAGE 3: 3D Model Animation ===")
    print(f"Animating 3D model: {model_path}")
    
    # Generate output file path
    output_file = animations_dir / f"{Path(model_path).stem}_animated.blend"
    
    try:
        # Animate model
        result = animate_model(
            model_path=str(model_path),
            output_file=str(output_file),
            animation_type="rotation",
            duration=5.0
        )
        
        if result and os.path.isfile(result):
            print(f"✅ Animation successful")
            print(f"📄 Output file: {result}")
            print(f"📊 File size: {os.path.getsize(result)} bytes")
            return result
        else:
            print(f"❌ Animation failed")
            return None
    except Exception as e:
        print(f"❌ Error animating model: {e}")
        return None

def test_rendering(animation_path):
    """Test rendering."""
    if not animation_path:
        print("⚠️ Skipping rendering due to failed animation")
        return None
    
    print(f"\n=== STAGE 4: Video Rendering ===")
    print(f"Rendering video from animation: {animation_path}")
    
    # Generate output file path
    output_file = videos_dir / f"{Path(animation_path).stem}.mp4"
    
    try:
        # Render video
        result = render_video(
            animation_path=str(animation_path),
            output_file=str(output_file),
            resolution="720p",
            quality="medium"
        )
        
        if result and os.path.isfile(result):
            print(f"✅ Rendering successful")
            print(f"📄 Output file: {result}")
            print(f"📊 File size: {os.path.getsize(result)} bytes")
            return result
        else:
            print(f"❌ Rendering failed")
            return None
    except Exception as e:
        print(f"❌ Error rendering video: {e}")
        return None

def run_full_pipeline_test():
    """Run a test of the full pipeline."""
    ensure_directories()
    
    print("\n🔍 SVG to Video Pipeline Full Test 🔍")
    print("=================================")
    
    # Get test prompt from user
    prompt = input("\nEnter a prompt for SVG generation (or press Enter for default): ")
    if not prompt:
        prompt = "Create a flowchart showing the process of making coffee"
    
    # Get provider from user
    provider = input("\nEnter LLM provider to use (claude-direct, openai, ollama, mock): ")
    if not provider:
        provider = "claude-direct"
    
    # Run the pipeline
    start_time = time.time()
    
    svg_file = test_svg_generation(prompt, provider)
    model_file = test_svg_to_3d_conversion(svg_file)
    animation_file = test_animation(model_file)
    video_file = test_rendering(animation_file)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print("\n=== Pipeline Test Summary ===")
    print(f"Total time: {duration:.2f} seconds")
    print(f"SVG Generation: {'✅ Success' if svg_file else '❌ Failed'}")
    print(f"SVG to 3D Conversion: {'✅ Success' if model_file else '❌ Failed'}")
    print(f"Animation: {'✅ Success' if animation_file else '❌ Failed'}")
    print(f"Rendering: {'✅ Success' if video_file else '❌ Failed'}")
    
    if video_file:
        print(f"\n🎉 Full pipeline test PASSED! 🎉")
        print(f"Final video: {video_file}")
        return True
    else:
        print(f"\n😞 Full pipeline test FAILED at some stage")
        return False

if __name__ == "__main__":
    success = run_full_pipeline_test()
    sys.exit(0 if success else 1)
