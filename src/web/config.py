"""
Configuration management for the Flask web application.

This module handles all configuration loading including environment variables,
.env file parsing, and default values.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Application configuration manager."""
    
    def __init__(self):
        """Initialize configuration by loading from environment and .env file."""
        self._load_env_file()
        self._setup_logging()
    
    def _load_env_file(self) -> None:
        """Load environment variables from .env file if it exists."""
        env_file = Path(__file__).parent.parent.parent / '.env'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"\'')
                        os.environ[key] = value
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @property
    def flask_config(self) -> Dict[str, Any]:
        """Get Flask application configuration."""
        return {
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
            'BLENDER_PATH': os.environ.get('BLENDER_EXECUTABLE_PATH', 'blender'),
            'BLENDER_TIMEOUT': int(os.environ.get('BLENDER_TIMEOUT', '30')),
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file upload
        }
    
    @property
    def port(self) -> int:
        """Get application port."""
        return int(os.environ.get('PORT', '5001'))
    
    @property
    def host(self) -> str:
        """Get application host."""
        return os.environ.get('HOST', '127.0.0.1')
    
    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Get Anthropic API key for AI integration."""
        return os.environ.get('ANTHROPIC_API_KEY')
    
    @property
    def export_dir(self) -> Path:
        """Get export directory path."""
        export_dir = os.environ.get('EXPORT_DIR', './exports')
        return Path(export_dir).resolve()
    
    @property
    def preview_dir(self) -> Path:
        """Get preview directory path."""
        return Path(__file__).parent.parent.parent / "previews"
    
    @property
    def scenes_dir(self) -> Path:
        """Get scenes directory path."""
        return Path(__file__).parent.parent.parent / "scenes"


# Global configuration instance
config = Config()