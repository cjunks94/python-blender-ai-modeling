"""
Tests for the dependency management system.

This module tests the DependencyManager class and service initialization.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web.services.dependency_manager import DependencyManager, ServiceStatus


class TestDependencyManager(unittest.TestCase):
    """Test cases for dependency management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dependency_manager = DependencyManager()
    
    def test_service_availability_checking(self):
        """Test service availability checking methods."""
        # Test checking available services
        self.assertIsInstance(self.dependency_manager.is_available('blender'), bool)
        self.assertIsInstance(self.dependency_manager.is_available('export'), bool)
        self.assertIsInstance(self.dependency_manager.is_available('ai'), bool)
        self.assertIsInstance(self.dependency_manager.is_available('scene_management'), bool)
        
        # Test checking non-existent service
        self.assertFalse(self.dependency_manager.is_available('non_existent_service'))
    
    def test_service_status_structure(self):
        """Test service status data structure."""
        status = self.dependency_manager.get_service_status('blender')
        
        if status:
            self.assertIsInstance(status, ServiceStatus)
            self.assertIsInstance(status.available, bool)
            
            if not status.available:
                self.assertIsInstance(status.error_message, str)
            else:
                self.assertIsNotNone(status.service_instance)
    
    def test_get_all_statuses(self):
        """Test getting all service statuses."""
        all_statuses = self.dependency_manager.get_all_statuses()
        
        expected_services = ['blender', 'export', 'ai', 'scene_management']
        for service in expected_services:
            self.assertIn(service, all_statuses)
            self.assertIsInstance(all_statuses[service], bool)
    
    def test_health_check_format(self):
        """Test health check response format."""
        health = self.dependency_manager.get_health_check()
        
        required_fields = [
            'status', 'version', 'blender_available', 
            'export_available', 'ai_available', 'scene_management_available',
            'scene_preview_available', 'scene_export_available'
        ]
        
        for field in required_fields:
            self.assertIn(field, health)
        
        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(health['version'], '0.1.0')
        
        # Boolean fields
        boolean_fields = [
            'blender_available', 'export_available', 'ai_available',
            'scene_management_available', 'scene_preview_available', 'scene_export_available'
        ]
        for field in boolean_fields:
            self.assertIsInstance(health[field], bool)
    
    @patch('web.services.dependency_manager.logger')
    def test_service_initialization_logging(self, mock_logger):
        """Test that service initialization is properly logged."""
        # Create a new dependency manager to trigger initialization
        DependencyManager()
        
        # Check that info logs were called (services successfully initialized)
        mock_logger.info.assert_called()
        
        # Check for expected log messages
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        expected_messages = [
            'Blender integration services initialized successfully',
            'Export services initialized successfully',
            'AI integration services initialized successfully',
            'Scene management services initialized successfully'
        ]
        
        # At least some services should have initialized successfully
        successful_initializations = [msg for msg in log_calls if msg in expected_messages]
        self.assertGreater(len(successful_initializations), 0)
    
    def test_service_instance_retrieval(self):
        """Test retrieving service instances."""
        # Test getting available service
        if self.dependency_manager.is_available('blender'):
            blender_service = self.dependency_manager.get_service('blender')
            self.assertIsNotNone(blender_service)
            self.assertIsInstance(blender_service, dict)
            
            # Check expected keys in service instance
            expected_keys = ['executor_class', 'generator_class', 'renderer_class', 'exceptions']
            for key in expected_keys:
                self.assertIn(key, blender_service)
        
        # Test getting unavailable service
        unavailable_service = self.dependency_manager.get_service('non_existent_service')
        self.assertIsNone(unavailable_service)
    
    @patch('web.services.dependency_manager.sys.path')
    def test_import_path_setup(self, mock_path):
        """Test that import paths are set up correctly."""
        # Import path should be modified during initialization
        DependencyManager()
        mock_path.insert.assert_called()
    
    def test_conditional_service_loading(self):
        """Test that optional services are handled gracefully."""
        # Scene preview and export services are optional
        scene_services = self.dependency_manager.get_service('scene_management')
        
        if scene_services:
            # Should always have core services
            self.assertIn('manager_class', scene_services)
            self.assertIn('validator_class', scene_services)
            
            # Optional services may or may not be present
            optional_services = ['preview_renderer', 'scene_exporter']
            for service in optional_services:
                if service in scene_services:
                    self.assertIsNotNone(scene_services[service])


class TestServiceStatus(unittest.TestCase):
    """Test cases for ServiceStatus dataclass."""
    
    def test_service_status_creation(self):
        """Test ServiceStatus dataclass creation."""
        # Available service
        available_status = ServiceStatus(
            available=True,
            service_instance={'test': 'data'}
        )
        
        self.assertTrue(available_status.available)
        self.assertIsNone(available_status.error_message)
        self.assertEqual(available_status.service_instance, {'test': 'data'})
        
        # Unavailable service
        unavailable_status = ServiceStatus(
            available=False,
            error_message="Service not found"
        )
        
        self.assertFalse(unavailable_status.available)
        self.assertEqual(unavailable_status.error_message, "Service not found")
        self.assertIsNone(unavailable_status.service_instance)


if __name__ == '__main__':
    unittest.main()