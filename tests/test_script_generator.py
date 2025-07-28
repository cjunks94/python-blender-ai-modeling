"""Tests for Blender script generation."""

import unittest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestScriptGenerator(unittest.TestCase):
    """Test cases for ScriptGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from blender_integration.script_generator import ScriptGenerator
        self.generator = ScriptGenerator()
    
    def test_init_default_settings(self):
        """Test ScriptGenerator initializes with default settings."""
        self.assertTrue(self.generator.clear_scene)
        self.assertEqual(self.generator.origin, (0, 0, 0))
    
    def test_init_custom_settings(self):
        """Test ScriptGenerator initializes with custom settings."""
        from blender_integration.script_generator import ScriptGenerator
        
        generator = ScriptGenerator(clear_scene=False, origin=(1, 2, 3))
        
        self.assertFalse(generator.clear_scene)
        self.assertEqual(generator.origin, (1, 2, 3))
    
    def test_generate_cube_script_basic(self):
        """Test basic cube script generation."""
        script = self.generator.generate_cube_script(size=2.0)
        
        # Verify script contains expected components
        self.assertIn('import bpy', script)
        self.assertIn('primitive_cube_add', script)
        self.assertIn('size=2.0', script)
        self.assertIn('location=(0, 0, 0)', script)  # Default origin
    
    def test_generate_cube_script_with_position(self):
        """Test cube script generation with custom position."""
        script = self.generator.generate_cube_script(
            size=1.5, 
            position=(2.0, -1.0, 0.5)
        )
        
        self.assertIn('size=1.5', script)
        self.assertIn('location=(2.0, -1.0, 0.5)', script)
    
    def test_generate_cube_script_with_rotation(self):
        """Test cube script generation with rotation."""
        script = self.generator.generate_cube_script(
            size=1.0,
            rotation=(0.0, 0.0, 1.57)  # 90 degrees in radians
        )
        
        self.assertIn('(0.0, 0.0, 1.57)', script)
        self.assertIn('bpy.context.object.rotation_euler', script)
    
    def test_generate_cube_script_with_all_parameters(self):
        """Test cube script generation with all parameters."""
        script = self.generator.generate_cube_script(
            size=3.0,
            position=(1.0, 2.0, 3.0),
            rotation=(0.1, 0.2, 0.3)
        )
        
        self.assertIn('size=3.0', script)
        self.assertIn('location=(1.0, 2.0, 3.0)', script)
        self.assertIn('(0.1, 0.2, 0.3)', script)
    
    def test_generate_cube_script_clear_scene_enabled(self):
        """Test cube script includes scene clearing when enabled."""
        script = self.generator.generate_cube_script(size=1.0)
        
        self.assertIn('# Clear existing objects', script)
        self.assertIn('bpy.ops.object.select_all', script)
        self.assertIn('bpy.ops.object.delete', script)
    
    def test_generate_cube_script_clear_scene_disabled(self):
        """Test cube script doesn't include scene clearing when disabled."""
        from blender_integration.script_generator import ScriptGenerator
        
        generator = ScriptGenerator(clear_scene=False)
        script = generator.generate_cube_script(size=1.0)
        
        self.assertNotIn('# Clear existing objects', script)
        self.assertNotIn('bpy.ops.object.select_all', script)
        self.assertNotIn('bpy.ops.object.delete', script)
    
    def test_generate_cube_script_validation_invalid_size(self):
        """Test cube script generation with invalid size parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test negative size
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cube_script(size=-1.0)
        
        # Test zero size
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cube_script(size=0.0)
        
        # Test non-numeric size
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cube_script(size="invalid")
    
    def test_generate_cube_script_validation_invalid_position(self):
        """Test cube script generation with invalid position parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test invalid position tuple length
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cube_script(size=1.0, position=(1.0, 2.0))  # Missing Z
        
        # Test non-numeric position values
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cube_script(size=1.0, position=("x", "y", "z"))
    
    def test_generate_cube_script_validation_invalid_rotation(self):
        """Test cube script generation with invalid rotation parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test invalid rotation tuple length
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cube_script(size=1.0, rotation=(1.0, 2.0))  # Missing Z
        
        # Test non-numeric rotation values
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cube_script(size=1.0, rotation=("x", "y", "z"))
    
    def test_generate_cube_script_output_is_valid_python(self):
        """Test that generated cube script is valid Python syntax."""
        import ast
        
        script = self.generator.generate_cube_script(
            size=2.0,
            position=(1.0, -1.0, 0.5),
            rotation=(0.0, 0.0, 1.57)
        )
        
        # Should not raise SyntaxError
        ast.parse(script)
    
    def test_generate_cube_script_includes_success_message(self):
        """Test that cube script includes success output message."""
        script = self.generator.generate_cube_script(size=1.0)
        
        self.assertIn('print("Cube generated successfully")', script)
    
    def test_validate_size_valid(self):
        """Test size validation with valid values."""
        # Should not raise exception
        self.generator._validate_size(1.0)
        self.generator._validate_size(10.5)
        self.generator._validate_size(0.001)
    
    def test_validate_size_invalid(self):
        """Test size validation with invalid values."""
        from blender_integration.script_generator import ScriptGenerationError
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_size(-1.0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_size(0.0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_size("invalid")
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_size(None)
    
    def test_validate_position_valid(self):
        """Test position validation with valid values."""
        # Should not raise exception
        self.generator._validate_position((0.0, 0.0, 0.0))
        self.generator._validate_position((1.5, -2.3, 10.0))
        self.generator._validate_position((-10, 0, 5))  # Integers should work
    
    def test_validate_position_invalid(self):
        """Test position validation with invalid values."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Wrong tuple length
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_position((1.0, 2.0))
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_position((1.0, 2.0, 3.0, 4.0))
        
        # Non-numeric values
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_position(("x", "y", "z"))
        
        # Wrong type
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_position([1.0, 2.0, 3.0])  # List instead of tuple
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_position(None)
    
    def test_validate_rotation_valid(self):
        """Test rotation validation with valid values."""
        import math
        
        # Should not raise exception
        self.generator._validate_rotation((0.0, 0.0, 0.0))
        self.generator._validate_rotation((math.pi, -math.pi/2, math.pi/4))
        self.generator._validate_rotation((0, 1.57, -1.57))  # Integers should work
    
    def test_validate_rotation_invalid(self):
        """Test rotation validation with invalid values."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Wrong tuple length
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_rotation((1.0, 2.0))
        
        # Non-numeric values
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_rotation(("x", "y", "z"))
        
        # Wrong type
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_rotation([0.0, 0.0, 0.0])  # List instead of tuple
    
    def test_format_vector_tuple(self):
        """Test vector tuple formatting."""
        result = self.generator._format_vector((1.0, 2.5, -3.0))
        self.assertEqual(result, "(1.0, 2.5, -3.0)")
        
        result = self.generator._format_vector((0, 0, 0))
        self.assertEqual(result, "(0, 0, 0)")
    
    def test_generate_clear_scene_script(self):
        """Test scene clearing script generation."""
        script = self.generator._generate_clear_scene_script()
        
        self.assertIn('# Clear existing objects', script)
        self.assertIn('bpy.ops.object.select_all(action=\'SELECT\')', script)
        self.assertIn('bpy.ops.object.delete(use_global=False)', script)


class TestScriptGenerationError(unittest.TestCase):
    """Test cases for ScriptGenerationError exception."""
    
    def test_script_generation_error(self):
        """Test ScriptGenerationError exception."""
        from blender_integration.script_generator import ScriptGenerationError
        
        error = ScriptGenerationError("Test generation error")
        self.assertEqual(str(error), "Test generation error")
        self.assertIsInstance(error, Exception)


if __name__ == '__main__':
    unittest.main()