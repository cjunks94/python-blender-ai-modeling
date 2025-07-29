"""
Scene Management Module

This module provides functionality for managing multi-object 3D scenes,
including scene composition, object relationships, coordinated operations,
and preview rendering.
"""

from .scene_models import Scene, SceneObject, ObjectRelationship, RelationshipType, SpatialConstraint
from .scene_manager import SceneManager
from .scene_validator import SceneValidator, ValidationResult, ValidationIssue, ValidationSeverity

# Try to import scene preview renderer (may not be available if dependencies missing)
try:
    from .scene_preview_renderer import ScenePreviewRenderer, ScenePreviewRenderError
    SCENE_PREVIEW_AVAILABLE = True
except ImportError:
    ScenePreviewRenderer = None
    ScenePreviewRenderError = Exception
    SCENE_PREVIEW_AVAILABLE = False

__all__ = [
    # Core models
    'Scene',
    'SceneObject', 
    'ObjectRelationship',
    'RelationshipType',
    'SpatialConstraint',
    
    # Management
    'SceneManager',
    
    # Validation
    'SceneValidator',
    'ValidationResult',
    'ValidationIssue', 
    'ValidationSeverity',
    
    # Preview rendering (if available)
    'ScenePreviewRenderer',
    'ScenePreviewRenderError',
    'SCENE_PREVIEW_AVAILABLE'
]