"""Tests for Blender subprocess integration."""

import unittest
from unittest.mock import patch, MagicMock, call
import subprocess
import sys
from pathlib import Path
import tempfile
import os

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestBlenderExecutor(unittest.TestCase):
    """Test cases for BlenderExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from blender_integration.executor import BlenderExecutor
        self.executor = BlenderExecutor()
    
    def test_init_default_blender_path(self):
        """Test BlenderExecutor initializes with default Blender path."""
        self.assertEqual(self.executor.blender_path, 'blender')
        self.assertEqual(self.executor.timeout, 30)
    
    def test_init_custom_blender_path(self):
        """Test BlenderExecutor initializes with custom Blender path."""
        from blender_integration.executor import BlenderExecutor
        
        custom_path = '/custom/path/to/blender'
        executor = BlenderExecutor(blender_path=custom_path, timeout=60)
        
        self.assertEqual(executor.blender_path, custom_path)
        self.assertEqual(executor.timeout, 60)
    
    @patch('subprocess.run')
    def test_execute_script_success(self, mock_subprocess):
        """Test successful script execution."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Blender script executed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        script_content = "import bpy; bpy.ops.mesh.primitive_cube_add()"
        
        result = self.executor.execute_script(script_content)
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        
        # Check command structure
        cmd = call_args[0][0]
        self.assertEqual(cmd[0], 'blender')
        self.assertIn('--background', cmd)
        self.assertIn('--python', cmd)
        
        # Check result
        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "Blender script executed successfully")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.return_code, 0)
    
    @patch('subprocess.run')
    def test_execute_script_failure(self, mock_subprocess):
        """Test script execution failure."""
        # Setup mock for failure
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: Python script failed to execute"
        mock_subprocess.return_value = mock_result
        
        script_content = "import bpy; raise Exception('Simulated Blender error')"
        
        result = self.executor.execute_script(script_content)
        
        # Verify result
        self.assertFalse(result.success)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "Error: Python script failed to execute")
        self.assertEqual(result.return_code, 1)
    
    @patch('subprocess.run')
    def test_execute_script_timeout(self, mock_subprocess):
        """Test script execution timeout."""
        from blender_integration.executor import BlenderExecutionError
        
        # Setup mock to raise timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired('blender', 30)
        
        script_content = "import time; time.sleep(60)"
        
        with self.assertRaises(BlenderExecutionError) as context:
            self.executor.execute_script(script_content)
        
        self.assertIn('timeout', str(context.exception).lower())
    
    @patch('subprocess.run')
    def test_execute_script_file_not_found(self, mock_subprocess):
        """Test script execution when Blender is not found."""
        from blender_integration.executor import BlenderExecutionError
        
        # Setup mock to raise FileNotFoundError
        mock_subprocess.side_effect = FileNotFoundError("Blender executable not found")
        
        script_content = "import bpy"
        
        with self.assertRaises(BlenderExecutionError) as context:
            self.executor.execute_script(script_content)
        
        self.assertIn('not found', str(context.exception).lower())
    
    def test_validate_script_valid(self):
        """Test script validation with valid Python code."""
        valid_script = "import bpy\nbpy.ops.mesh.primitive_cube_add()"
        
        # Should not raise exception
        self.executor.validate_script(valid_script)
    
    def test_validate_script_invalid_syntax(self):
        """Test script validation with invalid Python syntax."""
        from blender_integration.executor import BlenderScriptError
        
        invalid_script = "import bpy\ninvalid syntax here"
        
        with self.assertRaises(BlenderScriptError):
            self.executor.validate_script(invalid_script)
    
    def test_validate_script_empty(self):
        """Test script validation with empty script."""
        from blender_integration.executor import BlenderScriptError
        
        with self.assertRaises(BlenderScriptError):
            self.executor.validate_script("")
    
    def test_validate_script_none(self):
        """Test script validation with None script."""
        from blender_integration.executor import BlenderScriptError
        
        with self.assertRaises(BlenderScriptError):
            self.executor.validate_script(None)
    
    @patch('subprocess.run')
    def test_execute_script_with_output_file(self, mock_subprocess):
        """Test script execution with output file specification."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Script executed, file saved"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        script_content = "import bpy; bpy.ops.wm.save_as_mainfile(filepath='/tmp/test.blend')"
        output_file = "/tmp/test_output.obj"
        
        result = self.executor.execute_script(script_content, output_file=output_file)
        
        # Verify subprocess was called
        mock_subprocess.assert_called_once()
        
        # Verify result includes output file path
        self.assertTrue(result.success)
        self.assertEqual(result.output_file, output_file)
    
    def test_create_temp_script_file(self):
        """Test temporary script file creation."""
        script_content = "import bpy\nprint('Hello from Blender')"
        
        script_file = self.executor._create_temp_script_file(script_content)
        
        try:
            # Verify file exists and contains correct content
            self.assertTrue(script_file.exists())
            self.assertTrue(script_file.name.endswith('.py'))
            
            with open(script_file, 'r') as f:
                content = f.read()
            
            self.assertEqual(content, script_content)
            
        finally:
            # Clean up
            if script_file.exists():
                script_file.unlink()
    
    def test_build_blender_command(self):
        """Test Blender command building."""
        script_file = Path('/tmp/test_script.py')
        output_file = '/tmp/output.obj'
        
        cmd = self.executor._build_blender_command(script_file, output_file)
        
        expected_cmd = [
            'blender',
            '--background',
            '--python', str(script_file),
            '--',
            '--output', output_file
        ]
        
        self.assertEqual(cmd, expected_cmd)
    
    def test_build_blender_command_no_output(self):
        """Test Blender command building without output file."""
        script_file = Path('/tmp/test_script.py')
        
        cmd = self.executor._build_blender_command(script_file)
        
        expected_cmd = [
            'blender',
            '--background',
            '--python', str(script_file)
        ]
        
        self.assertEqual(cmd, expected_cmd)


class TestBlenderExecutionResult(unittest.TestCase):
    """Test cases for BlenderExecutionResult class."""
    
    def test_execution_result_success(self):
        """Test BlenderExecutionResult for successful execution."""
        from blender_integration.executor import BlenderExecutionResult
        
        result = BlenderExecutionResult(
            success=True,
            return_code=0,
            stdout="Success output",
            stderr="",
            output_file="/tmp/output.obj"
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.stdout, "Success output")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.output_file, "/tmp/output.obj")
    
    def test_execution_result_failure(self):
        """Test BlenderExecutionResult for failed execution."""
        from blender_integration.executor import BlenderExecutionResult
        
        result = BlenderExecutionResult(
            success=False,
            return_code=1,
            stdout="",
            stderr="Error occurred",
            output_file=None
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "Error occurred")
        self.assertIsNone(result.output_file)


class TestBlenderExceptions(unittest.TestCase):
    """Test cases for Blender-specific exceptions."""
    
    def test_blender_execution_error(self):
        """Test BlenderExecutionError exception."""
        from blender_integration.executor import BlenderExecutionError
        
        error = BlenderExecutionError("Test execution error")
        self.assertEqual(str(error), "Test execution error")
        self.assertIsInstance(error, Exception)
    
    def test_blender_script_error(self):
        """Test BlenderScriptError exception."""
        from blender_integration.executor import BlenderScriptError
        
        error = BlenderScriptError("Test script error")
        self.assertEqual(str(error), "Test script error")
        self.assertIsInstance(error, Exception)


class TestEnhancedErrorHandling(unittest.TestCase):
    """Test cases for enhanced error handling and recovery mechanisms."""
    
    def setUp(self):
        """Set up test fixtures."""
        from blender_integration.executor import BlenderExecutor
        self.executor = BlenderExecutor()
    
    @patch('subprocess.run')
    def test_execute_script_permission_denied(self, mock_subprocess):
        """Test script execution when permission is denied."""
        from blender_integration.executor import BlenderExecutionError
        
        # Setup mock to raise PermissionError
        mock_subprocess.side_effect = PermissionError("Permission denied")
        
        script_content = "import bpy"
        
        with self.assertRaises(BlenderExecutionError) as context:
            self.executor.execute_script(script_content)
        
        self.assertIn('permission', str(context.exception).lower())
    
    @patch('subprocess.run')
    def test_execute_script_memory_error(self, mock_subprocess):
        """Test script execution with memory errors."""
        from blender_integration.executor import BlenderExecutionError
        
        # Setup mock to raise MemoryError
        mock_subprocess.side_effect = MemoryError("Not enough memory")
        
        script_content = "import bpy"
        
        with self.assertRaises(BlenderExecutionError) as context:
            self.executor.execute_script(script_content)
        
        self.assertIn('memory', str(context.exception).lower())
    
    @patch('subprocess.run')
    def test_execute_script_with_retry_mechanism(self, mock_subprocess):
        """Test script execution with retry mechanism for transient failures."""
        # Setup mock to fail first time, succeed second time
        mock_subprocess.side_effect = [
            subprocess.TimeoutExpired('blender', 30),  # First call fails
            MagicMock(returncode=0, stdout="Success", stderr="")  # Second call succeeds
        ]
        
        script_content = "import bpy"
        
        # This should succeed with retry mechanism
        result = self.executor.execute_script_with_retry(script_content, max_retries=2)
        
        self.assertTrue(result.success)
        self.assertEqual(mock_subprocess.call_count, 2)
    
    @patch('subprocess.run')
    def test_execute_script_max_retries_exceeded(self, mock_subprocess):
        """Test script execution when max retries are exceeded."""
        from blender_integration.executor import BlenderExecutionError
        
        # Setup mock to always timeout (this creates retryable timeouts)
        mock_subprocess.side_effect = subprocess.TimeoutExpired('blender', 30)
        
        script_content = "import bpy"
        
        with self.assertRaises(BlenderExecutionError) as context:
            self.executor.execute_script_with_retry(script_content, max_retries=2)
        
        # The error should mention either max retries or timeout
        error_msg = str(context.exception).lower()
        self.assertTrue('max retries' in error_msg or 'timeout' in error_msg)
        self.assertEqual(mock_subprocess.call_count, 2)  # Should try exactly max_retries times
    
    def test_validate_script_with_complex_errors(self):
        """Test script validation with complex Python errors."""
        from blender_integration.executor import BlenderScriptError
        
        # Test script with actual indentation error - mixing tabs and spaces
        invalid_script = "import bpy\nif True:\n\tprint('tab')\n    print('spaces')"
        
        with self.assertRaises(BlenderScriptError) as context:
            self.executor.validate_script(invalid_script)
        
        # The error should be caught and re-raised as BlenderScriptError
        error_msg = str(context.exception).lower()
        self.assertTrue('syntax' in error_msg or 'indentation' in error_msg)
    
    def test_validate_script_with_import_errors(self):
        """Test script validation with import-related issues."""
        from blender_integration.executor import BlenderScriptError
        
        # Test script with potentially dangerous imports
        dangerous_script = "import os; os.system('rm -rf /')"
        
        with self.assertRaises(BlenderScriptError) as context:
            self.executor.validate_script_security(dangerous_script)
        
        self.assertIn('security', str(context.exception).lower())
    
    @patch('subprocess.run')
    def test_execute_script_cleanup_on_failure(self, mock_subprocess):
        """Test that temporary files are cleaned up even on failure."""
        # Setup mock to fail
        mock_subprocess.side_effect = subprocess.TimeoutExpired('blender', 30)
        from blender_integration.executor import BlenderExecutionError
        
        script_content = "import bpy"
        
        # Get initial temp file count
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        initial_py_files = len(list(temp_dir.glob("tmp*.py")))
        
        with self.assertRaises(BlenderExecutionError):
            self.executor.execute_script(script_content)
        
        # Check that no additional temp files remain
        final_py_files = len(list(temp_dir.glob("tmp*.py")))
        self.assertEqual(initial_py_files, final_py_files)
    
    def test_error_categorization(self):
        """Test that errors are properly categorized for user-friendly messages."""
        from blender_integration.executor import BlenderExecutionError
        
        # Test different error types
        timeout_error = BlenderExecutionError("Timeout occurred", error_type="timeout")
        self.assertEqual(timeout_error.error_type, "timeout")
        
        permission_error = BlenderExecutionError("Permission denied", error_type="permission")
        self.assertEqual(permission_error.error_type, "permission")
        
        script_error = BlenderExecutionError("Script syntax error", error_type="script")
        self.assertEqual(script_error.error_type, "script")


if __name__ == '__main__':
    unittest.main()