"""
AI service for handling AI-powered model and scene generation.

This service encapsulates the business logic for AI-powered 3D model creation
using natural language descriptions.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .dependency_manager import dependency_manager
from ..config import config
from ..security import InputValidator, ValidationError, SecurityError

logger = logging.getLogger(__name__)


class AIGenerationError(Exception):
    """Exception raised when AI generation fails."""
    pass


class AIService:
    """Service for handling AI-powered model and scene generation."""
    
    def __init__(self):
        """Initialize AI service with required dependencies."""
        self.ai_services = dependency_manager.get_service('ai')
        self.blender_services = dependency_manager.get_service('blender')
        self.scene_services = dependency_manager.get_service('scene_management')
        
        if not self.ai_services:
            logger.warning("AI service initialized without AI integration")
    
    def validate_ai_request(self, data: Dict[str, Any], request_type: str = 'model') -> Dict[str, Any]:
        """
        Validate AI generation request parameters using comprehensive security validation.
        
        Args:
            data: Request data
            request_type: Type of request ('model' or 'scene')
            
        Returns:
            Validated parameters
            
        Raises:
            AIGenerationError: If parameters are invalid
        """
        try:
            # Use comprehensive security validator
            validated = {}
            
            # Validate required description
            validated['description'] = InputValidator.validate_string(
                data.get('description'), 'description',
                max_length=InputValidator.MAX_DESCRIPTION_LENGTH,
                min_length=1
            )
            
            # Validate optional style parameters
            if 'preferred_style' in data:
                validated['preferred_style'] = InputValidator.validate_enum(
                    data['preferred_style'], 'preferred_style',
                    ['realistic', 'cartoon', 'abstract', 'minimalist', 'stylized'],
                    case_sensitive=False
                )
            else:
                validated['preferred_style'] = 'realistic'
            
            if 'complexity' in data:
                validated['complexity'] = InputValidator.validate_enum(
                    data['complexity'], 'complexity',
                    ['simple', 'medium', 'complex'],
                    case_sensitive=False
                )
            else:
                validated['complexity'] = 'medium'
            
            if 'user_level' in data:
                validated['user_level'] = InputValidator.validate_enum(
                    data['user_level'], 'user_level',
                    ['beginner', 'intermediate', 'advanced'],
                    case_sensitive=False
                )
            else:
                validated['user_level'] = 'beginner'
            
            # Scene-specific validation
            if request_type == 'scene':
                if 'max_objects' in data:
                    validated['max_objects'] = InputValidator.validate_numeric(
                        data['max_objects'], 'max_objects',
                        min_value=1, max_value=8, numeric_type=int
                    )
                else:
                    validated['max_objects'] = 5
                
                validated['generate_models'] = InputValidator.validate_boolean(
                    data.get('generate_models', True), 'generate_models'
                )
            
            return validated
            
        except (ValidationError, SecurityError) as e:
            logger.warning(f"AI request validation failed: {str(e)}")
            raise AIGenerationError(f"Invalid request: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected AI validation error: {str(e)}")
            raise AIGenerationError(f"Request validation failed: {str(e)}")
    
    def generate_ai_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a 3D model using AI from natural language description.
        
        Args:
            data: AI generation request data
            
        Returns:
            Generation result with model data
            
        Raises:
            AIGenerationError: If generation fails
        """
        if not dependency_manager.is_available('ai'):
            raise AIGenerationError('AI integration not available')
        
        # Validate parameters
        validated_data = self.validate_ai_request(data, 'model')
        
        try:
            # Initialize AI services
            client_class = self.ai_services['client_class']
            interpreter_class = self.ai_services['interpreter_class']
            engineer_class = self.ai_services['engineer_class']
            validator_class = self.ai_services['validator_class']
            
            ai_client = client_class()
            model_interpreter = interpreter_class()
            prompt_engineer = engineer_class()
            script_validator = validator_class()
            
            # Engineer the prompt
            engineered_prompt = prompt_engineer.create_model_prompt(
                validated_data['description'],
                validated_data['preferred_style'],
                validated_data['complexity'],
                validated_data['user_level']
            )
            
            # Get AI response
            ai_response = ai_client.generate_model_from_description(engineered_prompt)
            
            # Check if generation was successful
            if not ai_response.success:
                raise AIGenerationError(f"AI generation failed: {ai_response.error_message}")
            
            # Interpret and validate the response
            interpretation_result = model_interpreter.interpret_single_model(ai_response.model_data or {})
            
            if not interpretation_result.success or not interpretation_result.models:
                raise AIGenerationError(f"AI interpretation failed: {interpretation_result.error_message}")
            
            model_params = interpretation_result.models[0]  # Get first model
            
            # Validate the generated script would be safe
            if 'script' in model_params:
                is_safe, issues = script_validator.validate_script(model_params['script'])
                if not is_safe:
                    raise AIGenerationError(f"Generated script failed security validation: {issues}")
            
            # Generate unique model ID
            model_id = f"ai_{uuid.uuid4().hex[:8]}"
            
            result = {
                'id': model_id,
                'object_type': model_params.get('object_type', 'cube'),
                'parameters': model_params,
                'ai_info': {
                    'original_description': validated_data['description'],
                    'prompt_style': validated_data['preferred_style'],
                    'reasoning': getattr(ai_response, 'reasoning', ''),
                    'suggestions': getattr(ai_response, 'suggestions', []),
                    'warnings': getattr(ai_response, 'warnings', [])
                },
                'created_at': datetime.now().isoformat(),
                'success': True
            }
            
            logger.info(f"AI model generated successfully: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"AI model generation failed: {str(e)}")
            raise AIGenerationError(f"AI generation failed: {str(e)}")
    
    def generate_ai_scene(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a multi-object scene using AI.
        
        Args:
            data: Scene generation request data
            
        Returns:
            Scene generation result
            
        Raises:
            AIGenerationError: If generation fails
        """
        if not dependency_manager.is_available('ai'):
            raise AIGenerationError('AI integration not available')
        
        if not dependency_manager.is_available('scene_management'):
            raise AIGenerationError('Scene management not available')
        
        # Validate parameters
        validated_data = self.validate_ai_request(data, 'scene')
        
        try:
            # Initialize services
            client_class = self.ai_services['client_class']
            engineer_class = self.ai_services['engineer_class']
            validator_class = self.ai_services['validator_class']
            scene_manager_class = self.scene_services['manager_class']
            
            ai_client = client_class()
            prompt_engineer = engineer_class()
            script_validator = validator_class()
            scene_manager = scene_manager_class()
            
            # Create scene prompt
            scene_prompt = prompt_engineer.create_scene_prompt(
                validated_data['description'],
                validated_data['max_objects'],
                validated_data['complexity']
            )
            
            # Generate scene with AI
            scene_response = ai_client.generate_complex_scene(scene_prompt, validated_data['max_objects'])
            
            # Check if generation was successful
            if not scene_response.success:
                raise AIGenerationError(f"Scene generation failed: {scene_response.error_message}")
            
            # Get scene data from response
            scene_data = scene_response.model_data or {}
            objects_data = scene_data.get('objects', [])
            
            # Validate scene safety
            for obj in objects_data:
                if 'script' in obj:
                    is_safe, issues = script_validator.validate_script(obj['script'])
                    if not is_safe:
                        raise AIGenerationError(f"Scene object script failed validation: {issues}")
            
            # Create scene using scene manager
            scene_id = f"ai_scene_{uuid.uuid4().hex[:4]}"
            scene_name = scene_data.get('scene_name', validated_data['description'])
            scene = scene_manager.create_scene(scene_id, scene_name, validated_data['description'])
            
            # Generate models if requested
            if validated_data['generate_models'] and self.blender_services:
                self._generate_scene_models(scene, objects_data)
            
            return {
                'scene_id': scene_id,
                'name': scene.name,
                'object_count': scene.object_count,
                'ai_metadata': scene_data.get('metadata', {}),
                'success': True,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI scene generation failed: {str(e)}")
            raise AIGenerationError(f"Scene generation failed: {str(e)}")
    
    def _generate_scene_models(self, scene, ai_objects: list) -> None:
        """Generate Blender models for AI-generated scene objects."""
        if not self.blender_services:
            logger.warning("Skipping model generation - Blender not available")
            return
        
        try:
            executor_class = self.blender_services['executor_class']
            generator_class = self.blender_services['generator_class']
            
            executor = executor_class(
                blender_path=config.flask_config['BLENDER_PATH'],
                timeout=config.flask_config['BLENDER_TIMEOUT']
            )
            generator = generator_class(clear_scene=True)
            
            for obj in scene.objects:
                try:
                    # Generate script for this object
                    script = self._generate_object_script(generator, obj.parameters)
                    
                    # Execute script
                    result = executor.execute_script(script)
                    if result.success:
                        logger.info(f"Generated model for scene object: {obj.id}")
                    else:
                        logger.warning(f"Failed to generate model for {obj.id}: {result.stderr}")
                        
                except Exception as e:
                    logger.error(f"Error generating model for scene object {obj.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in scene model generation: {str(e)}")
    
    def _generate_object_script(self, generator, params: Dict[str, Any]) -> str:
        """Generate Blender script for an object."""
        object_type = params.get('object_type', 'cube')
        
        if object_type == 'cube':
            return generator.generate_cube_script(**params)
        elif object_type == 'sphere':
            return generator.generate_sphere_script(**params)
        elif object_type == 'cylinder':
            return generator.generate_cylinder_script(**params)
        elif object_type == 'plane':
            return generator.generate_plane_script(**params)
        else:
            raise AIGenerationError(f"Unsupported object type: {object_type}")


# Global AI service instance
ai_service = AIService()