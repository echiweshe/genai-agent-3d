            
            # 1. Generate SVG
            provider = options.get("provider", "claude")
            svg_content = await self.svg_generator.generate_svg(concept, provider=provider)
            
            svg_path = os.path.join(job_dir, "diagram.svg")
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            logger.info(f"Generated SVG saved to {svg_path}")
            
            # 2. Convert SVG to 3D model
            model_path = os.path.join(job_dir, "model.blend")
            await self._run_blender_script(
                "svg_to_3d_blender.py",
                [svg_path, model_path],
                "Converting SVG to 3D model"
            )
            
            logger.info(f"Converted 3D model saved to {model_path}")
            
            # 3. Apply animations
            animated_path = os.path.join(job_dir, "animated.blend")
            await self._run_blender_script(
                "scenex_animation.py",
                [model_path, animated_path],
                "Applying animations"
            )
            
            logger.info(f"Animated scene saved to {animated_path}")
            
            # 4. Render video
            render_quality = options.get("render_quality", "medium")
            await self._run_blender_script(
                "video_renderer.py",
                [animated_path, output_path, render_quality],
                "Rendering video"
            )
            
            logger.info(f"Video rendered to {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "job_id": job_id
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
    
    async def _run_blender_script(self, script_name, args, description):
        """Run a Blender script as a subprocess."""
        script_dir = self.config.get("script_dir", "scripts")
        script_path = os.path.join(script_dir, script_name)
        
        blender_path = self.config.get("blender_path", "blender")
        
        cmd = [
            blender_path,
            "--background",
            "--python", script_path,
            "--"
        ] + args
        
        logger.info(f"{description}: {' '.join(cmd)}")
        
        # Run the process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Capture output
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"Blender process failed: {error_msg}")
            raise RuntimeError(f"Blender process failed: {error_msg[:500]}...")
        
        return True
    
    async def generate_svg_only(self, concept, output_path=None, provider="claude"):
        """Generate an SVG diagram only (without further processing)."""
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
    
    async def convert_existing_svg(self, svg_path, output_path, options=None):
        """Process an existing SVG through the pipeline to create a video."""
        options = options or {}
        
        # Create unique job ID and working directory
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(self.temp_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        try:
            logger.info(f"Starting pipeline for existing SVG: {svg_path}")
            
            # 1. Convert SVG to 3D model
            model_path = os.path.join(job_dir, "model.blend")
            await self._run_blender_script(
                "svg_to_3d_blender.py",
                [svg_path, model_path],
                "Converting SVG to 3D model"
            )
            
            # 2. Apply animations
            animated_path = os.path.join(job_dir, "animated.blend")
            await self._run_blender_script(
                "scenex_animation.py",
                [model_path, animated_path],
                "Applying animations"
            )
            
            # 3. Render video
            render_quality = options.get("render_quality", "medium")
            await self._run_blender_script(
                "video_renderer.py",
                [animated_path, output_path, render_quality],
                "Rendering video"
            )
            
            return {
                "status": "success",
                "output_path": output_path,
                "job_id": job_id
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
```

### Configuration Management

To make the pipeline flexible and configurable, it's helpful to create a configuration management system:

```python
# pipeline_config.py
import os
import json
import logging

logger = logging.getLogger(__name__)

class PipelineConfig:
    """Configuration manager for the SVG to Video pipeline."""
    
    DEFAULT_CONFIG = {
        # Paths
        "temp_dir": os.path.join(os.path.expanduser("~"), "temp", "svg_pipeline"),
        "script_dir": "scripts",
        "output_dir": "outputs",
        
        # Blender settings
        "blender_path": "blender",
        
        # SVG generation settings
        "default_provider": "claude",
        
        # Rendering settings
        "default_render_quality": "medium",
        
        # Cleanup settings
        "cleanup_temp": True,
        
        # Logging
        "log_level": "INFO"
    }
    
    def __init__(self, config_path=None):
        """Initialize with optional config file path."""
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path):
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
                logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    
    def save_config(self, config_path):
        """Save current configuration to a JSON file."""
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
    
    def update(self, updates):
        """Update multiple configuration values."""
        self.config.update(updates)
```

### Pipeline CLI

A command-line interface makes it easy to use the pipeline:

```python
# pipeline_cli.py
import os
import asyncio
import argparse
import logging
from pipeline_config import PipelineConfig
from svg_to_video_pipeline import SVGToVideoPipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description='SVG to Video Pipeline')
    
    # Config options
    parser.add_argument('--config', help='Path to configuration file')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Full pipeline command
    pipeline_parser = subparsers.add_parser('generate', help='Generate video from concept')
    pipeline_parser.add_argument('concept', help='Concept description for diagram generation')
    pipeline_parser.add_argument('output', help='Output video file path')
    pipeline_parser.add_argument('--provider', help='LLM provider for SVG generation')
    pipeline_parser.add_argument('--quality', help='Rendering quality (low, medium, high)')
    
    # SVG-only command
    svg_parser = subparsers.add_parser('svg', help='Generate SVG only')
    svg_parser.add_argument('concept', help='Concept description for diagram generation')
    svg_parser.add_argument('output', help='Output SVG file path')
    svg_parser.add_argument('--provider', help='LLM provider for SVG generation')
    
    # Convert existing SVG command
    convert_parser = subparsers.add_parser('convert', help='Convert existing SVG to video')
    convert_parser.add_argument('svg_path', help='Input SVG file path')
    convert_parser.add_argument('output', help='Output video file path')
    convert_parser.add_argument('--quality', help='Rendering quality (low, medium, high)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = PipelineConfig(args.config)
    
    # Configure logging level
    logging.getLogger().setLevel(config.get("log_level", "INFO"))
    
    # Create pipeline
    pipeline = SVGToVideoPipeline(config.config)
    
    # Process commands
    if args.command == 'generate':
        options = {}
        if args.provider:
            options["provider"] = args.provider
        if args.quality:
            options["render_quality"] = args.quality
        
        result = await pipeline.process(args.concept, args.output, options)
        
        if result["status"] == "success":
            logger.info(f"Video generated successfully: {result['output_path']}")
        else:
            logger.error(f"Error generating video: {result.get('error', 'Unknown error')}")
    
    elif args.command == 'svg':
        provider = args.provider or config.get("default_provider")
        result = await pipeline.generate_svg_only(args.concept, args.output, provider)
        
        if result["status"] == "success":
            logger.info(f"SVG generated successfully: {result.get('output_path', 'No output path specified')}")
        else:
            logger.error(f"Error generating SVG: {result.get('error', 'Unknown error')}")
    
    elif args.command == 'convert':
        options = {}
        if args.quality:
            options["render_quality"] = args.quality
        
        result = await pipeline.convert_existing_svg(args.svg_path, args.output, options)
        
        if result["status"] == "success":
            logger.info(f"Video generated successfully: {result['output_path']}")
        else:
            logger.error(f"Error generating video: {result.get('error', 'Unknown error')}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage Examples

### Full Pipeline

Generate a video from a concept description:

```bash
python pipeline_cli.py generate "A microservices architecture with API Gateway, three services, and a database" output.mp4 --provider claude --quality medium
```

### SVG Generation Only

Generate just the SVG diagram:

```bash
python pipeline_cli.py svg "A flowchart showing user registration process" flowchart.svg --provider openai
```

### Convert Existing SVG

Convert an existing SVG to a video:

```bash
python pipeline_cli.py convert input.svg output.mp4 --quality high
```

## Python API Usage

The pipeline can also be used as a Python API:

```python
import asyncio
from pipeline_config import PipelineConfig
from svg_to_video_pipeline import SVGToVideoPipeline

async def generate_video():
    # Load configuration
    config = PipelineConfig("config.json")
    
    # Create pipeline
    pipeline = SVGToVideoPipeline(config.config)
    
    # Generate a video
    result = await pipeline.process(
        concept="A network diagram showing cloud infrastructure with VPC, subnets, and EC2 instances",
        output_path="network_diagram.mp4",
        options={
            "provider": "claude",
            "render_quality": "high"
        }
    )
    
    print(f"Result: {result}")

# Run the example
asyncio.run(generate_video())
```

## Implementation Notes

### Pipeline Flow

The pipeline follows these steps:

1. **Generate SVG**: Use LangChain to create an SVG diagram from a concept description
2. **SVG to 3D**: Convert the SVG to a 3D Blender scene
3. **Animation**: Apply animations to the 3D scene
4. **Rendering**: Render the animated scene to video

Each step is executed in sequence, with error handling at each stage.

### Temporary Files

The pipeline creates temporary working directories for each job:

1. Each job gets a unique UUID
2. Files are stored in a temporary directory with the job ID
3. Files are cleaned up after the pipeline completes (configurable)

### Error Handling

The pipeline includes comprehensive error handling:

1. Each stage is wrapped in a try/except block
2. Errors are logged and bubbled up to the caller
3. The pipeline returns a structured result with success/error status
4. Temporary files are cleaned up even if errors occur

### Configuration System

The configuration system allows for flexible customization:

1. Default configuration is provided for quick setup
2. Configuration can be loaded from JSON files
3. Command-line arguments can override configuration
4. Configuration can be programmatically updated

## Dependencies

- Python 3.9+
- Blender 3.0+
- LangChain
- Provider-specific packages (OpenAI, Anthropic, etc.)
- Standard Python libraries (asyncio, json, etc.)

## Testing

### Integration Testing

```python
# test_pipeline_integration.py
import os
import asyncio
import unittest
from pipeline_config import PipelineConfig
from svg_to_video_pipeline import SVGToVideoPipeline

class TestPipelineIntegration(unittest.TestCase):
    async def async_test_full_pipeline(self):
        # Create test configuration
        config = {
            "temp_dir": "test_temp",
            "script_dir": "../scripts",  # Adjust to your script directory
            "cleanup_temp": False  # Keep files for inspection during testing
        }
        
        # Create pipeline
        pipeline = SVGToVideoPipeline(config)
        
        # Test concept
        concept = "A simple flowchart with two boxes connected by an arrow"
        output_path = "test_output.mp4"
        
        # Run pipeline
        result = await pipeline.process(concept, output_path, {"render_quality": "low"})
        
        # Check result
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output_path))
        
        # Clean up
        os.remove(output_path)
        
    def test_full_pipeline(self):
        asyncio.run(self.async_test_full_pipeline())

if __name__ == "__main__":
    unittest.main()
```

## Known Limitations

1. Sequential processing (no parallel execution)
2. Basic error handling and recovery
3. Limited to Blender's capabilities
4. No progress monitoring during long operations

## Next Steps

1. Implement progress reporting for long-running operations
2. Add support for parallel processing of multiple jobs
3. Enhance error recovery mechanisms
4. Create a web interface for the pipeline
5. Implement job queuing and management
6. Add support for custom animation templates
7. Integrate with the infrastructure services