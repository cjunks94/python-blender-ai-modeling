"""Tests for GLTF export functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestGLTFExporter(unittest.TestCase):
    """Test cases for GLTFExporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from export.gltf_exporter import GLTFExporter
        
        with patch('export.gltf_exporter.BlenderExecutor'):
            self.exporter = GLTFExporter()
    
    def test_init_creates_output_directory(self):
        """Test that initialization creates output directory."""
        self.assertTrue(self.exporter.output_dir.exists())
        self.assertEqual(self.exporter.output_dir.name, "exports")
    
    @patch('export.gltf_exporter.BlenderExecutor')
    def test_init_with_custom_parameters(self, mock_executor):
        """Test initialization with custom parameters."""
        from export.gltf_exporter import GLTFExporter
        
        exporter = GLTFExporter(blender_path="/custom/blender", timeout=120)
        
        mock_executor.assert_called_once_with("/custom/blender", 120)
    
    def test_export_gltf_glb_format(self):
        """Test exporting model to GLB format."""
        # Mock the Blender executor
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = "GLTF export successful"
        mock_result.stderr = ""
        
        self.exporter.blender_executor.execute_script = Mock(return_value=mock_result)
        
        # Create a fake output file
        output_file = self.exporter.output_dir / "test_model.glb"
        output_file.write_text("fake glb data")
        
        # Test export
        model_params = {
            'object_type': 'cube',
            'size': 2.0,
            'pos_x': 0.0
        }
        
        result = self.exporter.export_gltf("test_model", model_params, binary=True)
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.model_id, "test_model")
        self.assertEqual(result.format, "glb")
        self.assertEqual(result.output_file, str(output_file))
        self.assertGreater(result.file_size, 0)
        
        # Clean up
        output_file.unlink()
    
    def test_export_gltf_json_format(self):
        """Test exporting model to GLTF (JSON) format."""
        # Mock the Blender executor
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = "GLTF export successful"
        mock_result.stderr = ""
        
        self.exporter.blender_executor.execute_script = Mock(return_value=mock_result)
        
        # Create a fake output file
        output_file = self.exporter.output_dir / "test_model.gltf"
        output_file.write_text("fake gltf data")
        
        # Test export
        model_params = {
            'object_type': 'sphere',
            'size': 1.5,
            'pos_x': 1.0
        }
        
        result = self.exporter.export_gltf("test_model", model_params, binary=False)
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.model_id, "test_model")
        self.assertEqual(result.format, "gltf")
        self.assertEqual(result.output_file, str(output_file))
        
        # Clean up
        output_file.unlink()
    
    def test_export_gltf_with_material(self):
        """Test exporting model with material properties."""
        # Mock the Blender executor
        mock_result = Mock()
        mock_result.success = True
        self.exporter.blender_executor.execute_script = Mock(return_value=mock_result)
        
        # Create output file
        output_file = self.exporter.output_dir / "test_model.glb"
        output_file.write_text("fake data")
        
        # Test export with material
        model_params = {
            'object_type': 'cube',
            'size': 2.0,
            'pos_x': 0.0,
            'color': '#FF0000',
            'metallic': 0.5,
            'roughness': 0.3
        }
        
        result = self.exporter.export_gltf("test_model", model_params)
        
        # Verify material properties were included in script
        call_args = self.exporter.blender_executor.execute_script.call_args[0][0]
        self.assertIn('color', call_args)
        self.assertIn('metallic', call_args)
        self.assertIn('roughness', call_args)
        
        # Clean up
        output_file.unlink()
    
    def test_export_gltf_validation_errors(self):
        """Test validation errors during export."""
        from export.gltf_exporter import ExportError
        
        # Test missing model_id
        result = self.exporter.export_gltf("", {'object_type': 'cube'})
        self.assertFalse(result.success)
        self.assertIn("Model ID is required", result.error_message)
        
        # Test missing model_params
        result = self.exporter.export_gltf("test_model", None)
        self.assertFalse(result.success)
        self.assertIn("Model parameters are required", result.error_message)
    
    def test_export_gltf_blender_execution_error(self):
        """Test handling of Blender execution errors."""
        from export.gltf_exporter import BlenderExecutionError
        
        # Mock execution error
        self.exporter.blender_executor.execute_script = Mock(
            side_effect=BlenderExecutionError("Blender crashed")
        )
        
        result = self.exporter.export_gltf("test_model", {'object_type': 'cube'})
        
        self.assertFalse(result.success)
        self.assertIn("Blender execution error", result.error_message)
    
    def test_cleanup_old_exports(self):
        """Test cleanup of old export files."""
        import time
        
        # Create test files
        old_file = self.exporter.output_dir / "old_model.glb"
        old_file.write_text("old data")
        
        new_file = self.exporter.output_dir / "new_model.gltf"
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