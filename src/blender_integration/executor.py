"""
Blender subprocess execution module.

This module provides functionality to execute Blender Python scripts
via subprocess calls in background mode.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import ast


class BlenderExecutionError(Exception):
    """Exception raised when Blender execution fails."""
    pass


class BlenderScriptError(Exception):
    """Exception raised when Blender script is invalid."""
    pass


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
        Execute a Blender Python script.
        
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
        
        # Create temporary script file
        script_file = self._create_temp_script_file(script_content)
        
        try:
            # Build Blender command
            cmd = self._build_blender_command(script_file, output_file)
            
            # Execute command
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False  # Don't raise exception on non-zero return code
                )
                
                return BlenderExecutionResult(
                    success=result.returncode == 0,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    output_file=output_file
                )
                
            except subprocess.TimeoutExpired as e:
                raise BlenderExecutionError(f"Blender execution timeout after {self.timeout} seconds")
            
            except FileNotFoundError as e:
                raise BlenderExecutionError(f"Blender executable not found at path: {self.blender_path}")
            
        finally:
            # Clean up temporary script file
            if script_file.exists():
                script_file.unlink()
    
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
            raise BlenderScriptError(f"Invalid Python syntax: {e}")
    
    def _create_temp_script_file(self, script_content: str) -> Path:
        """
        Create a temporary Python script file.
        
        Args:
            script_content: Python script content
            
        Returns:
            Path to temporary script file
        """
        # Create temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.py', prefix='blender_script_')
        
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(script_content)
        except Exception:
            # If writing fails, clean up the file descriptor
            os.close(fd)
            raise
        
        return Path(temp_path)
    
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