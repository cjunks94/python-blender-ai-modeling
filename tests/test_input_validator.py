"""
Tests for the comprehensive input validation and security system.

This module tests the InputValidator, ModelParameterValidator, and 
SceneParameterValidator classes for security and correctness.
"""

import unittest
from pathlib import Path
import tempfile
import os

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web.security import (
    InputValidator,
    ModelParameterValidator,
    SceneParameterValidator,
    ValidationError,
    SecurityError
)


class TestInputValidator(unittest.TestCase):
    """Test cases for the core InputValidator class."""
    
    def test_validate_string_success(self):
        """Test successful string validation."""
        result = InputValidator.validate_string("Hello World", "test_field")
        self.assertEqual(result, "Hello World")
        
        # Test with length constraints
        result = InputValidator.validate_string("Hi", "test", min_length=2, max_length=10)
        self.assertEqual(result, "Hi")
    
    def test_validate_string_failures(self):
        """Test string validation failures."""
        # None value
        with self.assertRaises(ValidationError):
            InputValidator.validate_string(None, "test")
        
        # Empty string when not allowed
        with self.assertRaises(ValidationError):
            InputValidator.validate_string("", "test", allow_empty=False)
        
        # Too short
        with self.assertRaises(ValidationError):
            InputValidator.validate_string("a", "test", min_length=2)
        
        # Too long
        with self.assertRaises(ValidationError):
            InputValidator.validate_string("a" * 100, "test", max_length=50)
    
    def test_security_pattern_detection(self):
        """Test detection of dangerous security patterns."""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "eval(malicious_code)",
            "exec(dangerous_script)",
            "__import__('os')",
            "subprocess.call(['rm', '-rf', '/'])",
            "../../../etc/passwd",
            "..\\..\\windows\\system32"
        ]
        
        for dangerous_input in dangerous_inputs:
            with self.assertRaises(SecurityError):
                InputValidator.validate_string(dangerous_input, "test_field")
    
    def test_validate_numeric_success(self):
        """Test successful numeric validation."""
        # Float validation
        result = InputValidator.validate_numeric(3.14, "test", min_value=0, max_value=10)
        self.assertEqual(result, 3.14)
        
        # Integer validation
        result = InputValidator.validate_numeric("5", "test", numeric_type=int)
        self.assertEqual(result, 5)
        
        # String to number conversion
        result = InputValidator.validate_numeric("2.5", "test")
        self.assertEqual(result, 2.5)
    
    def test_validate_numeric_failures(self):
        """Test numeric validation failures."""
        # None value
        with self.assertRaises(ValidationError):
            InputValidator.validate_numeric(None, "test")
        
        # Invalid format
        with self.assertRaises(ValidationError):
            InputValidator.validate_numeric("not_a_number", "test")
        
        # Below minimum
        with self.assertRaises(ValidationError):
            InputValidator.validate_numeric(5, "test", min_value=10)
        
        # Above maximum
        with self.assertRaises(ValidationError):
            InputValidator.validate_numeric(15, "test", max_value=10)
    
    def test_validate_boolean_success(self):
        """Test successful boolean validation."""
        # Native boolean
        self.assertTrue(InputValidator.validate_boolean(True, "test"))
        self.assertFalse(InputValidator.validate_boolean(False, "test"))
        
        # String representations
        self.assertTrue(InputValidator.validate_boolean("true", "test"))
        self.assertTrue(InputValidator.validate_boolean("TRUE", "test"))
        self.assertTrue(InputValidator.validate_boolean("1", "test"))
        self.assertTrue(InputValidator.validate_boolean("yes", "test"))
        
        self.assertFalse(InputValidator.validate_boolean("false", "test"))
        self.assertFalse(InputValidator.validate_boolean("0", "test"))
        self.assertFalse(InputValidator.validate_boolean("no", "test"))
    
    def test_validate_boolean_failures(self):
        """Test boolean validation failures."""
        with self.assertRaises(ValidationError):
            InputValidator.validate_boolean(None, "test")
        
        with self.assertRaises(ValidationError):
            InputValidator.validate_boolean("maybe", "test")
    
    def test_validate_enum_success(self):
        """Test successful enum validation."""
        allowed = ['red', 'green', 'blue']
        
        result = InputValidator.validate_enum('red', 'color', allowed)
        self.assertEqual(result, 'red')
        
        # Case insensitive
        result = InputValidator.validate_enum('RED', 'color', allowed, case_sensitive=False)
        self.assertEqual(result, 'red')
    
    def test_validate_enum_failures(self):
        """Test enum validation failures."""
        allowed = ['red', 'green', 'blue']
        
        with self.assertRaises(ValidationError):
            InputValidator.validate_enum('yellow', 'color', allowed)
        
        with self.assertRaises(ValidationError):
            InputValidator.validate_enum(None, 'color', allowed)
    
    def test_validate_color_success(self):
        """Test successful color validation."""
        valid_colors = ['#FF0000', '#00ff00', '#0000FF', '#123ABC']
        
        for color in valid_colors:
            result = InputValidator.validate_color(color, 'color')
            self.assertEqual(len(result), 7)
            self.assertTrue(result.startswith('#'))
            # Should be normalized to uppercase
            self.assertEqual(result, color.upper())
    
    def test_validate_color_failures(self):
        """Test color validation failures."""
        invalid_colors = [
            'FF0000',     # Missing #
            '#FF00',      # Too short
            '#FF000000',  # Too long
            '#GGGGGG',    # Invalid hex
            'red',        # Named color
            None
        ]
        
        for invalid_color in invalid_colors:
            with self.assertRaises(ValidationError):
                InputValidator.validate_color(invalid_color, 'color')
    
    def test_validate_file_path_success(self):
        """Test successful file path validation."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.obj', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Test relative path
            relative_path = tmp_path.name
            result = InputValidator.validate_file_path(relative_path, 'file', 'model')
            self.assertIsInstance(result, Path)
            
            # Test simple filename without absolute path
            result = InputValidator.validate_file_path('test_model.obj', 'file', 'model')
            self.assertIsInstance(result, Path)
        finally:
            tmp_path.unlink()
    
    def test_validate_file_path_failures(self):
        """Test file path validation failures."""
        # Path traversal attempts
        dangerous_paths = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32',
            '/absolute/path'
        ]
        
        for dangerous_path in dangerous_paths:
            with self.assertRaises(SecurityError):
                InputValidator.validate_file_path(dangerous_path, 'file')
        
        # Invalid extension
        with self.assertRaises(ValidationError):
            InputValidator.validate_file_path('test.exe', 'file', 'model')
        
        # Non-existent file when required
        with self.assertRaises(ValidationError):
            InputValidator.validate_file_path('nonexistent.obj', 'file', 'model', must_exist=True)
    
    def test_validate_url_success(self):
        """Test successful URL validation."""
        valid_urls = [
            'https://example.com',
            'http://localhost:8080',
            'https://api.example.com/v1/endpoint'
        ]
        
        for url in valid_urls:
            result = InputValidator.validate_url(url, 'url')
            self.assertEqual(result, url)
    
    def test_validate_url_failures(self):
        """Test URL validation failures."""
        invalid_urls = [
            'not-a-url',
            'ftp://invalid-scheme.com',  # Not in allowed schemes
            'javascript:alert(1)',       # Dangerous scheme
            'relative/path'
        ]
        
        for invalid_url in invalid_urls:
            with self.assertRaises((ValidationError, SecurityError)):
                InputValidator.validate_url(invalid_url, 'url')
    
    def test_validate_json_data_success(self):
        """Test successful JSON data validation."""
        valid_data = {
            'name': 'Test Object',
            'properties': {
                'size': 2.0,
                'color': 'red'
            },
            'tags': ['cube', 'basic']
        }
        
        result = InputValidator.validate_json_data(valid_data, 'data')
        self.assertEqual(result['name'], 'Test Object')
    
    def test_validate_json_data_failures(self):
        """Test JSON data validation failures."""
        # Not a dict
        with self.assertRaises(ValidationError):
            InputValidator.validate_json_data("not a dict", 'data')
        
        # Too deeply nested
        deep_data = {'level1': {'level2': {'level3': {'level4': {'level5': {}}}}}}
        with self.assertRaises(ValidationError):
            InputValidator.validate_json_data(deep_data, 'data', max_depth=3)
        
        # Missing required keys
        with self.assertRaises(ValidationError):
            InputValidator.validate_json_data({}, 'data', required_keys=['name'])
        
        # Dangerous content in values
        dangerous_data = {'script': '<script>alert("xss")</script>'}
        with self.assertRaises(SecurityError):
            InputValidator.validate_json_data(dangerous_data, 'data')
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ('normal_file.txt', 'normal_file.txt'),
            ('file with spaces.txt', 'file with spaces.txt'),
            ('file<>:|"?*.txt', 'file_______.txt'),
            ('file\x00\x01\x1f.txt', 'file.txt'),
            ('', 'file_20250729_132959'),  # Will contain timestamp
            ('a' * 300 + '.txt', 'a' * 251 + '.txt')  # Length limit
        ]
        
        for input_name, expected_pattern in test_cases[:-2]:  # Skip empty and long tests
            result = InputValidator.sanitize_filename(input_name)
            self.assertEqual(result, expected_pattern)
        
        # Test empty filename gets timestamp
        empty_result = InputValidator.sanitize_filename('')
        self.assertTrue(empty_result.startswith('file_'))
        
        # Test length limit
        long_result = InputValidator.sanitize_filename('a' * 300 + '.txt')
        self.assertLessEqual(len(long_result), 255)


class TestModelParameterValidator(unittest.TestCase):
    """Test cases for model parameter validation."""
    
    def test_validate_model_parameters_success(self):
        """Test successful model parameter validation."""
        valid_params = {
            'object_type': 'cube',
            'size': 2.5,
            'pos_x': 1.0,
            'pos_y': -1.0,
            'pos_z': 0.5,
            'rot_x': 45,
            'rot_y': -90,
            'rot_z': 180,
            'color': '#ff0000',
            'metallic': 0.8,
            'roughness': 0.3,
            'emission': '#ffff00',
            'emission_strength': 2.0
        }
        
        result = ModelParameterValidator.validate_model_parameters(valid_params)
        
        self.assertEqual(result['object_type'], 'cube')
        self.assertEqual(result['size'], 2.5)
        self.assertEqual(result['color'], '#FF0000')  # Normalized to uppercase
        self.assertEqual(result['emission'], '#FFFF00')
    
    def test_validate_model_parameters_with_defaults(self):
        """Test model parameter validation with defaults."""
        minimal_params = {'object_type': 'sphere'}
        
        result = ModelParameterValidator.validate_model_parameters(minimal_params)
        
        self.assertEqual(result['object_type'], 'sphere')
        self.assertEqual(result['size'], 2.0)  # Default
        self.assertEqual(result['pos_x'], 0.0)  # Default
        self.assertEqual(result['color'], '#0080FF')  # Default
    
    def test_validate_model_parameters_failures(self):
        """Test model parameter validation failures."""
        # Missing object_type
        with self.assertRaises(ValidationError):
            ModelParameterValidator.validate_model_parameters({})
        
        # Invalid object_type
        with self.assertRaises(ValidationError):
            ModelParameterValidator.validate_model_parameters({'object_type': 'invalid'})
        
        # Size out of range
        with self.assertRaises(ValidationError):
            ModelParameterValidator.validate_model_parameters({
                'object_type': 'cube',
                'size': 15.0  # Max is 10.0
            })
        
        # Invalid color
        with self.assertRaises(ValidationError):
            ModelParameterValidator.validate_model_parameters({
                'object_type': 'cube',
                'color': 'invalid'
            })
    
    def test_validate_export_parameters_success(self):
        """Test successful export parameter validation."""
        valid_params = {
            'format': 'obj',
            'filename': 'my_model.obj',
            'ascii': True
        }
        
        result = ModelParameterValidator.validate_export_parameters(valid_params)
        
        self.assertEqual(result['format'], 'obj')
        self.assertIn('filename', result)
    
    def test_validate_export_parameters_failures(self):
        """Test export parameter validation failures."""
        # Missing format
        with self.assertRaises(ValidationError):
            ModelParameterValidator.validate_export_parameters({})
        
        # Invalid format
        with self.assertRaises(ValidationError):
            ModelParameterValidator.validate_export_parameters({'format': 'invalid'})


class TestSceneParameterValidator(unittest.TestCase):
    """Test cases for scene parameter validation."""
    
    def test_validate_scene_parameters_success(self):
        """Test successful scene parameter validation."""
        valid_params = {
            'name': 'Test Scene',
            'description': 'A test scene for validation',
            'scene_id': 'test_scene_123'
        }
        
        result = SceneParameterValidator.validate_scene_parameters(valid_params)
        
        self.assertEqual(result['name'], 'Test Scene')
        self.assertEqual(result['description'], 'A test scene for validation')
        self.assertEqual(result['scene_id'], 'test_scene_123')
    
    def test_validate_scene_parameters_failures(self):
        """Test scene parameter validation failures."""
        # Missing name
        with self.assertRaises(ValidationError):
            SceneParameterValidator.validate_scene_parameters({'description': 'test'})
        
        # Missing description
        with self.assertRaises(ValidationError):
            SceneParameterValidator.validate_scene_parameters({'name': 'test'})
        
        # Invalid scene_id format
        with self.assertRaises(ValidationError):
            SceneParameterValidator.validate_scene_parameters({
                'name': 'test',
                'description': 'test',
                'scene_id': 'invalid scene id!'  # Contains spaces and special chars
            })
    
    def test_validate_composition_parameters_success(self):
        """Test successful composition parameter validation."""
        # Align operation
        align_params = {
            'operation': 'align',
            'axis': 'x',
            'mode': 'center'
        }
        result = SceneParameterValidator.validate_composition_parameters(align_params)
        self.assertEqual(result['operation'], 'align')
        self.assertEqual(result['axis'], 'x')
        self.assertEqual(result['mode'], 'center')
        
        # Distribute operation
        distribute_params = {
            'operation': 'distribute',
            'axis': 'y',
            'spacing': 2.5
        }
        result = SceneParameterValidator.validate_composition_parameters(distribute_params)
        self.assertEqual(result['operation'], 'distribute')
        self.assertEqual(result['spacing'], 2.5)
        
        # Arrange operation
        arrange_params = {
            'operation': 'arrange',
            'pattern': 'grid',
            'rows': 3,
            'columns': 4,
            'spacing': 1.5
        }
        result = SceneParameterValidator.validate_composition_parameters(arrange_params)
        self.assertEqual(result['pattern'], 'grid')
        self.assertEqual(result['rows'], 3)
        self.assertEqual(result['columns'], 4)
    
    def test_validate_composition_parameters_failures(self):
        """Test composition parameter validation failures."""
        # Missing operation
        with self.assertRaises(ValidationError):
            SceneParameterValidator.validate_composition_parameters({})
        
        # Invalid operation
        with self.assertRaises(ValidationError):
            SceneParameterValidator.validate_composition_parameters({'operation': 'invalid'})
        
        # Missing required parameters for align
        with self.assertRaises(ValidationError):
            SceneParameterValidator.validate_composition_parameters({'operation': 'align'})
        
        # Invalid axis
        with self.assertRaises(ValidationError):
            SceneParameterValidator.validate_composition_parameters({
                'operation': 'align',
                'axis': 'invalid',
                'mode': 'center'
            })


if __name__ == '__main__':
    unittest.main()