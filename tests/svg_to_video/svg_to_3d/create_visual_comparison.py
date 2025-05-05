"""
Create a visual comparison SVG showing what works and what doesn't
"""

import os

def create_visual_comparison():
    """Create an SVG that shows working vs non-working features"""
    
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect x="0" y="0" width="800" height="600" fill="#f0f0f0"/>
    
    <!-- Title -->
    <text x="400" y="40" text-anchor="middle" font-size="32" font-weight="bold" fill="#000000">SVG to 3D Converter Status</text>
    
    <!-- Working Features Section -->
    <rect x="50" y="80" width="700" height="200" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
    <text x="70" y="110" font-size="24" font-weight="bold" fill="#2e7d32">✅ Working Features</text>
    
    <!-- Working examples -->
    <rect x="70" y="130" width="60" height="40" fill="#ff0000"/>
    <text x="100" y="190" text-anchor="middle" font-size="12">Solid Fill</text>
    
    <circle cx="200" cy="150" r="20" fill="#00ff00"/>
    <text x="200" y="190" text-anchor="middle" font-size="12">Circles</text>
    
    <ellipse cx="300" cy="150" rx="30" ry="15" fill="#0000ff"/>
    <text x="300" y="190" text-anchor="middle" font-size="12">Ellipses</text>
    
    <path d="M380,130 L420,170 L380,170 Z" fill="#ff00ff"/>
    <text x="400" y="190" text-anchor="middle" font-size="12">Paths</text>
    
    <text x="500" y="155" font-size="24" fill="#000000">Text</text>
    <text x="500" y="190" text-anchor="middle" font-size="12">3D Text</text>
    
    <polyline points="580,130 620,170 660,130 700,170" fill="none" stroke="#000000" stroke-width="3"/>
    <text x="640" y="190" text-anchor="middle" font-size="12">Lines/Polylines</text>
    
    <!-- Not Working Features Section -->
    <rect x="50" y="300" width="700" height="250" fill="#ffebee" stroke="#f44336" stroke-width="2"/>
    <text x="70" y="330" font-size="24" font-weight="bold" fill="#c62828">❌ Not Working Features</text>
    
    <!-- Not working examples -->
    <circle cx="100" cy="380" r="30" fill="#ff00ff" opacity="0.5"/>
    <text x="100" y="430" text-anchor="middle" font-size="12">Transparency</text>
    <text x="100" y="445" text-anchor="middle" font-size="10">(Shows as solid)</text>
    
    <circle cx="250" cy="380" r="30" fill="#00ffff" stroke="#000000" stroke-width="8"/>
    <text x="250" y="430" text-anchor="middle" font-size="12">Strokes on Circles</text>
    <text x="250" y="445" text-anchor="middle" font-size="10">(Stroke not visible)</text>
    
    <circle cx="400" cy="380" r="30" fill="none" stroke="#ff0000" stroke-width="8"/>
    <text x="400" y="430" text-anchor="middle" font-size="12">Stroke Only</text>
    <text x="400" y="445" text-anchor="middle" font-size="10">(Not rendering)</text>
    
    <rect x="520" y="350" width="60" height="60" fill="#0000ff" fill-opacity="0.3" stroke="#000000" stroke-width="4" stroke-opacity="0.7"/>
    <text x="550" y="430" text-anchor="middle" font-size="12">Mixed Opacity</text>
    <text x="550" y="445" text-anchor="middle" font-size="10">(All show as solid)</text>
    
    <path d="M650,350 Q680,320 710,350 T770,350" fill="none" stroke="#ff0088" stroke-width="6" stroke-dasharray="5,5"/>
    <text x="710" y="430" text-anchor="middle" font-size="12">Dashed Strokes</text>
    <text x="710" y="445" text-anchor="middle" font-size="10">(Not implemented)</text>
</svg>"""
    
    # Save the visual comparison
    output_path = os.path.join(os.path.dirname(__file__), 'visual_comparison.svg')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"Visual comparison saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_visual_comparison()
