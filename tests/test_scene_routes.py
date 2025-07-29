"""
Tests for scene management routes.

This module tests the Flask routes for scene management functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web.app_factory import create_app


class TestSceneRoutes(unittest.TestCase):
    """Test cases for scene management routes."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test app with scene management enabled
        test_config = {
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key'
        }
        
        # Mock scene management availability
        with patch('web.services.dependency_manager.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = True
            mock_dep.get_service.return_value = {
                'manager_class': MagicMock,
                'validator_class': MagicMock
            }
            
            self.app = create_app(test_config)
            self.client = self.app.test_client()
            self.app_context = self.app.app_context()
            self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_list_scenes_endpoint(self):
        """Test the /api/scenes endpoint."""
        mock_scenes = [
            {
                'scene_id': 'test_scene_1',
                'name': 'Test Scene 1',
                'description': 'A test scene',
                'object_count': 2,
                'created_at': '2024-01-01T00:00:00'
            }
        ]
        
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_manager.list_scenes.return_value = mock_scenes
            
            response = self.client.get('/api/scenes')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['scenes']), 1)
            self.assertEqual(data['scenes'][0]['scene_id'], 'test_scene_1')
    
    def test_create_scene_endpoint(self):
        """Test the /api/scenes POST endpoint."""
        scene_data = {
            'name': 'New Test Scene',
            'description': 'A newly created test scene'
        }
        
        mock_scene = MagicMock()
        mock_scene.scene_id = 'new_scene_123'
        mock_scene.name = 'New Test Scene'
        mock_scene.description = 'A newly created test scene'
        mock_scene.object_count = 0
        mock_scene.created_at.isoformat.return_value = '2024-01-01T00:00:00'
        
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_manager.create_scene.return_value = mock_scene
            
            response = self.client.post('/api/scenes',
                                      data=json.dumps(scene_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['scene']['scene_id'], 'new_scene_123')
            
            # Verify scene manager was called correctly
            mock_manager.create_scene.assert_called_once_with(
                scene_data['name'], scene_data['description']
            )
    
    def test_create_scene_validation_errors(self):
        """Test scene creation with validation errors."""
        # Missing name
        invalid_data = {'description': 'Missing name'}
        response = self.client.post('/api/scenes',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Name is required', data['error'])
        
        # Missing description
        invalid_data = {'name': 'Test Scene'}
        response = self.client.post('/api/scenes',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Description is required', data['error'])
    
    def test_get_scene_endpoint(self):
        """Test the /api/scenes/<scene_id> GET endpoint."""
        mock_scene = MagicMock()
        mock_scene.scene_id = 'test_scene_1'
        mock_scene.name = 'Test Scene'
        mock_scene.description = 'A test scene'
        mock_scene.objects = []
        mock_scene.to_dict.return_value = {
            'scene_id': 'test_scene_1',
            'name': 'Test Scene',
            'description': 'A test scene',
            'objects': []
        }
        
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_manager.get_scene.return_value = mock_scene
            
            response = self.client.get('/api/scenes/test_scene_1')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['scene']['scene_id'], 'test_scene_1')
    
    def test_get_scene_not_found(self):
        """Test getting a non-existent scene."""
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_manager.get_scene.return_value = None
            
            response = self.client.get('/api/scenes/nonexistent')
            
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('Scene not found', data['error'])
    
    def test_scene_preview_endpoint(self):
        """Test the /api/scenes/<scene_id>/preview endpoint."""
        with patch.object(self.app, 'scene_preview_renderer', create=True) as mock_renderer:
            mock_renderer.render_scene_preview.return_value = {
                'success': True,
                'preview_path': '/path/to/preview.png'
            }
            
            response = self.client.post('/api/scenes/test_scene/preview')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('preview_path', data)
    
    def test_scene_preview_service_unavailable(self):
        """Test scene preview when service is unavailable."""
        # App without scene_preview_renderer attribute
        response = self.client.post('/api/scenes/test_scene/preview')
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Scene preview not available', data['error'])
    
    def test_scene_export_endpoint(self):
        """Test the /api/scenes/<scene_id>/export endpoint."""
        export_data = {
            'format': 'obj',
            'export_type': 'complete'
        }
        
        with patch.object(self.app, 'scene_exporter', create=True) as mock_exporter:
            mock_exporter.export_complete_scene.return_value = {
                'success': True,
                'export_path': '/path/to/export.obj'
            }
            
            response = self.client.post('/api/scenes/test_scene/export',
                                      data=json.dumps(export_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('export_path', data)
    
    def test_scene_export_validation(self):
        """Test scene export with validation errors."""
        # Invalid format
        invalid_data = {'format': 'invalid', 'export_type': 'complete'}
        response = self.client.post('/api/scenes/test_scene/export',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid format', data['error'])
        
        # Invalid export type
        invalid_data = {'format': 'obj', 'export_type': 'invalid'}
        response = self.client.post('/api/scenes/test_scene/export',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid export_type', data['error'])
    
    def test_scene_validate_endpoint(self):
        """Test the /api/scenes/<scene_id>/validate endpoint."""
        with patch.object(self.app, 'scene_validator') as mock_validator:
            mock_validator.validate_scene.return_value = {
                'valid': True,
                'warnings': [],
                'errors': []
            }
            
            response = self.client.get('/api/scenes/test_scene/validate')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertTrue(data['validation']['valid'])
    
    def test_scene_composition_endpoint(self):
        """Test the /api/scenes/<scene_id>/compose endpoint."""
        composition_data = {
            'operation': 'align',
            'axis': 'x',
            'mode': 'center'
        }
        
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_scene = MagicMock()
            mock_manager.get_scene.return_value = mock_scene
            
            with patch('web.routes.scene_routes.SceneCompositor') as mock_compositor_class:
                mock_compositor = MagicMock()
                mock_compositor_class.return_value = mock_compositor
                mock_compositor.align_objects.return_value = True
                
                response = self.client.post('/api/scenes/test_scene/compose',
                                          data=json.dumps(composition_data),
                                          content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertIn('Objects aligned successfully', data['message'])
    
    def test_scene_composition_validation(self):
        """Test scene composition with validation errors."""
        # Invalid operation
        invalid_data = {'operation': 'invalid'}
        response = self.client.post('/api/scenes/test_scene/compose',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid operation', data['error'])
    
    def test_delete_scene_endpoint(self):
        """Test the /api/scenes/<scene_id> DELETE endpoint."""
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_manager.delete_scene.return_value = True
            
            response = self.client.delete('/api/scenes/test_scene')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('Scene deleted successfully', data['message'])
            
            # Verify scene manager was called
            mock_manager.delete_scene.assert_called_once_with('test_scene')
    
    def test_delete_scene_failure(self):
        """Test scene deletion failure."""
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_manager.delete_scene.return_value = False
            
            response = self.client.delete('/api/scenes/test_scene')
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('Failed to delete scene', data['error'])
    
    def test_scene_statistics_endpoint(self):
        """Test the /api/scenes/<scene_id>/statistics endpoint."""
        mock_stats = {
            'scene_id': 'test_scene',
            'name': 'Test Scene',
            'object_count': 3,
            'export_ready_count': 2,
            'object_types': {'cube': 2, 'sphere': 1},
            'total_relationships': 1,
            'collisions': 0
        }
        
        with patch.object(self.app, 'scene_manager') as mock_manager:
            mock_manager.get_scene_statistics.return_value = mock_stats
            
            response = self.client.get('/api/scenes/test_scene/statistics')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['statistics']['object_count'], 3)
            self.assertEqual(data['statistics']['collisions'], 0)
    
    def test_error_handling_missing_scene_manager(self):
        """Test error handling when scene manager is not available."""
        # Create app without scene management
        with patch('web.services.dependency_manager.dependency_manager') as mock_dep:
            mock_dep.is_available.return_value = False
            
            test_app = create_app({'TESTING': True})
            client = test_app.test_client()
            
            # Scene routes should not be registered when scene management is unavailable
            response = client.get('/api/scenes')
            self.assertEqual(response.status_code, 404)
    
    def test_json_parsing_errors(self):
        """Test handling of JSON parsing errors."""
        # Invalid JSON
        response = self.client.post('/api/scenes',
                                  data='{"invalid": json}',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid JSON', data['error'])


if __name__ == '__main__':
    unittest.main()