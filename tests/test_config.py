"""
Tests for the configuration management system.

This module tests the Config class and environment variable handling.
"""

import os
import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original environment
        self.original_env = dict(os.environ)
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_config_initialization(self):
        """Test config initialization with defaults."""
        config = Config()
        
        # Test default values
        self.assertEqual(config.port, 5001)
        self.assertEqual(config.host, '127.0.0.1')
        self.assertIn('SECRET_KEY', config.flask_config)
        self.assertEqual(config.flask_config['BLENDER_PATH'], 'blender')
        self.assertEqual(config.flask_config['BLENDER_TIMEOUT'], 30)
    
    def test_config_with_environment_variables(self):
        """Test config with custom environment variables."""
        os.environ.update({
            'PORT': '8080',
            'HOST': '0.0.0.0',
            'BLENDER_EXECUTABLE_PATH': '/custom/blender',
            'BLENDER_TIMEOUT': '60',
            'FLASK_DEBUG': 'true'
        })
        
        config = Config()
        
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.host, '0.0.0.0')
        self.assertEqual(config.flask_config['BLENDER_PATH'], '/custom/blender')
        self.assertEqual(config.flask_config['BLENDER_TIMEOUT'], 60)
        self.assertTrue(config.flask_config['DEBUG'])
    
    @patch('builtins.open', mock_open(read_data='ANTHROPIC_API_KEY=test-key\nPORT=9000\n'))
    @patch('pathlib.Path.exists', return_value=True)
    def test_env_file_loading(self, mock_exists):
        """Test loading configuration from .env file."""
        config = Config()
        
        self.assertEqual(config.anthropic_api_key, 'test-key')
        self.assertEqual(config.port, 9000)
    
    @patch('builtins.open', mock_open(read_data='INVALID_LINE\nVALID_KEY=value\n# Comment line\n'))
    @patch('pathlib.Path.exists', return_value=True)
    def test_env_file_parsing_robustness(self, mock_exists):
        """Test .env file parsing handles malformed lines gracefully."""
        # Should not raise exception
        config = Config()
        # Valid key should still be loaded
        self.assertEqual(os.environ.get('VALID_KEY'), 'value')
    
    def test_directory_properties(self):
        """Test directory path properties."""
        config = Config()
        
        # Test that directories are Path objects
        self.assertIsInstance(config.export_dir, Path)
        self.assertIsInstance(config.preview_dir, Path)
        self.assertIsInstance(config.scenes_dir, Path)
        
        # Test default paths
        self.assertTrue(str(config.export_dir).endswith('exports'))
        self.assertTrue(str(config.preview_dir).endswith('previews'))
        self.assertTrue(str(config.scenes_dir).endswith('scenes'))
    
    def test_anthropic_api_key_optional(self):
        """Test that Anthropic API key is optional."""
        config = Config()
        
        # Without API key set, should return None
        api_key = config.anthropic_api_key
        self.assertIsNone(api_key)
        
        # With API key set
        os.environ['ANTHROPIC_API_KEY'] = 'test-key-123'
        config_with_key = Config()
        self.assertEqual(config_with_key.anthropic_api_key, 'test-key-123')


if __name__ == '__main__':
    unittest.main()