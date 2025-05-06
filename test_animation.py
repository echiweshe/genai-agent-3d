"""
Test script for animation.
This script tests the animation functionality.
"""

import os
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project")
sys.path.insert(0, str(project_dir))

# Import animation module
try:
    from genai_agent_project.genai_agent.svg_to_video.animation import animate_model, get_supported_animation_types, get_animation_options
    print("Successfully imported animation module")
except ImportError as e:
    print(f"Error importing animation module: {e}")
    sys.exit(1)

# Define paths
project_root = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d")
models_dir = project_root / "output" / "svg_to_video" / "models"
animations_dir = project_root / "output" / "svg_to_video" / "animations"

def list_3d_models():
    """List available 3D models."""
    if not models_dir.exists():
        print(f"Models directory not found: {models_dir}")
        return []
    
    model_files = list(models_dir.glob("*.obj")) + list(models_dir.glob("*.stl")) + \
                  list(models_dir.glob("*.fbx")) + list(models_dir.glob("*.glb")) + \
                  list(models_dir.glob("*.gltf"))
    return model_files

def test_animation(model_path, animation_type="rotation"):
    """Test animation with a specific 3D model."""
    print(f"\nTesting animation with: {model_path}")
    print(f"Animation type: {animation_type}")
    
    # Create animations directory if it doesn't exist
    os.makedirs(animations_dir, exist_ok=True)
    
    # Generate output file path
    output_file = animations_dir / f"{model_path.stem}_{animation_type}.blend"
    
    try:
        # Animate model
        result = animate_model(
            model_path=str(model_path),
            output_file=str(output_file),
            animation_type=animation_type,
            duration=5.0
        )
        
        if result and os.path.isfile(result):
            print(f"Success! Animation generated at: {result}")
            print(f"File size: {os.path.getsize(result)} bytes")
            return True
        else:
            print("Failed to animate model")
            return False
    except Exception as e:
        print(f"Error animating model: {e}")
        return False

def main():
    """Main function to test animation."""
    print("3D Model Animation Test")
    print("======================")
    
    # Get supported animation types
    supported_types = get_supported_animation_types()
    print(f"Supported animation types: {', '.join(supported_types)}")
    
    # Get animation options
    options = get_animation_options()
    print(f"Available animation options: {', '.join(options.keys())}")
    
    # List available 3D models
    model_files = list_3d_models()
    if not model_files:
        print("No 3D model files found to test animation.")
        return False
    
    print(f"\nFound {len(model_files)} 3D model files:")
    for i, file in enumerate(model_files):
        print(f"{i+1}. {file.name}")
    
    # Select a 3D model to test
    if len(model_files) == 1:
        model_file = model_files[0]
    else:
        while True:
            try:
                choice = input("\nEnter the number of the 3D model to animate (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return False
                
                index = int(choice) - 1
                if 0 <= index < len(model_files):
                    model_file = model_files[index]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(model_files)}")
            except ValueError:
                print("Please enter a valid number")
    
    # Select animation type
    while True:
        type_choice = input(f"\nEnter animation type ({', '.join(supported_types)}): ")
        if type_choice.lower() in [t.lower() for t in supported_types]:
            # Find the correct case for the animation type
            animation_type = next(t for t in supported_types if t.lower() == type_choice.lower())
            break
        else:
            print(f"Please enter a supported animation type: {', '.join(supported_types)}")
    
    # Test the animation
    success = test_animation(model_file, animation_type)
    
    if success:
        print("\nAnimation test PASSED!")
    else:
        print("\nAnimation test FAILED!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
