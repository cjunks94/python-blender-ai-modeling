"""Tests for Flask web application."""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestWebApp(unittest.TestCase):
    """Test cases for Flask web application."""
    
    def setUp(self):
        """Set up test client."""
        from web.app import create_app
        
        self.app = create_app({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key'
        })
        self.client = self.app.test_client()
    
    def test_index_route(self):
        """Test main page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Python Blender AI Modeling', response.data)
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], '0.1.0')
        self.assertIn('blender_path', data)
    
    def test_generate_model_success(self):
        """Test successful model generation."""
        payload = {
            'object_type': 'cube',
            'size': 2.0,
            'pos_x': 0.0
        }
        
        response = self.client.post('/api/generate',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['object_type'], 'cube')
        self.assertEqual(data['status'], 'generated')
    
    def test_generate_model_missing_field(self):
        """Test model generation with missing required field."""
        payload = {
            'object_type': 'cube',
            'size': 2.0
            # Missing pos_x
        }
        
        response = self.client.post('/api/generate',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('pos_x', data['error'])
    
    def test_generate_model_invalid_object_type(self):
        """Test model generation with invalid object type."""
        payload = {
            'object_type': 'invalid_type',
            'size': 2.0,
            'pos_x': 0.0
        }
        
        response = self.client.post('/api/generate',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('Invalid object type', data['error'])
    
    def test_generate_model_invalid_size(self):
        """Test model generation with invalid size."""
        payload = {
            'object_type': 'cube',
            'size': 15.0,  # Too large
            'pos_x': 0.0
        }
        
        response = self.client.post('/api/generate',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('Size must be between', data['error'])
    
    def test_export_model_success(self):
        """Test successful model export."""
        payload = {
            'model_id': 'test_model_123',
            'format': 'obj'
        }
        
        response = self.client.post('/api/export',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['model_id'], 'test_model_123')
        self.assertEqual(data['format'], 'obj')
        self.assertIn('filename', data)
        self.assertIn('download_url', data)
    
    def test_export_model_invalid_format(self):
        """Test model export with invalid format."""
        payload = {
            'model_id': 'test_model_123',
            'format': 'invalid_format'
        }
        
        response = self.client.post('/api/export',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('Invalid format', data['error'])
    
    def test_download_file_not_implemented(self):
        """Test file download endpoint (currently not implemented)."""
        response = self.client.get('/api/download/test_file.obj')
        
        self.assertEqual(response.status_code, 501)  # Not Implemented
        
        data = json.loads(response.data)
        self.assertIn('not yet implemented', data['error'])
    
    def test_404_api_endpoint(self):
        """Test 404 handling for API endpoints."""
        response = self.client.get('/api/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('API endpoint not found', data['error'])
    
    def test_404_spa_fallback(self):
        """Test 404 handling for SPA routes."""
        response = self.client.get('/nonexistent-page')
        
        self.assertEqual(response.status_code, 404)
        # Should return the main page (SPA fallback)
        self.assertIn(b'Python Blender AI Modeling', response.data)
    
    def test_method_not_allowed(self):
        """Test 405 handling."""
        response = self.client.get('/api/generate')  # Should be POST
        
        self.assertEqual(response.status_code, 405)
        
        data = json.loads(response.data)
        self.assertIn('Method not allowed', data['error'])


if __name__ == '__main__':
    unittest.main()