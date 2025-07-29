"""
STL export functionality for 3D models.

This module provides functionality to export 3D models to STL format
using Blender's export capabilities.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from blender_integration.executor import BlenderExecutor, BlenderExecutionError
from blender_integration.script_generator import ScriptGenerator, ScriptGenerationError


@dataclass
class STLExportResult:
    """Result of STL export operation."""
    success: bool
    model_id: str
    format: str
    output_file: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None


class ExportError(Exception):
    """Exception raised when export fails."""
    pass


class STLExporter:
    """Handles exporting 3D models to STL format."""
    
    def __init__(self, blender_path: str = 'blender', timeout: int = 60):
        """
        Initialize STLExporter.
        
        Args:
            blender_path: Path to Blender executable
            timeout: Timeout for export operations in seconds
        """
        self.blender_executor = BlenderExecutor(blender_path, timeout)
        self.script_generator = ScriptGenerator()
        self.output_dir = Path("exports")
        self.output_dir.mkdir(exist_ok=True)
    
    def export_stl(self, model_id: str, model_params: Dict[str, Any], 
                   ascii_format: bool = False) -> STLExportResult:
        """
        Export a model to STL format.
        
        Args:
            model_id: Unique identifier for the model
            model_params: Parameters used to generate the model
            ascii_format: If True, export as ASCII STL, otherwise binary
            
        Returns:
            STLExportResult with export status and details
        """
        try:
            # Validate parameters
            if not model_id:
                raise ExportError("Model ID is required")
            
            if not model_params:
                raise ExportError("Model parameters are required")
            
            # Generate output filename
            output_filename = f"{model_id}.stl"
            output_path = self.output_dir / output_filename
            
            # Generate the complete Blender script
            export_script = self._generate_export_script(model_params, str(output_path), ascii_format)
            
            # Execute the export script
            result = self.blender_executor.execute_script(export_script)
            
            if result.success and output_path.exists():
                file_size = output_path.stat().st_size
                
                return STLExportResult(
                    success=True,
                    model_id=model_id,
                    format='stl',
                    output_file=str(output_path),
                    file_size=file_size
                )
            else:
                error_msg = result.stderr or "Export failed for unknown reason"
                return STLExportResult(
                    success=False,
                    model_id=model_id,
                    format='stl',
                    error_message=error_msg
                )
                
        except BlenderExecutionError as e:
            return STLExportResult(
                success=False,
                model_id=model_id,
                format='stl',
                error_message=f"Blender execution error: {str(e)}"
            )
        except Exception as e:
            return STLExportResult(
                success=False,
                model_id=model_id,
                format='stl',
                error_message=f"Export error: {str(e)}"
            )
    
    def _generate_export_script(self, model_params: Dict[str, Any], 
                               output_path: str, ascii_format: bool) -> str:
        """
        Generate complete Blender script for model creation and STL export.
        
        Args:
            model_params: Parameters for model generation
            output_path: Path where STL file should be saved
            ascii_format: Whether to export as ASCII STL
            
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
        
        # Extract material if present (Note: STL doesn't support materials, but we still generate with them)
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
            raise ExportError(f"Unsupported object type: {object_type}")
        
        # Add STL export commands
        export_commands = f'''

# Export to STL
import bpy

# Select all mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

# Apply scale and rotation transforms before export
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Export to STL
try:
    # Try new Blender 4.5 syntax first
    bpy.ops.wm.stl_export(
        filepath=r'{output_path}',
        export_selected_objects=True,
        ascii_format={ascii_format},
        apply_modifiers=True
    )
    print(f"STL export successful: {output_path}")
except:
    # Fallback to legacy export for older Blender versions
    try:
        bpy.ops.export_mesh.stl(
            filepath=r'{output_path}',
            use_selection=True,
            ascii={ascii_format},
            apply_modifiers=True
        )
        print(f"STL export successful (legacy): {output_path}")
    except Exception as e:
        print(f"STL export failed: {{e}}")
        raise
'''
        
        return model_script + export_commands
    
    def cleanup_old_exports(self, days: int = 7) -> int:
        """
        Remove old export files.
        
        Args:
            days: Remove files older than this many days
            
        Returns:
            Number of files removed
        """
        import time
        
        count = 0
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for file_path in self.output_dir.glob("*.stl"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    count += 1
                except Exception:
                    pass
        
        return count