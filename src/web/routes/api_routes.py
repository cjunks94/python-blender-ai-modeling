"""
API routes for model generation, preview, and export functionality.

This module contains the core API endpoints for the web application.
"""

import logging
from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
from typing import Dict, Any

from ..services.model_service import model_service, ModelGenerationError
from ..services.dependency_manager import dependency_manager
from ..config import config

logger = logging.getLogger(__name__)

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with service availability information."""
    try:
        health_info = dependency_manager.get_health_check()
        
        # Add additional configuration info
        if dependency_manager.is_available('blender'):
            health_info.update({
                'blender_path': config.flask_config['BLENDER_PATH'],
                'blender_timeout': config.flask_config['BLENDER_TIMEOUT']
            })
        
        return jsonify(health_info), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Health check failed'
        }), 500


@api_bp.route('/generate', methods=['POST'])
def generate_model():
    """Generate a 3D model with the provided parameters."""
    try:
        # Get parameters from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate model
        result = model_service.generate_model(data)
        
        # Generate preview if successful
        preview_path = model_service.generate_preview(result['id'], result['parameters'])
        if preview_path:
            result['preview_url'] = f"/api/preview/{result['id']}"
        
        return jsonify(result), 200
        
    except ModelGenerationError as e:
        logger.error(f"Model generation failed: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in generate_model: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/preview/<model_id>', methods=['GET'])
def get_preview(model_id: str):
    """Serve a model preview image."""
    try:
        # Sanitize model_id to prevent path traversal
        safe_model_id = ''.join(c for c in model_id if c.isalnum() or c in '-_')
        
        # Look for preview file with common extensions
        preview_dir = config.preview_dir
        for ext in ['.png', '.jpg', '.jpeg']:
            preview_path = preview_dir / f"{safe_model_id}{ext}"
            if preview_path.exists():
                return send_file(str(preview_path), mimetype=f'image/{ext[1:]}')
        
        return jsonify({'error': 'Preview not found'}), 404
        
    except Exception as e:
        logger.error(f"Error serving preview for {model_id}: {str(e)}")
        return jsonify({'error': 'Internal server error serving preview'}), 500


@api_bp.route('/export', methods=['POST'])
def export_model():
    """Export a model to the specified format."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['model_id', 'format', 'model_params']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Export model
        result = model_service.export_model(
            data['model_id'],
            data['format'],
            data['model_params']
        )
        
        return jsonify(result), 200
        
    except ModelGenerationError as e:
        logger.error(f"Model export failed: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in export_model: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename: str):
    """Download an exported model file."""
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = ''.join(c for c in filename if c.isalnum() or c in '-_.')
        
        # Check if file exists in export directory
        file_path = config.export_dir / safe_filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Determine mimetype based on extension
        ext = file_path.suffix.lower()
        mimetype_map = {
            '.obj': 'application/octet-stream',
            '.gltf': 'model/gltf+json',
            '.glb': 'model/gltf-binary',
            '.stl': 'application/octet-stream'
        }
        mimetype = mimetype_map.get(ext, 'application/octet-stream')
        
        return send_file(
            str(file_path),
            mimetype=mimetype,
            as_attachment=True
        )
        
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def register_api_routes(app):
    """Register API routes with the Flask application."""
    app.register_blueprint(api_bp)
    logger.info("API routes registered successfully")