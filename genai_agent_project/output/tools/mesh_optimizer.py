import bpy
import bmesh
import math

def optimize_mesh(obj=None, ratio=0.5, method='COLLAPSE'):
    """
    Optimize a mesh by reducing its polygon count.
    
    Args:
        obj: The object to optimize (if None, uses active object)
        ratio: Reduction ratio (0.5 = 50% reduction)
        method: 'COLLAPSE' or 'DECIMATE'
    """
    if obj is None:
        obj = bpy.context.active_object
    
    if obj is None or obj.type != 'MESH':
        print("No valid mesh object selected")
        return False
    
    print(f"Optimizing mesh: {obj.name}")
    print(f"Original vertices: {len(obj.data.vertices)}")
    print(f"Original polygons: {len(obj.data.polygons)}")
    
    if method == 'COLLAPSE':
        # Use edge collapse modifier
        modifier = obj.modifiers.new(name="EdgeCollapse", type='DECIMATE')
        modifier.decimate_type = 'COLLAPSE'
        modifier.ratio = ratio
        bpy.ops.object.modifier_apply(modifier="EdgeCollapse")
    else:
        # Use decimate modifier
        modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
        modifier.decimate_type = 'UNSUBDIV'
        modifier.iterations = int(-math.log(ratio, 2))
        bpy.ops.object.modifier_apply(modifier="Decimate")
    
    print(f"Optimized vertices: {len(obj.data.vertices)}")
    print(f"Optimized polygons: {len(obj.data.polygons)}")
    print(f"Reduction achieved: {1.0 - len(obj.data.polygons)/len(obj.data.polygons):.2f}%")
    
    return True

def clean_mesh(obj=None, remove_doubles=True, recalc_normals=True, distance=0.0001):
    """
    Clean a mesh by removing doubles and recalculating normals.
    
    Args:
        obj: The object to clean (if None, uses active object)
        remove_doubles: Whether to remove duplicate vertices
        recalc_normals: Whether to recalculate normals
        distance: Merge distance for removing doubles
    """
    if obj is None:
        obj = bpy.context.active_object
    
    if obj is None or obj.type != 'MESH':
        print("No valid mesh object selected")
        return False
    
    print(f"Cleaning mesh: {obj.name}")
    
    # Get the mesh data
    mesh = obj.data
    
    # Create a BMesh from the mesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    if remove_doubles:
        # Remove duplicate vertices
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
    
    if recalc_normals:
        # Recalculate normals
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    # Update the mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Update mesh display
    mesh.update()
    
    print("Mesh cleaning completed")
    return True

def execute_tool():
    """
    Main function to execute when the tool is run from Blender.
    """
    # Check if there's a selected object
    if not bpy.context.selected_objects:
        print("No objects selected. Please select a mesh object.")
        return
    
    # Get the active object
    obj = bpy.context.active_object
    
    if obj.type != 'MESH':
        print("Selected object is not a mesh. Please select a mesh object.")
        return
    
    # Optimize the mesh
    print("\n===== MESH OPTIMIZER TOOL =====")
    optimize_mesh(obj, ratio=0.5, method='COLLAPSE')
    clean_mesh(obj, remove_doubles=True, recalc_normals=True)
    print("===== OPTIMIZATION COMPLETE =====\n")

# Execute the tool when run directly
if __name__ == "__main__":
    execute_tool()
