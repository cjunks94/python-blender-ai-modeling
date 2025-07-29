"""
Scene Export Module for multi-object scenes.

This module provides functionality to export individual objects, selective objects,
or complete scenes from multi-object Scene instances to various 3D formats.
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

# Import scene management components
try:
    from scene_management import Scene, SceneObject
    SCENE_MANAGEMENT_AVAILABLE = True
except ImportError:
    SCENE_MANAGEMENT_AVAILABLE = False
    Scene = None
    SceneObject = None

# Import existing export functionality
from .obj_exporter import OBJExporter, ExportResult, ExportError
from .stl_exporter import STLExporter
from .gltf_exporter import GLTFExporter

# Import script generation
from blender_integration.script_generator import ScriptGenerator
from blender_integration.executor import BlenderExecutor

logger = logging.getLogger(__name__)


@dataclass
class SceneExportResult:
    """Result of scene export operation."""
    success: bool
    scene_id: str
    export_type: str  # 'individual', 'selective', 'complete'
    format: str
    exported_objects: List[str]  # Object IDs that were exported
    output_files: List[str]  # Paths to exported files
    total_file_size: int = 0
    error_message: Optional[str] = None
    export_timestamp: datetime = None
    
    def __post_init__(self):
        if self.export_timestamp is None:
            self.export_timestamp = datetime.now()


class SceneExportError(Exception):
    """Exception raised when scene export operations fail."""
    pass


class SceneExporter:
    """Exports individual objects, selective objects, or complete scenes to various formats."""
    
    def __init__(self, output_dir: Optional[Path] = None, 
                 blender_path: str = 'blender', timeout: int = 60):
        """
        Initialize SceneExporter.
        
        Args:
            output_dir: Directory to save exported files
            blender_path: Path to Blender executable
            timeout: Maximum execution time in seconds
        """
        if not SCENE_MANAGEMENT_AVAILABLE:
            raise SceneExportError("Scene management not available - missing dependencies")
        
        self.output_dir = output_dir or Path.cwd() / "scene_exports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize format-specific exporters
        self.obj_exporter = OBJExporter(self.output_dir, blender_path=blender_path, timeout=timeout)
        self.stl_exporter = STLExporter(self.output_dir, blender_path=blender_path, timeout=timeout)
        self.gltf_exporter = GLTFExporter(self.output_dir, blender_path=blender_path, timeout=timeout)
        
        # Initialize script generation
        self.script_generator = ScriptGenerator(clear_scene=True)
        self.blender_executor = BlenderExecutor(blender_path, timeout)
        
        logger.info(f"SceneExporter initialized with output directory: {self.output_dir}")
    
    def export_individual_object(self, scene_object: SceneObject, scene_context: Optional[Scene] = None,
                                format: str = 'obj', custom_filename: Optional[str] = None) -> SceneExportResult:
        """
        Export a single object from a scene.
        
        Args:
            scene_object: Object to export
            scene_context: Optional scene for context (lighting, materials)
            format: Export format ('obj', 'stl', 'gltf')
            custom_filename: Optional custom filename (without extension)
            
        Returns:
            SceneExportResult with export details
        """
        try:
            logger.info(f"Exporting individual object: {scene_object.name} ({format.upper()})")
            
            # Build filename
            if custom_filename:
                filename = custom_filename
            else:
                scene_prefix = f"{scene_context.scene_id}_" if scene_context else ""
                filename = f"{scene_prefix}{scene_object.id}_{scene_object.name}"
            
            # Sanitize filename
            filename = self._sanitize_filename(filename)
            
            # Create object export directory
            object_export_dir = self.output_dir / "individual_objects"
            object_export_dir.mkdir(exist_ok=True)
            
            # Generate export script
            export_script = self._generate_individual_object_export_script(
                scene_object, scene_context, format, object_export_dir / f"{filename}.{format}"
            )
            
            # Execute export
            result = self.blender_executor.execute_script(export_script)
            
            if not result.success:
                raise SceneExportError(f"Export execution failed: {result.stderr}")
            
            # Verify output file
            output_file = object_export_dir / f"{filename}.{format}"
            if not output_file.exists():
                raise SceneExportError(f"Export file was not created: {output_file}")
            
            file_size = output_file.stat().st_size
            
            return SceneExportResult(
                success=True,
                scene_id=scene_context.scene_id if scene_context else "no_scene",
                export_type="individual",
                format=format,
                exported_objects=[scene_object.id],
                output_files=[str(output_file)],
                total_file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Individual object export failed: {str(e)}")
            return SceneExportResult(
                success=False,
                scene_id=scene_context.scene_id if scene_context else "no_scene",
                export_type="individual",
                format=format,
                exported_objects=[],
                output_files=[],
                error_message=str(e)
            )
    
    def export_selective_objects(self, object_ids: List[str], scene: Scene,
                               format: str = 'obj', combined_file: bool = True,
                               custom_filename: Optional[str] = None) -> SceneExportResult:
        """
        Export selected objects from a scene.
        
        Args:
            object_ids: List of object IDs to export
            scene: Scene containing the objects
            format: Export format ('obj', 'stl', 'gltf')
            combined_file: If True, export as single file; if False, separate files
            custom_filename: Optional custom filename for combined export
            
        Returns:
            SceneExportResult with export details
        """
        try:
            logger.info(f"Exporting {len(object_ids)} selective objects from scene: {scene.name}")
            
            # Validate object IDs
            selected_objects = []
            for obj_id in object_ids:
                obj = scene.get_object_by_id(obj_id)
                if obj:
                    selected_objects.append(obj)
                else:
                    logger.warning(f"Object not found in scene: {obj_id}")
            
            if not selected_objects:
                raise SceneExportError("No valid objects found for selective export")
            
            # Create selective export directory
            selective_export_dir = self.output_dir / "selective_objects"
            selective_export_dir.mkdir(exist_ok=True)
            
            exported_files = []
            total_size = 0
            
            if combined_file:
                # Export as single combined file
                filename = custom_filename or f"{scene.scene_id}_selective_{len(selected_objects)}objects"
                filename = self._sanitize_filename(filename)
                
                export_script = self._generate_selective_objects_export_script(
                    selected_objects, scene, format, selective_export_dir / f"{filename}.{format}"
                )
                
                result = self.blender_executor.execute_script(export_script)
                
                if not result.success:
                    raise SceneExportError(f"Selective export execution failed: {result.stderr}")
                
                output_file = selective_export_dir / f"{filename}.{format}"
                if output_file.exists():
                    exported_files.append(str(output_file))
                    total_size += output_file.stat().st_size
                
            else:
                # Export as separate files
                for obj in selected_objects:
                    filename = f"{scene.scene_id}_{obj.id}_{obj.name}"
                    filename = self._sanitize_filename(filename)
                    
                    export_script = self._generate_individual_object_export_script(
                        obj, scene, format, selective_export_dir / f"{filename}.{format}"
                    )
                    
                    result = self.blender_executor.execute_script(export_script)
                    
                    if result.success:
                        output_file = selective_export_dir / f"{filename}.{format}"
                        if output_file.exists():
                            exported_files.append(str(output_file))
                            total_size += output_file.stat().st_size
                    else:
                        logger.warning(f"Failed to export object {obj.name}: {result.stderr}")
            
            if not exported_files:
                raise SceneExportError("No files were successfully exported")
            
            return SceneExportResult(
                success=True,
                scene_id=scene.scene_id,
                export_type="selective",
                format=format,
                exported_objects=[obj.id for obj in selected_objects],
                output_files=exported_files,
                total_file_size=total_size
            )
            
        except Exception as e:
            logger.error(f"Selective objects export failed: {str(e)}")
            return SceneExportResult(
                success=False,
                scene_id=scene.scene_id,
                export_type="selective",
                format=format,
                exported_objects=[],
                output_files=[],
                error_message=str(e)
            )
    
    def export_complete_scene(self, scene: Scene, format: str = 'obj',
                            custom_filename: Optional[str] = None) -> SceneExportResult:
        """
        Export complete scene with all objects.
        
        Args:
            scene: Scene to export
            format: Export format ('obj', 'stl', 'gltf')
            custom_filename: Optional custom filename
            
        Returns:
            SceneExportResult with export details
        """
        try:
            logger.info(f"Exporting complete scene: {scene.name} with {scene.object_count} objects")
            
            if scene.object_count == 0:
                raise SceneExportError("Cannot export empty scene")
            
            # Create complete scene export directory
            scene_export_dir = self.output_dir / "complete_scenes"
            scene_export_dir.mkdir(exist_ok=True)
            
            # Build filename
            filename = custom_filename or f"{scene.scene_id}_{scene.name}_complete"
            filename = self._sanitize_filename(filename)
            
            # Generate complete scene export script
            export_script = self._generate_complete_scene_export_script(
                scene, format, scene_export_dir / f"{filename}.{format}"
            )
            
            # Execute export
            result = self.blender_executor.execute_script(export_script)
            
            if not result.success:
                raise SceneExportError(f"Complete scene export execution failed: {result.stderr}")
            
            # Verify output file
            output_file = scene_export_dir / f"{filename}.{format}"
            if not output_file.exists():
                raise SceneExportError(f"Scene export file was not created: {output_file}")
            
            file_size = output_file.stat().st_size
            
            return SceneExportResult(
                success=True,
                scene_id=scene.scene_id,
                export_type="complete",
                format=format,
                exported_objects=[obj.id for obj in scene.objects],
                output_files=[str(output_file)],
                total_file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Complete scene export failed: {str(e)}")
            return SceneExportResult(
                success=False,
                scene_id=scene.scene_id,
                export_type="complete",
                format=format,
                exported_objects=[],
                output_files=[],
                error_message=str(e)
            )
    
    def export_scene_formats(self, scene: Scene, formats: List[str] = ['obj', 'stl', 'gltf'],
                           export_type: str = 'complete') -> List[SceneExportResult]:
        """
        Export scene in multiple formats.
        
        Args:
            scene: Scene to export
            formats: List of formats to export
            export_type: Type of export ('complete', 'individual_all')
            
        Returns:
            List of SceneExportResult for each format
        """
        results = []
        
        for format in formats:
            try:
                if export_type == 'complete':
                    result = self.export_complete_scene(scene, format)
                elif export_type == 'individual_all':
                    # Export all objects individually
                    for obj in scene.objects:
                        result = self.export_individual_object(obj, scene, format)
                        results.append(result)
                    continue
                else:
                    raise SceneExportError(f"Unsupported export type: {export_type}")
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Multi-format export failed for format {format}: {str(e)}")
                results.append(SceneExportResult(
                    success=False,
                    scene_id=scene.scene_id,
                    export_type=export_type,
                    format=format,
                    exported_objects=[],
                    output_files=[],
                    error_message=str(e)
                ))
        
        return results
    
    def _generate_individual_object_export_script(self, scene_object: SceneObject, 
                                                scene_context: Optional[Scene],
                                                format: str, output_file: Path) -> str:
        """Generate Blender script for individual object export."""
        
        # Generate object creation script with scene context
        object_script = self.script_generator.generate_individual_object_script(
            scene_object, scene_context
        )
        
        # Add format-specific export commands
        export_commands = self._get_format_export_commands(format, str(output_file))
        
        return object_script + export_commands
    
    def _generate_selective_objects_export_script(self, selected_objects: List[SceneObject],
                                                scene: Scene, format: str, output_file: Path) -> str:
        """Generate Blender script for selective objects export."""
        
        # Generate selective objects script
        object_ids = [obj.id for obj in selected_objects]
        selective_script = self.script_generator.generate_selective_objects_script(object_ids, scene)
        
        # Add format-specific export commands
        export_commands = self._get_format_export_commands(format, str(output_file))
        
        return selective_script + export_commands
    
    def _generate_complete_scene_export_script(self, scene: Scene, format: str, output_file: Path) -> str:
        """Generate Blender script for complete scene export."""
        
        # Generate complete scene script
        scene_script = self.script_generator.generate_scene_script(scene)
        
        # Add format-specific export commands
        export_commands = self._get_format_export_commands(format, str(output_file))
        
        return scene_script + export_commands
    
    def _get_format_export_commands(self, format: str, output_file: str) -> str:
        """Get export commands for specific format."""
        
        format = format.lower()
        
        if format == 'obj':
            return f'''

# Export to OBJ format
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
except:
    # Fallback to legacy export for older Blender versions
    bpy.ops.export_scene.obj(
        filepath=r'{output_file}',
        use_selection=True,
        use_materials=True
    )
    print(f"OBJ export successful (legacy): {output_file}")
'''
        
        elif format == 'stl':
            return f'''

# Export to STL format
import bpy

# Select all mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)

# Export to STL
bpy.ops.export_mesh.stl(
    filepath=r'{output_file}',
    use_selection=True
)
print(f"STL export successful: {output_file}")
'''
        
        elif format == 'gltf':
            return f'''

# Export to GLTF format
import bpy

# Select all mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)

# Export to GLTF
bpy.ops.export_scene.gltf(
    filepath=r'{output_file}',
    use_selection=True,
    export_materials='EXPORT'
)
print(f"GLTF export successful: {output_file}")
'''
        
        else:
            raise SceneExportError(f"Unsupported export format: {format}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove multiple consecutive underscores
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        
        # Ensure filename isn't empty
        if not filename:
            filename = "exported_object"
        
        return filename
    
    def list_exports(self, scene_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all exported files, optionally filtered by scene ID.
        
        Args:
            scene_id: Optional scene ID to filter exports
            
        Returns:
            List of export information dictionaries
        """
        exports = []
        
        for export_dir in self.output_dir.iterdir():
            if export_dir.is_dir():
                for export_file in export_dir.glob('*'):
                    if export_file.is_file():
                        # Extract scene ID from filename if possible
                        file_scene_id = export_file.stem.split('_')[0] if '_' in export_file.stem else None
                        
                        if scene_id is None or file_scene_id == scene_id:
                            exports.append({
                                'filename': export_file.name,
                                'path': str(export_file),
                                'size': export_file.stat().st_size,
                                'format': export_file.suffix.lstrip('.'),
                                'export_type': export_dir.name,
                                'scene_id': file_scene_id,
                                'created': datetime.fromtimestamp(export_file.stat().st_ctime)
                            })
        
        return sorted(exports, key=lambda x: x['created'], reverse=True)