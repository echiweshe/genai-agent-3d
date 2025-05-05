# SVG to Video Pipeline

The SVG to Video pipeline is a comprehensive system for converting text descriptions to animated 3D videos through a multi-stage process:

1. **SVG Generation**: Convert natural language descriptions to SVG diagrams using LLMs (Claude, OpenAI, etc.)
2. **3D Conversion**: Transform SVG elements into 3D models
3. **Animation**: Add animations and camera movements to the 3D scene
4. **Rendering**: Generate the final video output

## Features

- **Multiple LLM Integrations**:
  - Direct Claude API integration
  - LangChain-based integrations (Claude, OpenAI, Ollama)
  - Redis-based LLM service integration with the main project
  
- **Specialized Diagram Types**:
  - Flowcharts
  - Network diagrams
  - Sequence diagrams
  - General diagrams
  
- **Animation System**:
  - Animation type detection based on diagram structure
  - Animation patterns for different diagram types
  - Customizable duration and timing
  
- **Rendering Options**:
  - Multiple quality settings
  - Configurable resolution and frame rate
  - Output format selection

## Architecture

The pipeline consists of the following main components:

- **SVG Generator**: Creates SVG diagrams based on text descriptions using LLMs
- **SVG to 3D Converter**: Transforms SVG elements into 3D models
- **Animation System**: Applies animations to the 3D models
- **Video Renderer**: Renders the animated 3D scene to video

## Usage

### Basic Usage

```python
from genai_agent.svg_to_video import SVGToVideoPipeline

async def generate_video():
    # Create pipeline instance
    pipeline = SVGToVideoPipeline(debug=True)
    
    # Initialize the pipeline
    await pipeline.initialize()
    
    # Generate video from description
    result = await pipeline.generate_video_from_description(
        description="A flowchart showing user authentication process",
        provider="claude-direct",      # LLM provider to use
        diagram_type="flowchart",      # Type of diagram to generate
        render_quality="medium",       # Rendering quality
        duration=10                    # Animation duration in seconds
    )
    
    # Print output file paths
    print("Generated files:")
    for file_type, file_path in result.items():
        print(f"  {file_type}: {file_path}")
```

### Generating SVG Only

```python
# Generate only an SVG diagram
svg_content, svg_path = await pipeline.generate_svg_only(
    description="A network diagram showing a client-server architecture",
    provider="claude-direct",
    diagram_type="network"
)
```

### Converting Existing SVG to Video

```python
# Convert an existing SVG file to video
result = await pipeline.convert_svg_to_video(
    svg_path="path/to/diagram.svg",
    animation_type="flowchart",
    render_quality="high",
    duration=15
)
```

## LLM Integration

The SVG Generator component supports multiple methods for LLM integration:

### Direct Claude Integration

```python
# Using Claude Direct API
svg_content, svg_path = await pipeline.generate_svg_only(
    description="A flowchart diagram",
    provider="claude-direct",
    diagram_type="flowchart"
)
```

### LangChain Integration

```python
# Using LangChain with OpenAI
svg_content, svg_path = await pipeline.generate_svg_only(
    description="A network diagram",
    provider="langchain-openai",
    diagram_type="network"
)
```

### Redis-based LLM Service

```python
# Using the project's Redis-based LLM service
svg_content, svg_path = await pipeline.generate_svg_only(
    description="A sequence diagram",
    provider="service-claude",
    diagram_type="sequence"
)
```

## Testing

Use the provided test scripts to test the pipeline:

```bash
# Test SVG generation with Claude
python scripts/test_svg_generator.py --provider claude-direct --diagram-type flowchart --description "A flowchart showing user authentication" --output-dir output/svg

# Test the full pipeline
python scripts/test/test_svg_to_video_full.py --provider claude-direct --diagram-type network --description "A network diagram showing client-server architecture" --svg-only
```

## Dependencies

- Python 3.8+
- LangChain (for LangChain integrations)
- Anthropic Python SDK (for direct Claude integration)
- Redis (for Redis-based LLM service)
- Blender (for 3D conversion and rendering)

## Configuration

The pipeline uses the following environment variables:

- `ANTHROPIC_API_KEY`: API key for Claude direct integration
- `OPENAI_API_KEY`: API key for OpenAI integration
- `SVG_OUTPUT_DIR`: Directory for SVG output files
- `OUTPUT_DIR`: Base directory for all output files
