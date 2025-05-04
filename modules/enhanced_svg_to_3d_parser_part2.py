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