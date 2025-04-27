## 9. Integration with GenAI Agent 3D

SceneX is integrated into the GenAI Agent 3D system as follows:

### 9.1 Service Registration

```python
from genai_agent.services import ServiceRegistry
from scenex import SceneXService

def register_scenex_service():
    """Register SceneX service with the GenAI Agent system."""
    scenex_service = SceneXService()
    ServiceRegistry.register("scenex", scenex_service)
```

### 9.2 Tool Integration

```python
from genai_agent.tools import ToolRegistry
from scenex.tools import (
    SVGToSceneTool, 
    AnimationGeneratorTool,
    SceneExporterTool
)

def register_scenex_tools():
    """Register SceneX-related tools with the tool registry."""
    ToolRegistry.register("svg_to_scene", SVGToSceneTool())
    ToolRegistry.register("generate_animation", AnimationGeneratorTool())
    ToolRegistry.register("export_scene", SceneExporterTool())
```

### 9.3 API Endpoints

```python
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse
from scenex import SceneX

router = APIRouter()

@router.post("/api/scenex/convert-svg")
async def convert_svg_to_scene(
    svg_file: UploadFile = File(...),
    animation_type: str = Form("reveal"),
    output_format: str = Form("mp4")
):
    """Convert an SVG file to a 3D scene with animation."""
    # Create a temporary file for the SVG
    svg_path = f"temp/{svg_file.filename}"
    with open(svg_path, "wb") as f:
        f.write(await svg_file.read())
    
    # Create a new scene
    scene = SceneX.Scene()
    
    # Import SVG
    svg_importer = SceneX.SVGImporter()
    elements = svg_importer.import_svg(svg_path)
    
    # Add elements to scene
    scene.add(*elements)
    
    # Generate animation based on type
    if animation_type == "reveal":
        SceneX.animation.generate_reveal_animation(scene)
    elif animation_type == "flow":
        SceneX.animation.generate_flow_animation(scene)
    elif animation_type == "explode":
        SceneX.animation.generate_explode_animation(scene)
    
    # Render and return
    output_path = f"output/{svg_file.filename}.{output_format}"
    scene.render(output_path, format=output_format)
    
    return FileResponse(output_path)
```
