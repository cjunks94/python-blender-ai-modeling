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
            result = self._execute_blender_script(script_content)
            
            if result.returncode != 0:
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
            
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            if isinstance(e, FileNotFoundError):
                raise ExportError(f"Blender executable not found: {self.blender_path}")
            elif isinstance(e, subprocess.TimeoutExpired):
                raise ExportError(f"Export timeout after {self.timeout} seconds")
            else:
                raise ExportError(f"Blender execution error: {e}")
    
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
        
        # Validate object type (currently only cube is supported)
        valid_types = ['cube']
        if model_params['object_type'] not in valid_types:
            raise ExportError(f"Unsupported object type: {model_params['object_type']}. "
                            f"Supported types: {valid_types}")
        
        # Check required parameters for cube
        if model_params['object_type'] == 'cube':
            required_params = ['size']
            for param in required_params:
                if param not in model_params:
                    raise ExportError(f"Missing required parameter for cube: {param}")
    
    def _generate_export_script(self, model_params: Dict[str, Any], output_file: str) -> str:
        """
        Generate Blender Python script for creating and exporting model.
        
        Args:
            model_params: Parameters describing the model
            output_file: Path where to save the exported file
            
        Returns:
            Complete Blender Python script as string
            
        Raises:
            ExportError: If object type is not supported
        """
        object_type = model_params['object_type']
        
        if object_type == 'cube':
            return self._generate_cube_export_script(model_params, output_file)
        else:
            raise ExportError(f"Export script generation not implemented for: {object_type}")
    
    def _generate_cube_export_script(self, model_params: Dict[str, Any], output_file: str) -> str:
        """Generate export script for cube object."""
        size = model_params['size']
        
        # Get position parameters with defaults
        pos_x = model_params.get('pos_x', 0)
        pos_y = model_params.get('pos_y', 0)
        pos_z = model_params.get('pos_z', 0)
        
        script_parts = [
            "import bpy",
            "",
            "# Clear existing objects",
            "bpy.ops.object.select_all(action='SELECT')",
            "bpy.ops.object.delete(use_global=False)",
            "",
            "# Create cube",
            f"bpy.ops.mesh.primitive_cube_add(size={size}, location=({pos_x}, {pos_y}, {pos_z}))",
            "",
            "# Export to OBJ",
            f'bpy.ops.export_scene.obj(filepath="{output_file}", use_selection=False)',
            "",
            'print("OBJ export completed successfully")'
        ]
        
        return "\n".join(script_parts)
    
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
    
    def _execute_blender_script(self, script_content: str) -> subprocess.CompletedProcess:
        """
        Execute Blender script via subprocess.
        
        Args:
            script_content: Python script to execute in Blender
            
        Returns:
            Subprocess result
            
        Raises:
            Various subprocess exceptions
        """
        # Create temporary script file
        fd, temp_path = tempfile.mkstemp(suffix='.py', prefix='export_script_')
        
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(script_content)
            
            # Build Blender command
            cmd = [
                self.blender_path,
                '--background',  # Run without UI
                '--python', temp_path
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False  # Don't raise exception on non-zero return code
            )
            
            return result
            
        finally:
            # Clean up temporary script file
            if os.path.exists(temp_path):
                os.unlink(temp_path)