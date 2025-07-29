"""
Resource management utilities for temp files and subprocess cleanup.

This module provides context managers and utilities for proper cleanup
of temporary files, subprocess calls, and other system resources.
"""

import atexit
import contextlib
import logging
import os
import signal
import subprocess
import tempfile
import threading
import time
import weakref
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, ContextManager
import uuid


logger = logging.getLogger(__name__)


class ResourceTracker:
    """Global registry for tracking and cleaning up resources."""
    
    def __init__(self):
        self._temp_files: Set[Path] = set()
        self._temp_dirs: Set[Path] = set()
        self._processes: Dict[int, subprocess.Popen] = {}
        self._lock = threading.RLock()
        self._cleanup_registered = False
        
    def register_temp_file(self, file_path: Union[str, Path]) -> None:
        """Register a temporary file for cleanup."""
        with self._lock:
            self._temp_files.add(Path(file_path))
            self._ensure_cleanup_registered()
    
    def register_temp_dir(self, dir_path: Union[str, Path]) -> None:
        """Register a temporary directory for cleanup."""
        with self._lock:
            self._temp_dirs.add(Path(dir_path))
            self._ensure_cleanup_registered()
    
    def register_process(self, process: subprocess.Popen) -> None:
        """Register a subprocess for cleanup."""
        with self._lock:
            if process.pid:
                self._processes[process.pid] = process
                self._ensure_cleanup_registered()
    
    def unregister_temp_file(self, file_path: Union[str, Path]) -> None:
        """Remove a temporary file from tracking."""
        with self._lock:
            self._temp_files.discard(Path(file_path))
    
    def unregister_temp_dir(self, dir_path: Union[str, Path]) -> None:
        """Remove a temporary directory from tracking."""
        with self._lock:
            self._temp_dirs.discard(Path(dir_path))
    
    def unregister_process(self, process: subprocess.Popen) -> None:
        """Remove a subprocess from tracking."""
        with self._lock:
            if process.pid and process.pid in self._processes:
                del self._processes[process.pid]
    
    def cleanup_temp_files(self) -> int:
        """Clean up all tracked temporary files."""
        cleaned = 0
        with self._lock:
            for file_path in list(self._temp_files):
                try:
                    if file_path.exists():
                        file_path.unlink()
                        cleaned += 1
                        logger.debug(f"Cleaned up temp file: {file_path}")
                except (OSError, FileNotFoundError) as e:
                    logger.warning(f"Could not clean up temp file {file_path}: {e}")
                finally:
                    self._temp_files.discard(file_path)
        return cleaned
    
    def cleanup_temp_dirs(self) -> int:
        """Clean up all tracked temporary directories."""
        cleaned = 0
        with self._lock:
            for dir_path in list(self._temp_dirs):
                try:
                    if dir_path.exists() and dir_path.is_dir():
                        # Remove all files in directory first
                        for file_path in dir_path.rglob('*'):
                            if file_path.is_file():
                                file_path.unlink()
                        # Remove directory
                        dir_path.rmdir()
                        cleaned += 1
                        logger.debug(f"Cleaned up temp dir: {dir_path}")
                except (OSError, FileNotFoundError) as e:
                    logger.warning(f"Could not clean up temp dir {dir_path}: {e}")
                finally:
                    self._temp_dirs.discard(dir_path)
        return cleaned
    
    def cleanup_processes(self, timeout: float = 5.0) -> int:
        """Clean up all tracked processes."""
        cleaned = 0
        with self._lock:
            for pid, process in list(self._processes.items()):
                try:
                    if process.poll() is None:  # Process still running
                        logger.info(f"Terminating process {pid}")
                        process.terminate()
                        
                        # Wait for graceful termination
                        try:
                            process.wait(timeout=timeout)
                            cleaned += 1
                        except subprocess.TimeoutExpired:
                            # Force kill if termination didn't work
                            logger.warning(f"Force killing process {pid}")
                            process.kill()
                            process.wait()
                            cleaned += 1
                    
                except (OSError, ProcessLookupError) as e:
                    logger.debug(f"Process {pid} already terminated: {e}")
                finally:
                    self._processes.pop(pid, None)
        return cleaned
    
    def cleanup_all(self) -> Dict[str, int]:
        """Clean up all tracked resources."""
        results = {
            'temp_files': self.cleanup_temp_files(),
            'temp_dirs': self.cleanup_temp_dirs(),
            'processes': self.cleanup_processes()
        }
        logger.info(f"Resource cleanup completed: {results}")
        return results
    
    def _ensure_cleanup_registered(self) -> None:
        """Ensure cleanup is registered with atexit."""
        if not self._cleanup_registered:
            atexit.register(self.cleanup_all)
            self._cleanup_registered = True


# Global resource tracker instance
_resource_tracker = ResourceTracker()


class ManagedTempFile:
    """Context manager for temporary files with automatic cleanup."""
    
    def __init__(self, suffix: str = '', prefix: str = 'tmp', 
                 dir: Optional[str] = None, delete_on_exit: bool = True):
        """
        Initialize managed temporary file.
        
        Args:
            suffix: File suffix
            prefix: File prefix  
            dir: Directory to create file in
            delete_on_exit: Whether to delete file when context exits
        """
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir
        self.delete_on_exit = delete_on_exit
        self.file_path: Optional[Path] = None
        self.file_descriptor: Optional[int] = None
    
    def __enter__(self) -> Path:
        """Create and return temporary file path."""
        fd, temp_path = tempfile.mkstemp(
            suffix=self.suffix, 
            prefix=self.prefix, 
            dir=self.dir
        )
        
        self.file_descriptor = fd
        self.file_path = Path(temp_path)
        
        # Register for cleanup
        _resource_tracker.register_temp_file(self.file_path)
        
        return self.file_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary file."""
        if self.file_descriptor is not None:
            try:
                os.close(self.file_descriptor)
            except OSError:
                pass  # Already closed
        
        if self.file_path and self.delete_on_exit:
            try:
                if self.file_path.exists():
                    self.file_path.unlink()
                    logger.debug(f"Cleaned up temp file: {self.file_path}")
            except (OSError, FileNotFoundError) as e:
                logger.warning(f"Could not clean up temp file {self.file_path}: {e}")
            finally:
                _resource_tracker.unregister_temp_file(self.file_path)


class ManagedTempDir:
    """Context manager for temporary directories with automatic cleanup."""
    
    def __init__(self, suffix: str = '', prefix: str = 'tmp', 
                 dir: Optional[str] = None, delete_on_exit: bool = True):
        """
        Initialize managed temporary directory.
        
        Args:
            suffix: Directory suffix
            prefix: Directory prefix
            dir: Parent directory to create temp dir in
            delete_on_exit: Whether to delete directory when context exits
        """
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir
        self.delete_on_exit = delete_on_exit
        self.dir_path: Optional[Path] = None
    
    def __enter__(self) -> Path:
        """Create and return temporary directory path."""
        temp_path = tempfile.mkdtemp(
            suffix=self.suffix,
            prefix=self.prefix,
            dir=self.dir
        )
        
        self.dir_path = Path(temp_path)
        
        # Register for cleanup
        _resource_tracker.register_temp_dir(self.dir_path)
        
        return self.dir_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary directory."""
        if self.dir_path and self.delete_on_exit:
            try:
                if self.dir_path.exists():
                    # Remove all files recursively
                    for file_path in self.dir_path.rglob('*'):
                        if file_path.is_file():
                            file_path.unlink()
                    
                    # Remove directory
                    self.dir_path.rmdir()
                    logger.debug(f"Cleaned up temp dir: {self.dir_path}")
                    
            except (OSError, FileNotFoundError) as e:
                logger.warning(f"Could not clean up temp dir {self.dir_path}: {e}")
            finally:
                _resource_tracker.unregister_temp_dir(self.dir_path)


class ManagedProcess:
    """Context manager for subprocess with automatic cleanup."""
    
    def __init__(self, cmd: List[str], timeout: Optional[float] = None, 
                 kill_on_exit: bool = True, **popen_kwargs):
        """
        Initialize managed subprocess.
        
        Args:
            cmd: Command to execute
            timeout: Optional timeout for process
            kill_on_exit: Whether to kill process when context exits
            **popen_kwargs: Additional arguments for subprocess.Popen
        """
        self.cmd = cmd
        self.timeout = timeout
        self.kill_on_exit = kill_on_exit
        self.popen_kwargs = popen_kwargs
        self.process: Optional[subprocess.Popen] = None
    
    def __enter__(self) -> subprocess.Popen:
        """Start and return subprocess."""
        # Handle capture_output for Python version compatibility
        popen_kwargs = self.popen_kwargs.copy()
        capture_output = popen_kwargs.pop('capture_output', False)
        if capture_output:
            popen_kwargs.update({
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE
            })
        
        self.process = subprocess.Popen(self.cmd, **popen_kwargs)
        
        # Register for cleanup
        _resource_tracker.register_process(self.process)
        
        return self.process
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up subprocess."""
        if self.process and self.kill_on_exit:
            try:
                if self.process.poll() is None:  # Still running
                    self.process.terminate()
                    
                    # Wait for graceful termination
                    try:
                        self.process.wait(timeout=5.0)
                    except subprocess.TimeoutExpired:
                        # Force kill
                        self.process.kill()
                        self.process.wait()
                        
                    logger.debug(f"Cleaned up process {self.process.pid}")
                    
            except (OSError, ProcessLookupError):
                pass  # Process already terminated
            finally:
                _resource_tracker.unregister_process(self.process)


def cleanup_old_temp_files(directory: Union[str, Path], 
                          pattern: str = "blender_*", 
                          max_age_hours: int = 24) -> int:
    """
    Clean up old temporary files in a directory.
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match
        max_age_hours: Maximum age of files to keep
        
    Returns:
        Number of files cleaned up
    """
    directory = Path(directory)
    if not directory.exists():
        return 0
    
    cutoff_time = time.time() - (max_age_hours * 3600)
    cleaned = 0
    
    for file_path in directory.glob(pattern):
        try:
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                cleaned += 1
                logger.debug(f"Cleaned up old temp file: {file_path}")
        except (OSError, FileNotFoundError) as e:
            logger.warning(f"Could not clean up old temp file {file_path}: {e}")
    
    return cleaned


def create_temp_script_file(content: str, suffix: str = '.py') -> ContextManager[Path]:
    """
    Create a temporary script file with automatic cleanup.
    
    Args:
        content: Script content to write
        suffix: File suffix
        
    Returns:
        Context manager yielding temporary file path
    """
    @contextlib.contextmanager
    def _temp_script():
        with ManagedTempFile(suffix=suffix, prefix='blender_script_') as temp_path:
            # Write content to file
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                yield temp_path
            except (OSError, UnicodeEncodeError) as e:
                logger.error(f"Failed to write script to temp file {temp_path}: {e}")
                raise RuntimeError(f"Failed to write script to temporary file: {e}") from e
    
    return _temp_script()


def execute_with_timeout(cmd: List[str], timeout: float = 30.0, 
                        **popen_kwargs) -> subprocess.CompletedProcess:
    """
    Execute command with timeout and proper cleanup.
    
    Args:
        cmd: Command to execute
        timeout: Timeout in seconds
        **popen_kwargs: Additional arguments for subprocess
        
    Returns:
        CompletedProcess result
        
    Raises:
        subprocess.TimeoutExpired: If command times out
    """
    # Handle capture_output for Python version compatibility
    capture_output = popen_kwargs.pop('capture_output', False)
    if capture_output:
        popen_kwargs.update({
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE
        })
    
    with ManagedProcess(cmd, timeout=timeout, **popen_kwargs) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return subprocess.CompletedProcess(
                cmd, process.returncode, stdout, stderr
            )
        except subprocess.TimeoutExpired:
            # Process will be cleaned up by context manager
            raise


# Convenience functions for global resource management
def register_temp_file(file_path: Union[str, Path]) -> None:
    """Register a temp file for global cleanup."""
    _resource_tracker.register_temp_file(file_path)


def register_temp_dir(dir_path: Union[str, Path]) -> None:
    """Register a temp directory for global cleanup."""
    _resource_tracker.register_temp_dir(dir_path)


def register_process(process: subprocess.Popen) -> None:
    """Register a process for global cleanup."""
    _resource_tracker.register_process(process)


def cleanup_all_resources() -> Dict[str, int]:
    """Clean up all registered resources."""
    return _resource_tracker.cleanup_all()


# Setup signal handlers for cleanup on termination
def _setup_signal_handlers():
    """Setup signal handlers for graceful cleanup."""
    def cleanup_handler(signum, frame):
        logger.info(f"Received signal {signum}, cleaning up resources...")
        cleanup_all_resources()
        
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, cleanup_handler)
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, cleanup_handler)


# Initialize signal handlers
_setup_signal_handlers()