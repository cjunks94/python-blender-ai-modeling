"""Export module for 3D model formats and scene exports."""

from .obj_exporter import OBJExporter, ExportResult, ExportError
from .stl_exporter import STLExporter  
from .gltf_exporter import GLTFExporter

# Try to import scene exporter (may not be available if dependencies missing)
try:
    from .scene_exporter import SceneExporter, SceneExportResult, SceneExportError
    SCENE_EXPORT_AVAILABLE = True
except ImportError:
    SceneExporter = None
    SceneExportResult = None
    SceneExportError = Exception
    SCENE_EXPORT_AVAILABLE = False

__all__ = [
    # Individual model exporters
    'OBJExporter',
    'STLExporter', 
    'GLTFExporter',
    'ExportResult',
    'ExportError',
    
    # Scene exporters (if available)
    'SceneExporter',
    'SceneExportResult',
    'SceneExportError',
    'SCENE_EXPORT_AVAILABLE'
]