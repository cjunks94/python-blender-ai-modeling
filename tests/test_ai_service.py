"""
Tests for the AI service business logic.

This module tests the AIService class and AI-powered generation functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web.services.ai_service import AIService, AIGenerationError


class TestAIService(unittest.TestCase):
    """Test cases for AI service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the dependency manager to avoid real service initialization
        with patch('web.services.ai_service.dependency_manager') as mock_dep:
            mock_dep.get_service.return_value = None
            self.ai_service = AIService()
    
    def test_ai_service_initialization(self):
        """Test AI service initialization."""
        self.assertIsInstance(self.ai_service, AIService)
    
    @patch('web.services.ai_service.dependency_manager')
    def test_generate_ai_model_service_unavailable(self, mock_dependency_manager):
        """Test AI model generation when AI service is unavailable."""
        mock_dependency_manager.is_available.return_value = False
        
        with self.assertRaises(AIGenerationError) as context:
            self.ai_service.generate_ai_model("Create a red cube")
        
        self.assertIn('AI integration not available', str(context.exception))
    
    @patch('web.services.ai_service.dependency_manager')
    @patch('web.services.ai_service.config')
    def test_generate_ai_model_success(self, mock_config, mock_dependency_manager):
        """Test successful AI model generation."""
        # Mock dependencies
        mock_dependency_manager.is_available.return_value = True
        mock_config.anthropic_api_key = 'test-api-key'
        
        # Mock AI services
        mock_client = MagicMock()
        mock_interpreter = MagicMock()
        mock_prompt_engineer = MagicMock()
        mock_validator = MagicMock()
        
        # Mock AI responses
        mock_prompt_engineer.create_model_prompt.return_value = "Create a red cube"
        mock_ai_response = MagicMock()
        mock_ai_response.success = True
        mock_ai_response.model_data = {
            'object_type': 'cube',
            'color': '#FF0000',
            'size': 2.0
        }
        mock_ai_response.content = '{"reasoning": "Generated a red cube", "suggestions": [], "warnings": []}'
        mock_client.generate_model_from_description.return_value = mock_ai_response
        mock_interpretation_result = MagicMock()
        mock_interpretation_result.success = True
        mock_interpretation_result.models = [{
            'object_type': 'cube',
            'color': '#FF0000',
            'size': 2.0,
            'pos_x': 0.0,
            'pos_y': 0.0,
            'pos_z': 0.0
        }]
        mock_interpreter.interpret_single_model.return_value = mock_interpretation_result
        mock_validator.validate_script.return_value = (True, [])
        
        mock_services = {
            'client_class': MagicMock(return_value=mock_client),
            'interpreter_class': MagicMock(return_value=mock_interpreter),
            'engineer_class': MagicMock(return_value=mock_prompt_engineer),
            'validator_class': MagicMock(return_value=mock_validator)
        }
        mock_dependency_manager.get_service.return_value = mock_services
        
        # Test generation
        result = self.ai_service.generate_ai_model({"description": "Create a red cube"})
        
        # Verify result structure
        self.assertTrue(result['success'])
        self.assertIn('id', result)
        self.assertEqual(result['object_type'], 'cube')
        self.assertIn('parameters', result)
        self.assertIn('ai_info', result)
        self.assertIn('created_at', result)
        
        # Verify AI services were called correctly
        mock_prompt_engineer.create_model_prompt.assert_called_once()
        mock_client.generate_model_from_description.assert_called_once()
        mock_interpreter.interpret_single_model.assert_called_once()
    
    def test_input_validation_description_required(self):
        """Test that description is required for AI generation."""
        with patch('web.services.ai_service.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = True
            
            # Empty description
            with self.assertRaises(AIGenerationError) as context:
                self.ai_service.generate_ai_model({"description": ""})
            self.assertIn('Description cannot be empty', str(context.exception))
            
            # Missing description
            with self.assertRaises(AIGenerationError) as context:
                self.ai_service.generate_ai_model({})
            self.assertIn('Missing required field: description', str(context.exception))
    
    def test_input_validation_description_length(self):
        """Test description length validation."""
        with patch('web.services.ai_service.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = True
            
            # Too long description
            long_description = "x" * 2001  # Over 2000 character limit
            with self.assertRaises(AIGenerationError) as context:
                self.ai_service.generate_ai_model({"description": long_description})
            self.assertIn('Description too long', str(context.exception))
    
    def test_input_validation_prohibited_content(self):
        """Test that prohibited content is blocked."""
        with patch('web.services.ai_service.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = True
            
            prohibited_inputs = [
                "import os",
                "exec(",
                "eval(",
                "__import__"
            ]
            
            for prohibited in prohibited_inputs:
                with self.assertRaises(AIGenerationError) as context:
                    self.ai_service.generate_ai_model({"description": f"Create a cube and {prohibited}"})
                self.assertIn('forbidden terms', str(context.exception))
    
    @patch('web.services.ai_service.dependency_manager')
    def test_generate_ai_scene_service_unavailable(self, mock_dependency_manager):
        """Test AI scene generation when AI service is unavailable."""
        mock_dependency_manager.is_available.return_value = False
        
        with self.assertRaises(AIGenerationError) as context:
            self.ai_service.generate_ai_scene({"description": "Create a living room", "max_objects": 3})
        
        self.assertIn('AI integration not available', str(context.exception))
    
    @patch('web.services.ai_service.dependency_manager')
    @patch('web.services.ai_service.config')
    def test_generate_ai_scene_success(self, mock_config, mock_dependency_manager):
        """Test successful AI scene generation."""
        # Mock dependencies
        mock_dependency_manager.is_available.return_value = True
        mock_config.anthropic_api_key = 'test-api-key'
        
        # Mock AI services
        mock_client = MagicMock()
        mock_interpreter = MagicMock()
        mock_prompt_engineer = MagicMock()
        mock_validator = MagicMock()
        
        # Mock AI responses
        mock_prompt_engineer.create_scene_prompt.return_value = "Create a living room with 3 objects"
        mock_scene_response = MagicMock()
        mock_scene_response.success = True
        mock_scene_response.model_data = {
            'scene_name': 'Living Room',
            'objects': [
                {'object_type': 'cube', 'ai_name': 'table'},
                {'object_type': 'cylinder', 'ai_name': 'lamp'},
                {'object_type': 'sphere', 'ai_name': 'decoration'}
            ]
        }
        mock_scene_response.content = '{"metadata": {}}'
        mock_client.generate_complex_scene.return_value = mock_scene_response
        mock_validator.validate_script.return_value = (True, [])
        
        # Mock scene management services
        mock_scene_manager = MagicMock()
        mock_scene = MagicMock()
        mock_scene.name = 'Living Room'
        mock_scene.object_count = 3
        mock_scene_manager.create_scene.return_value = mock_scene
        
        # Mock service dictionaries
        ai_services = {
            'client_class': MagicMock(return_value=mock_client),
            'interpreter_class': MagicMock(return_value=mock_interpreter),
            'engineer_class': MagicMock(return_value=mock_prompt_engineer),
            'validator_class': MagicMock(return_value=mock_validator)
        }
        
        scene_services = {
            'manager_class': MagicMock(return_value=mock_scene_manager)
        }
        
        def get_service_side_effect(service_name):
            if service_name == 'ai':
                return ai_services
            elif service_name == 'scene_management':
                return scene_services
            return None
            
        mock_dependency_manager.get_service.side_effect = get_service_side_effect
        
        # Test generation
        result = self.ai_service.generate_ai_scene({"description": "Create a living room", "max_objects": 3})
        
        # Verify result structure
        self.assertTrue(result['success'])
        self.assertIn('scene_id', result)
        self.assertEqual(result['name'], 'Living Room')
        self.assertEqual(result['object_count'], 3)
        self.assertIn('created_at', result)
        
        # Verify AI services were called correctly
        mock_prompt_engineer.create_scene_prompt.assert_called_once_with("Create a living room", 3, "medium")
        mock_client.generate_complex_scene.assert_called_once()
        # Scene manager should have been called
        mock_scene_manager.create_scene.assert_called_once()
    
    def test_scene_input_validation(self):
        """Test scene generation input validation."""
        with patch('web.services.ai_service.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = True
            
            # Max objects should be limited to 8
            result_data = self.ai_service.validate_ai_request(
                {"description": "Create a scene", "max_objects": 10}, 'scene'
            )
            # Should be capped at 8
            self.assertEqual(result_data['max_objects'], 8)
    
    @patch('web.services.ai_service.dependency_manager')
    @patch('web.services.ai_service.config')
    def test_ai_generation_error_handling(self, mock_config, mock_dependency_manager):
        """Test error handling during AI generation."""
        # Mock dependencies
        mock_dependency_manager.is_available.return_value = True
        mock_config.anthropic_api_key = 'test-api-key'
        
        # Mock AI services that raise exceptions
        mock_client = MagicMock()
        mock_client.generate_model_from_description.side_effect = Exception("API Error")
        
        mock_services = {
            'client_class': MagicMock(return_value=mock_client),
            'interpreter_class': MagicMock(),
            'engineer_class': MagicMock(),
            'validator_class': MagicMock()
        }
        mock_dependency_manager.get_service.return_value = mock_services
        
        # Test that AI errors are handled gracefully
        with self.assertRaises(AIGenerationError) as context:
            self.ai_service.generate_ai_model({"description": "Create a cube"})
        
        self.assertIn('AI generation failed', str(context.exception))
    
    def test_missing_api_key_handling(self):
        """Test handling of missing API key."""
        with patch('web.services.ai_service.dependency_manager') as mock_dep:
            with patch('web.services.ai_service.config') as mock_config:
                mock_dep.is_available.return_value = True
                mock_config.anthropic_api_key = None
                
                with self.assertRaises(AIGenerationError) as context:
                    self.ai_service.generate_ai_model({"description": "Create a cube"})
                
                self.assertIn('AI generation failed', str(context.exception))
    
    def test_parameter_validation_edge_cases(self):
        """Test parameter validation edge cases."""
        with patch('web.services.ai_service.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = True
            
            # Test whitespace-only description
            with self.assertRaises(AIGenerationError) as context:
                self.ai_service.generate_ai_model({"description": "   \n\t   "})
            self.assertIn('Description cannot be empty', str(context.exception))
            
            # Test valid boundary cases
            valid_description = "x" * 2000  # Exactly at limit
            validated = self.ai_service.validate_ai_request({"description": valid_description})
            self.assertEqual(validated['description'], valid_description)


if __name__ == '__main__':
    unittest.main()