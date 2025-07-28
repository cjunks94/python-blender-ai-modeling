"""Tests for main application entry point."""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestMainApplication(unittest.TestCase):
    """Test cases for main application functionality."""
    
    @patch('main.MainWindow')
    @patch('main.setup_logging')
    def test_main_function_success(self, mock_setup_logging, mock_main_window):
        """Test successful application startup."""
        # Import main after patching to avoid import errors
        import main
        
        mock_app = MagicMock()
        mock_main_window.return_value = mock_app
        
        # Run main function
        main.main()
        
        # Verify setup was called
        mock_setup_logging.assert_called_once()
        mock_main_window.assert_called_once()
        mock_app.run.assert_called_once()
    
    @patch('main.MainWindow')
    @patch('main.setup_logging')
    def test_main_function_keyboard_interrupt(self, mock_setup_logging, mock_main_window):
        """Test application handles keyboard interrupt gracefully."""
        import main
        
        mock_app = MagicMock()
        mock_app.run.side_effect = KeyboardInterrupt()
        mock_main_window.return_value = mock_app
        
        # Should not raise exception
        main.main()
        
        mock_setup_logging.assert_called_once()
        mock_main_window.assert_called_once()
    
    @patch('main.MainWindow')
    @patch('main.setup_logging')
    @patch('sys.exit')
    def test_main_function_exception(self, mock_exit, mock_setup_logging, mock_main_window):
        """Test application handles exceptions and exits properly."""
        import main
        
        mock_app = MagicMock()
        mock_app.run.side_effect = Exception("Test error")
        mock_main_window.return_value = mock_app
        
        main.main()
        
        mock_setup_logging.assert_called_once()
        mock_main_window.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    def test_setup_logging(self):
        """Test logging configuration."""
        import main
        
        # Should not raise exception
        main.setup_logging()


if __name__ == '__main__':
    unittest.main()