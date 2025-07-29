"""
AI routes for AI-powered model and scene generation.

This module contains routes for AI integration functionality.
"""

import logging
from flask import Blueprint, request, jsonify

from ..services.ai_service import ai_service, AIGenerationError
from ..services.dependency_manager import dependency_manager

logger = logging.getLogger(__name__)

# Create blueprint for AI routes
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/generate', methods=['POST'])
def ai_generate_model():
    """Generate a 3D model using AI from natural language description."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'description' not in data:
            return jsonify({'error': 'Missing required field: description'}), 400
        
        description = data['description'].strip()
        if not description:
            return jsonify({'error': 'Description cannot be empty'}), 400
        
        # Check if AI integration is available
        if not dependency_manager.is_available('ai'):
            return jsonify({
                'error': 'AI integration not available',
                'message': 'AI functionality is not configured or available'
            }), 503
        
        # Generate model with AI
        result = ai_service.generate_ai_model(data)
        
        return jsonify(result), 200
        
    except AIGenerationError as e:
        logger.error(f"AI model generation failed: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in AI model generation: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during AI generation'
        }), 500


@ai_bp.route('/scene', methods=['POST'])
def ai_generate_scene():
    """Generate a multi-object scene using AI."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'description' not in data:
            return jsonify({'error': 'Missing required field: description'}), 400
        
        description = data['description'].strip()
        if not description:
            return jsonify({'error': 'Description cannot be empty'}), 400
        
        # Check if AI and scene management are available
        if not dependency_manager.is_available('ai'):
            return jsonify({
                'error': 'AI integration not available',
                'message': 'AI functionality is not configured or available'
            }), 503
        
        if not dependency_manager.is_available('scene_management'):
            return jsonify({
                'error': 'Scene management not available',
                'message': 'Scene functionality is not available'
            }), 503
        
        # Generate scene with AI
        result = ai_service.generate_ai_scene(data)
        
        return jsonify(result), 200
        
    except AIGenerationError as e:
        logger.error(f"AI scene generation failed: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in AI scene generation: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during AI scene generation'
        }), 500


def register_ai_routes(app):
    """Register AI routes with the Flask application."""
    app.register_blueprint(ai_bp)
    logger.info("AI routes registered successfully")