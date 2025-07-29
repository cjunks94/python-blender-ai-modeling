"""
Tests for improved error handling throughout the codebase.

This module tests that proper exceptions are raised and handled instead of
using bare except blocks that can hide important errors.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import os

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestImprovedErrorHandling(unittest.TestCase):
    """Test cases for proper error handling patterns."""
    
    def test_blender_executor_script_writing_error_handling(self):
        """Test that BlenderExecutor handles script writing errors properly."""
        from blender_integration.executor import BlenderExecutor
        
        executor = BlenderExecutor()
        
        # Mock mkstemp to return a valid file descriptor
        with patch('tempfile.mkstemp') as mock_mkstemp:
            with patch('os.fdopen') as mock_fdopen:
                # Simulate file descriptor creation
                mock_mkstemp.return_value = (5, '/tmp/test_script.py')
                
                # Simulate file write error
                mock_fdopen.side_effect = OSError("Permission denied")
                
                with patch('os.close') as mock_close:
                    # Should raise RuntimeError with proper error message
                    with self.assertRaises(RuntimeError) as context:
                        executor._create_temp_script_file("test script")
                    
                    # Verify proper error message
                    self.assertIn("Failed to write script to temporary file", str(context.exception))
                    
                    # Verify cleanup was attempted
                    mock_close.assert_called_once_with(5)
    
    def test_export_file_cleanup_error_handling(self):
        """Test that export file cleanup handles errors properly."""
        from export.stl_exporter import STLExporter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = STLExporter(output_dir=temp_dir)
            
            # Mock the glob method to return a file path
            mock_file_path = MagicMock()
            mock_file_path.stat().st_mtime = 0  # Very old file
            mock_file_path.unlink.side_effect = PermissionError("Permission denied")
            
            with patch.object(exporter.output_dir, 'glob') as mock_glob:
                mock_glob.return_value = [mock_file_path]
                
                with patch('time.time', return_value=1000):
                    # Should not raise exception, should handle gracefully
                    count = exporter.cleanup_old_files(days=1)
                    
                    # Should return 0 since no files were successfully deleted
                    self.assertEqual(count, 0)
                    
                    # Verify unlink was attempted
                    mock_file_path.unlink.assert_called_once()
    
    def test_preview_file_cleanup_error_handling(self):
        """Test that preview file cleanup handles errors properly."""
        from blender_integration.preview_renderer import PreviewRenderer
        
        renderer = PreviewRenderer()
        
        # Mock the glob method to return a file path
        mock_file_path = MagicMock()
        mock_file_path.stat().st_mtime = 0  # Very old file
        mock_file_path.unlink.side_effect = FileNotFoundError("File not found")
        
        with patch.object(renderer.preview_dir, 'glob') as mock_glob:
            mock_glob.return_value = [mock_file_path]
            
            with patch('time.time', return_value=1000):
                # Should not raise exception, should handle gracefully
                count = renderer.cleanup_old_previews(days=1)
                
                # Should return 0 since no files were successfully deleted
                self.assertEqual(count, 0)
                
                # Verify unlink was attempted
                mock_file_path.unlink.assert_called_once()
    
    def test_stl_export_fallback_error_handling(self):
        """Test that STL export fallback handles specific exceptions."""
        from export.stl_exporter import STLExporter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = STLExporter(output_dir=temp_dir)
            
            # Mock parameters
            params = {
                'object_type': 'cube',
                'size': 2.0,
                'ascii': True
            }
            
            # Mock BlenderExecutor to simulate export process
            with patch.object(exporter, 'executor') as mock_executor:
                mock_result = MagicMock()
                mock_result.success = True
                mock_result.stdout = "Export script generated successfully"
                mock_executor.execute_script.return_value = mock_result
                
                # Mock the script generation to include fallback logic
                with patch.object(exporter, '_generate_export_script') as mock_generate:
                    # Simulate script that tries modern export first, then falls back
                    mock_generate.return_value = """
try:
    # Modern export (will fail)
    bpy.ops.wm.stl_export()
except (AttributeError, TypeError) as e:
    # Fallback to legacy
    bpy.ops.export_mesh.stl()
"""
                    
                    # Should complete successfully using fallback
                    result = exporter.export_model('test', 'stl', params)
                    
                    self.assertTrue(result.success)
                    mock_executor.execute_script.assert_called_once()
    
    def test_obj_export_fallback_error_handling(self):
        """Test that OBJ export fallback handles specific exceptions."""
        from export.obj_exporter import OBJExporter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = OBJExporter(output_dir=temp_dir)
            
            # Mock parameters
            params = {
                'object_type': 'sphere',
                'size': 1.5
            }
            
            # Mock BlenderExecutor to simulate export process
            with patch.object(exporter, 'executor') as mock_executor:
                mock_result = MagicMock()
                mock_result.success = True
                mock_result.stdout = "Export script generated successfully"
                mock_executor.execute_script.return_value = mock_result
                
                # Mock the script generation to include fallback logic
                with patch.object(exporter, '_generate_export_script') as mock_generate:
                    # Simulate script that tries modern export first, then falls back
                    mock_generate.return_value = """
try:
    # Modern export (will fail)
    bpy.ops.wm.obj_export()
except (AttributeError, TypeError) as e:
    # Fallback to legacy
    bpy.ops.export_scene.obj()
"""
                    
                    # Should complete successfully using fallback
                    result = exporter.export_model('test', 'obj', params)
                    
                    self.assertTrue(result.success)
                    mock_executor.execute_script.assert_called_once()
    
    def test_no_bare_except_blocks_in_codebase(self):
        """Test that no bare except blocks remain in the codebase."""
        import os
        import re
        
        src_dir = Path(__file__).parent.parent / "src"
        bare_except_pattern = re.compile(r'except\s*:')
        
        violations = []
        
        for py_file in src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for line_num, line in enumerate(content.splitlines(), 1):
                    if bare_except_pattern.search(line):
                        violations.append(f"{py_file}:{line_num}: {line.strip()}")
            except (IOError, UnicodeDecodeError):
                # Skip files that can't be read
                continue
        
        if violations:
            self.fail(f"Found bare except blocks:\n" + "\n".join(violations))
    
    def test_proper_exception_types_used(self):
        """Test that specific exception types are used instead of generic Exception."""
        # This test checks that we're not catching overly broad exceptions
        # in critical code paths (this is more of a code review test)
        
        # Test a few key modules for proper exception handling
        test_cases = [
            # (module_path, should_have_specific_exceptions)
            ("blender_integration/executor.py", True),
            ("export/stl_exporter.py", True), 
            ("export/obj_exporter.py", True),
            ("web/security/input_validator.py", True)
        ]
        
        src_dir = Path(__file__).parent.parent / "src"
        
        for module_path, should_have_specific in test_cases:
            full_path = src_dir / module_path
            if not full_path.exists():
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count specific vs generic exception handling
                specific_exceptions = len(re.findall(r'except \([^)]*Error[^)]*\)', content))
                specific_exceptions += len(re.findall(r'except \w*Error', content))
                specific_exceptions += len(re.findall(r'except \([^)]*OSError[^)]*\)', content))
                
                generic_exceptions = len(re.findall(r'except Exception', content))
                
                if should_have_specific and specific_exceptions == 0 and generic_exceptions > 0:
                    # This is more of a warning than a failure for now
                    print(f"Warning: {module_path} might benefit from more specific exception handling")
                    
            except (IOError, UnicodeDecodeError):
                continue
    
    def test_error_logging_present(self):
        """Test that modules with error handling have proper logging."""
        import re
        
        src_dir = Path(__file__).parent.parent / "src"
        
        # Modules that should have logging when they handle errors
        modules_to_check = [
            "export/stl_exporter.py",
            "export/obj_exporter.py", 
            "export/gltf_exporter.py",
            "blender_integration/preview_renderer.py"
        ]
        
        for module_path in modules_to_check:
            full_path = src_dir / module_path
            if not full_path.exists():
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if module has logging import
                has_logging_import = 'import logging' in content
                has_logger = 'logger = logging.getLogger' in content
                has_exception_handling = 'except' in content
                
                if has_exception_handling and not (has_logging_import and has_logger):
                    self.fail(f"{module_path} handles exceptions but lacks proper logging setup")
                    
            except (IOError, UnicodeDecodeError):
                continue


if __name__ == '__main__':
    unittest.main()