
"""
SVG generator service for the web UI.
"""

import os
from pathlib import Path

class SVGGeneratorService:
    """Service for SVG generator functionality."""
    
    def __init__(self):
        # Use the consolidated output directory
        self.output_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_svg_files(self):
        """Get a list of all SVG files in the output directory."""
        if not self.output_dir.exists():
            return []
        
        svg_files = list(self.output_dir.glob("*.svg"))
        return [
            {
                "filename": file.name,
                "path": str(file),
                "size": file.stat().st_size,
                "modified": file.stat().st_mtime
            }
            for file in svg_files
        ]
    
    def delete_svg_file(self, filename):
        """Delete an SVG file."""
        file_path = self.output_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
