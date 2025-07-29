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
        Validate AI generation request parameters.
        
        Args:
            data: Request data
            request_type: Type of request ('model' or 'scene')
            
        Returns:
            Validated parameters
            
        Raises:
            AIGenerationError: If parameters are invalid
        """
        if 'description' not in data:
            raise AIGenerationError('Missing required field: description')
        
        description = data['description'].strip()
        if not description:
            raise AIGenerationError('Description cannot be empty')
        
        # Basic security validation
        if len(description) > 2000:
            raise AIGenerationError('Description too long (max 2000 characters)')
        
        # Check for potentially harmful content
        forbidden_terms = ['script', 'import', 'exec', 'eval', '__']
        if any(term in description.lower() for term in forbidden_terms):
            raise AIGenerationError('Description contains forbidden terms')
        
        validated = {
            'description': description,
            'preferred_style': data.get('preferred_style', 'realistic'),
            'complexity': data.get('complexity', 'medium'),
            'user_level': data.get('user_level', 'beginner')
        }
        
        if request_type == 'scene':
            validated.update({
                'max_objects': min(int(data.get('max_objects', 5)), 8),  # Limit to 8 objects
                'generate_models': data.get('generate_models', True)
            })
        
        return validated
    
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
            ai_response = ai_client.generate_model(engineered_prompt)
            
            # Interpret and validate the response
            model_params = model_interpreter.interpret_response(ai_response)
            
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
                    'reasoning': ai_response.get('reasoning', ''),
                    'suggestions': ai_response.get('suggestions', []),
                    'warnings': ai_response.get('warnings', [])
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
            scene_response = ai_client.generate_scene(scene_prompt)
            
            # Validate scene safety
            if 'objects' in scene_response:
                for obj in scene_response['objects']:
                    if 'script' in obj:
                        is_safe, issues = script_validator.validate_script(obj['script'])
                        if not is_safe:
                            raise AIGenerationError(f"Scene object script failed validation: {issues}")
            
            # Create scene using scene manager
            scene_id = f"ai_scene_{uuid.uuid4().hex[:4]}"
            scene = scene_manager.create_scene(
                scene_id,
                validated_data['description'],
                scene_response.get('objects', [])
            )
            
            # Generate models if requested
            if validated_data['generate_models'] and self.blender_services:
                self._generate_scene_models(scene, scene_response.get('objects', []))
            
            return {
                'scene_id': scene_id,
                'name': scene.name,
                'object_count': scene.object_count,
                'ai_metadata': scene_response.get('metadata', {}),
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