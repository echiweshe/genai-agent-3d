@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo                   SVG to Video Pipeline Runner                        
echo ================================================================================
echo.

:: Activate virtual environment if it exists
if exist "genai_agent_project\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "genai_agent_project\venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found.
)

:: First, ensure the directory structure is correct
echo Running directory synchronization script...
python sync_svg_directories.py

:: Setup default values
set DIAGRAM_TYPE=flowchart
set ANIMATION_TYPE=simple
set PROVIDER=claude-direct
set VIDEO_QUALITY=medium
set DURATION=10

:: Check if description is provided as argument
if "%~1"=="" (
    echo No diagram description provided.
    echo.
    echo Enter a description for your diagram:
    set /p DESCRIPTION=
) else (
    set DESCRIPTION=%~1
)

:: Ask for options if description is provided
if not "!DESCRIPTION!"=="" (
    :: Ask for diagram type
    echo.
    echo Select diagram type:
    echo 1. Flowchart [default]
    echo 2. Network diagram
    echo 3. Sequence diagram
    echo 4. Class diagram
    echo 5. Entity-relationship diagram
    echo 6. Mind map
    echo 7. General diagram
    echo.
    set /p TYPE_CHOICE="Enter choice [1-7, default=1]: "

    if "!TYPE_CHOICE!"=="2" set DIAGRAM_TYPE=network
    if "!TYPE_CHOICE!"=="3" set DIAGRAM_TYPE=sequence
    if "!TYPE_CHOICE!"=="4" set DIAGRAM_TYPE=class
    if "!TYPE_CHOICE!"=="5" set DIAGRAM_TYPE=er
    if "!TYPE_CHOICE!"=="6" set DIAGRAM_TYPE=mindmap
    if "!TYPE_CHOICE!"=="7" set DIAGRAM_TYPE=general

    :: Ask for animation type
    echo.
    echo Select animation type:
    echo 1. Simple [default]
    echo 2. Rotation
    echo 3. Explode
    echo 4. Flow (good for flowcharts)
    echo 5. Network (good for network diagrams)
    echo.
    set /p ANIM_CHOICE="Enter choice [1-5, default=1]: "

    if "!ANIM_CHOICE!"=="2" set ANIMATION_TYPE=rotate
    if "!ANIM_CHOICE!"=="3" set ANIMATION_TYPE=explode
    if "!ANIM_CHOICE!"=="4" set ANIMATION_TYPE=flow
    if "!ANIM_CHOICE!"=="5" set ANIMATION_TYPE=network

    :: Ask for video quality
    echo.
    echo Select video quality:
    echo 1. Low (faster rendering)
    echo 2. Medium [default]
    echo 3. High (slower rendering)
    echo.
    set /p QUALITY_CHOICE="Enter choice [1-3, default=2]: "

    if "!QUALITY_CHOICE!"=="1" set VIDEO_QUALITY=low
    if "!QUALITY_CHOICE!"=="3" set VIDEO_QUALITY=high

    :: Ask for duration
    echo.
    set /p DURATION="Enter video duration in seconds [default=10]: "
    if "!DURATION!"=="" set DURATION=10

    :: Ask for name
    echo.
    set /p NAME="Enter name for your project [optional]: "
)

:: Run the SVG to Video pipeline
echo.
echo Running SVG to Video pipeline with the following parameters:
echo - Description: !DESCRIPTION!
echo - Diagram Type: !DIAGRAM_TYPE!
echo - Animation Type: !ANIMATION_TYPE!
echo - Video Quality: !VIDEO_QUALITY!
echo - Duration: !DURATION! seconds
if not "!NAME!"=="" echo - Name: !NAME!
echo.

echo Starting pipeline...
echo.

python -c "
import os
import sys
import logging
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%%asctime)s - %%levelname)s - %%message)s')
logger = logging.getLogger()

# Add project root to path
project_root = os.path.abspath('genai_agent_project')
sys.path.insert(0, project_root)

try:
    # Import the pipeline
    from genai_agent.svg_to_video.pipeline_integrated import SVGToVideoPipeline
    
    # Create the pipeline
    pipeline = SVGToVideoPipeline()
    
    # Get pipeline status and print info
    status = pipeline.get_pipeline_status()
    print('Pipeline Status:')
    if status['status'] == 'available':
        print('✅ All components are available')
    else:
        print('⚠️ Some components are not available:')
        for component, available in status['components'].items():
            print(f'  - {component}: {"✅" if available else "❌"}')
    
    print(f'Blender: {"✅ Available at " + status["blender"]["path"] if status["blender"]["available"] else "❌ Not available"}')
    print()
    
    # Get parameters
    description = r'%DESCRIPTION%'
    diagram_type = r'%DIAGRAM_TYPE%'
    animation_type = r'%ANIMATION_TYPE%'
    video_quality = r'%VIDEO_QUALITY%'
    duration = float(r'%DURATION%')
    name = r'%NAME%' if r'%NAME%' else None
    
    if not description:
        print('❌ No description provided. Cannot proceed.')
        sys.exit(1)
    
    print(f'Starting SVG generation for {diagram_type} diagram...')
    start_time = time.time()
    
    # Run steps individually for better progress reporting
    svg_result = pipeline.generate_svg_only(
        description,
        diagram_type=diagram_type,
        name=name,
        provider='claude-direct'
    )
    
    print(f'SVG Generation: {"✅ Success" if svg_result.get("status") == "success" else "❌ Failed"}')
    if svg_result.get('status') != 'success':
        print(f'Error: {svg_result.get("error", "Unknown error")}')
        sys.exit(1)
    
    svg_path = svg_result['file_path']
    print(f'SVG file: {svg_path}')
    
    # Only continue if 3D conversion is available
    if status['components']['svg_to_3d']:
        print('\\nStarting SVG to 3D conversion...')
        model_result = pipeline.convert_svg_to_3d_only(svg_path)
        
        print(f'3D Conversion: {"✅ Success" if model_result.get("status") == "success" else "❌ Failed"}')
        if model_result.get('status') != 'success':
            print(f'Error: {model_result.get("error", "Unknown error")}')
            sys.exit(1)
        
        model_path = model_result['model_path']
        print(f'3D Model: {model_path}')
        
        # Only continue if animation is available
        if status['components']['model_animator']:
            print('\\nStarting 3D model animation...')
            animation_result = pipeline.animate_model_only(
                model_path, 
                animation_type=animation_type,
                duration=duration
            )
            
            print(f'Animation: {"✅ Success" if animation_result.get("status") == "success" else "❌ Failed"}')
            if animation_result.get('status') != 'success':
                print(f'Error: {animation_result.get("error", "Unknown error")}')
                sys.exit(1)
            
            animated_model_path = animation_result['animated_model_path']
            print(f'Animated Model: {animated_model_path}')
            
            # Only continue if rendering is available
            if status['components']['video_renderer']:
                print('\\nStarting video rendering...')
                video_result = pipeline.render_video_only(
                    animated_model_path, 
                    quality=video_quality,
                    duration=duration
                )
                
                print(f'Video Rendering: {"✅ Success" if video_result.get("status") == "success" else "❌ Failed"}')
                if video_result.get('status') != 'success':
                    print(f'Error: {video_result.get("error", "Unknown error")}')
                    sys.exit(1)
                
                video_path = video_result['video_path']
                print(f'Video: {video_path}')
                
                # Calculate total time
                end_time = time.time()
                total_time = end_time - start_time
                print(f'\\nTotal Processing Time: {total_time:.2f} seconds')
                
                print('\\n✅ SVG to Video pipeline completed successfully!')
                print(f'\\nOutput Files:')
                print(f'- SVG: {svg_path}')
                print(f'- 3D Model: {model_path}')
                print(f'- Animated Model: {animated_model_path}')
                print(f'- Video: {video_path}')
            else:
                print('\\n⚠️ Video rendering is not available. Pipeline stopped at animation stage.')
        else:
            print('\\n⚠️ Animation is not available. Pipeline stopped at 3D conversion stage.')
    else:
        print('\\n⚠️ 3D conversion is not available. Pipeline stopped at SVG generation stage.')
    
except Exception as e:
    logger.error(f'Error during pipeline execution: {str(e)}')
    print(f'\\n❌ Pipeline failed with error: {str(e)}')
    import traceback
    traceback.print_exc()
"

echo.
echo ================================================================================
echo Pipeline execution completed. Press any key to exit...
pause >nul
