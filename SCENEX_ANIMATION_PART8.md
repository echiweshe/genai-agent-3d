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
```
