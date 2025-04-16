"""
SVG Processor Tool for working with SVG files
"""

import logging
import os
import re
import uuid
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.asset_manager import AssetManager

logger = logging.getLogger(__name__)

class SVGProcessorTool(Tool):
    """
    Tool for processing SVG files and converting them to 3D models
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the SVG Processor Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
        """
        super().__init__(
            name="svg_processor",
            description="Processes SVG files and converts them to 3D models"
        )
        
        self.redis_bus = redis_bus
        self.config = config or {}
        
        # Output directory for processed SVGs
        self.output_dir = self.config.get('output_dir', 'output/svg/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # We'll need to get these services from the service registry
        self.asset_manager = None
        
        logger.info("SVG Processor Tool initialized")
    
    def _ensure_services(self):
        """Ensure required services are available"""
        if self.asset_manager is None:
            # Register for Asset Manager service availability
            self.redis_bus.subscribe('service:asset_manager:available', self._handle_asset_manager_available)
    
    async def _handle_asset_manager_available(self, message: Dict[str, Any]):
        """Handle Asset Manager service availability"""
        service_id = message.get('service_id')
        # Request service instance via RPC
        response = await self.redis_bus.call_rpc('service:get', {'service_id': service_id})
        if 'error' not in response:
            self.asset_manager = response.get('service')
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an SVG file
        
        Args:
            parameters: Processing parameters
                - svg_content: SVG content string
                - svg_file: Path to SVG file (alternative to svg_content)
                - operation: Operation to perform (analyze, convert_to_3d, extract_paths)
                - extrude_depth: Extrusion depth for 3D conversion (default: 0.1)
                - name: Output name
                
        Returns:
            Processing result
        """
        self._ensure_services()
        
        # Get parameters
        svg_content = parameters.get('svg_content')
        svg_file = parameters.get('svg_file')
        operation = parameters.get('operation', 'analyze')
        extrude_depth = parameters.get('extrude_depth', 0.1)
        name = parameters.get('name', f"SVG_{uuid.uuid4().hex[:8]}")
        
        # Either svg_content or svg_file must be provided
        if not svg_content and not svg_file:
            return {
                'status': 'error',
                'error': "Either svg_content or svg_file must be provided"
            }
        
        try:
            # Get SVG content from file if not provided directly
            if not svg_content and svg_file:
                if not os.path.exists(svg_file):
                    return {
                        'status': 'error',
                        'error': f"SVG file not found: {svg_file}"
                    }
                
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
            
            # Process SVG based on operation
            if operation == 'analyze':
                result = self._analyze_svg(svg_content)
            elif operation == 'convert_to_3d':
                result = await self._convert_to_3d(svg_content, name, extrude_depth)
            elif operation == 'extract_paths':
                result = self._extract_paths(svg_content)
            else:
                return {
                    'status': 'error',
                    'error': f"Unsupported operation: {operation}"
                }
            
            # Add operation and name to result
            result['operation'] = operation
            result['name'] = name
            
            return result
        except Exception as e:
            logger.error(f"Error processing SVG: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _analyze_svg(self, svg_content: str) -> Dict[str, Any]:
        """
        Analyze SVG content
        
        Args:
            svg_content: SVG content string
            
        Returns:
            Analysis result
        """
        try:
            # Parse SVG
            root = ET.fromstring(svg_content)
            
            # Get SVG namespace
            ns = self._get_svg_namespace(root)
            
            # Get SVG dimensions
            width, height = self._get_svg_dimensions(root)
            
            # Count elements
            element_counts = {}
            
            # Recursive function to count elements
            def count_elements(element):
                tag = element.tag
                if ns and tag.startswith('{' + ns + '}'):
                    tag = tag[len(ns) + 2:]  # Remove namespace
                
                element_counts[tag] = element_counts.get(tag, 0) + 1
                
                for child in element:
                    count_elements(child)
            
            count_elements(root)
            
            # Extract viewBox
            viewbox = root.get('viewBox')
            
            return {
                'status': 'success',
                'width': width,
                'height': height,
                'viewBox': viewbox,
                'element_counts': element_counts,
                'message': f"Analyzed SVG with {sum(element_counts.values())} elements"
            }
        except Exception as e:
            logger.error(f"Error analyzing SVG: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _convert_to_3d(self, svg_content: str, name: str, extrude_depth: float) -> Dict[str, Any]:
        """
        Convert SVG to 3D model
        
        Args:
            svg_content: SVG content string
            name: Output name
            extrude_depth: Extrusion depth
            
        Returns:
            Conversion result
        """
        try:
            # Generate Blender script for SVG extrusion
            script = self._generate_svg_extrusion_script(svg_content, name, extrude_depth)
            
            # Save SVG file
            svg_path = os.path.join(self.output_dir, f"{name}.svg")
            with open(svg_path, 'w') as f:
                f.write(svg_content)
            
            # Save script file
            script_path = os.path.join(self.output_dir, f"{name}_extrude.py")
            with open(script_path, 'w') as f:
                f.write(script)
            
            # Model output path (would be created by Blender script)
            model_path = os.path.join(self.output_dir, f"{name}.blend")
            
            # Store files as assets if asset manager is available
            asset_ids = {}
            if self.asset_manager:
                # Store SVG file
                svg_asset_id = await self.asset_manager.store_asset(svg_path, {
                    'name': name,
                    'type': 'svg',
                    'extrude_depth': extrude_depth
                })
                asset_ids['svg'] = svg_asset_id
                
                # Store script file
                script_asset_id = await self.asset_manager.store_asset(script_path, {
                    'name': f"{name}_extrude",
                    'type': 'blender_script',
                    'related_svg': svg_asset_id
                }, 'script')
                asset_ids['script'] = script_asset_id
            
            return {
                'status': 'success',
                'svg_path': svg_path,
                'script_path': script_path,
                'model_path': model_path,  # Would be created by executing the script
                'asset_ids': asset_ids,
                'message': f"Generated SVG extrusion script for '{name}' with depth {extrude_depth}",
                'script': script[:500] + "..." if len(script) > 500 else script  # Preview
            }
        except Exception as e:
            logger.error(f"Error converting SVG to 3D: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_paths(self, svg_content: str) -> Dict[str, Any]:
        """
        Extract paths from SVG
        
        Args:
            svg_content: SVG content string
            
        Returns:
            Extracted paths
        """
        try:
            # Parse SVG
            root = ET.fromstring(svg_content)
            
            # Get SVG namespace
            ns = self._get_svg_namespace(root)
            
            # Find all path elements
            path_tag = '{' + ns + '}path' if ns else 'path'
            paths = []
            
            # Recursive function to find paths
            def find_paths(element):
                if element.tag == path_tag:
                    path_data = {
                        'id': element.get('id', f"path_{len(paths)}"),
                        'd': element.get('d', ''),
                        'style': element.get('style', ''),
                        'fill': element.get('fill', ''),
                        'stroke': element.get('stroke', ''),
                        'stroke-width': element.get('stroke-width', '')
                    }
                    paths.append(path_data)
                
                for child in element:
                    find_paths(child)
            
            find_paths(root)
            
            return {
                'status': 'success',
                'paths': paths,
                'path_count': len(paths),
                'message': f"Extracted {len(paths)} paths from SVG"
            }
        except Exception as e:
            logger.error(f"Error extracting paths from SVG: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_svg_extrusion_script(self, svg_content: str, name: str, extrude_depth: float) -> str:
        """
        Generate Blender script for SVG extrusion
        
        Args:
            svg_content: SVG content string
            name: Output name
            extrude_depth: Extrusion depth
            
        Returns:
            Blender Python script
        """
        # Save SVG to temporary file (will be read by Blender)
        svg_path = os.path.join(self.output_dir, f"{name}.svg")
        
        # Generate script
        script = f"""# Blender script to import and extrude SVG: {name}
import bpy
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import SVG
svg_path = "{svg_path.replace('\\', '/')}"
bpy.ops.import_curve.svg(filepath=svg_path)

# Select all curve objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type == 'CURVE':
        obj.select_set(True)
        
        # Set curve properties for extrusion
        obj.data.dimensions = '3D'
        obj.data.bevel_depth = {extrude_depth}
        obj.data.bevel_resolution = 4
        
        # Add material
        if len(obj.data.materials) == 0:
            mat = bpy.data.materials.new(name=f"{{obj.name}}_material")
            mat.diffuse_color = (0.8, 0.8, 0.8, 1.0)
            obj.data.materials.append(mat)

# Join all curve objects into one
if len(bpy.context.selected_objects) > 1:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    
    # Rename the joined object
    bpy.context.active_object.name = "{name}"

# Add a camera for rendering
bpy.ops.object.camera_add(location=(0, 0, 10))
camera = bpy.context.active_object
camera.name = "{name}_camera"
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
light = bpy.context.active_object
light.name = "{name}_light"
light.data.energy = 2.0

# Save the file
output_path = os.path.join("{self.output_dir.replace('\\', '/')}", "{name}.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"Completed SVG extrusion for {name} with depth {extrude_depth}")
"""
        return script
    
    def _get_svg_namespace(self, root) -> Optional[str]:
        """
        Get SVG namespace from root element
        
        Args:
            root: SVG root element
            
        Returns:
            Namespace string or None
        """
        # Extract namespace from root tag
        match = re.match(r'(\{(.*?)\})', root.tag)
        if match:
            return match.group(2)
        return None
    
    def _get_svg_dimensions(self, root) -> Tuple[Optional[float], Optional[float]]:
        """
        Get SVG dimensions from root element
        
        Args:
            root: SVG root element
            
        Returns:
            (width, height) tuple
        """
        width = root.get('width')
        height = root.get('height')
        
        # Convert to float if possible
        try:
            width = float(width) if width else None
        except ValueError:
            # Handle units like '100px'
            match = re.match(r'(\d+(\.\d+)?)([a-z]+)?', width)
            if match:
                width = float(match.group(1))
            else:
                width = None
        
        try:
            height = float(height) if height else None
        except ValueError:
            # Handle units like '100px'
            match = re.match(r'(\d+(\.\d+)?)([a-z]+)?', height)
            if match:
                height = float(match.group(1))
            else:
                height = None
        
        return width, height
