# Technology Stack Strategy for GenAI Agent 3D

This document outlines both the long-term enterprise-scale architecture goal and the immediate scaled-down implementation plan focused on the SVG-to-Video pipeline.

## Enterprise-Scale Architecture (Future Goal)

This section describes the technology stack recommended for scaling the GenAI Agent 3D to enterprise-level production use.

### Core Components

1. **Message Broker: RabbitMQ**
   - Reliable message delivery with advanced routing capabilities
   - Support for complex exchange types (direct, topic, fanout)
   - Message persistence and acknowledgment
   - Priority queues for different workloads
   - Dead letter queues for error handling

2. **LLM Framework: LangChain + LlamaIndex**
   - **LangChain**:
     - Unified interface for multiple LLM providers (Claude, OpenAI, Ollama, Hunyuan3D)
     - Built-in prompt engineering capabilities
     - Tool integration for agent frameworks
     - Memory management for conversational context
   - **LlamaIndex**:
     - Advanced data ingestion and retrieval
     - Better document processing capabilities
     - Enhanced RAG (Retrieval Augmented Generation) 
     - Query optimization for LLMs

3. **Container Orchestration: Kubernetes**
   - Scalable deployment of microservices
   - Resource allocation for specialized workloads (GPU for rendering)
   - Self-healing capabilities for increased resilience
   - Horizontal scaling for handling varying workloads
   - Rolling updates for zero-downtime deployments

4. **Workflow Management: Temporal.io**
   - Durable execution of the SVG → 3D → Animation → Video pipeline
   - Resilient handling of long-running processes
   - Built-in retry mechanisms and error handling
   - State persistence across service restarts
   - Visual workflow visualization and debugging

5. **Distributed Processing: Ray**
   - Specialized framework for AI and compute-intensive workloads
   - Distributed rendering for video generation
   - Dynamic resource allocation based on workload
   - Seamless Python integration
   - Support for both batch and streaming processing

6. **Monitoring and Observability: OpenTelemetry + Prometheus/Grafana**
   - End-to-end tracing across the entire pipeline
   - Comprehensive metrics collection
   - Centralized logging
   - Custom dashboards for performance monitoring
   - Alerts for system anomalies

### Architecture Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  User Interface │────>│  API Gateway     │────>│  LangChain +      │
│                 │     │  (Kubernetes)    │     │  LlamaIndex       │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  OpenTelemetry  │<────│  RabbitMQ        │<────│  Temporal.io      │
│  + Prometheus   │     │  Message Broker   │     │  Workflow Engine  │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                                           │
                                                           ▼
                         ┌──────────────────┐     ┌───────────────────┐
                         │  Ray             │────>│  SVG -> 3D -> Video │
                         │  Compute Cluster │     │  Pipeline Services │
                         └──────────────────┘     └───────────────────┘
```

### Implementation Phases (Full Plan)

1. **Phase 1: Foundation** (Weeks 1-4)
   - LangChain integration 
   - Redis to RabbitMQ migration
   - Basic container deployment

2. **Phase 2: Pipeline Enhancement** (Weeks 5-8)
   - LlamaIndex integration
   - Full Kubernetes deployment
   - Pipeline monitoring with OpenTelemetry

3. **Phase 3: Workflow Orchestration** (Weeks 9-12)
   - Temporal.io implementation
   - Advanced workflow capabilities
   - Error handling and retry mechanisms

4. **Phase 4: Scale and Performance** (Weeks 13-16)
   - Ray integration for distributed processing
   - Performance optimization
   - Full monitoring and alerting setup

5. **Phase 5: Production Readiness** (Weeks 17-20)
   - Security hardening
   - Documentation and training
   - Production deployment and validation

## Immediate Implementation: SVG-to-Video Focus

This section describes the scaled-down implementation plan focused on getting the SVG-to-Video pipeline working quickly.

### Core Components (Simplified)

1. **LLM Integration: Minimal LangChain**
   - Basic model connectors for Claude, OpenAI, Ollama
   - Simple prompt templates for SVG generation
   - Minimal memory management for conversation context
   - Focus only on essential interfaces needed for SVG generation

2. **Message Passing: Keep Redis Initially**
   - Continue using existing Redis infrastructure
   - Defer RabbitMQ migration until after pipeline is functional
   - Use simple pub/sub patterns for inter-service communication

3. **Pipeline Orchestration: Simple Python Coordinator**
   - Straightforward async workflow manager
   - Basic error handling and retries
   - File-based state management
   - No complex workflow engine dependencies

4. **SVG to 3D Conversion: Direct Blender Integration**
   - Run Blender as a subprocess with Python scripts
   - Simple SVG parsing and element extraction
   - Direct mapping to 3D primitives
   - Focus on reliability over performance

5. **Animation: Core SceneX Features**
   - Implement essential animation primitives
   - Standard camera movements and transitions
   - Basic material and lighting setup
   - Simplified animation sequencing

6. **Rendering: Local Processing First**
   - Use Blender's built-in rendering engine (EEVEE for speed)
   - Local rendering process before distributed approach
   - Standard output formats (MP4 with H.264)
   - Basic quality settings

### Implementation Approach

```python
# Simplified pipeline architecture

class SVGToVideoPipeline:
    """Simple pipeline coordinator for SVG to Video conversion."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.temp_dir = self.config.get("temp_dir", "/tmp/svg_pipeline")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def process(self, svg_content, output_path, options=None):
        """Process an SVG through the entire pipeline to create a video."""
        options = options or {}
        
        # Create unique job ID and working directory
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(self.temp_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        try:
            # 1. Save SVG to disk
            svg_path = os.path.join(job_dir, "diagram.svg")
            with open(svg_path, "w") as f:
                f.write(svg_content)
            
            # 2. Convert SVG to 3D model
            model_path = await self._convert_svg_to_3d(
                svg_path, 
                os.path.join(job_dir, "model.blend"),
                options.get("model_options", {})
            )
            
            # 3. Apply animations
            scene_path = await self._apply_animations(
                model_path,
                os.path.join(job_dir, "animated.blend"),
                options.get("animation_options", {})
            )
            
            # 4. Render to video
            video_path = await self._render_video(
                scene_path,
                output_path,
                options.get("render_options", {})
            )
            
            return video_path
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            raise
        finally:
            # Cleanup temporary files if needed
            if self.config.get("cleanup_temp", True):
                shutil.rmtree(job_dir)
    
    async def _convert_svg_to_3d(self, svg_path, output_path, options):
        """Convert SVG to 3D model using Blender."""
        # Run Blender as subprocess
        cmd = [
            "blender", "--background", "--python",
            "scripts/svg_to_3d.py", "--",
            svg_path, output_path
        ]
        
        # Add any additional options as command-line parameters
        for key, value in options.items():
            cmd.extend([f"--{key}", str(value)])
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Blender conversion failed: {stderr.decode()}")
        
        return output_path
    
    async def _apply_animations(self, model_path, output_path, options):
        """Apply SceneX animations to the 3D model."""
        # Similar implementation to _convert_svg_to_3d
        # ...
        return output_path
    
    async def _render_video(self, scene_path, output_path, options):
        """Render the animated scene to video."""
        # Similar implementation to _convert_svg_to_3d
        # ...
        return output_path
```

### Development Milestones

1. **Milestone 1: Basic SVG Generation with LangChain**
   - Implement LangChain model connectors
   - Create SVG generation prompts
   - Test with different providers (Claude, OpenAI, Ollama)

2. **Milestone 2: SVG to 3D Conversion**
   - Develop Blender script for SVG import
   - Implement basic element parsing
   - Create 3D primitives for SVG elements
   - Test with simple diagrams

3. **Milestone 3: Animation System**
   - Implement core SceneX animation framework
   - Create standard animation sequences
   - Develop camera control system
   - Add basic material support

4. **Milestone 4: Video Rendering**
   - Configure Blender rendering settings
   - Implement rendering script
   - Add basic post-processing
   - Output to standard video formats

5. **Milestone 5: End-to-End Integration**
   - Connect all components
   - Create end-to-end pipeline coordinator
   - Add basic error handling
   - Test with various diagram types

### Advantages of This Approach

1. **Faster Time to Value**: Focus on getting a working pipeline before optimizing infrastructure
2. **Reduced Complexity**: Minimize dependencies and infrastructure changes
3. **Easier Debugging**: Simpler system with fewer moving parts
4. **Lower Resource Requirements**: Can run on standard hardware without complex orchestration
5. **Incremental Enhancement**: Can gradually add enterprise features as the pipeline matures

## Transition Strategy

Once the simplified SVG-to-Video pipeline is working reliably, the transition to the full enterprise architecture can be implemented in stages:

1. **Start with RabbitMQ Migration**: Replace Redis with RabbitMQ for more robust messaging
2. **Add Kubernetes Deployment**: Containerize services and deploy to Kubernetes
3. **Implement Temporal.io**: Replace the simple coordinator with proper workflow management
4. **Add Ray for Distributed Processing**: Scale up the rendering capabilities
5. **Deploy Full Monitoring**: Implement comprehensive observability

This phased approach balances the need for a working pipeline quickly with the long-term goal of a robust, enterprise-scale system.
