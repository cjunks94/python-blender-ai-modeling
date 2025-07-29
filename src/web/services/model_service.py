"""
Model service for handling 3D model generation business logic.

This service encapsulates the business logic for generating, previewing,
and exporting 3D models using Blender integration.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from .dependency_manager import dependency_manager
from ..config import config
from ..security import ModelParameterValidator, ValidationError, SecurityError

logger = logging.getLogger(__name__)


class ModelGenerationError(Exception):
    """Exception raised when model generation fails."""
    pass


class ModelService:
    """Service for handling 3D model operations."""
    
    def __init__(self):
        """Initialize model service with required dependencies."""
        self.blender_services = dependency_manager.get_service('blender')
        self.export_services = dependency_manager.get_service('export')
        
        if not self.blender_services:
            logger.warning("Model service initialized without Blender integration")
    
    def validate_model_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize model parameters using comprehensive security validation.
        
        Args:
            params: Raw model parameters from request
            
        Returns:
            Validated and sanitized parameters
            
        Raises:
            ModelGenerationError: If parameters are invalid
        """
        try:
            # Use the comprehensive security validator
            return ModelParameterValidator.validate_model_parameters(params)
        except (ValidationError, SecurityError) as e:
            logger.warning(f"Model parameter validation failed: {str(e)}")
            raise ModelGenerationError(f"Invalid parameters: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            raise ModelGenerationError(f"Parameter validation failed: {str(e)}")
    
    
    def generate_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a 3D model with the given parameters.
        
        Args:
            params: Model generation parameters
            
        Returns:
            Generation result with model ID and metadata
            
        Raises:
            ModelGenerationError: If generation fails
        """
        if not dependency_manager.is_available('blender'):
            raise ModelGenerationError("Blender integration not available")
        
        # Validate parameters
        validated_params = self.validate_model_parameters(params)
        
        # Generate unique model ID
        model_id = f"{validated_params['object_type']}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Initialize Blender services
            executor_class = self.blender_services['executor_class']
            generator_class = self.blender_services['generator_class']
            
            executor = executor_class(
                blender_path=config.flask_config['BLENDER_PATH'],
                timeout=config.flask_config['BLENDER_TIMEOUT']
            )
            generator = generator_class(clear_scene=True)
            
            # Generate Blender script
            script = self._generate_object_script(generator, validated_params)
            
            # Execute script
            result = executor.execute_script(script)
            
            if not result.success:
                raise ModelGenerationError(f"Blender execution failed: {result.stderr}")
            
            return {
                'id': model_id,
                'object_type': validated_params['object_type'],
                'parameters': validated_params,
                'created_at': datetime.now().isoformat(),
                'blender_output': result.stdout,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Model generation failed for {model_id}: {str(e)}")
            raise ModelGenerationError(f"Failed to generate model: {str(e)}")
    
    def _generate_object_script(self, generator, params: Dict[str, Any]) -> str:
        """Generate Blender script for the specified object type."""
        object_type = params['object_type']
        
        try:
            if object_type == 'cube':
                return generator.generate_cube_script(**params)
            elif object_type == 'sphere':
                return generator.generate_sphere_script(**params)
            elif object_type == 'cylinder':
                return generator.generate_cylinder_script(**params)
            elif object_type == 'plane':
                return generator.generate_plane_script(**params)
            else:
                raise ModelGenerationError(f"Unsupported object type: {object_type}")
                
        except Exception as e:
            raise ModelGenerationError(f"Script generation failed: {str(e)}")
    
    def generate_preview(self, model_id: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Generate a preview image for the model.
        
        Args:
            model_id: Unique model identifier
            params: Model parameters
            
        Returns:
            Path to preview image file or None if generation failed
        """
        if not dependency_manager.is_available('blender'):
            logger.warning("Preview generation skipped - Blender not available")
            return None
        
        try:
            renderer_class = self.blender_services['renderer_class']
            renderer = renderer_class(
                blender_path=config.flask_config['BLENDER_PATH'],
                timeout=config.flask_config['BLENDER_TIMEOUT']
            )
            
            # Override preview directory to use absolute path
            renderer.preview_dir = config.preview_dir
            renderer.preview_dir.mkdir(exist_ok=True)
            
            # Generate preview
            preview_path = renderer.generate_preview(model_id, params)
            
            if preview_path and Path(preview_path).exists():
                logger.info(f"Preview generated successfully: {preview_path}")
                return preview_path
            else:
                logger.warning(f"Preview generation failed for model {model_id}")
                return None
                
        except Exception as e:
            logger.error(f"Preview generation error for {model_id}: {str(e)}")
            return None
    
    def export_model(self, model_id: str, format: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export a model to the specified format.
        
        Args:
            model_id: Unique model identifier
            format: Export format (obj, gltf, stl)
            params: Model parameters
            
        Returns:
            Export result with file path and metadata
            
        Raises:
            ModelGenerationError: If export fails
        """
        if not dependency_manager.is_available('export'):
            raise ModelGenerationError("Export functionality not available")
        
        # Validate export parameters using security validator
        try:
            export_params = ModelParameterValidator.validate_export_parameters({
                'format': format
            })
            format = export_params['format']
        except (ValidationError, SecurityError) as e:
            raise ModelGenerationError(f"Invalid export parameters: {str(e)}")
        
        try:
            # Get appropriate exporter
            if format == 'obj':
                exporter_class = self.export_services['obj_exporter']
            elif format in ['gltf', 'glb']:
                exporter_class = self.export_services['gltf_exporter']
            elif format == 'stl':
                exporter_class = self.export_services['stl_exporter']
            
            # Initialize exporter
            exporter = exporter_class(
                output_dir=config.export_dir,
                blender_path=config.flask_config['BLENDER_PATH'],
                timeout=config.flask_config['BLENDER_TIMEOUT']
            )
            
            # Export model
            result = exporter.export_model(model_id, params)
            
            if result.success:
                return {
                    'success': True,
                    'model_id': model_id,
                    'format': format,
                    'output_file': result.output_file,
                    'file_size': result.file_size
                }
            else:
                raise ModelGenerationError(f"Export failed: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Export failed for {model_id}: {str(e)}")
            raise ModelGenerationError(f"Export failed: {str(e)}")


# Global model service instance
model_service = ModelService()