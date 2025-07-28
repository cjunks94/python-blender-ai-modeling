"""Tests for OBJ export functionality."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
from pathlib import Path
import tempfile
import os

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestOBJExporter(unittest.TestCase):
    """Test cases for OBJExporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from export.obj_exporter import OBJExporter
        self.exporter = OBJExporter()
    
    def test_init_default_settings(self):
        """Test OBJExporter initializes with default settings."""
        self.assertEqual(self.exporter.output_dir, Path.cwd() / "exports")
        self.assertTrue(self.exporter.create_dir_if_missing)
    
    def test_init_custom_settings(self):
        """Test OBJExporter initializes with custom settings."""
        from export.obj_exporter import OBJExporter
        
        custom_dir = Path("/tmp/custom_exports")
        exporter = OBJExporter(output_dir=custom_dir, create_dir_if_missing=False)
        
        self.assertEqual(exporter.output_dir, custom_dir)
        self.assertFalse(exporter.create_dir_if_missing)
    
    @patch('subprocess.run')
    def test_export_obj_success(self, mock_subprocess):
        """Test successful OBJ export."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "OBJ export completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock file existence, stat, and mkdir
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('pathlib.Path.mkdir'):
            
            # Mock stat result
            mock_stat_result = MagicMock()
            mock_stat_result.st_size = 1024
            mock_stat.return_value = mock_stat_result
            
            result = self.exporter.export_obj(
                model_id="test_model",
                model_params={'object_type': 'cube', 'size': 2.0, 'pos_x': 1.0}
            )
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.format, "obj")
        self.assertTrue(result.output_file.endswith(".obj"))
        self.assertEqual(result.model_id, "test_model")
        self.assertEqual(result.file_size, 1024)
    
    @patch('subprocess.run')
    def test_export_obj_blender_failure(self, mock_subprocess):
        """Test OBJ export when Blender execution fails."""
        from export.obj_exporter import ExportError
        
        # Setup mock to fail
        mock_subprocess.side_effect = FileNotFoundError("Blender not found")
        
        with self.assertRaises(ExportError) as context:
            self.exporter.export_obj(
                model_id="test_model",
                model_params={'object_type': 'cube', 'size': 2.0, 'pos_x': 1.0}
            )
        
        self.assertIn('blender', str(context.exception).lower())
    
    def test_export_obj_invalid_model_params(self):
        """Test OBJ export with invalid model parameters."""
        from export.obj_exporter import ExportError
        
        # Test missing object_type
        with self.assertRaises(ExportError):
            self.exporter.export_obj(
                model_id="test_model",
                model_params={'size': 2.0, 'pos_x': 1.0}
            )
        
        # Test invalid object_type
        with self.assertRaises(ExportError):
            self.exporter.export_obj(
                model_id="test_model",
                model_params={'object_type': 'invalid', 'size': 2.0, 'pos_x': 1.0}
            )
    
    def test_export_obj_invalid_model_id(self):
        """Test OBJ export with invalid model ID."""
        from export.obj_exporter import ExportError
        
        # Test empty model_id
        with self.assertRaises(ExportError):
            self.exporter.export_obj(
                model_id="",
                model_params={'object_type': 'cube', 'size': 2.0, 'pos_x': 1.0}
            )
        
        # Test None model_id
        with self.assertRaises(ExportError):
            self.exporter.export_obj(
                model_id=None,
                model_params={'object_type': 'cube', 'size': 2.0, 'pos_x': 1.0}
            )
    
    def test_generate_export_script_cube(self):
        """Test generation of Blender export script for cube."""
        script = self.exporter._generate_export_script(
            model_params={'object_type': 'cube', 'size': 2.0, 'pos_x': 1.0, 'pos_y': 0, 'pos_z': 0},
            output_file="/tmp/test.obj"
        )
        
        # Verify script contains expected components
        self.assertIn('import bpy', script)
        self.assertIn('primitive_cube_add', script)
        self.assertIn('size=2.0', script)
        self.assertIn('location=(1.0, 0, 0)', script)
        self.assertIn('bpy.ops.export_scene.obj', script)
        self.assertIn('filepath="/tmp/test.obj"', script)
    
    def test_generate_export_script_unsupported_object(self):
        """Test export script generation for unsupported object type."""
        from export.obj_exporter import ExportError
        
        with self.assertRaises(ExportError):
            self.exporter._generate_export_script(
                model_params={'object_type': 'sphere', 'size': 2.0},
                output_file="/tmp/test.obj"
            )
    
    def test_validate_model_params_valid(self):
        """Test model parameter validation with valid parameters."""
        # Should not raise exception
        self.exporter._validate_model_params({
            'object_type': 'cube',
            'size': 2.0,
            'pos_x': 1.0
        })
    
    def test_validate_model_params_invalid(self):
        """Test model parameter validation with invalid parameters."""
        from export.obj_exporter import ExportError
        
        # Missing object_type
        with self.assertRaises(ExportError):
            self.exporter._validate_model_params({
                'size': 2.0,
                'pos_x': 1.0
            })
        
        # Invalid object_type
        with self.assertRaises(ExportError):
            self.exporter._validate_model_params({
                'object_type': 'invalid',
                'size': 2.0,
                'pos_x': 1.0
            })
        
        # Missing size
        with self.assertRaises(ExportError):
            self.exporter._validate_model_params({
                'object_type': 'cube',
                'pos_x': 1.0
            })
    
    def test_build_output_filepath(self):
        """Test output file path generation."""
        filepath = self.exporter._build_output_filepath("test_model", "obj")
        
        expected_path = self.exporter.output_dir / "test_model.obj"
        self.assertEqual(filepath, expected_path)
    
    def test_create_output_directory(self):
        """Test output directory creation."""
        from export.obj_exporter import OBJExporter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_output = Path(temp_dir) / "test_exports"
            exporter = OBJExporter(output_dir=custom_output)
            
            # Directory should not exist initially
            self.assertFalse(custom_output.exists())
            
            # Should create directory
            exporter._create_output_directory()
            self.assertTrue(custom_output.exists())
            self.assertTrue(custom_output.is_dir())
    
    @patch('subprocess.run')
    def test_export_obj_file_not_created(self, mock_subprocess):
        """Test OBJ export when output file is not created."""
        from export.obj_exporter import ExportError
        
        # Setup mock to succeed but file doesn't exist
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Export completed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock file to not exist after export
        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(ExportError) as context:
                self.exporter.export_obj(
                    model_id="test_model",
                    model_params={'object_type': 'cube', 'size': 2.0, 'pos_x': 1.0}
                )
        
        self.assertIn('not created', str(context.exception).lower())


class TestExportResult(unittest.TestCase):
    """Test cases for ExportResult class."""
    
    def test_export_result_success(self):
        """Test ExportResult for successful export."""
        from export.obj_exporter import ExportResult
        
        result = ExportResult(
            success=True,
            model_id="test_model",
            format="obj",
            output_file="/tmp/test.obj",
            file_size=1024
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.model_id, "test_model")
        self.assertEqual(result.format, "obj")
        self.assertEqual(result.output_file, "/tmp/test.obj")
        self.assertEqual(result.file_size, 1024)
    
    def test_export_result_failure(self):
        """Test ExportResult for failed export."""
        from export.obj_exporter import ExportResult
        
        result = ExportResult(
            success=False,
            model_id="test_model",
            format="obj",
            output_file=None,
            error_message="Export failed"
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.model_id, "test_model")
        self.assertEqual(result.format, "obj")
        self.assertIsNone(result.output_file)
        self.assertEqual(result.error_message, "Export failed")


class TestExportError(unittest.TestCase):
    """Test cases for ExportError exception."""
    
    def test_export_error(self):
        """Test ExportError exception."""
        from export.obj_exporter import ExportError
        
        error = ExportError("Test export error")
        self.assertEqual(str(error), "Test export error")
        self.assertIsInstance(error, Exception)


if __name__ == '__main__':
    unittest.main()