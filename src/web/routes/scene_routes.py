"""
Scene management routes for multi-object scene operations.

This module contains routes for scene creation, management, composition, and export.
"""

import logging
from flask import Blueprint, request, jsonify
from pathlib import Path
from typing import Dict, Any

from ..services.dependency_manager import dependency_manager
from ..config import config

logger = logging.getLogger(__name__)

# Create blueprint for scene routes
scene_bp = Blueprint('scene', __name__, url_prefix='/api')


@scene_bp.route('/scenes', methods=['GET'])
def list_scenes():
    """List all available scenes."""
    try:
        if not dependency_manager.is_available('scene_management'):
            return jsonify({'error': 'Scene management not available'}), 503
        
        scene_services = dependency_manager.get_service('scene_management')
        scene_manager_class = scene_services['manager_class']
        scene_manager = scene_manager_class(scenes_dir=config.scenes_dir)
        
        scenes = scene_manager.list_scenes()
        return jsonify({'scenes': scenes}), 200
        
    except Exception as e:
        logger.error(f"Error listing scenes: {str(e)}")
        return jsonify({'error': 'Failed to list scenes'}), 500


@scene_bp.route('/scenes', methods=['POST'])
def create_scene():
    """Create a new scene."""
    try:
        if not dependency_manager.is_available('scene_management'):
            return jsonify({'error': 'Scene management not available'}), 503
        
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Scene name is required'}), 400
        
        scene_services = dependency_manager.get_service('scene_management')
        scene_manager_class = scene_services['manager_class']
        scene_manager = scene_manager_class(scenes_dir=config.scenes_dir)
        
        scene = scene_manager.create_scene(
            scene_id=data.get('scene_id'),
            name=data['name'],
            description=data.get('description', ''),
            objects=data.get('objects', [])
        )
        
        return jsonify({
            'scene_id': scene.scene_id,
            'name': scene.name,
            'description': scene.description,
            'object_count': scene.object_count,
            'created_at': scene.created_at
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating scene: {str(e)}")
        return jsonify({'error': f'Failed to create scene: {str(e)}'}), 500


@scene_bp.route('/scenes/<scene_id>', methods=['GET'])
def get_scene(scene_id: str):
    """Get scene details by ID."""
    try:
        if not dependency_manager.is_available('scene_management'):
            return jsonify({'error': 'Scene management not available'}), 503
        
        scene_services = dependency_manager.get_service('scene_management')
        scene_manager_class = scene_services['manager_class']
        scene_manager = scene_manager_class(scenes_dir=config.scenes_dir)
        
        scene = scene_manager.load_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404
        
        return jsonify({
            'scene_id': scene.scene_id,
            'name': scene.name,
            'description': scene.description,
            'objects': [obj.to_dict() for obj in scene.objects],
            'object_count': scene.object_count,
            'created_at': scene.created_at,
            'scene_bounds': scene.scene_bounds.__dict__ if scene.scene_bounds else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scene {scene_id}: {str(e)}")
        return jsonify({'error': f'Failed to get scene: {str(e)}'}), 500


@scene_bp.route('/scenes/<scene_id>/preview', methods=['POST'])
def generate_scene_preview(scene_id: str):
    """Generate a preview for the scene."""
    try:
        if not dependency_manager.is_available('scene_management'):
            return jsonify({'error': 'Scene management not available'}), 503
        
        scene_services = dependency_manager.get_service('scene_management')
        scene_manager_class = scene_services['manager_class']
        scene_manager = scene_manager_class(scenes_dir=config.scenes_dir)
        
        scene = scene_manager.load_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404
        
        # Check if scene preview renderer is available
        if 'preview_renderer' not in scene_services:
            return jsonify({'error': 'Scene preview rendering not available'}), 503
        
        try:
            preview_renderer_class = scene_services['preview_renderer']
            preview_renderer = preview_renderer_class(
                blender_executable=config.flask_config['BLENDER_PATH']
            )
            
            # Generate preview
            preview_path = preview_renderer.render_scene(scene)
            
            if preview_path:
                return jsonify({
                    'success': True,
                    'preview_url': f'/api/preview/{scene_id}_scene',
                    'preview_path': str(preview_path)
                }), 200
            else:
                return jsonify({'error': 'Preview generation failed'}), 500
                
        except Exception as e:
            logger.error(f"Preview generation error: {str(e)}")
            return jsonify({'error': f'Preview generation failed: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Error generating preview for scene {scene_id}: {str(e)}")
        return jsonify({'error': f'Failed to generate preview: {str(e)}'}), 500


@scene_bp.route('/scenes/<scene_id>/validate', methods=['POST'])
def validate_scene(scene_id: str):
    """Validate a scene for issues."""
    try:
        if not dependency_manager.is_available('scene_management'):
            return jsonify({'error': 'Scene management not available'}), 503
        
        scene_services = dependency_manager.get_service('scene_management')
        scene_manager_class = scene_services['manager_class']
        validator_class = scene_services['validator_class']
        
        scene_manager = scene_manager_class(scenes_dir=config.scenes_dir)
        validator = validator_class()
        
        scene = scene_manager.load_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404
        
        validation_result = validator.validate_scene(scene)
        
        return jsonify({
            'valid': validation_result.is_valid,
            'issues': [issue.__dict__ for issue in validation_result.issues],
            'warnings': validation_result.warnings,
            'suggestions': validation_result.suggestions
        }), 200
        
    except Exception as e:
        logger.error(f"Error validating scene {scene_id}: {str(e)}")
        return jsonify({'error': f'Failed to validate scene: {str(e)}'}), 500


@scene_bp.route('/scene/<scene_id>/export', methods=['POST'])
def export_scene_api(scene_id: str):
    """Export a scene in the specified format."""
    try:
        if not dependency_manager.is_available('scene_management'):
            return jsonify({'error': 'Scene management not available'}), 503
        
        data = request.get_json() or {}
        format = data.get('format', 'obj').lower()
        export_type = data.get('export_type', 'complete')  # complete, selective, individual
        
        scene_services = dependency_manager.get_service('scene_management')
        
        # Check if scene exporter is available
        if 'scene_exporter' not in scene_services:
            return jsonify({'error': 'Scene export not available'}), 503
        
        scene_manager_class = scene_services['manager_class']
        scene_exporter_class = scene_services['scene_exporter']
        
        scene_manager = scene_manager_class(scenes_dir=config.scenes_dir)
        scene = scene_manager.load_scene(scene_id)
        
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404
        
        # Initialize scene exporter
        scene_exporter = scene_exporter_class(
            output_dir=config.export_dir / "scene_exports",
            blender_path=config.flask_config['BLENDER_PATH'],
            timeout=config.flask_config['BLENDER_TIMEOUT']
        )
        
        # Perform export based on type
        if export_type == 'complete':
            result = scene_exporter.export_complete_scene(scene, format)
        elif export_type == 'selective':
            object_ids = data.get('object_ids', [])
            if not object_ids:
                return jsonify({'error': 'object_ids required for selective export'}), 400
            result = scene_exporter.export_selective_objects(object_ids, scene, format)
        elif export_type == 'individual':
            object_id = data.get('object_id')
            if not object_id:
                return jsonify({'error': 'object_id required for individual export'}), 400
            
            scene_object = scene.get_object_by_id(object_id)
            if not scene_object:
                return jsonify({'error': 'Object not found in scene'}), 404
            
            result = scene_exporter.export_individual_object(scene_object, scene, format)
        else:
            return jsonify({'error': 'Invalid export_type. Must be: complete, selective, or individual'}), 400
        
        if result.success:
            return jsonify({
                'success': True,
                'export_type': result.export_type,
                'format': result.format,
                'exported_objects': result.exported_objects,
                'output_files': result.output_files,
                'total_file_size': result.total_file_size
            }), 200
        else:
            return jsonify({'error': result.error_message}), 500
        
    except Exception as e:
        logger.error(f"Error exporting scene {scene_id}: {str(e)}")
        return jsonify({'error': f'Failed to export scene: {str(e)}'}), 500


@scene_bp.route('/scene/<scene_id>/compose', methods=['POST'])
def compose_scene(scene_id: str):
    """Apply composition operations to scene objects."""
    try:
        if not dependency_manager.is_available('scene_management'):
            return jsonify({'error': 'Scene management not available'}), 503
        
        data = request.get_json()
        if not data or 'operation' not in data:
            return jsonify({'error': 'Operation is required'}), 400
        
        operation = data['operation']
        valid_operations = ['align', 'distribute', 'arrange']
        
        if operation not in valid_operations:
            return jsonify({'error': f'Invalid operation. Must be one of: {valid_operations}'}), 400
        
        scene_services = dependency_manager.get_service('scene_management')
        scene_manager_class = scene_services['manager_class']
        scene_manager = scene_manager_class(scenes_dir=config.scenes_dir)
        
        scene = scene_manager.load_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404
        
        # Get selected objects or use all objects
        object_ids = data.get('object_ids', [obj.id for obj in scene.objects])
        selected_objects = [scene.get_object_by_id(obj_id) for obj_id in object_ids]
        selected_objects = [obj for obj in selected_objects if obj is not None]
        
        if not selected_objects:
            return jsonify({'error': 'No valid objects selected'}), 400
        
        # Import and use scene compositor
        try:
            from scene_management.scene_compositor import SceneCompositor, AlignmentAxis, AlignmentMode, ArrangementPattern
            compositor = SceneCompositor()
            
            if operation == 'align':
                axis_str = data.get('axis', 'x').lower()
                mode_str = data.get('mode', 'center').lower()
                
                axis = AlignmentAxis(axis_str)
                mode = AlignmentMode(mode_str)
                
                compositor.align_objects(selected_objects, axis, mode)
                
            elif operation == 'distribute':
                axis_str = data.get('axis', 'x').lower()
                axis = AlignmentAxis(axis_str)
                spacing = data.get('spacing')
                
                compositor.distribute_objects(selected_objects, axis, spacing)
                
            elif operation == 'arrange':
                pattern_str = data.get('pattern', 'grid').lower()
                pattern = ArrangementPattern(pattern_str)
                
                if pattern == ArrangementPattern.GRID:
                    columns = data.get('columns')
                    spacing = data.get('spacing')
                    center_point = data.get('center_point', (0, 0, 0))
                    compositor.arrange_in_grid(selected_objects, columns, spacing, center_point)
                elif pattern == ArrangementPattern.CIRCLE:
                    radius = data.get('radius')
                    center_point = data.get('center_point', (0, 0, 0))
                    compositor.arrange_in_circle(selected_objects, radius, center_point)
                elif pattern == ArrangementPattern.SPIRAL:
                    spacing = data.get('spacing')
                    center_point = data.get('center_point', (0, 0, 0))
                    compositor.arrange_in_spiral(selected_objects, spacing, center_point)
            
            # Save the updated scene
            scene_manager.save_scene(scene)
            
            return jsonify({
                'success': True,
                'operation': operation,
                'affected_objects': len(selected_objects),
                'message': f'Successfully applied {operation} to {len(selected_objects)} objects'
            }), 200
            
        except ImportError as e:
            logger.error(f"Scene compositor not available: {str(e)}")
            return jsonify({'error': 'Scene composition functionality not available'}), 503
        
    except Exception as e:
        logger.error(f"Error composing scene {scene_id}: {str(e)}")
        return jsonify({'error': f'Failed to compose scene: {str(e)}'}), 500


def register_scene_routes(app):
    """Register scene routes with the Flask application."""
    app.register_blueprint(scene_bp)
    logger.info("Scene routes registered successfully")