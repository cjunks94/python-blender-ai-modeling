"""
Preview renderer module for generating model thumbnails.

This module provides functionality to render preview images of 3D models
using Blender's rendering capabilities.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .executor import BlenderExecutor, BlenderExecutionError
from .script_generator import ScriptGenerator, ScriptGenerationError


@dataclass
class PreviewResult:
    """Result of preview rendering operation."""
    success: bool
    image_path: Optional[str] = None
    image_data: Optional[bytes] = None
    width: Optional[int] = None
    height: Optional[int] = None
    error_message: Optional[str] = None


class PreviewRenderer:
    """Handles rendering preview images of 3D models."""
    
    def __init__(self, blender_path: str = 'blender', timeout: int = 30):
        """
        Initialize PreviewRenderer.
        
        Args:
            blender_path: Path to Blender executable
            timeout: Timeout for render operations in seconds
        """
        self.blender_executor = BlenderExecutor(blender_path, timeout)
        self.script_generator = ScriptGenerator()
        self.preview_dir = Path("previews")
        self.preview_dir.mkdir(exist_ok=True)
    
    def render_preview(
        self, 
        model_id: str, 
        model_params: Dict[str, Any],
        resolution: Tuple[int, int] = (400, 400),
        samples: int = 32
    ) -> PreviewResult:
        """
        Render a preview image of a 3D model.
        
        Args:
            model_id: Unique identifier for the model
            model_params: Parameters used to generate the model
            resolution: Output image resolution (width, height)
            samples: Number of render samples (higher = better quality)
            
        Returns:
            PreviewResult with render status and image data
        """
        try:
            # Generate output filename
            output_filename = f"{model_id}_preview.png"
            output_path = self.preview_dir / output_filename
            
            # Generate the complete render script
            render_script = self._generate_render_script(
                model_params, 
                str(output_path), 
                resolution,
                samples
            )
            
            # Execute the render script
            result = self.blender_executor.execute_script(render_script)
            
            if result.success and output_path.exists():
                # Read the image data
                with open(output_path, 'rb') as f:
                    image_data = f.read()
                
                return PreviewResult(
                    success=True,
                    image_path=str(output_path),
                    image_data=image_data,
                    width=resolution[0],
                    height=resolution[1]
                )
            else:
                error_msg = result.stderr or "Render failed for unknown reason"
                return PreviewResult(
                    success=False,
                    error_message=error_msg
                )
                
        except BlenderExecutionError as e:
            return PreviewResult(
                success=False,
                error_message=f"Blender execution error: {str(e)}"
            )
        except Exception as e:
            return PreviewResult(
                success=False,
                error_message=f"Preview render error: {str(e)}"
            )
    
    def _generate_render_script(
        self, 
        model_params: Dict[str, Any], 
        output_path: str,
        resolution: Tuple[int, int],
        samples: int
    ) -> str:
        """
        Generate complete Blender script for model creation and rendering.
        
        Args:
            model_params: Parameters for model generation
            output_path: Path where image should be saved
            resolution: Output resolution
            samples: Render samples
            
        Returns:
            Complete Blender Python script
        """
        # First, generate the model creation script
        object_type = model_params.get('object_type', 'cube')
        
        # Extract parameters
        size = model_params.get('size', 2.0)
        pos_x = model_params.get('pos_x', 0.0)
        position = (pos_x, 0, 0)
        
        # Extract rotation if present
        rotation = None
        if 'rotation' in model_params:
            rot = model_params['rotation']
            import math
            rotation = (
                math.radians(rot.get('x', 0)),
                math.radians(rot.get('y', 0)),
                math.radians(rot.get('z', 0))
            )
        elif any(k in model_params for k in ['rot_x', 'rot_y', 'rot_z']):
            import math
            rotation = (
                math.radians(model_params.get('rot_x', 0)),
                math.radians(model_params.get('rot_y', 0)),
                math.radians(model_params.get('rot_z', 0))
            )
        
        # Extract material if present
        material = None
        if any(k in model_params for k in ['color', 'metallic', 'roughness', 'emission']):
            material = {}
            for key in ['color', 'metallic', 'roughness', 'emission', 'emission_strength']:
                if key in model_params:
                    material[key] = model_params[key]
        
        # Generate object creation script based on type
        if object_type == 'cube':
            model_script = self.script_generator.generate_cube_script(
                size=size, position=position, rotation=rotation, material=material
            )
        elif object_type == 'sphere':
            model_script = self.script_generator.generate_sphere_script(
                radius=size, position=position, rotation=rotation, material=material
            )
        elif object_type == 'cylinder':
            model_script = self.script_generator.generate_cylinder_script(
                radius=size, depth=size*2, position=position, rotation=rotation, material=material
            )
        elif object_type == 'plane':
            model_script = self.script_generator.generate_plane_script(
                size=size, position=position, rotation=rotation, material=material
            )
        else:
            raise ValueError(f"Unsupported object type: {object_type}")
        
        # Add rendering setup and commands
        render_commands = f'''

# Set up rendering
import bpy
import math

# Set render engine to Cycles for better quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = {samples}
bpy.context.scene.cycles.use_denoising = True

# Set render resolution
bpy.context.scene.render.resolution_x = {resolution[0]}
bpy.context.scene.render.resolution_y = {resolution[1]}
bpy.context.scene.render.resolution_percentage = 100

# Set output format
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'
bpy.context.scene.render.film_transparent = True

# Add camera if not exists
if 'Camera' not in bpy.data.objects:
    bpy.ops.object.camera_add(location=(7, -7, 5))
    camera = bpy.context.object
    camera.rotation_euler = (1.1, 0, 0.785)
else:
    camera = bpy.data.objects['Camera']

# Point camera at the object
# Calculate distance based on object size
distance = max({size} * 4, 5)
angle = math.radians(45)
camera.location = (
    distance * math.cos(angle),
    -distance * math.sin(angle),
    distance * 0.7
)

# Add constraint to track object
if camera.constraints:
    camera.constraints.clear()

# Find the generated object to track
target_object = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.name != 'Camera':
        target_object = obj
        break

if target_object:
    bpy.ops.object.constraint_add(type='TRACK_TO')
    camera.constraints["Track To"].target = target_object
    camera.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    camera.constraints["Track To"].up_axis = 'UP_Y'

# Add lighting
# Remove existing lights
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Add key light
bpy.ops.object.light_add(type='AREA', location=(5, -5, 8))
key_light = bpy.context.object
key_light.data.energy = 500
key_light.data.size = 3
key_light.rotation_euler = (0.6, 0, 0.785)

# Add fill light
bpy.ops.object.light_add(type='AREA', location=(-5, -5, 3))
fill_light = bpy.context.object
fill_light.data.energy = 200
fill_light.data.size = 5
fill_light.rotation_euler = (1.2, 0, -0.785)

# Add rim light
bpy.ops.object.light_add(type='AREA', location=(0, 5, 2))
rim_light = bpy.context.object
rim_light.data.energy = 300
rim_light.data.size = 2

# Set world background to neutral gray
world = bpy.data.worlds["World"]
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (0.15, 0.15, 0.15, 1.0)
bg_node.inputs[1].default_value = 0.5

# Set camera as active
bpy.context.scene.camera = camera

# Render the image
bpy.context.scene.render.filepath = r'{output_path}'
bpy.ops.render.render(write_still=True)

print(f"Preview rendered successfully: {output_path}")
'''
        
        return model_script + render_commands
    
    def cleanup_old_previews(self, days: int = 1) -> int:
        """
        Remove old preview files.
        
        Args:
            days: Remove files older than this many days
            
        Returns:
            Number of files removed
        """
        import time
        
        count = 0
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for file_path in self.preview_dir.glob("*_preview.png"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    count += 1
                except Exception:
                    pass
        
        return count