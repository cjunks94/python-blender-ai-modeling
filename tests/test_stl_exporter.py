"""Tests for STL export functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSTLExporter(unittest.TestCase):
    """Test cases for STLExporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from export.stl_exporter import STLExporter
        
        with patch('export.stl_exporter.BlenderExecutor'):
            self.exporter = STLExporter()
    
    def test_init_creates_output_directory(self):
        """Test that initialization creates output directory."""
        self.assertTrue(self.exporter.output_dir.exists())
        self.assertEqual(self.exporter.output_dir.name, "exports")
    
    @patch('export.stl_exporter.BlenderExecutor')
    def test_init_with_custom_parameters(self, mock_executor):
        """Test initialization with custom parameters."""
        from export.stl_exporter import STLExporter
        
        exporter = STLExporter(blender_path="/custom/blender", timeout=120)
        
        mock_executor.assert_called_once_with("/custom/blender", 120)
    
    def test_export_stl_binary_format(self):
        """Test exporting model to binary STL format."""
        # Mock the Blender executor
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = "STL export successful"
        mock_result.stderr = ""
        
        self.exporter.blender_executor.execute_script = Mock(return_value=mock_result)
        
        # Create a fake output file
        output_file = self.exporter.output_dir / "test_model.stl"
        output_file.write_bytes(b"fake binary stl data")
        
        # Test export
        model_params = {
            'object_type': 'cube',
            'size': 2.0,
            'pos_x': 0.0
        }
        
        result = self.exporter.export_stl("test_model", model_params, ascii_format=False)
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.model_id, "test_model")
        self.assertEqual(result.format, "stl")
        self.assertEqual(result.output_file, str(output_file))
        self.assertGreater(result.file_size, 0)
        
        # Clean up
        output_file.unlink()
    
    def test_export_stl_ascii_format(self):
        """Test exporting model to ASCII STL format."""
        # Mock the Blender executor
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = "STL export successful"
        mock_result.stderr = ""
        
        self.exporter.blender_executor.execute_script = Mock(return_value=mock_result)
        
        # Create a fake output file
        output_file = self.exporter.output_dir / "test_model.stl"
        output_file.write_text("solid test\nfacet normal 0 0 0\nendfacet\nendsolid")
        
        # Test export
        model_params = {
            'object_type': 'sphere',
            'size': 1.5,
            'pos_x': 1.0
        }
        
        result = self.exporter.export_stl("test_model", model_params, ascii_format=True)
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.model_id, "test_model")
        self.assertEqual(result.format, "stl")
        
        # Verify ASCII format was requested
        call_args = self.exporter.blender_executor.execute_script.call_args[0][0]
        self.assertIn("ascii=true", call_args)
        
        # Clean up
        output_file.unlink()
    
    def test_export_stl_applies_transforms(self):
        """Test that STL export applies transforms before exporting."""
        # Mock the Blender executor
        mock_result = Mock()
        mock_result.success = True
        self.exporter.blender_executor.execute_script = Mock(return_value=mock_result)
        
        # Create output file
        output_file = self.exporter.output_dir / "test_model.stl"
        output_file.write_text("fake data")
        
        # Test export
        model_params = {
            'object_type': 'cube',
            'size': 2.0,
            'pos_x': 0.0,
            'rotation': {'x': 45, 'y': 30, 'z': 0}
        }
        
        result = self.exporter.export_stl("test_model", model_params)
        
        # Verify transform application in script
        call_args = self.exporter.blender_executor.execute_script.call_args[0][0]
        self.assertIn('transform_apply', call_args)
        self.assertIn('rotation=True', call_args)
        self.assertIn('scale=True', call_args)
        
        # Clean up
        output_file.unlink()
    
    def test_export_stl_validation_errors(self):
        """Test validation errors during export."""
        from export.stl_exporter import ExportError
        
        # Test missing model_id
        result = self.exporter.export_stl("", {'object_type': 'cube'})
        self.assertFalse(result.success)
        self.assertIn("Model ID is required", result.error_message)
        
        # Test missing model_params
        result = self.exporter.export_stl("test_model", None)
        self.assertFalse(result.success)
        self.assertIn("Model parameters are required", result.error_message)
    
    def test_export_stl_unsupported_object_type(self):
        """Test handling of unsupported object types."""
        # Mock the script generator to raise error
        self.exporter.script_generator.generate_cube_script = Mock(
            side_effect=Exception("Unsupported type")
        )
        
        model_params = {
            'object_type': 'invalid_type',
            'size': 2.0
        }
        
        result = self.exporter.export_stl("test_model", model_params)
        
        self.assertFalse(result.success)
        self.assertIn("Unsupported object type", result.error_message)
    
    def test_export_stl_blender_execution_error(self):
        """Test handling of Blender execution errors."""
        from export.stl_exporter import BlenderExecutionError
        
        # Mock execution error
        self.exporter.blender_executor.execute_script = Mock(
            side_effect=BlenderExecutionError("Blender crashed")
        )
        
        result = self.exporter.export_stl("test_model", {'object_type': 'cube'})
        
        self.assertFalse(result.success)
        self.assertIn("Blender execution error", result.error_message)
    
    def test_cleanup_old_exports(self):
        """Test cleanup of old export files."""
        import time
        
        # Create test files
        old_file = self.exporter.output_dir / "old_model.stl"
        old_file.write_text("old data")
        
        new_file = self.exporter.output_dir / "new_model.stl"
        new_file.write_text("new data")
        
        # Make old_file older
        old_time = time.time() - (8 * 24 * 60 * 60)  # 8 days old
        os.utime(old_file, (old_time, old_time))
        
        # Run cleanup
        removed_count = self.exporter.cleanup_old_exports(days=7)
        
        # Verify
        self.assertEqual(removed_count, 1)
        self.assertFalse(old_file.exists())
        self.assertTrue(new_file.exists())
        
        # Clean up
        if new_file.exists():
            new_file.unlink()


if __name__ == '__main__':
    unittest.main()