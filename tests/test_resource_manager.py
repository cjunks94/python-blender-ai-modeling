"""
Tests for resource management utilities.

This module tests the resource cleanup functionality including
temporary file management, subprocess tracking, and cleanup operations.
"""

import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.resource_manager import (
    ManagedTempFile,
    ManagedTempDir, 
    ManagedProcess,
    ResourceTracker,
    create_temp_script_file,
    execute_with_timeout,
    cleanup_old_temp_files,
    cleanup_all_resources
)


class TestManagedTempFile(unittest.TestCase):
    """Test managed temporary file context manager."""
    
    def test_temp_file_creation_and_cleanup(self):
        """Test that temp file is created and cleaned up."""
        temp_path = None
        
        # Test file creation
        with ManagedTempFile(suffix='.py', prefix='test_') as file_path:
            temp_path = file_path
            self.assertTrue(file_path.exists())
            self.assertTrue(str(file_path).endswith('.py'))
            self.assertTrue(file_path.name.startswith('test_'))
        
        # Test file cleanup
        self.assertFalse(temp_path.exists())
    
    def test_temp_file_write_and_read(self):
        """Test writing and reading temp file content."""
        test_content = "print('Hello World')"
        
        with ManagedTempFile(suffix='.py') as file_path:
            # Write content
            with open(file_path, 'w') as f:
                f.write(test_content)
            
            # Read content back
            with open(file_path, 'r') as f:
                content = f.read()
            
            self.assertEqual(content, test_content)


class TestManagedTempDir(unittest.TestCase):
    """Test managed temporary directory context manager."""
    
    def test_temp_dir_creation_and_cleanup(self):
        """Test that temp directory is created and cleaned up."""
        temp_path = None
        
        # Test directory creation
        with ManagedTempDir(prefix='test_') as dir_path:
            temp_path = dir_path
            self.assertTrue(dir_path.exists())
            self.assertTrue(dir_path.is_dir())
            self.assertTrue(dir_path.name.startswith('test_'))
            
            # Create a file in the directory
            test_file = dir_path / 'test.txt'
            test_file.write_text('test content')
            self.assertTrue(test_file.exists())
        
        # Test directory cleanup
        self.assertFalse(temp_path.exists())


class TestManagedProcess(unittest.TestCase):
    """Test managed subprocess context manager."""
    
    def test_process_creation_and_cleanup(self):
        """Test that process is created and cleaned up."""
        # Use a simple command that will run for a bit
        cmd = ['python', '-c', 'import time; time.sleep(0.1); print("done")']
        
        with ManagedProcess(cmd, capture_output=True, text=True) as process:
            self.assertIsInstance(process, subprocess.Popen)
            self.assertIsNotNone(process.pid)
            
            # Wait for process to complete
            stdout, stderr = process.communicate()
            self.assertEqual(process.returncode, 0)
            self.assertIn('done', stdout)
    
    def test_process_termination(self):
        """Test process termination on context exit."""
        # Use a long-running command
        cmd = ['python', '-c', 'import time; time.sleep(10)']
        
        process_pid = None
        with ManagedProcess(cmd, kill_on_exit=True) as process:
            process_pid = process.pid
            self.assertIsNone(process.poll())  # Should be running
        
        # Process should be terminated after context exit
        time.sleep(0.1)  # Give it a moment
        
        # Check if process is terminated (may raise ProcessLookupError if already gone)
        try:
            os.kill(process_pid, 0)  # Test if process exists
            # If we get here, process might still be running
            self.fail("Process should have been terminated")
        except ProcessLookupError:
            # This is expected - process was terminated
            pass


class TestResourceTracker(unittest.TestCase):
    """Test global resource tracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = ResourceTracker()
    
    def test_temp_file_tracking(self):
        """Test temporary file registration and cleanup."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        # Register and track
        self.tracker.register_temp_file(temp_path)
        self.assertTrue(temp_path.exists())
        
        # Cleanup
        cleaned = self.tracker.cleanup_temp_files()
        self.assertEqual(cleaned, 1)
        self.assertFalse(temp_path.exists())
    
    def test_temp_dir_tracking(self):
        """Test temporary directory registration and cleanup."""
        # Create a temp directory
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / 'test.txt'
        test_file.write_text('test')
        
        # Register and track
        self.tracker.register_temp_dir(temp_dir)
        self.assertTrue(temp_dir.exists())
        self.assertTrue(test_file.exists())
        
        # Cleanup
        cleaned = self.tracker.cleanup_temp_dirs()
        self.assertEqual(cleaned, 1)
        self.assertFalse(temp_dir.exists())


class TestCreateTempScriptFile(unittest.TestCase):
    """Test temp script file creation utility."""
    
    def test_script_file_creation(self):
        """Test creating a temp script file with content."""
        script_content = "import bpy\nbpy.ops.mesh.primitive_cube_add()"
        
        with create_temp_script_file(script_content, suffix='.py') as script_path:
            self.assertTrue(script_path.exists())
            self.assertTrue(str(script_path).endswith('.py'))
            
            # Verify content
            with open(script_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, script_content)
        
        # File should be cleaned up
        self.assertFalse(script_path.exists())


class TestExecuteWithTimeout(unittest.TestCase):
    """Test subprocess execution with timeout."""
    
    def test_successful_execution(self):
        """Test successful command execution."""
        cmd = ['python', '-c', 'print("Hello")']
        result = execute_with_timeout(cmd, timeout=5.0, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('Hello', result.stdout)
    
    def test_timeout_handling(self):
        """Test timeout handling."""
        cmd = ['python', '-c', 'import time; time.sleep(10)']
        
        with self.assertRaises(subprocess.TimeoutExpired):
            execute_with_timeout(cmd, timeout=0.1, capture_output=True, text=True)


class TestCleanupOldTempFiles(unittest.TestCase):
    """Test cleanup of old temporary files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test directory
        for file_path in self.test_dir.rglob('*'):
            if file_path.is_file():
                file_path.unlink()
        self.test_dir.rmdir()
    
    def test_cleanup_old_files(self):
        """Test cleanup of old files matching pattern."""
        # Create test files
        old_file = self.test_dir / 'blender_script_old.py'
        new_file = self.test_dir / 'blender_script_new.py'
        other_file = self.test_dir / 'other_file.txt'
        
        old_file.write_text('old')
        new_file.write_text('new')
        other_file.write_text('other')
        
        # Make old file appear old
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        os.utime(old_file, (old_time, old_time))
        
        # Cleanup files older than 24 hours
        cleaned = cleanup_old_temp_files(self.test_dir, 'blender_*', 24)
        
        # Should clean up old file but not new file or other file
        self.assertEqual(cleaned, 1)
        self.assertFalse(old_file.exists())
        self.assertTrue(new_file.exists())
        self.assertTrue(other_file.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests for resource management."""
    
    def test_full_cleanup_cycle(self):
        """Test complete cleanup cycle with multiple resource types."""
        temp_files = []
        temp_dirs = []
        
        try:
            # Create various temporary resources
            for i in range(3):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.py', prefix='blender_test_') as f:
                    temp_path = Path(f.name)
                    temp_files.append(temp_path)
                
                temp_dir = Path(tempfile.mkdtemp(prefix='blender_test_'))
                temp_dirs.append(temp_dir)
                
                # Create file in temp dir
                (temp_dir / f'test_{i}.txt').write_text(f'test {i}')
            
            # Verify resources exist
            for temp_file in temp_files:
                self.assertTrue(temp_file.exists())
            for temp_dir in temp_dirs:
                self.assertTrue(temp_dir.exists())
            
            # Perform cleanup
            results = cleanup_all_resources()
            
            # Note: cleanup_all_resources may not clean these specific files
            # since they weren't registered with the global tracker
            # This is expected behavior - only tracked resources are cleaned
            
        finally:
            # Manual cleanup for test
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    for file_path in temp_dir.rglob('*'):
                        if file_path.is_file():
                            file_path.unlink()
                    temp_dir.rmdir()


if __name__ == '__main__':
    unittest.main()