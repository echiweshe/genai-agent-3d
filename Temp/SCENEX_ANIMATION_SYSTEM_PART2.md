## 8. SVG Import and Processing

The SVG import system is a crucial component that enables conversion from SVG diagrams to 3D visualizations:

```python
class SVGImporter:
    """Imports SVG files into SceneX."""
    
    def __init__(self):
        self.element_types = {
            "rect": self._convert_rect,
            "circle": self._convert_circle,
            "ellipse": self._convert_ellipse,
            "line": self._convert_line,
            "polyline": self._convert_polyline,
            "polygon": self._convert_polygon,
            "path": self._convert_path,
            "text": self._convert_text,
            "g": self._convert_group,
        }
        self.elements_by_type = {}
        
    def import_svg(self, filepath, depth=0.2):
        """Import an SVG file and convert to SceneX elements."""
        # Parse the SVG file
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Get SVG dimensions
        width, height = self._parse_dimensions(root)
        
        # Setup element type tracking
        self.elements_by_type = {
            "node": [],
            "connector": [],
            "label": [],
            "group": [],
            "decoration": [],
        }
        
        # Convert elements
        elements = self._convert_element(root, depth)
        
        # Analyze relationships
        self._analyze_relationships(elements)
        
        return elements
        
    def get_elements_by_type(self, element_type):
        """Get elements of a specific type."""
        return self.elements_by_type.get(element_type, [])
        
    def _parse_dimensions(self, svg_root):
        """Parse width and height from SVG."""
        width = svg_root.get("width")
        height = svg_root.get("height")
        
        # Handle different formats
        width = self._parse_dimension(width)
        height = self._parse_dimension(height)
        
        # Fallback to viewBox if necessary
        if width is None or height is None:
            viewbox = svg_root.get("viewBox")
            if viewbox:
                parts = viewbox.strip().split()
                if len(parts) == 4:
                    _, _, width, height = map(float, parts)
                    
        return width or 100, height or 100
        
    def _parse_dimension(self, value):
        """Parse dimension value with units."""
        if value is None:
            return None
            
        # Strip units
        if value.endswith(("px", "pt", "mm", "cm", "in")):
            value = value[:-2]
        elif value.endswith("%"):
            # Percentage is more complex, default to None for now
            return None
            
        try:
            return float(value)
        except ValueError:
            return None
            
    def _convert_element(self, element, depth, parent=None):
        """Convert an SVG element to a SceneX element."""
        tag = element.tag.split("}")[-1]  # Remove namespace
        
        # Get conversion function for this tag
        converter = self.element_types.get(tag)
        if converter:
            scenex_elements = converter(element, depth, parent)
        else:
            # Unknown element type
            scenex_elements = []
            
        # Process children for groups and SVG root
        if tag in ("svg", "g"):
            for child in element:
                child_elements = self._convert_element(child, depth, scenex_elements[0] if scenex_elements else parent)
                if child_elements:
                    if scenex_elements:
                        # Add children to group
                        scenex_elements[0].add(*child_elements)
                    else:
                        # Add to list if no parent
                        scenex_elements.extend(child_elements)
                        
        return scenex_elements
        
    def _convert_rect(self, element, depth, parent):
        """Convert SVG rect to a ShapeElement."""
        # Parse attributes
        x = float(element.get("x", 0))
        y = float(element.get("y", 0))
        width = float(element.get("width", 0))
        height = float(element.get("height", 0))
        rx = float(element.get("rx", 0))
        
        # Parse style
        style = self._parse_style(element)
        
        # Create element
        if rx > 0:
            # Rounded rectangle
            shape = ShapeElement(
                shape_type="rounded_cube",
                size=(width, height, depth),
                position=(x + width/2, y + height/2, 0),
                corner_radius=rx
            )
        else:
            # Regular rectangle
            shape = ShapeElement(
                shape_type="cube",
                size=(width, height, depth),
                position=(x + width/2, y + height/2, 0)
            )
            
        # Apply style
        self._apply_style(shape, style)
        
        # Determine element type
        element_type = self._determine_element_type(element, "rect")
        self.elements_by_type[element_type].append(shape)
        
        return [shape]
        
    def _convert_circle(self, element, depth, parent):
        """Convert SVG circle to a ShapeElement."""
        # Parse attributes
        cx = float(element.get("cx", 0))
        cy = float(element.get("cy", 0))
        r = float(element.get("r", 0))
        
        # Parse style
        style = self._parse_style(element)
        
        # Create element
        shape = ShapeElement(
            shape_type="cylinder",
            size=r * 2,
            position=(cx, cy, 0),
            height=depth
        )
        
        # Apply style
        self._apply_style(shape, style)
        
        # Determine element type
        element_type = self._determine_element_type(element, "circle")
        self.elements_by_type[element_type].append(shape)
        
        return [shape]
        
    def _convert_path(self, element, depth, parent):
        """Convert SVG path to a PathElement."""
        # Parse attributes
        d = element.get("d", "")
        
        # Parse style
        style = self._parse_style(element)
        
        # Create element
        path = PathElement(
            path_data=d,
            depth=depth
        )
        
        # Apply style
        self._apply_style(path, style)
        
        # Determine element type (paths are often connectors)
        element_type = self._determine_element_type(element, "path")
        self.elements_by_type[element_type].append(path)
        
        return [path]
        
    def _parse_style(self, element):
        """Parse inline and CSS styles from an SVG element."""
        style = {}
        
        # Inline style attribute
        style_attr = element.get("style")
        if style_attr:
            pairs = style_attr.split(";")
            for pair in pairs:
                if ":" in pair:
                    key, value = pair.split(":", 1)
                    style[key.strip()] = value.strip()
                    
        # Direct attributes (override inline styles)
        for attr in ["fill", "stroke", "stroke-width", "opacity", "fill-opacity", "stroke-opacity"]:
            if attr in element.attrib:
                style[attr] = element.get(attr)
                
        return style
        
    def _apply_style(self, element, style):
        """Apply SVG style to a SceneX element."""
        # Fill color
        fill = style.get("fill", "#000000")
        if fill != "none":
            # Convert color format
            color = self._parse_color(fill)
            element.set_color(color)
            
        # Opacity
        opacity = float(style.get("opacity", 1.0))
        fill_opacity = float(style.get("fill-opacity", 1.0))
        element.set_opacity(opacity * fill_opacity)
        
        # Store original style for reference
        element.svg_style = style
        
    def _parse_color(self, color_str):
        """Parse SVG color to RGB tuple."""
        if color_str.startswith("#"):
            # Hex color
            if len(color_str) == 4:  # #RGB
                r = int(color_str[1] + color_str[1], 16) / 255
                g = int(color_str[2] + color_str[2], 16) / 255
                b = int(color_str[3] + color_str[3], 16) / 255
            else:  # #RRGGBB
                r = int(color_str[1:3], 16) / 255
                g = int(color_str[3:5], 16) / 255
                b = int(color_str[5:7], 16) / 255
            return (r, g, b)
        elif color_str.startswith("rgb("):
            # RGB function
            rgb = color_str[4:-1].split(",")
            r = float(rgb[0].strip()) / 255
            g = float(rgb[1].strip()) / 255
            b = float(rgb[2].strip()) / 255
            return (r, g, b)
        else:
            # Named colors - simplified for brevity
            colors = {
                "red": (1, 0, 0),
                "green": (0, 1, 0),
                "blue": (0, 0, 1),
                "black": (0, 0, 0),
                "white": (1, 1, 1),
                # Add more colors as needed
            }
            return colors.get(color_str.lower(), (0, 0, 0))
            
    def _determine_element_type(self, element, tag):
        """Determine the semantic type of an element based on attributes and context."""
        # Get ID and class
        element_id = element.get("id", "")
        element_class = element.get("class", "")
        
        # Check for explicit classification in ID or class
        if any(keyword in element_id.lower() for keyword in ["node", "component", "entity"]):
            return "node"
        elif any(keyword in element_id.lower() for keyword in ["connector", "link", "arrow", "connection"]):
            return "connector"
        elif any(keyword in element_id.lower() for keyword in ["label", "text", "title"]):
            return "label"
        elif tag == "g":
            return "group"
        elif tag == "text":
            return "label"
        
        # Heuristic classification based on shape and attributes
        if tag == "rect" or tag == "circle" or tag == "ellipse":
            # Likely a node
            return "node"
        elif tag == "line" or tag == "polyline":
            # Likely a connector
            return "connector"
        elif tag == "path":
            # Could be either - check if it looks like a connector
            path_data = element.get("d", "")
            if "M" in path_data and "L" in path_data and path_data.count("M") == 1:
                # Simple path with one move and line segments - likely a connector
                return "connector"
            else:
                # Complex path - might be a node or decoration
                return "node"
        
        # Default to decoration for unclassified elements
        return "decoration"
        
    def _analyze_relationships(self, elements):
        """Analyze spatial relationships between elements."""
        nodes = self.elements_by_type["node"]
        connectors = self.elements_by_type["connector"]
        
        # For each connector, try to find its endpoints
        for conn in connectors:
            if isinstance(conn, ConnectorElement):
                # Already a connector element with endpoints
                continue
                
            # Find nodes at the endpoints of this connector
            start_point, end_point = self._get_connector_endpoints(conn)
            
            # Find the closest nodes to these points
            start_element = self._find_closest_node(start_point, nodes)
            end_element = self._find_closest_node(end_point, nodes)
            
            if start_element and end_element:
                # Create a proper ConnectorElement
                new_conn = ConnectorElement(
                    start_element=start_element,
                    end_element=end_element,
                    color=conn.color,
                    opacity=conn.opacity
                )
                
                # Replace the original connector in the list
                idx = connectors.index(conn)
                connectors[idx] = new_conn
                
                # Update the element's parent if needed
                if conn.parent:
                    parent_idx = conn.parent.children.index(conn)
                    conn.parent.children[parent_idx] = new_conn
                    new_conn.parent = conn.parent
        
    def _get_connector_endpoints(self, connector):
        """Extract the endpoints of a connector element."""
        if isinstance(connector, PathElement):
            # Parse the path data to find endpoints
            path_data = connector.path_data
            # Simplified parsing - would need proper SVG path parsing
            if path_data.startswith("M") and "L" in path_data:
                parts = path_data.strip().split()
                start = parts[0][1:].split(",")  # After M
                end = parts[-1].split(",")       # Last point
                
                try:
                    start_point = (float(start[0]), float(start[1]), 0)
                    end_point = (float(end[0]), float(end[1]), 0)
                    return start_point, end_point
                except (ValueError, IndexError):
                    # Fallback to bounding box
                    bbox = connector.bounding_box
                    return (bbox.x, bbox.y, 0), (bbox.x + bbox.width, bbox.y + bbox.height, 0)
            else:
                # Fallback to bounding box
                bbox = connector.bounding_box
                return (bbox.x, bbox.y, 0), (bbox.x + bbox.width, bbox.y + bbox.height, 0)
        else:
            # Default to bounding box for other element types
            bbox = connector.bounding_box
            return (bbox.x, bbox.y, 0), (bbox.x + bbox.width, bbox.y + bbox.height, 0)
        
    def _find_closest_node(self, point, nodes):
        """Find the node closest to a point."""
        closest = None
        min_dist = float('inf')
        
        for node in nodes:
            dist = self._point_distance(point, node.position)
            if dist < min_dist:
                min_dist = dist
                closest = node
                
        # Only return if reasonably close
        return closest if min_dist < 20 else None
        
    def _point_distance(self, p1, p2):
        """Calculate distance between two points."""
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
```

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
