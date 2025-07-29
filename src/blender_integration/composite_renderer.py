"""
Composite Scene Renderer for stable multi-object preview generation.

This module provides a robust approach to rendering multi-object scenes
by using a simplified rendering pipeline optimized for stability.
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CompositeRenderer:
    """Handles composite scene rendering with stability optimizations."""
    
    def __init__(self, blender_path: str = "blender"):
        """Initialize the composite renderer."""
        self.blender_path = blender_path
        self.max_objects = 10  # Safety limit
        self.render_timeout = 30  # seconds
        
    def generate_stable_composite_script(self, objects: List[Dict[str, Any]], 
                                       scene_name: str = "Composite Scene") -> str:
        """
        Generate a stable composite script optimized for preview rendering.
        
        Args:
            objects: List of object dictionaries with parameters
            scene_name: Name of the scene
            
        Returns:
            Complete Blender Python script as string
        """
        script = f'''#!/usr/bin/env python3
# Stable Composite Scene Renderer
# Scene: {scene_name}

import bpy
import sys
import math

# Error handling wrapper
def safe_execute(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {{func.__name__}}: {{str(e)}}", file=sys.stderr)
            return None
    return wrapper

@safe_execute
def clear_scene():
    """Clear all objects from the scene."""
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # Delete all mesh objects
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete(use_global=False)
    
    # Clear orphaned data
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    
    for material in bpy.data.materials:
        if material.users == 0:
            bpy.data.materials.remove(material)

@safe_execute
def create_object(obj_data):
    """Create a single object with error handling."""
    obj_type = obj_data.get('object_type', 'cube')
    size = float(obj_data.get('size', 2.0))
    pos_x = float(obj_data.get('pos_x', 0))
    pos_y = float(obj_data.get('pos_y', 0))
    pos_z = float(obj_data.get('pos_z', 0))
    
    # Limit position values for stability
    pos_x = max(-50, min(50, pos_x))
    pos_y = max(-50, min(50, pos_y))
    pos_z = max(-50, min(50, pos_z))
    size = max(0.1, min(10, size))
    
    # Create object
    if obj_type == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=size, location=(pos_x, pos_y, pos_z))
    elif obj_type == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=(pos_x, pos_y, pos_z))
    elif obj_type == 'cylinder':
        bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size*2, location=(pos_x, pos_y, pos_z))
    elif obj_type == 'plane':
        bpy.ops.mesh.primitive_plane_add(size=size, location=(pos_x, pos_y, pos_z))
    else:
        print(f"Unknown object type: {{obj_type}}", file=sys.stderr)
        return None
    
    obj = bpy.context.active_object
    
    # Apply rotation
    rot_x = math.radians(float(obj_data.get('rot_x', 0)))
    rot_y = math.radians(float(obj_data.get('rot_y', 0)))
    rot_z = math.radians(float(obj_data.get('rot_z', 0)))
    obj.rotation_euler = (rot_x, rot_y, rot_z)
    
    # Apply simple material
    mat = bpy.data.materials.new(name=f"Mat_{{obj.name}}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    
    if bsdf and obj_data.get('color'):
        color = obj_data['color']
        if isinstance(color, str) and color.startswith('#'):
            color = color.lstrip('#')
            r = int(color[0:2], 16) / 255.0
            g = int(color[2:4], 16) / 255.0
            b = int(color[4:6], 16) / 255.0
            bsdf.inputs['Base Color'].default_value = (r, g, b, 1.0)
            bsdf.inputs['Metallic'].default_value = float(obj_data.get('metallic', 0.0))
            bsdf.inputs['Roughness'].default_value = float(obj_data.get('roughness', 0.5))
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return obj

@safe_execute
def setup_scene():
    """Set up scene with camera and lighting."""
    # Set up render engine (use Eevee for speed and stability)
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.taa_render_samples = 16
    bpy.context.scene.eevee.use_ssr = False  # Disable screen space reflections
    bpy.context.scene.eevee.use_bloom = False  # Disable bloom for cleaner preview
    
    # Set render resolution
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 600
    bpy.context.scene.render.resolution_percentage = 100
    
    # Camera setup
    if 'Camera' not in bpy.data.objects:
        bpy.ops.object.camera_add()
    
    camera = bpy.data.objects['Camera']
    camera.location = (10, -10, 8)
    camera.rotation_euler = (1.1, 0, 0.785)
    
    # Make camera active
    bpy.context.scene.camera = camera
    
    # Lighting setup
    # Remove existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj)
    
    # Add key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.active_object
    key_light.data.energy = 1.0
    key_light.rotation_euler = (0.6, 0, -0.785)
    
    # Add fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 0.5
    fill_light.data.size = 5
    
    # Set world background
    world = bpy.context.scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.1, 0.1, 0.15, 1.0)
        bg_node.inputs['Strength'].default_value = 0.5

@safe_execute 
def render_preview(output_path):
    """Render the scene to an image."""
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.film_transparent = False
    
    # Render
    bpy.ops.render.render(write_still=True)
    print(f"Rendered preview to: {{output_path}}")

# Main execution
def main():
    print("Starting composite scene generation...")
    
    # Clear scene
    clear_scene()
    print("Scene cleared")
    
    # Object data
    objects = {objects}
    
    # Create objects (limit to first {self.max_objects} for safety)
    created_count = 0
    for i, obj_data in enumerate(objects[:{{self.max_objects}}]):
        print(f"Creating object {{i+1}}/{{len(objects)}}")
        if create_object(obj_data):
            created_count += 1
    
    print(f"Created {{created_count}} objects")
    
    # Set up scene
    setup_scene()
    print("Scene setup complete")
    
    # Frame all objects in view
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.view3d.camera_to_view_selected()
    
    # Render preview if output path is set
    import os
    output_path = os.environ.get('BLENDER_RENDER_OUTPUT')
    if output_path:
        render_preview(output_path)
    
    # Save blend file if path is set
    blend_path = os.environ.get('BLENDER_SAVE_PATH')
    if blend_path:
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"Saved blend file to: {{blend_path}}")
    
    print("Composite scene generation complete!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Fatal error: {{str(e)}}", file=sys.stderr)
        sys.exit(1)
'''
        
        return script
    
    def simplify_objects_for_preview(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simplify object parameters for stable preview rendering.
        
        Args:
            objects: Original object list
            
        Returns:
            Simplified object list
        """
        simplified = []
        
        for obj in objects[:self.max_objects]:  # Limit object count
            params = obj.get('parameters', obj)
            
            simplified_obj = {
                'object_type': params.get('object_type', 'cube'),
                'size': min(10, max(0.1, float(params.get('size', 2.0)))),
                'pos_x': min(50, max(-50, float(params.get('pos_x', 0)))),
                'pos_y': min(50, max(-50, float(params.get('pos_y', 0)))),
                'pos_z': min(50, max(-50, float(params.get('pos_z', 0)))),
                'rot_x': float(params.get('rot_x', 0)) % 360,
                'rot_y': float(params.get('rot_y', 0)) % 360,
                'rot_z': float(params.get('rot_z', 0)) % 360,
                'color': params.get('color', '#808080'),
                'metallic': min(1, max(0, float(params.get('metallic', 0)))),
                'roughness': min(1, max(0, float(params.get('roughness', 0.5))))
            }
            
            simplified.append(simplified_obj)
        
        return simplified
    
    def calculate_scene_bounds(self, objects: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Calculate bounding box for all objects in scene."""
        if not objects:
            return {'min': [0, 0, 0], 'max': [0, 0, 0]}
        
        min_coords = [float('inf')] * 3
        max_coords = [float('-inf')] * 3
        
        for obj in objects:
            params = obj.get('parameters', obj)
            pos = [
                float(params.get('pos_x', 0)),
                float(params.get('pos_y', 0)),
                float(params.get('pos_z', 0))
            ]
            size = float(params.get('size', 2.0))
            
            for i in range(3):
                min_coords[i] = min(min_coords[i], pos[i] - size)
                max_coords[i] = max(max_coords[i], pos[i] + size)
        
        return {'min': min_coords, 'max': max_coords}
    
    def get_optimal_camera_position(self, bounds: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate optimal camera position for scene bounds."""
        center = [
            (bounds['min'][i] + bounds['max'][i]) / 2
            for i in range(3)
        ]
        
        size = max(
            bounds['max'][i] - bounds['min'][i]
            for i in range(3)
        )
        
        # Calculate camera distance based on scene size
        distance = max(15, size * 2)
        height = max(8, size * 0.8)
        
        return {
            'location': [
                center[0] + distance * 0.7,
                center[1] - distance * 0.7,
                center[2] + height
            ],
            'rotation': [1.1, 0, 0.785],  # Look down at scene
            'distance': distance
        }