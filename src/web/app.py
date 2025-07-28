#!/usr/bin/env python3
"""
Flask web application for Python Blender AI Modeling.

This module provides the web interface and API endpoints for the application.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config: Dict[str, Any] = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configure app
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        'BLENDER_PATH': os.environ.get('BLENDER_EXECUTABLE_PATH', 'blender'),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file upload
    })
    
    if config:
        app.config.update(config)
    
    # Register routes
    register_routes(app)
    register_error_handlers(app)
    
    logger.info("Flask application created successfully")
    return app


def register_routes(app: Flask) -> None:
    """Register application routes."""
    
    @app.route('/')
    def index():
        """Main application page."""
        return render_template('index.html')
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'version': '0.1.0',
            'blender_path': app.config['BLENDER_PATH']
        })
    
    @app.route('/api/generate', methods=['POST'])
    def generate_model():
        """Generate a 3D model based on parameters."""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['object_type', 'size', 'pos_x']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Validate object type
            valid_types = ['cube', 'sphere', 'cylinder', 'plane']
            if data['object_type'] not in valid_types:
                return jsonify({'error': f'Invalid object type. Must be one of: {valid_types}'}), 400
            
            # Validate numeric parameters
            try:
                size = float(data['size'])
                pos_x = float(data['pos_x'])
                
                if not (0.1 <= size <= 10):
                    return jsonify({'error': 'Size must be between 0.1 and 10'}), 400
                
                if not (-10 <= pos_x <= 10):
                    return jsonify({'error': 'Position X must be between -10 and 10'}), 400
                    
            except (ValueError, TypeError):
                return jsonify({'error': 'Size and position must be valid numbers'}), 400
            
            # TODO: Implement actual Blender integration
            # For now, return a mock response
            model_id = f"model_{data['object_type']}_{int(size*10)}_{int(pos_x*10)}"
            
            response = {
                'id': model_id,
                'object_type': data['object_type'],
                'parameters': {
                    'size': size,
                    'pos_x': pos_x
                },
                'status': 'generated',
                'message': f'Successfully generated {data["object_type"]} with size {size} at position X={pos_x}',
                'created_at': '2024-01-01T12:00:00Z'  # TODO: Use actual timestamp
            }
            
            logger.info(f"Generated model: {model_id}")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Model generation failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error during model generation'}), 500
    
    @app.route('/api/export', methods=['POST'])
    def export_model():
        """Export a generated model to specified format."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if 'model_id' not in data:
                return jsonify({'error': 'Missing required field: model_id'}), 400
            
            if 'format' not in data:
                return jsonify({'error': 'Missing required field: format'}), 400
            
            # Validate format
            valid_formats = ['obj', 'gltf', 'stl']
            if data['format'] not in valid_formats:
                return jsonify({'error': f'Invalid format. Must be one of: {valid_formats}'}), 400
            
            # TODO: Implement actual export functionality
            # For now, return a mock response
            model_id = data['model_id']
            format_ext = data['format']
            filename = f"{model_id}.{format_ext}"
            
            response = {
                'model_id': model_id,
                'format': format_ext,
                'filename': filename,
                'download_url': f'/api/download/{filename}',
                'size': '1.2 KB',  # Mock size
                'created_at': '2024-01-01T12:00:00Z'
            }
            
            logger.info(f"Exported model {model_id} as {format_ext}")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error during export'}), 500
    
    @app.route('/api/download/<filename>')
    def download_file(filename: str):
        """Download exported model file."""
        try:
            # TODO: Implement actual file serving
            # For now, return a placeholder response
            return jsonify({
                'error': 'File download not yet implemented',
                'filename': filename,
                'message': 'This will serve the actual exported file in the future'
            }), 501
            
        except Exception as e:
            logger.error(f"Download failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error during download'}), 500


def register_error_handlers(app: Flask) -> None:
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'API endpoint not found'}), 404
        return render_template('index.html'), 404  # SPA fallback
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file upload size errors."""
        return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Flask development server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)