"""
OBJ exporter module for 3D models.

This module provides functionality to export generated 3D models to OBJ format
using Blender's export capabilities.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from blender_integration.executor import BlenderExecutor, BlenderExecutionError
from blender_integration.script_generator import ScriptGenerator, ScriptGenerationError


class ExportError(Exception):
    """Exception raised when export operations fail."""
    pass


@dataclass
class ExportResult:
    """Result of export operation."""
    success: bool
    model_id: str
    format: str
    output_file: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None


class OBJExporter:
    """Exports 3D models to OBJ format using Blender."""
    
    def __init__(self, output_dir: Optional[Path] = None, create_dir_if_missing: bool = True,
                 blender_path: str = 'blender', timeout: int = 30):
        """
        Initialize OBJExporter.
        
        Args:
            output_dir: Directory to save exported files. Defaults to ./exports
            create_dir_if_missing: Whether to create output directory if it doesn't exist
            blender_path: Path to Blender executable
            timeout: Maximum execution time in seconds
        """
        self.output_dir = output_dir or Path.cwd() / "exports"
        self.create_dir_if_missing = create_dir_if_missing
        self.blender_path = blender_path
        self.timeout = timeout
        self.blender_executor = BlenderExecutor(blender_path, timeout)
        self.script_generator = ScriptGenerator()
    
    def export_obj(self, model_id: str, model_params: Dict[str, Any]) -> ExportResult:
        """
        Export a 3D model to OBJ format.
        
        Args:
            model_id: Unique identifier for the model
            model_params: Parameters describing the model to create and export
            
        Returns:
            ExportResult with export details
            
        Raises:
            ExportError: If export fails
        """
        # Validate inputs
        if not model_id or model_id is None:
            raise ExportError("Model ID cannot be empty or None")
        
        self._validate_model_params(model_params)
        
        # Create output directory if needed
        if self.create_dir_if_missing:
            self._create_output_directory()
        
        # Build output file path
        output_file = self._build_output_filepath(model_id, "obj")
        
        # Generate Blender export script
        script_content = self._generate_export_script(model_params, str(output_file))
        
        # Execute Blender script
        try:
            result = self.blender_executor.execute_script(script_content)
            
            if not result.success:
                raise ExportError(f"Blender export failed: {result.stderr}")
            
            # Verify output file was created
            if not output_file.exists():
                raise ExportError(f"Export file was not created: {output_file}")
            
            # Get file size
            file_size = output_file.stat().st_size
            
            return ExportResult(
                success=True,
                model_id=model_id,
                format="obj",
                output_file=str(output_file),
                file_size=file_size
            )
            
        except BlenderExecutionError as e:
            raise ExportError(f"Blender execution error: {str(e)}")
    
    def _validate_model_params(self, model_params: Dict[str, Any]) -> None:
        """
        Validate model parameters.
        
        Args:
            model_params: Parameters to validate
            
        Raises:
            ExportError: If parameters are invalid
        """
        # Check required fields
        if 'object_type' not in model_params:
            raise ExportError("Missing required parameter: object_type")
        
        # Validate object type
        valid_types = ['cube', 'sphere', 'cylinder', 'plane']
        if model_params['object_type'] not in valid_types:
            raise ExportError(f"Unsupported object type: {model_params['object_type']}. "
                            f"Supported types: {valid_types}")
        
        # Check required parameters (size is required for all object types)
        if 'size' not in model_params:
            raise ExportError("Missing required parameter: size")
    
    def _generate_export_script(self, model_params: Dict[str, Any], output_file: str) -> str:
        """
        Generate complete Blender script for model creation and OBJ export.
        
        Args:
            model_params: Parameters for model generation
            output_file: Path where OBJ file should be saved
            
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
            raise ExportError(f"Unsupported object type: {object_type}")
        
        # Add OBJ export commands
        export_commands = f'''

# Export to OBJ
import bpy

# Select all mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

# Export to OBJ
try:
    bpy.ops.wm.obj_export(
        filepath=r'{output_file}',
        export_materials=True,
        export_selected_objects=True
    )
    print(f"OBJ export successful: {output_file}")
except (AttributeError, TypeError) as e:
    # Fallback to legacy export for older Blender versions or API changes
    print(f"Modern OBJ export failed ({e}), trying legacy method...")
    bpy.ops.export_scene.obj(
        filepath=r'{output_file}',
        use_selection=True,
        use_materials=True
    )
    print(f"OBJ export successful (legacy): {output_file}")
'''
        
        return model_script + export_commands
    
    def _build_output_filepath(self, model_id: str, format_ext: str) -> Path:
        """
        Build output file path.
        
        Args:
            model_id: Model identifier
            format_ext: File format extension
            
        Returns:
            Complete output file path
        """
        filename = f"{model_id}.{format_ext}"
        return self.output_dir / filename
    
    def _create_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)