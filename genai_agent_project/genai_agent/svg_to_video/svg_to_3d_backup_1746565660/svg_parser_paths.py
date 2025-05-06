"""
SVG Path Parser Module

This module handles parsing SVG path elements and path data.
"""

import re
import math
import traceback
from .svg_utils import log


def _parse_path(self, element, style, transform_matrix):
    """Parse a path element with enhanced path commands support."""
    try:
        d = element.attrib.get('d', '')
        
        if not d:
            log("Empty path data")
            return None
                
        # Parse path data
        path_data = self._parse_path_data(d, transform_matrix)
        
        # Check if we got any valid commands
        if not path_data:
            log("No valid path commands found")
            return None
        
        return {
            'type': 'path',
            'path_data': path_data,
            'style': style,
            'transform': transform_matrix
        }
    except Exception as e:
        log(f"Error parsing path: {e}")
        traceback.print_exc()
        return None


def _parse_path_data(self, d, transform_matrix):
    """
    Parse SVG path data string into a list of path commands.
    Handles SVG path commands: M, m, L, l, H, h, V, v, C, c, S, s, Q, q, T, t, A, a, Z, z
    """
    if not d:
        return []
        
    # Command patterns
    command_pattern = r'([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)'
    
    # Extract commands and parameters
    commands = []
    matches = re.findall(command_pattern, d)
    
    current_point = (0, 0)  # Current point for relative commands
    start_point = (0, 0)    # Start point for closepath
    last_control_point = None  # For smooth curves
    
    for cmd, params_str in matches:
        # Parse parameters for this command
        params = []
        if cmd != 'Z' and cmd != 'z':
            # Extract all numbers from the parameters string
            params = [float(p) for p in re.findall(r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', params_str)]
        
        # Process command based on type
        if cmd == 'M' or cmd == 'm':  # Moveto
            is_relative = (cmd == 'm')
            points = []
            
            # First point is treated as moveto
            if len(params) >= 2:
                x, y = params[0], params[1]
                if is_relative:
                    x += current_point[0]
                    y += current_point[1]
                
                if transform_matrix:
                    x, y = self._apply_transform(x, y, transform_matrix)
                    
                current_point = (x, y)
                start_point = current_point  # Update start point for closepath
                points.append((x, y))
            
            # Remaining points are treated as lineto
            for i in range(2, len(params), 2):
                if i+1 < len(params):
                    x, y = params[i], params[i+1]
                    if is_relative:
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        x, y = self._apply_transform(x, y, transform_matrix)
                        
                    current_point = (x, y)
                    points.append((x, y))
            
            if points:
                commands.append({
                    'command': 'M',
                    'points': points
                })
        
        elif cmd == 'L' or cmd == 'l':  # Lineto
            is_relative = (cmd == 'l')
            points = []
            
            for i in range(0, len(params), 2):
                if i+1 < len(params):
                    x, y = params[i], params[i+1]
                    if is_relative:
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        x, y = self._apply_transform(x, y, transform_matrix)
                        
                    current_point = (x, y)
                    points.append((x, y))
            
            if points:
                commands.append({
                    'command': 'L',
                    'points': points
                })
        
        elif cmd == 'H' or cmd == 'h':  # Horizontal lineto
            is_relative = (cmd == 'h')
            points = []
            
            for x in params:
                if is_relative:
                    x += current_point[0]
                
                # For horizontal lines, y remains the same
                y = current_point[1]
                
                if transform_matrix:
                    x, y = self._apply_transform(x, y, transform_matrix)
                    
                current_point = (x, y)
                points.append((x, y))
            
            if points:
                commands.append({
                    'command': 'L',  # Convert to regular lineto for simplicity
                    'points': points
                })
        
        elif cmd == 'V' or cmd == 'v':  # Vertical lineto
            is_relative = (cmd == 'v')
            points = []
            
            for y in params:
                if is_relative:
                    y += current_point[1]
                
                # For vertical lines, x remains the same
                x = current_point[0]
                
                if transform_matrix:
                    x, y = self._apply_transform(x, y, transform_matrix)
                    
                current_point = (x, y)
                points.append((x, y))
            
            if points:
                commands.append({
                    'command': 'L',  # Convert to regular lineto for simplicity
                    'points': points
                })
        
        elif cmd == 'C' or cmd == 'c':  # Cubic Bezier curve
            is_relative = (cmd == 'c')
            curves = []
            
            for i in range(0, len(params), 6):
                if i+5 < len(params):
                    x1, y1 = params[i], params[i+1]      # First control point
                    x2, y2 = params[i+2], params[i+3]    # Second control point
                    x, y = params[i+4], params[i+5]      # End point
                    
                    if is_relative:
                        x1 += current_point[0]
                        y1 += current_point[1]
                        x2 += current_point[0]
                        y2 += current_point[1]
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                        x2, y2 = self._apply_transform(x2, y2, transform_matrix)
                        x, y = self._apply_transform(x, y, transform_matrix)
                    
                    curves.append((
                        current_point,  # Start point
                        (x1, y1),       # Control point 1
                        (x2, y2),       # Control point 2
                        (x, y)          # End point
                    ))
                    
                    current_point = (x, y)
                    last_control_point = (x2, y2)  # Store for smooth curves
            
            if curves:
                commands.append({
                    'command': 'C',
                    'curves': curves
                })
        
        elif cmd == 'S' or cmd == 's':  # Smooth cubic Bezier curve
            is_relative = (cmd == 's')
            curves = []
            
            for i in range(0, len(params), 4):
                if i+3 < len(params):
                    # The first control point is the reflection of the second control point
                    # of the previous command relative to the current point
                    if last_control_point and commands and commands[-1]['command'] in ('C', 'S'):
                        # Reflect previous control point
                        x1 = 2 * current_point[0] - last_control_point[0]
                        y1 = 2 * current_point[1] - last_control_point[1]
                    else:
                        # If previous command was not a cubic Bezier, the first control point is the current point
                        x1, y1 = current_point
                    
                    x2, y2 = params[i], params[i+1]    # Second control point
                    x, y = params[i+2], params[i+3]    # End point
                    
                    if is_relative:
                        x2 += current_point[0]
                        y2 += current_point[1]
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                        x2, y2 = self._apply_transform(x2, y2, transform_matrix)
                        x, y = self._apply_transform(x, y, transform_matrix)
                    
                    curves.append((
                        current_point,  # Start point
                        (x1, y1),       # Control point 1 (reflected)
                        (x2, y2),       # Control point 2
                        (x, y)          # End point
                    ))
                    
                    current_point = (x, y)
                    last_control_point = (x2, y2)  # Store for future smooth curves
            
            if curves:
                commands.append({
                    'command': 'C',  # Convert to regular cubic Bezier
                    'curves': curves
                })
        
        elif cmd == 'Q' or cmd == 'q':  # Quadratic Bezier curve
            is_relative = (cmd == 'q')
            curves = []
            
            for i in range(0, len(params), 4):
                if i+3 < len(params):
                    x1, y1 = params[i], params[i+1]    # Control point
                    x, y = params[i+2], params[i+3]    # End point
                    
                    if is_relative:
                        x1 += current_point[0]
                        y1 += current_point[1]
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                        x, y = self._apply_transform(x, y, transform_matrix)
                    
                    curves.append((
                        current_point,  # Start point
                        (x1, y1),       # Control point
                        (x, y)          # End point
                    ))
                    
                    current_point = (x, y)
                    last_control_point = (x1, y1)  # Store for smooth curves
            
            if curves:
                commands.append({
                    'command': 'Q',
                    'curves': curves
                })
        
        elif cmd == 'T' or cmd == 't':  # Smooth quadratic Bezier curve
            is_relative = (cmd == 't')
            curves = []
            
            for i in range(0, len(params), 2):
                if i+1 < len(params):
                    # The control point is the reflection of the control point
                    # of the previous command relative to the current point
                    if last_control_point and commands and commands[-1]['command'] in ('Q', 'T'):
                        # Reflect previous control point
                        x1 = 2 * current_point[0] - last_control_point[0]
                        y1 = 2 * current_point[1] - last_control_point[1]
                    else:
                        # If previous command was not a quadratic Bezier, use current point
                        x1, y1 = current_point
                    
                    x, y = params[i], params[i+1]    # End point
                    
                    if is_relative:
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                        x, y = self._apply_transform(x, y, transform_matrix)
                    
                    curves.append((
                        current_point,  # Start point
                        (x1, y1),       # Control point (reflected)
                        (x, y)          # End point
                    ))
                    
                    current_point = (x, y)
                    last_control_point = (x1, y1)
            
            if curves:
                commands.append({
                    'command': 'Q',  # Convert to regular quadratic Bezier
                    'curves': curves
                })
        
        elif cmd == 'A' or cmd == 'a':  # Elliptical arc
            is_relative = (cmd == 'a')
            arcs = []
            
            for i in range(0, len(params), 7):
                if i+6 < len(params):
                    rx = params[i]       # X radius
                    ry = params[i+1]     # Y radius
                    angle = params[i+2]  # X-axis rotation
                    large_arc = int(params[i+3]) != 0  # Large arc flag
                    sweep = int(params[i+4]) != 0      # Sweep flag
                    x, y = params[i+5], params[i+6]    # End point
                    
                    if is_relative:
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        # Note: This is a simplification. For proper handling,
                        # the arc parameters should be transformed correctly
                        x, y = self._apply_transform(x, y, transform_matrix)
                    
                    arcs.append({
                        'start': current_point,
                        'end': (x, y),
                        'rx': rx,
                        'ry': ry,
                        'angle': angle,
                        'large_arc': large_arc,
                        'sweep': sweep
                    })
                    
                    current_point = (x, y)
            
            if arcs:
                commands.append({
                    'command': 'A',
                    'arcs': arcs
                })
        
        elif cmd == 'Z' or cmd == 'z':  # Closepath
            if current_point != start_point:
                commands.append({
                    'command': 'L',
                    'points': [start_point]
                })
                current_point = start_point
                
            commands.append({
                'command': 'Z'
            })
    
    return commands
