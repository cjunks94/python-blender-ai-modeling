"""
Tests for the model service business logic.

This module tests the ModelService class and model generation functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web.services.model_service import ModelService, ModelGenerationError


class TestModelService(unittest.TestCase):
    """Test cases for model service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model_service = ModelService()
    
    def test_parameter_validation_success(self):
        """Test successful parameter validation."""
        valid_params = {
            'object_type': 'cube',
            'size': 2.0,
            'pos_x': 1.0,
            'pos_y': -1.0,
            'pos_z': 0.5,
            'rot_x': 45,
            'rot_y': -90,
            'rot_z': 180,
            'color': '#FF0000',
            'metallic': 0.8,
            'roughness': 0.3
        }
        
        validated = self.model_service.validate_model_parameters(valid_params)
        
        # Check all parameters are present and correctly typed
        self.assertEqual(validated['object_type'], 'cube')
        self.assertEqual(validated['size'], 2.0)
        self.assertEqual(validated['pos_x'], 1.0)
        self.assertEqual(validated['color'], '#FF0000')
        self.assertEqual(validated['metallic'], 0.8)
    
    def test_parameter_validation_with_defaults(self):
        """Test parameter validation with default values."""
        minimal_params = {'object_type': 'sphere'}
        
        validated = self.model_service.validate_model_parameters(minimal_params)
        
        # Check defaults are applied
        self.assertEqual(validated['object_type'], 'sphere')
        self.assertEqual(validated['size'], 2.0)
        self.assertEqual(validated['pos_x'], 0.0)
        self.assertEqual(validated['pos_y'], 0.0)
        self.assertEqual(validated['pos_z'], 0.0)
        self.assertEqual(validated['color'], '#0080FF')
        self.assertEqual(validated['metallic'], 0.0)
        self.assertEqual(validated['roughness'], 0.5)
    
    def test_parameter_validation_failures(self):
        """Test parameter validation error cases."""
        # Missing object_type
        with self.assertRaises(ModelGenerationError) as context:
            self.model_service.validate_model_parameters({})
        self.assertIn('Missing required parameter: object_type', str(context.exception))
        
        # Invalid object_type
        with self.assertRaises(ModelGenerationError) as context:
            self.model_service.validate_model_parameters({'object_type': 'invalid'})
        self.assertIn('Invalid object_type', str(context.exception))
        
        # Size out of range
        with self.assertRaises(ModelGenerationError) as context:
            self.model_service.validate_model_parameters({
                'object_type': 'cube',
                'size': 15.0  # Max is 10.0
            })
        self.assertIn('size must be between', str(context.exception))
        
        # Invalid color format
        with self.assertRaises(ModelGenerationError) as context:
            self.model_service.validate_model_parameters({
                'object_type': 'cube',
                'color': 'invalid-color'
            })
        self.assertIn('Color must be in hex format', str(context.exception))
    
    def test_numeric_parameter_validation(self):
        """Test numeric parameter validation edge cases."""
        # Test boundary values
        params = {
            'object_type': 'cube',
            'size': 0.1,  # Minimum
            'pos_x': -10.0,  # Minimum
            'pos_y': 10.0,  # Maximum
            'rot_x': -180,  # Minimum
            'rot_y': 180,  # Maximum
            'metallic': 0.0,  # Minimum
            'roughness': 1.0  # Maximum
        }
        
        # Should not raise exception
        validated = self.model_service.validate_model_parameters(params)
        self.assertEqual(validated['size'], 0.1)
        self.assertEqual(validated['pos_x'], -10.0)
        self.assertEqual(validated['metallic'], 0.0)
    
    def test_color_validation(self):
        """Test color parameter validation."""
        test_cases = [
            ('#FF0000', True),  # Valid red
            ('#00FF00', True),  # Valid green
            ('#0000FF', True),  # Valid blue
            ('#ffffff', True),  # Valid lowercase
            ('#123ABC', True),  # Valid mixed case
            ('FF0000', False),  # Missing #
            ('#FF00', False),   # Too short
            ('#FF000000', False),  # Too long
            ('#GGGGGG', False),  # Invalid hex
            ('not-a-color', False),  # Invalid format
        ]
        
        for color, should_be_valid in test_cases:
            params = {'object_type': 'cube', 'color': color}
            
            if should_be_valid:
                validated = self.model_service.validate_model_parameters(params)
                self.assertEqual(validated['color'], color)
            else:
                with self.assertRaises(ModelGenerationError):
                    self.model_service.validate_model_parameters(params)
    
    def test_emission_parameters(self):
        """Test emission parameter handling."""
        params = {
            'object_type': 'sphere',
            'emission': '#FFFF00',
            'emission_strength': 2.5
        }
        
        validated = self.model_service.validate_model_parameters(params)
        
        self.assertEqual(validated['emission'], '#FFFF00')
        self.assertEqual(validated['emission_strength'], 2.5)
        
        # Test emission without strength (should get default)
        params_no_strength = {
            'object_type': 'sphere',
            'emission': '#FFFF00'
        }
        
        validated = self.model_service.validate_model_parameters(params_no_strength)
        self.assertEqual(validated['emission_strength'], 1.0)
    
    @patch('web.services.model_service.dependency_manager')
    def test_generate_model_service_unavailable(self, mock_dependency_manager):
        """Test model generation when Blender service is unavailable."""
        mock_dependency_manager.is_available.return_value = False
        
        with self.assertRaises(ModelGenerationError) as context:
            self.model_service.generate_model({'object_type': 'cube'})
        
        self.assertIn('Blender integration not available', str(context.exception))
    
    @patch('web.services.model_service.dependency_manager')
    @patch('web.services.model_service.config')
    def test_generate_model_success(self, mock_config, mock_dependency_manager):
        """Test successful model generation."""
        # Mock dependencies
        mock_dependency_manager.is_available.return_value = True
        mock_config.flask_config = {
            'BLENDER_PATH': '/mock/blender',
            'BLENDER_TIMEOUT': 30
        }
        
        # Mock Blender services
        mock_executor = MagicMock()
        mock_generator = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.stdout = 'Success output'
        
        mock_executor.execute_script.return_value = mock_result
        mock_generator.generate_cube_script.return_value = 'mock_script'
        
        mock_services = {
            'executor_class': MagicMock(return_value=mock_executor),
            'generator_class': MagicMock(return_value=mock_generator)
        }
        mock_dependency_manager.get_service.return_value = mock_services
        
        # Test generation
        params = {'object_type': 'cube', 'size': 2.0}
        result = self.model_service.generate_model(params)
        
        # Verify result structure
        self.assertTrue(result['success'])
        self.assertIn('id', result)
        self.assertEqual(result['object_type'], 'cube')
        self.assertIn('parameters', result)
        self.assertIn('created_at', result)
        self.assertEqual(result['blender_output'], 'Success output')
        
        # Verify services were called correctly
        mock_generator.generate_cube_script.assert_called_once()
        mock_executor.execute_script.assert_called_once_with('mock_script')
    
    @patch('web.services.model_service.dependency_manager')
    def test_generate_preview_service_unavailable(self, mock_dependency_manager):
        """Test preview generation when Blender service is unavailable."""
        mock_dependency_manager.is_available.return_value = False
        
        result = self.model_service.generate_preview('test_id', {'object_type': 'cube'})
        
        self.assertIsNone(result)
    
    @patch('web.services.model_service.dependency_manager')
    def test_export_model_service_unavailable(self, mock_dependency_manager):
        """Test model export when export service is unavailable."""
        mock_dependency_manager.is_available.return_value = False
        
        with self.assertRaises(ModelGenerationError) as context:
            self.model_service.export_model('test_id', 'obj', {'object_type': 'cube'})
        
        self.assertIn('Export functionality not available', str(context.exception))
    
    def test_export_format_validation(self):
        """Test export format validation."""
        # Mock export service as available
        with patch('web.services.model_service.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = True
            
            # Test invalid format
            with self.assertRaises(ModelGenerationError) as context:
                self.model_service.export_model('test_id', 'invalid_format', {'object_type': 'cube'})
            
            self.assertIn('Invalid format', str(context.exception))


if __name__ == '__main__':
    unittest.main()