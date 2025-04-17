"""
Diagram Generator Tool for creating diagrams and visualizations
"""

import logging
import os
import uuid
import json
from typing import Dict, Any, List, Optional, Union

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.llm import LLMService
from genai_agent.services.asset_manager import AssetManager

logger = logging.getLogger(__name__)

class DiagramGeneratorTool(Tool):
    """
    Tool for generating diagrams and visualizations
    
    Supports various diagram types including:
    - Flowcharts
    - Entity-Relationship Diagrams
    - UML Diagrams
    - Scene Layout Diagrams
    - Object Hierarchy Diagrams
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the Diagram Generator Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
        """
        super().__init__(
            name="diagram_generator",
            description="Generates diagrams and visualizations from descriptions"
        )
        
        self.redis_bus = redis_bus
        self.config = config or {}
        
        # Output directory for generated diagrams
        self.output_dir = self.config.get('output_dir', 'output/diagrams/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Reference to services
        self.llm_service = None
        self.asset_manager = None
        
        logger.info("Diagram Generator Tool initialized")
    
    async def _ensure_services(self):
        """Ensure required services are available"""
        if self.llm_service is None:
            # Register for LLM service availability
            await self.redis_bus.subscribe('service:llm_service:available', self._handle_llm_service_available)
        
        if self.asset_manager is None:
            # Register for Asset Manager service availability
            await self.redis_bus.subscribe('service:asset_manager:available', self._handle_asset_manager_available)
    
    async def _handle_llm_service_available(self, message: Dict[str, Any]):
        """Handle LLM service availability"""
        service_id = message.get('service_id')
        # Request service instance via RPC
        response = await self.redis_bus.call_rpc('service:get', {'service_id': service_id})
        if 'error' not in response:
            self.llm_service = response.get('service')
    
    async def _handle_asset_manager_available(self, message: Dict[str, Any]):
        """Handle Asset Manager service availability"""
        service_id = message.get('service_id')
        # Request service instance via RPC
        response = await self.redis_bus.call_rpc('service:get', {'service_id': service_id})
        if 'error' not in response:
            self.asset_manager = response.get('service')
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a diagram based on the provided parameters
        
        Args:
            parameters: Diagram parameters
                - description: Text description of the diagram
                - diagram_type: Type of diagram (flowchart, erd, uml, scene_layout, hierarchy)
                - format: Output format (mermaid, svg, dot)
                - name: Optional name for the diagram
                
        Returns:
            Diagram generation result
        """
        try:
            # Connect required services
            await self._ensure_services()
            
            # Get parameters
            description = parameters.get('description', '')
            diagram_type = parameters.get('diagram_type', 'flowchart')
            output_format = parameters.get('format', 'mermaid')
            name = parameters.get('name', f"Diagram_{uuid.uuid4().hex[:8]}")
            
            # Validate required parameters
            if not description:
                return {
                    'status': 'error',
                    'error': 'No description provided'
                }
            
            # Generate diagram code based on type and format
            diagram_code = await self._generate_diagram_code(description, diagram_type, output_format)
            
            # Create file paths for output
            diagram_file_path = os.path.join(self.output_dir, f"{name}.{self._get_file_extension(output_format)}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(diagram_file_path), exist_ok=True)
            
            # Save the diagram code to file
            with open(diagram_file_path, 'w') as f:
                f.write(diagram_code)
                
            # Store as asset if asset manager is available
            asset_id = None
            if self.asset_manager:
                asset_id = await self.asset_manager.store_asset(diagram_file_path, {
                    'name': name,
                    'description': description,
                    'diagram_type': diagram_type,
                    'format': output_format,
                    'type': 'diagram'
                })
                
            # Generate a preview version for visualization if needed
            preview_path = None
            if output_format == 'mermaid':
                # For mermaid diagrams, we could generate a preview image, but we'll skip for now
                # This would be a good place to integrate with a renderer
                pass
            
            return {
                'status': 'success',
                'name': name,
                'description': description,
                'diagram_type': diagram_type,
                'format': output_format,
                'file_path': diagram_file_path,
                'asset_id': asset_id,
                'preview_path': preview_path,
                'code': diagram_code if len(diagram_code) < 1000 else diagram_code[:1000] + "...",
                'message': f"Generated {diagram_type} diagram in {output_format} format"
            }
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _generate_diagram_code(self, description: str, diagram_type: str, output_format: str) -> str:
        """
        Generate diagram code based on the description, type, and format
        
        Args:
            description: Text description of the diagram
            diagram_type: Type of diagram
            output_format: Output format
            
        Returns:
            Diagram code in the specified format
        """
        try:
            # Create prompt for LLM
            prompt = self._create_diagram_generation_prompt(description, diagram_type, output_format)
            
            # Get diagram code from LLM
            if self.llm_service:
                response = await self.llm_service.generate(prompt, parameters={'temperature': 0.2})
            else:
                # Fallback for development/testing
                logger.warning("LLM service not available, using fallback diagram")
                response = self._get_fallback_diagram(diagram_type, output_format)
            
            # Extract code from response
            import re
            
            if output_format == 'mermaid':
                pattern = r'```mermaid\s*(.*?)\s*```'
            elif output_format == 'svg':
                pattern = r'```svg\s*(.*?)\s*```'
            elif output_format == 'dot':
                pattern = r'```dot\s*(.*?)\s*```'
            else:
                pattern = r'```(?:.*?)\s*(.*?)\s*```'
                
            code_match = re.search(pattern, response, re.DOTALL)
            
            if code_match:
                diagram_code = code_match.group(1)
            else:
                # If no code block found, try to find anything that looks like diagram code
                lines = response.split('\n')
                diagram_lines = []
                in_diagram = False
                
                for line in lines:
                    if output_format == 'mermaid' and (line.strip().startswith('graph ') or 
                                                      line.strip().startswith('flowchart ') or
                                                      line.strip().startswith('sequenceDiagram') or
                                                      line.strip().startswith('classDiagram') or
                                                      line.strip().startswith('erDiagram')):
                        in_diagram = True
                        
                    if in_diagram:
                        diagram_lines.append(line)
                
                if diagram_lines:
                    diagram_code = '\n'.join(diagram_lines)
                else:
                    # If all extraction methods fail, use the whole response
                    logger.warning("Could not extract diagram code with regex, using full response")
                    diagram_code = response
            
            return diagram_code
        except Exception as e:
            logger.error(f"Error generating diagram code: {str(e)}")
            return self._get_fallback_diagram(diagram_type, output_format)
    
    def _create_diagram_generation_prompt(self, description: str, diagram_type: str, output_format: str) -> str:
        """
        Create a prompt for generating a diagram
        
        Args:
            description: Text description of the diagram
            diagram_type: Type of diagram
            output_format: Output format
            
        Returns:
            LLM prompt
        """
        # Base prompt template
        prompt = f"""Generate a {diagram_type} diagram based on the following description:

Description: {description}

Please create the diagram in {output_format} format.
"""
        
        # Add specific instructions based on diagram type
        if diagram_type == 'flowchart':
            prompt += """
For a flowchart, include:
- Clear start and end points
- Logical process flow
- Decision points with Yes/No or True/False branches
- Appropriate symbols for different operation types
"""
        elif diagram_type == 'erd':
            prompt += """
For an Entity-Relationship Diagram, include:
- Entities with attributes
- Relationships between entities
- Cardinality (one-to-one, one-to-many, many-to-many)
- Primary and foreign keys
"""
        elif diagram_type == 'uml':
            prompt += """
For a UML diagram, include:
- Classes with attributes and methods
- Relationships (inheritance, composition, aggregation, association)
- Access modifiers (public, private, protected)
- Interface definitions if applicable
"""
        elif diagram_type == 'scene_layout':
            prompt += """
For a scene layout diagram, include:
- Main objects in the scene
- Spatial relationships
- Camera positions if applicable
- Light sources if applicable
- Scale indicators
"""
        elif diagram_type == 'hierarchy':
            prompt += """
For an object hierarchy diagram, include:
- Parent-child relationships
- Clear hierarchy levels
- Node types or categories
- Connections between related nodes
"""
        
        # Add format-specific instructions
        if output_format == 'mermaid':
            prompt += """
Use Mermaid.js syntax for the diagram. For example:

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

Ensure the syntax is correct and the diagram will render properly in Mermaid.
"""
        elif output_format == 'svg':
            prompt += """
Create an SVG diagram with standard SVG syntax. Include proper SVG headers and viewBox attributes.

```svg
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
    <!-- SVG elements go here -->
</svg>
```

Keep it simple and avoid complex filters or effects.
"""
        elif output_format == 'dot':
            prompt += """
Use GraphViz DOT language syntax:

```dot
digraph G {
    A -> B [label="Label"];
    B -> C;
    C -> D;
    D -> A;
}
```

Ensure the DOT syntax is correct for use with GraphViz.
"""
        
        prompt += """
Only return the diagram code without additional explanations or notes.
"""
        
        return prompt
    
    def _get_fallback_diagram(self, diagram_type: str, output_format: str) -> str:
        """
        Get a fallback diagram when LLM generation fails
        
        Args:
            diagram_type: Type of diagram
            output_format: Output format
            
        Returns:
            Fallback diagram code
        """
        if output_format == 'mermaid':
            if diagram_type == 'flowchart':
                return """graph TD
    A[Start] --> B{Is it a 3D scene?}
    B -->|Yes| C[Create Scene]
    B -->|No| D[Create Simple Object]
    C --> E[Add Camera]
    C --> F[Add Lighting]
    D --> G[Apply Materials]
    E --> H[Render Scene]
    F --> H
    G --> H
    H --> I[End]
"""
            elif diagram_type == 'erd':
                return """erDiagram
    SCENE ||--o{ OBJECT : contains
    SCENE ||--|{ CAMERA : has
    SCENE ||--|{ LIGHT : has
    OBJECT ||--o{ MATERIAL : uses
    MATERIAL ||--o{ TEXTURE : has
"""
            elif diagram_type == 'uml':
                return """classDiagram
    class Scene {
        +String name
        +addObject(Object obj)
        +removeObject(Object obj)
        +render()
    }
    class Object {
        +String name
        +Vector3 position
        +Vector3 rotation
        +Vector3 scale
        +setPosition(Vector3 pos)
        +setRotation(Vector3 rot)
        +applyMaterial(Material mat)
    }
    class Camera {
        +Vector3 position
        +Vector3 target
        +float fov
        +setPosition(Vector3 pos)
        +lookAt(Vector3 target)
    }
    Scene "1" *-- "many" Object
    Scene "1" *-- "1..n" Camera
"""
            elif diagram_type == 'scene_layout':
                return """graph TD
    subgraph Scene
        A[Camera] -->|views| B[Center Object]
        C[Light 1] -->|illuminates| B
        D[Light 2] -->|illuminates| B
        B -->|contains| E[Component 1]
        B -->|contains| F[Component 2]
        B -->|contains| G[Component 3]
        H[Floor Plane] -->|supports| B
    end
"""
            elif diagram_type == 'hierarchy':
                return """graph TD
    A[Scene Root] --> B[Group 1]
    A --> C[Group 2]
    B --> D[Object 1]
    B --> E[Object 2]
    C --> F[Object 3]
    C --> G[Object 4]
    D --> H[Mesh Component]
    D --> I[Material Component]
"""
            else:
                return """graph TD
    A[Start] --> B[Process]
    B --> C[End]
"""
        elif output_format == 'svg':
            return """<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="80" height="80" fill="#f5f5f5" stroke="#000000" stroke-width="2"/>
  <circle cx="150" cy="50" r="40" fill="#f5f5f5" stroke="#000000" stroke-width="2"/>
  <line x1="90" y1="50" x2="110" y2="50" stroke="#000000" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="50" y="50" text-anchor="middle" dominant-baseline="middle" font-family="Arial">Object 1</text>
  <text x="150" y="50" text-anchor="middle" dominant-baseline="middle" font-family="Arial">Object 2</text>
</svg>"""
        elif output_format == 'dot':
            return """digraph G {
    node [shape=box, style=filled, fillcolor=lightblue];
    A [label="Scene"];
    B [label="Camera"];
    C [label="Light"];
    D [label="Object 1"];
    E [label="Object 2"];
    
    A -> B [label="contains"];
    A -> C [label="contains"];
    A -> D [label="contains"];
    A -> E [label="contains"];
}"""
        else:
            return "# Fallback diagram\n# Format not supported"
    
    def _get_file_extension(self, output_format: str) -> str:
        """
        Get file extension based on the output format
        
        Args:
            output_format: Output format
            
        Returns:
            File extension
        """
        format_extensions = {
            'mermaid': 'mmd',
            'svg': 'svg',
            'dot': 'dot'
        }
        
        return format_extensions.get(output_format, 'txt')
