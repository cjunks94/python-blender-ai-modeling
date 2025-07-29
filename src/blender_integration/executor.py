"""
Blender subprocess execution module.

This module provides functionality to execute Blender Python scripts
via subprocess calls in background mode.
"""

import subprocess
import tempfile
import os
import time
import logging
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import ast
import re
import sys

# Add utils to path for resource manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.resource_manager import (
    ManagedTempFile, 
    create_temp_script_file, 
    execute_with_timeout,
    cleanup_old_temp_files
)

logger = logging.getLogger(__name__)


class BlenderExecutionError(Exception):
    """Exception raised when Blender execution fails."""
    
    def __init__(self, message: str, error_type: str = "execution"):
        """
        Initialize BlenderExecutionError with categorized error type.
        
        Args:
            message: Error message
            error_type: Type of error (execution, timeout, permission, memory, etc.)
        """
        super().__init__(message)
        self.error_type = error_type


class BlenderScriptError(Exception):
    """Exception raised when Blender script is invalid."""
    
    def __init__(self, message: str, error_type: str = "script"):
        """
        Initialize BlenderScriptError with categorized error type.
        
        Args:
            message: Error message
            error_type: Type of error (script, syntax, security, etc.)
        """
        super().__init__(message)
        self.error_type = error_type


@dataclass
class BlenderExecutionResult:
    """Result of Blender script execution."""
    success: bool
    return_code: int
    stdout: str
    stderr: str
    output_file: Optional[str] = None


class BlenderExecutor:
    """Executes Blender Python scripts via subprocess."""
    
    def __init__(self, blender_path: str = 'blender', timeout: int = 30):
        """
        Initialize BlenderExecutor.
        
        Args:
            blender_path: Path to Blender executable
            timeout: Maximum execution time in seconds
        """
        self.blender_path = blender_path
        self.timeout = timeout
    
    def execute_script(self, script_content: str, output_file: Optional[str] = None) -> BlenderExecutionResult:
        """
        Execute a Blender Python script with automatic resource cleanup.
        
        Args:
            script_content: Python script to execute in Blender
            output_file: Optional output file path
            
        Returns:
            BlenderExecutionResult with execution details
            
        Raises:
            BlenderExecutionError: If execution fails due to system issues
        """
        # Validate script first
        self.validate_script(script_content)
        
        # Use managed temporary script file with automatic cleanup
        with create_temp_script_file(script_content, suffix='.py') as script_file:
            try:
                # Build Blender command
                cmd = self._build_blender_command(script_file, output_file)
                
                # Execute command with managed process and timeout
                try:
                    result = execute_with_timeout(
                        cmd,
                        timeout=self.timeout,
                        capture_output=True,
                        text=True
                    )
                    
                    return BlenderExecutionResult(
                        success=result.returncode == 0,
                        return_code=result.returncode,
                        stdout=result.stdout or "",
                        stderr=result.stderr or "",
                        output_file=output_file
                    )
                    
                except subprocess.TimeoutExpired as e:
                    raise BlenderExecutionError(
                        f"Blender execution timeout after {self.timeout} seconds", 
                        error_type="timeout"
                    )
                
                except FileNotFoundError as e:
                    raise BlenderExecutionError(
                        f"Blender executable not found at path: {self.blender_path}",
                        error_type="not_found"
                    )
                
                except PermissionError as e:
                    raise BlenderExecutionError(
                        f"Permission denied accessing Blender at path: {self.blender_path}",
                        error_type="permission"
                    )
                
                except MemoryError as e:
                    raise BlenderExecutionError(
                        "Insufficient memory to execute Blender script",
                        error_type="memory"
                    )
                
            except RuntimeError as e:
                # Handle script file creation errors
                raise BlenderExecutionError(
                    f"Failed to create temporary script file: {str(e)}",
                    error_type="file_creation"
                )
    
    def validate_script(self, script_content: str) -> None:
        """
        Validate Python script syntax.
        
        Args:
            script_content: Python script to validate
            
        Raises:
            BlenderScriptError: If script is invalid
        """
        if not script_content or script_content is None:
            raise BlenderScriptError("Script content cannot be empty or None")
        
        if not isinstance(script_content, str):
            raise BlenderScriptError("Script content must be a string")
        
        # Check for basic Python syntax
        try:
            ast.parse(script_content)
        except SyntaxError as e:
            raise BlenderScriptError(f"Invalid Python syntax: {e}", error_type="syntax")
        except IndentationError as e:
            raise BlenderScriptError(f"Invalid Python indentation: {e}", error_type="indentation")
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files created by Blender operations.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
            
        Returns:
            Number of files cleaned up
        """
        temp_dir = Path(tempfile.gettempdir())
        patterns = ['blender_script_*', 'blender_*', 'tmp*_preview.png']
        
        total_cleaned = 0
        for pattern in patterns:
            cleaned = cleanup_old_temp_files(temp_dir, pattern, max_age_hours)
            total_cleaned += cleaned
            
        if total_cleaned > 0:
            logger.info(f"Cleaned up {total_cleaned} old temporary files")
            
        return total_cleaned
    
    def _build_blender_command(self, script_file: Path, output_file: Optional[str] = None) -> List[str]:
        """
        Build Blender command line arguments.
        
        Args:
            script_file: Path to Python script file
            output_file: Optional output file path
            
        Returns:
            List of command arguments
        """
        cmd = [
            self.blender_path,
            '--background',  # Run without UI
            '--python', str(script_file)
        ]
        
        # Add output file parameter if specified
        if output_file:
            cmd.extend(['--', '--output', output_file])
        
        return cmd
    
    def execute_script_with_retry(self, script_content: str, output_file: Optional[str] = None, 
                                max_retries: int = 3, retry_delay: float = 1.0) -> BlenderExecutionResult:
        """
        Execute a Blender Python script with retry mechanism for transient failures.
        
        Args:
            script_content: Python script to execute in Blender
            output_file: Optional output file path
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            BlenderExecutionResult with execution details
            
        Raises:
            BlenderExecutionError: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.execute_script(script_content, output_file)
            
            except BlenderExecutionError as e:
                last_exception = e
                
                # Only retry on specific error types (timeout, temporary system issues)
                if e.error_type in ["timeout", "memory"] and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    # Don't retry on permanent errors like file not found, permission denied
                    raise
        
        # If we exhausted all retries
        raise BlenderExecutionError(
            f"Script execution failed after {max_retries} retries. Last error: {last_exception}",
            error_type="max_retries"
        )
    
    def validate_script_security(self, script_content: str) -> None:
        """
        Perform security validation on script content to prevent dangerous operations.
        
        Args:
            script_content: Python script to validate
            
        Raises:
            BlenderScriptError: If script contains potentially dangerous operations
        """
        if not script_content or script_content is None:
            raise BlenderScriptError("Script content cannot be empty or None")
        
        # Define patterns for potentially dangerous operations
        dangerous_patterns = [
            r'import\s+os\s*;.*os\.(system|popen|exec)',  # OS system calls
            r'import\s+subprocess',  # Subprocess calls
            r'import\s+shutil',  # File system operations
            r'__import__\s*\(',  # Dynamic imports
            r'eval\s*\(',  # Code evaluation
            r'exec\s*\(',  # Code execution
            r'open\s*\([^)]*["\'][^"\']*\.(py|sh|bat|cmd)["\'][^)]*["\']w["\']',  # File writing
        ]
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, script_content, re.IGNORECASE):
                raise BlenderScriptError(
                    f"Script contains potentially dangerous operations. Security validation failed.",
                    error_type="security"
                )
        
        # Also run basic syntax validation
        self.validate_script(script_content)