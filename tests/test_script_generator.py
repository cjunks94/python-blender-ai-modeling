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
    
    # Sphere generation tests
    def test_generate_sphere_script_basic(self):
        """Test basic sphere script generation."""
        script = self.generator.generate_sphere_script(radius=1.5)
        
        # Verify script contains expected components
        self.assertIn('import bpy', script)
        self.assertIn('primitive_uv_sphere_add', script)
        self.assertIn('radius=1.5', script)
        self.assertIn('location=(0, 0, 0)', script)  # Default origin
        self.assertIn('subdivisions=2', script)  # Default subdivisions
    
    def test_generate_sphere_script_with_position(self):
        """Test sphere script generation with custom position."""
        script = self.generator.generate_sphere_script(
            radius=2.0, 
            position=(1.0, -2.0, 3.0)
        )
        
        self.assertIn('radius=2.0', script)
        self.assertIn('location=(1.0, -2.0, 3.0)', script)
    
    def test_generate_sphere_script_with_subdivisions(self):
        """Test sphere script generation with custom subdivisions."""
        script = self.generator.generate_sphere_script(
            radius=1.0,
            subdivisions=4
        )
        
        self.assertIn('subdivisions=4', script)
    
    def test_generate_sphere_script_validation_invalid_radius(self):
        """Test sphere script generation with invalid radius parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test negative radius
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_sphere_script(radius=-1.0)
        
        # Test zero radius
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_sphere_script(radius=0.0)
    
    def test_generate_sphere_script_validation_invalid_subdivisions(self):
        """Test sphere script generation with invalid subdivisions parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test subdivisions out of range
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_sphere_script(radius=1.0, subdivisions=0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_sphere_script(radius=1.0, subdivisions=7)
        
        # Test non-integer subdivisions
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_sphere_script(radius=1.0, subdivisions=2.5)
    
    # Cylinder generation tests
    def test_generate_cylinder_script_basic(self):
        """Test basic cylinder script generation."""
        script = self.generator.generate_cylinder_script(radius=1.0, depth=2.0)
        
        # Verify script contains expected components
        self.assertIn('import bpy', script)
        self.assertIn('primitive_cylinder_add', script)
        self.assertIn('radius=1.0', script)
        self.assertIn('depth=2.0', script)
        self.assertIn('location=(0, 0, 0)', script)  # Default origin
        self.assertIn('vertices=32', script)  # Default vertices
    
    def test_generate_cylinder_script_with_position(self):
        """Test cylinder script generation with custom position."""
        script = self.generator.generate_cylinder_script(
            radius=0.5, 
            depth=3.0,
            position=(-1.0, 2.0, 0.5)
        )
        
        self.assertIn('radius=0.5', script)
        self.assertIn('depth=3.0', script)
        self.assertIn('location=(-1.0, 2.0, 0.5)', script)
    
    def test_generate_cylinder_script_with_vertices(self):
        """Test cylinder script generation with custom vertices."""
        script = self.generator.generate_cylinder_script(
            radius=1.0,
            depth=2.0,
            vertices=64
        )
        
        self.assertIn('vertices=64', script)
    
    def test_generate_cylinder_script_validation_invalid_depth(self):
        """Test cylinder script generation with invalid depth parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test negative depth
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cylinder_script(radius=1.0, depth=-2.0)
        
        # Test zero depth
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cylinder_script(radius=1.0, depth=0.0)
    
    def test_generate_cylinder_script_validation_invalid_vertices(self):
        """Test cylinder script generation with invalid vertices parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test vertices out of range
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cylinder_script(radius=1.0, depth=2.0, vertices=4)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cylinder_script(radius=1.0, depth=2.0, vertices=200)
        
        # Test non-integer vertices
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_cylinder_script(radius=1.0, depth=2.0, vertices=32.5)
    
    # Plane generation tests
    def test_generate_plane_script_basic(self):
        """Test basic plane script generation."""
        script = self.generator.generate_plane_script(size=2.0)
        
        # Verify script contains expected components
        self.assertIn('import bpy', script)
        self.assertIn('primitive_plane_add', script)
        self.assertIn('size=2.0', script)
        self.assertIn('location=(0, 0, 0)', script)  # Default origin
    
    def test_generate_plane_script_with_position(self):
        """Test plane script generation with custom position."""
        script = self.generator.generate_plane_script(
            size=5.0, 
            position=(0.0, 0.0, -1.0)
        )
        
        self.assertIn('size=5.0', script)
        self.assertIn('location=(0.0, 0.0, -1.0)', script)
    
    def test_generate_plane_script_with_rotation(self):
        """Test plane script generation with rotation."""
        import math
        script = self.generator.generate_plane_script(
            size=3.0,
            rotation=(math.pi/2, 0.0, 0.0)  # 90 degrees rotation on X axis
        )
        
        self.assertIn(f'({math.pi/2}, 0.0, 0.0)', script)
        self.assertIn('bpy.context.object.rotation_euler', script)
    
    def test_generate_plane_script_validation_invalid_size(self):
        """Test plane script generation with invalid size parameter."""
        from blender_integration.script_generator import ScriptGenerationError
        
        # Test negative size
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_plane_script(size=-1.0)
        
        # Test zero size
        with self.assertRaises(ScriptGenerationError):
            self.generator.generate_plane_script(size=0.0)
    
    # Validate radius tests
    def test_validate_radius_valid(self):
        """Test radius validation with valid values."""
        # Should not raise exception
        self.generator._validate_radius(0.1)
        self.generator._validate_radius(5.0)
        self.generator._validate_radius(100.0)
    
    def test_validate_radius_invalid(self):
        """Test radius validation with invalid values."""
        from blender_integration.script_generator import ScriptGenerationError
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_radius(-1.0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_radius(0.0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_radius("invalid")
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_radius(None)
    
    # Validate depth tests
    def test_validate_depth_valid(self):
        """Test depth validation with valid values."""
        # Should not raise exception
        self.generator._validate_depth(0.1)
        self.generator._validate_depth(10.0)
        self.generator._validate_depth(50)
    
    def test_validate_depth_invalid(self):
        """Test depth validation with invalid values."""
        from blender_integration.script_generator import ScriptGenerationError
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_depth(-1.0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_depth(0.0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_depth("invalid")
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_depth(None)
    
    # Validate subdivisions tests
    def test_validate_subdivisions_valid(self):
        """Test subdivisions validation with valid values."""
        # Should not raise exception
        self.generator._validate_subdivisions(1)
        self.generator._validate_subdivisions(3)
        self.generator._validate_subdivisions(6)
    
    def test_validate_subdivisions_invalid(self):
        """Test subdivisions validation with invalid values."""
        from blender_integration.script_generator import ScriptGenerationError
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_subdivisions(0)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_subdivisions(7)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_subdivisions(2.5)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_subdivisions("3")
    
    # Validate vertices tests
    def test_validate_vertices_valid(self):
        """Test vertices validation with valid values."""
        # Should not raise exception
        self.generator._validate_vertices(8)
        self.generator._validate_vertices(32)
        self.generator._validate_vertices(128)
    
    def test_validate_vertices_invalid(self):
        """Test vertices validation with invalid values."""
        from blender_integration.script_generator import ScriptGenerationError
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_vertices(4)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_vertices(256)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_vertices(32.5)
        
        with self.assertRaises(ScriptGenerationError):
            self.generator._validate_vertices("32")


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