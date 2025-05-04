            elif cmd_type == 'C':
                # Convert the spline to bezier
                if spline is None:
                    # If no spline exists yet, create one
                    spline = curve.splines.new('BEZIER')
                    is_first_point = True
                    continue
                    
                # We need to convert to BEZIER type for curves
                if spline.type != 'BEZIER':
                    # Create a new bezier spline
                    bezier_spline = curve.splines.new('BEZIER')
                    bezier_spline.use_cyclic_u = False
                    
                    # Copy existing points to bezier spline
                    bezier_spline.bezier_points.add(len(spline.points) - 1)
                    for i, point in enumerate(spline.points):
                        x, y = point.co.x, point.co.y
                        bezier_spline.bezier_points[i].co = (x, y, 0)
                        bezier_spline.bezier_points[i].handle_left_type = 'AUTO'
                        bezier_spline.bezier_points[i].handle_right_type = 'AUTO'
                    
                    # Remove old spline
                    curve.splines.remove(spline)
                    spline = bezier_spline
                
                # Add bezier curves
                curves = cmd['curves']
                for curve_points in curves:
                    start, cp1, cp2, end = curve_points
                    
                    # Convert points to Blender coordinates
                    bx = (end[0] - self.width/2) * self.scale_factor
                    by = (self.height/2 - end[1]) * self.scale_factor
                    
                    # Convert control points
                    cp1x = (cp1[0] - self.width/2) * self.scale_factor
                    cp1y = (self.height/2 - cp1[1]) * self.scale_factor
                    cp2x = (cp2[0] - self.width/2) * self.scale_factor
                    cp2y = (self.height/2 - cp2[1]) * self.scale_factor
                    
                    # Add new bezier point
                    spline.bezier_points.add(1)
                    spline.bezier_points[-1].co = (bx, by, 0)
                    
                    # Set handle types
                    spline.bezier_points[-2].handle_right_type = 'FREE'
                    spline.bezier_points[-1].handle_left_type = 'FREE'
                    
                    # Set handle positions
                    spline.bezier_points[-2].handle_right = (cp1x, cp1y, 0)
                    spline.bezier_points[-1].handle_left = (cp2x, cp2y, 0)
            
            elif cmd_type == 'Q':
                # Quadratic bezier - similar to cubic bezier but with one control point
                if spline is None:
                    # If no spline exists yet, create one
                    spline = curve.splines.new('BEZIER')
                    is_first_point = True
                    continue
                    
                # Convert to BEZIER type
                if spline.type != 'BEZIER':
                    bezier_spline = curve.splines.new('BEZIER')
                    bezier_spline.use_cyclic_u = False
                    
                    # Copy existing points to bezier spline
                    bezier_spline.bezier_points.add(len(spline.points) - 1)
                    for i, point in enumerate(spline.points):
                        x, y = point.co.x, point.co.y
                        bezier_spline.bezier_points[i].co = (x, y, 0)
                        bezier_spline.bezier_points[i].handle_left_type = 'AUTO'
                        bezier_spline.bezier_points[i].handle_right_type = 'AUTO'
                    
                    # Remove old spline
                    curve.splines.remove(spline)
                    spline = bezier_spline
                
                # Add quadratic bezier curves - convert to cubic
                curves = cmd['curves']
                for curve_points in curves:
                    start, cp, end = curve_points
                    
                    # Convert points to Blender coordinates
                    bx = (end[0] - self.width/2) * self.scale_factor
                    by = (self.height/2 - end[1]) * self.scale_factor
                    
                    # Convert control point
                    cpx = (cp[0] - self.width/2) * self.scale_factor
                    cpy = (self.height/2 - cp[1]) * self.scale_factor
                    
                    # Get start point coordinates
                    start_x = spline.bezier_points[-1].co.x
                    start_y = spline.bezier_points[-1].co.y
                    
                    # Convert quadratic to cubic bezier control points
                    # P1 = start + 2/3 * (CP - start)
                    # P2 = end + 2/3 * (CP - end)
                    cp1x = start_x + 2/3 * (cpx - start_x)
                    cp1y = start_y + 2/3 * (cpy - start_y)
                    cp2x = bx + 2/3 * (cpx - bx)
                    cp2y = by + 2/3 * (cpy - by)
                    
                    # Add new bezier point
                    spline.bezier_points.add(1)
                    spline.bezier_points[-1].co = (bx, by, 0)
                    
                    # Set handle types
                    spline.bezier_points[-2].handle_right_type = 'FREE'
                    spline.bezier_points[-1].handle_left_type = 'FREE'
                    
                    # Set handle positions
                    spline.bezier_points[-2].handle_right = (cp1x, cp1y, 0)
                    spline.bezier_points[-1].handle_left = (cp2x, cp2y, 0)
            
            elif cmd_type == 'A':
                # Elliptical arcs - approximated with bezier curves
                if spline is None:
                    # If no spline exists yet, create one
                    spline = curve.splines.new('BEZIER')
                    is_first_point = True
                    continue
                    
                # Convert to BEZIER type if needed
                if spline.type != 'BEZIER':
                    bezier_spline = curve.splines.new('BEZIER')
                    bezier_spline.use_cyclic_u = False
                    
                    # Copy existing points to bezier spline
                    bezier_spline.bezier_points.add(len(spline.points) - 1)
                    for i, point in enumerate(spline.points):
                        x, y = point.co.x, point.co.y
                        bezier_spline.bezier_points[i].co = (x, y, 0)
                        bezier_spline.bezier_points[i].handle_left_type = 'AUTO'
                        bezier_spline.bezier_points[i].handle_right_type = 'AUTO'
                    
                    # Remove old spline
                    curve.splines.remove(spline)
                    spline = bezier_spline
                
                # Add approximated arc segments
                arcs = cmd['arcs']
                for arc in arcs:
                    # Get arc parameters
                    start_point = arc['start']
                    end_point = arc['end']
                    rx, ry = arc['rx'], arc['ry']
                    angle = arc['angle']
                    large_arc = arc['large_arc']
                    sweep = arc['sweep']
                    
                    # Convert to Blender coordinates
                    start_x = (start_point[0] - self.width/2) * self.scale_factor
                    start_y = (self.height/2 - start_point[1]) * self.scale_factor
                    end_x = (end_point[0] - self.width/2) * self.scale_factor
                    end_y = (self.height/2 - end_point[1]) * self.scale_factor
                    
                    # Simple approximation - add a few bezier points
                    # For better arc approximation, add multiple bezier points
                    num_segments = 4
                    
                    for i in range(num_segments):
                        t = (i + 1) / num_segments  # Parameter from 0 to 1
                        
                        # Simple circular interpolation (this is an approximation)
                        theta = t * math.pi * (2 if large_arc else 1) * (1 if sweep else -1)
                        
                        # Calculate point on approximated arc
                        center_x = (start_x + end_x) / 2
                        center_y = (start_y + end_y) / 2
                        px = center_x + rx * math.cos(theta) * (1 if sweep else -1)
                        py = center_y + ry * math.sin(theta) * (1 if sweep else -1)
                        
                        # Add point with automatic handles
                        spline.bezier_points.add(1)
                        spline.bezier_points[-1].co = (px, py, 0)
                        spline.bezier_points[-1].handle_left_type = 'AUTO'
                        spline.bezier_points[-1].handle_right_type = 'AUTO'
                    
                    # Ensure the last point is exactly at the end position
                    spline.bezier_points[-1].co = (end_x, end_y, 0)
            
            elif cmd_type == 'Z':
                if spline:
                    spline.use_cyclic_u = True
        
        # Set bevel depth based on whether it's a filled path or just stroke
        if has_fill:
            # Use extrude for filled paths
            curve.extrude = self.extrude_depth
            curve.bevel_depth = 0
        else:
            # Use bevel for stroke paths
            stroke_width = float(element['style'].get('stroke-width', 1))
            curve.bevel_depth = stroke_width * self.scale_factor * 0.5
            curve.extrude = 0
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Path_{len(bpy.data.objects)}"
        
        log(f"Path created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D path: {e}")
        traceback.print_exc()
        return None


def create_3d_group(self, element):
    """Create a 3D group from SVG group element."""
    try:
        group_id = element.get('id', f"Group_{len(bpy.data.collections)}")
        
        log(f"Creating 3D group: {group_id}")
        
        # Create a new collection for the group
        collection = bpy.data.collections.new(group_id)
        bpy.context.scene.collection.children.link(collection)
        
        # Create an empty object to serve as the group's parent
        group_obj = bpy.data.objects.new(group_id, None)
        bpy.context.collection.objects.link(group_obj)
        
        # Process child elements
        child_objects = []
        for child in element.get('children', []):
            obj = self.create_3d_object(child)
            if obj:
                # Parent the object to our group object
                obj.parent = group_obj
                
                # Move the object to this collection
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                collection.objects.link(obj)
                
                child_objects.append(obj)
        
        # Store reference to group objects
        self.group_objects[group_id] = child_objects
        
        log(f"Group created successfully: {group_id} with {len(child_objects)} child objects")
        return group_obj
    except Exception as e:
        log(f"Error creating 3D group: {e}")
        traceback.print_exc()
        return None