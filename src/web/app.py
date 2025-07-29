#!/usr/bin/env python3
"""
Flask web application for Python Blender AI Modeling.

This module provides the web interface and API endpoints for the application.
"""

import os
import sys
import logging
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from typing import Dict, Any

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file if it exists
from pathlib import Path
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                # Remove quotes if present
                value = value.strip('"\'')
                os.environ[key] = value

# Import Blender integration
try:
    from blender_integration.executor import BlenderExecutor, BlenderExecutionError, BlenderScriptError
    from blender_integration.script_generator import ScriptGenerator, ScriptGenerationError
    from blender_integration.preview_renderer import PreviewRenderer
    BLENDER_AVAILABLE = True
except ImportError as e:
    BLENDER_AVAILABLE = False
    BlenderExecutor = None
    ScriptGenerator = None
    PreviewRenderer = None
    print(f"Warning: Blender integration not available: {e}")

# Import export functionality
try:
    from export.obj_exporter import OBJExporter
    from export.gltf_exporter import GLTFExporter
    from export.stl_exporter import STLExporter
    from export.obj_exporter import ExportError
    EXPORT_AVAILABLE = True
except ImportError as e:
    EXPORT_AVAILABLE = False
    OBJExporter = None
    GLTFExporter = None
    STLExporter = None
    ExportError = None
    print(f"Warning: Export functionality not available: {e}")

# Import AI integration
try:
    from ai_integration.ai_client import AIClient
    from ai_integration.model_interpreter import ModelInterpreter
    from ai_integration.prompt_engineer import PromptEngineer
    from ai_integration.script_validator import ScriptValidator
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    AIClient = None
    ModelInterpreter = None
    PromptEngineer = None
    ScriptValidator = None
    print(f"Warning: AI integration not available: {e}")

# Import scene management
try:
    from scene_management import Scene, SceneObject, SceneManager, SceneValidator, ScenePreviewRenderer, SCENE_PREVIEW_AVAILABLE
    from export import SceneExporter, SCENE_EXPORT_AVAILABLE
    SCENE_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    SCENE_MANAGEMENT_AVAILABLE = False
    Scene = None
    SceneObject = None
    SceneManager = None
    SceneValidator = None
    ScenePreviewRenderer = None
    SceneExporter = None
    SCENE_PREVIEW_AVAILABLE = False
    SCENE_EXPORT_AVAILABLE = False
    print(f"Warning: Scene management not available: {e}")

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
        'BLENDER_TIMEOUT': int(os.environ.get('BLENDER_TIMEOUT', '30')),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file upload
    })
    
    # Initialize Blender tools if available
    if BLENDER_AVAILABLE:
        app.blender_executor = BlenderExecutor(
            blender_path=app.config['BLENDER_PATH'],
            timeout=app.config['BLENDER_TIMEOUT']
        )
        app.script_generator = ScriptGenerator(clear_scene=True)
        # Use absolute path for preview directory
        preview_dir = Path(__file__).parent.parent.parent / "previews"
        app.preview_renderer = PreviewRenderer(
            blender_path=app.config['BLENDER_PATH'],
            timeout=app.config['BLENDER_TIMEOUT']
        )
        # Override the preview directory to use absolute path
        app.preview_renderer.preview_dir = preview_dir
        app.preview_renderer.preview_dir.mkdir(exist_ok=True)
    
    # Initialize export tools if available
    if EXPORT_AVAILABLE:
        app.obj_exporter = OBJExporter(
            blender_path=app.config['BLENDER_PATH'],
            timeout=app.config['BLENDER_TIMEOUT']
        )
        app.gltf_exporter = GLTFExporter(
            blender_path=app.config['BLENDER_PATH'],
            timeout=app.config['BLENDER_TIMEOUT']
        )
        app.stl_exporter = STLExporter(
            blender_path=app.config['BLENDER_PATH'],
            timeout=app.config['BLENDER_TIMEOUT']
        )
    
    # Initialize AI tools if available
    if AI_AVAILABLE:
        try:
            app.ai_client = AIClient()
            app.model_interpreter = ModelInterpreter()
            app.prompt_engineer = PromptEngineer()
            app.script_validator = ScriptValidator()
            logger.info("AI integration initialized successfully")
        except Exception as e:
            logger.warning(f"AI integration initialization failed: {e}")
            # Set AI_AVAILABLE to False to prevent using these features
            globals()['AI_AVAILABLE'] = False
    
    # Initialize scene management if available
    if SCENE_MANAGEMENT_AVAILABLE:
        try:
            # Create scenes directory for persistence
            scenes_dir = Path(__file__).parent.parent.parent / "scenes"
            app.scene_manager = SceneManager(scenes_dir)
            app.scene_validator = SceneValidator()
            
            # Initialize scene preview renderer if available (optional)
            app.scene_preview_renderer = None
            if SCENE_PREVIEW_AVAILABLE:
                try:
                    app.scene_preview_renderer = ScenePreviewRenderer(
                        blender_executable=app.config['BLENDER_PATH']
                    )
                    logger.info("Scene preview renderer initialized")
                except Exception as e:
                    logger.warning(f"Scene preview renderer initialization failed: {e}")
                    globals()['SCENE_PREVIEW_AVAILABLE'] = False
            
            # Initialize scene exporter if available (optional)
            app.scene_exporter = None
            if SCENE_EXPORT_AVAILABLE:
                try:
                    exports_dir = Path(__file__).parent.parent.parent / "scene_exports"
                    app.scene_exporter = SceneExporter(
                        output_dir=exports_dir,
                        blender_path=app.config['BLENDER_PATH'],
                        timeout=app.config['BLENDER_TIMEOUT']
                    )
                    logger.info("Scene exporter initialized")
                except Exception as e:
                    logger.warning(f"Scene exporter initialization failed: {e}")
                    globals()['SCENE_EXPORT_AVAILABLE'] = False
            
            logger.info("Scene management initialized successfully")
        except Exception as e:
            logger.warning(f"Scene management core initialization failed: {e}")
            globals()['SCENE_MANAGEMENT_AVAILABLE'] = False
    
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
            'blender_path': app.config['BLENDER_PATH'],
            'blender_available': BLENDER_AVAILABLE,
            'export_available': EXPORT_AVAILABLE,
            'ai_available': AI_AVAILABLE,
            'scene_management_available': SCENE_MANAGEMENT_AVAILABLE,
            'scene_preview_available': SCENE_PREVIEW_AVAILABLE,
            'scene_export_available': SCENE_EXPORT_AVAILABLE,
            'blender_timeout': app.config['BLENDER_TIMEOUT']
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
                
                # Validate optional rotation parameters
                rotation = None
                if any(key in data for key in ['rot_x', 'rot_y', 'rot_z']):
                    rot_x = float(data.get('rot_x', 0))
                    rot_y = float(data.get('rot_y', 0))
                    rot_z = float(data.get('rot_z', 0))
                    
                    # Validate rotation ranges (degrees)
                    if not all(-180 <= r <= 180 for r in [rot_x, rot_y, rot_z]):
                        return jsonify({'error': 'Rotation values must be between -180 and 180 degrees'}), 400
                    
                    # Convert degrees to radians for Blender
                    rotation = (
                        math.radians(rot_x),
                        math.radians(rot_y),
                        math.radians(rot_z)
                    )
                
                # Validate optional material parameters
                material = None
                if any(key in data for key in ['color', 'metallic', 'roughness', 'emission']):
                    material = {}
                    
                    if 'color' in data:
                        material['color'] = data['color']
                    
                    if 'metallic' in data:
                        metallic = float(data['metallic'])
                        if not (0 <= metallic <= 1):
                            return jsonify({'error': 'Metallic value must be between 0 and 1'}), 400
                        material['metallic'] = metallic
                    
                    if 'roughness' in data:
                        roughness = float(data['roughness'])
                        if not (0 <= roughness <= 1):
                            return jsonify({'error': 'Roughness value must be between 0 and 1'}), 400
                        material['roughness'] = roughness
                    
                    if data.get('emission', False):
                        material['emission'] = True
                        if 'emission_strength' in data:
                            emission_strength = float(data['emission_strength'])
                            if not (0 <= emission_strength <= 10):
                                return jsonify({'error': 'Emission strength must be between 0 and 10'}), 400
                            material['emission_strength'] = emission_strength
                    
            except (ValueError, TypeError):
                return jsonify({'error': 'Size, position, and rotation must be valid numbers'}), 400
            
            # Check if Blender integration is available
            if not BLENDER_AVAILABLE:
                return jsonify({
                    'error': 'Blender integration not available',
                    'message': 'Please ensure Blender is installed and accessible'
                }), 503
            
            # Generate bpy script using ScriptGenerator
            try:
                if data['object_type'] == 'cube':
                    script_content = app.script_generator.generate_cube_script(
                        size=size,
                        position=(pos_x, 0, 0),
                        rotation=rotation,
                        material=material
                    )
                elif data['object_type'] == 'sphere':
                    # For sphere, size represents radius
                    script_content = app.script_generator.generate_sphere_script(
                        radius=size,
                        position=(pos_x, 0, 0),
                        rotation=rotation,
                        material=material
                    )
                elif data['object_type'] == 'cylinder':
                    # For cylinder, size represents radius, depth is twice the radius
                    script_content = app.script_generator.generate_cylinder_script(
                        radius=size,
                        depth=size * 2,  # Default height is 2x radius
                        position=(pos_x, 0, 0),
                        rotation=rotation,
                        material=material
                    )
                elif data['object_type'] == 'plane':
                    script_content = app.script_generator.generate_plane_script(
                        size=size,
                        position=(pos_x, 0, 0),
                        rotation=rotation,
                        material=material
                    )
                else:
                    # This should not happen due to earlier validation
                    return jsonify({
                        'error': f"Object type '{data['object_type']}' not supported",
                        'message': 'Invalid object type'
                    }), 400
                    
            except ScriptGenerationError as e:
                logger.error(f"Script generation error: {e}")
                return jsonify({
                    'error': 'Script generation failed',
                    'message': str(e)
                }), 400
            
            try:
                # Execute Blender script with retry mechanism for resilience
                result = app.blender_executor.execute_script_with_retry(
                    script_content, 
                    max_retries=2, 
                    retry_delay=1.0
                )
                
                if result.success:
                    model_id = f"model_{data['object_type']}_{int(size*10)}_{int(pos_x*10)}"
                    
                    # Build parameters dict
                    parameters = {
                        'size': size,
                        'pos_x': pos_x
                    }
                    
                    # Add rotation to parameters if provided
                    if rotation:
                        parameters['rotation'] = {
                            'x': round(math.degrees(rotation[0]), 1),
                            'y': round(math.degrees(rotation[1]), 1),
                            'z': round(math.degrees(rotation[2]), 1)
                        }
                    
                    # Generate preview image
                    preview_url = None
                    try:
                        # Build complete model params for preview
                        preview_params = data.copy()
                        preview_result = app.preview_renderer.render_preview(model_id, preview_params)
                        if preview_result.success:
                            preview_url = f'/api/preview/{model_id}_preview.png'
                            logger.info(f"Preview rendered for model {model_id}")
                        else:
                            logger.warning(f"Preview generation failed: {preview_result.error_message}")
                    except Exception as e:
                        logger.error(f"Preview generation error: {str(e)}")
                    
                    # Build message
                    message = f'Successfully generated {data["object_type"]} with size {size} at position X={pos_x}'
                    if rotation:
                        message += f' and rotation X={parameters["rotation"]["x"]}°, Y={parameters["rotation"]["y"]}°, Z={parameters["rotation"]["z"]}°'
                    
                    response = {
                        'id': model_id,
                        'object_type': data['object_type'],
                        'parameters': parameters,
                        'status': 'generated',
                        'message': message,
                        'blender_output': result.stdout,
                        'preview_url': preview_url,
                        'created_at': '2024-01-01T12:00:00Z'  # TODO: Use actual timestamp
                    }
                else:
                    return jsonify({
                        'error': 'Blender execution failed',
                        'details': result.stderr,
                        'return_code': result.return_code
                    }), 500
                    
            except BlenderExecutionError as e:
                logger.error(f"Blender execution error: {e}")
                
                # Provide user-friendly error messages based on error type
                error_responses = {
                    'timeout': {
                        'error': 'Blender execution timeout',
                        'message': 'The operation took too long to complete. Please try again or reduce complexity.',
                        'code': 504
                    },
                    'not_found': {
                        'error': 'Blender not found',
                        'message': 'Blender is not installed or not in PATH. Run: python setup_blender.py to configure.',
                        'code': 503
                    },
                    'permission': {
                        'error': 'Permission denied',
                        'message': 'Permission denied accessing Blender. Please check file permissions.',
                        'code': 503
                    },
                    'memory': {
                        'error': 'Insufficient memory',
                        'message': 'Not enough memory to execute the operation. Please try again or reduce complexity.',
                        'code': 503
                    },
                    'max_retries': {
                        'error': 'Operation failed after retries',
                        'message': 'System is experiencing issues. Please try again in a few moments.',
                        'code': 503
                    }
                }
                
                error_type = getattr(e, 'error_type', 'execution')
                error_info = error_responses.get(error_type, {
                    'error': 'Blender execution failed',
                    'message': str(e),
                    'code': 500
                })
                
                return jsonify({
                    'error': error_info['error'],
                    'message': error_info['message'],
                    'error_type': error_type
                }), error_info['code']
            
            except BlenderScriptError as e:
                logger.error(f"Blender script error: {e}")
                
                # Provide user-friendly error messages based on script error type
                script_error_responses = {
                    'syntax': {
                        'error': 'Script syntax error',
                        'message': 'The generated script has invalid Python syntax. Please try again.',
                        'code': 400
                    },
                    'indentation': {
                        'error': 'Script indentation error',
                        'message': 'The generated script has indentation issues. Please try again.',
                        'code': 400
                    },
                    'security': {
                        'error': 'Security validation failed',
                        'message': 'The script contains potentially unsafe operations and cannot be executed.',
                        'code': 403
                    }
                }
                
                error_type = getattr(e, 'error_type', 'script')
                error_info = script_error_responses.get(error_type, {
                    'error': 'Invalid Blender script',
                    'message': str(e),
                    'code': 400
                })
                
                return jsonify({
                    'error': error_info['error'],
                    'message': error_info['message'],
                    'error_type': error_type
                }), error_info['code']
            
            except ScriptGenerationError as e:
                logger.error(f"Script generation error: {e}")
                return jsonify({
                    'error': 'Script generation failed',
                    'message': str(e)
                }), 400
            
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
            
            if 'model_params' not in data:
                return jsonify({'error': 'Missing required field: model_params'}), 400
            
            # Validate format
            valid_formats = ['obj', 'gltf', 'glb', 'stl']
            if data['format'] not in valid_formats:
                return jsonify({'error': f'Invalid format. Must be one of: {valid_formats}'}), 400
            
            # Check if export functionality is available
            if not EXPORT_AVAILABLE:
                return jsonify({
                    'error': 'Export functionality not available',
                    'message': 'Export module could not be loaded'
                }), 503
            
            model_id = data['model_id']
            format_ext = data['format']
            model_params = data['model_params']
            
            try:
                # Export the model based on format
                if format_ext == 'obj':
                    result = app.obj_exporter.export_obj(model_id, model_params)
                elif format_ext in ['gltf', 'glb']:
                    binary = (format_ext == 'glb')
                    result = app.gltf_exporter.export_gltf(model_id, model_params, binary=binary)
                elif format_ext == 'stl':
                    result = app.stl_exporter.export_stl(model_id, model_params)
                else:
                    return jsonify({
                        'error': f'Format {format_ext} not supported',
                        'message': 'Invalid export format'
                    }), 400
                
                if result.success:
                    # Convert file size to human readable format
                    if result.file_size:
                        if result.file_size < 1024:
                            size_str = f"{result.file_size} B"
                        elif result.file_size < 1024 * 1024:
                            size_str = f"{result.file_size / 1024:.1f} KB"
                        else:
                            size_str = f"{result.file_size / (1024 * 1024):.1f} MB"
                    else:
                        size_str = "Unknown"
                    
                    response = {
                        'model_id': result.model_id,
                        'format': result.format,
                        'filename': Path(result.output_file).name,
                        'download_url': f'/api/download/{Path(result.output_file).name}',
                        'size': size_str,
                        'file_path': result.output_file,
                        'created_at': '2024-01-01T12:00:00Z'  # TODO: Use actual timestamp
                    }
                    
                    logger.info(f"Successfully exported model {model_id} as {format_ext}")
                    return jsonify(response)
                else:
                    return jsonify({
                        'error': 'Export failed',
                        'message': result.error_message or 'Unknown export error'
                    }), 500
                    
            except ExportError as e:
                logger.error(f"Export error: {e}")
                return jsonify({
                    'error': 'Export failed',
                    'message': str(e)
                }), 400
            
        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error during export'}), 500
    
    @app.route('/api/download/<filename>')
    def download_file(filename: str):
        """Download exported model file."""
        try:
            # Check if export functionality is available
            if not EXPORT_AVAILABLE:
                return jsonify({
                    'error': 'Export functionality not available',
                    'message': 'Export module could not be loaded'
                }), 503
            
            # Build file path from exporter's output directory
            file_path = app.obj_exporter.output_dir / filename
            
            # Check if file exists
            if not file_path.exists():
                return jsonify({
                    'error': 'File not found',
                    'filename': filename,
                    'message': f'The requested file {filename} does not exist'
                }), 404
            
            # Serve the file
            return send_file(
                str(file_path),
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )
            
        except Exception as e:
            logger.error(f"Download failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error during download'}), 500
    
    @app.route('/api/preview/<filename>')
    def preview_image(filename: str):
        """Serve preview image."""
        try:
            # Check if Blender functionality is available
            if not BLENDER_AVAILABLE:
                return jsonify({
                    'error': 'Preview functionality not available',
                    'message': 'Blender integration not loaded'
                }), 503
            
            # Check if preview renderer is available
            if not hasattr(app, 'preview_renderer'):
                return jsonify({
                    'error': 'Preview renderer not initialized',
                    'message': 'Preview functionality not properly configured'
                }), 503
            
            # Build file path from preview renderer's output directory
            file_path = app.preview_renderer.preview_dir / filename
            
            # Check if file exists
            if not file_path.exists():
                return jsonify({
                    'error': 'Preview not found',
                    'filename': filename,
                    'message': f'The preview image {filename} does not exist'
                }), 404
            
            # Serve the image
            return send_file(
                str(file_path),
                mimetype='image/png',
                as_attachment=False
            )
            
        except Exception as e:
            logger.error(f"Preview serve failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error serving preview'}), 500
    
    @app.route('/api/ai/generate', methods=['POST'])
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
            if not AI_AVAILABLE:
                return jsonify({
                    'error': 'AI integration not available',
                    'message': 'AI functionality is not configured or available'
                }), 503
            
            # Get generation context from request
            context = {
                'user_level': data.get('user_level', 'intermediate'),
                'preferred_style': data.get('preferred_style', 'creative'),
                'complexity': data.get('complexity', 'medium')
            }
            
            try:
                # Step 1: Optimize the user prompt
                prompt_result = app.prompt_engineer.optimize_user_input(description, context)
                if not prompt_result['success']:
                    return jsonify({
                        'error': 'Prompt optimization failed',
                        'message': prompt_result.get('error', 'Unknown prompt error')
                    }), 400
                
                # Step 2: Generate model using AI
                ai_response = app.ai_client.generate_model_from_description(
                    prompt_result['optimized_prompt'], 
                    context
                )
                
                if not ai_response.success:
                    return jsonify({
                        'error': 'AI model generation failed',
                        'message': ai_response.error_message
                    }), 500
                
                # Step 3: Interpret AI response
                interpretation = app.model_interpreter.interpret_single_model(ai_response.model_data)
                if not interpretation.success:
                    return jsonify({
                        'error': 'AI response interpretation failed', 
                        'message': interpretation.error_message
                    }), 400
                
                # Step 4: Validate the interpreted model
                model_params = interpretation.models[0]
                validation = app.script_validator.validate_model_parameters(model_params)
                
                if not validation.is_safe:
                    critical_issues = [i for i in validation.issues if i.severity.value == 'critical']
                    return jsonify({
                        'error': 'AI-generated model failed safety validation',
                        'message': f"Safety issues: {', '.join([i.message for i in critical_issues])}"
                    }), 400
                
                # Step 5: Generate the model using our existing pipeline
                # Use the AI-interpreted parameters to generate the model
                if not BLENDER_AVAILABLE:
                    return jsonify({
                        'error': 'Blender integration not available', 
                        'message': 'Blender is required for model generation'
                    }), 503
                
                # Generate script using our ScriptGenerator
                try:
                    object_type = model_params['object_type']
                    size = model_params['size']
                    position = (model_params.get('pos_x', 0), model_params.get('pos_y', 0), model_params.get('pos_z', 0))
                    
                    # Convert rotation from degrees to radians if present
                    rotation = None
                    if any(key in model_params for key in ['rot_x', 'rot_y', 'rot_z']):
                        import math
                        rotation = (
                            math.radians(model_params.get('rot_x', 0)),
                            math.radians(model_params.get('rot_y', 0)),
                            math.radians(model_params.get('rot_z', 0))
                        )
                    
                    # Build material dict if present
                    material = None
                    if 'color' in model_params:
                        material = {
                            'color': model_params.get('color', '#888888'),
                            'metallic': model_params.get('metallic', 0.0),
                            'roughness': model_params.get('roughness', 0.5),
                        }
                        if model_params.get('emission'):
                            material['emission'] = True
                            material['emission_strength'] = model_params.get('emission_strength', 1.0)
                    
                    # Generate script based on object type
                    if object_type == 'cube':
                        script_content = app.script_generator.generate_cube_script(
                            size=size, position=position, rotation=rotation, material=material
                        )
                    elif object_type == 'sphere':
                        script_content = app.script_generator.generate_sphere_script(
                            radius=size, position=position, rotation=rotation, material=material
                        )
                    elif object_type == 'cylinder':
                        script_content = app.script_generator.generate_cylinder_script(
                            radius=size, depth=size * 2, position=position, rotation=rotation, material=material
                        )
                    elif object_type == 'plane':
                        script_content = app.script_generator.generate_plane_script(
                            size=size, position=position, rotation=rotation, material=material
                        )
                    else:
                        return jsonify({
                            'error': f"Unsupported object type: {object_type}",
                            'message': 'AI generated an unsupported object type'
                        }), 400
                        
                except Exception as e:
                    logger.error(f"Script generation error: {e}")
                    return jsonify({
                        'error': 'Script generation failed',
                        'message': str(e)
                    }), 400
                
                # Step 6: Execute the Blender script
                try:
                    result = app.blender_executor.execute_script_with_retry(
                        script_content, max_retries=2, retry_delay=1.0
                    )
                    
                    if not result.success:
                        return jsonify({
                            'error': 'Blender execution failed',
                            'details': result.stderr,
                            'return_code': result.return_code
                        }), 500
                    
                    # Step 7: Generate model ID and preview
                    model_id = f"ai_model_{hash(description) % 10000}"
                    
                    # Generate preview
                    preview_url = None
                    try:
                        preview_result = app.preview_renderer.render_preview(model_id, model_params)
                        if preview_result.success:
                            preview_url = f'/api/preview/{model_id}_preview.png'
                            logger.info(f"Preview rendered for AI model {model_id}")
                        else:
                            logger.warning(f"Preview generation failed: {preview_result.error_message}")
                    except Exception as e:
                        logger.error(f"Preview generation error: {str(e)}")
                    
                    # Build response
                    response = {
                        'id': model_id,
                        'source': 'ai_generated',
                        'description': description,
                        'object_type': object_type,
                        'parameters': model_params,
                        'ai_info': {
                            'prompt_style': prompt_result.get('style'),
                            'template_used': prompt_result.get('template_used'),
                            'reasoning': ai_response.model_data.get('reasoning', ''),
                            'suggestions': prompt_result.get('suggestions', []),
                            'warnings': interpretation.scene_info.get('warnings', []) if interpretation.scene_info else [],
                            'usage': ai_response.usage
                        },
                        'status': 'generated',
                        'message': f'Successfully generated {object_type} using AI from description: "{description}"',
                        'blender_output': result.stdout,
                        'preview_url': preview_url,
                        'created_at': '2024-01-01T12:00:00Z'  # TODO: Use actual timestamp
                    }
                    
                    logger.info(f"AI model generated successfully: {model_id}")
                    return jsonify(response)
                    
                except Exception as e:
                    logger.error(f"Blender execution failed: {e}")
                    return jsonify({
                        'error': 'Model generation failed',
                        'message': str(e)
                    }), 500
                    
            except Exception as e:
                logger.error(f"AI generation pipeline failed: {e}")
                return jsonify({
                    'error': 'AI generation pipeline failed',
                    'message': str(e)
                }), 500
                
        except Exception as e:
            logger.error(f"AI model generation failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error during AI model generation'}), 500
    
    @app.route('/api/ai/scene', methods=['POST'])
    def ai_generate_scene():
        """Generate a complex 3D scene using AI from natural language description."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if 'description' not in data:
                return jsonify({'error': 'Missing required field: description'}), 400
            
            description = data['description'].strip()
            if not description:
                return jsonify({'error': 'Description cannot be empty'}), 400
            
            # Check if AI integration is available
            if not AI_AVAILABLE:
                return jsonify({
                    'error': 'AI integration not available',
                    'message': 'AI functionality is not configured or available'
                }), 503
            
            max_objects = min(int(data.get('max_objects', 5)), 8)  # Cap at 8 objects
            complexity = data.get('complexity', 'medium')
            
            try:
                # Step 1: Enhance prompt for scene generation
                scene_prompt = app.prompt_engineer.enhance_for_scene_generation(description, complexity)
                
                # Step 2: Generate scene using AI
                ai_response = app.ai_client.generate_complex_scene(scene_prompt, max_objects)
                
                if not ai_response.success:
                    return jsonify({
                        'error': 'AI scene generation failed',
                        'message': ai_response.error_message
                    }), 500
                
                # Step 3: Interpret scene response
                interpretation = app.model_interpreter.interpret_scene(ai_response.model_data)
                if not interpretation.success:
                    return jsonify({
                        'error': 'AI scene interpretation failed',
                        'message': interpretation.error_message
                    }), 400
                
                # For now, return the interpreted scene data
                # Full scene generation would require orchestrating multiple Blender calls
                response = {
                    'scene_id': f"ai_scene_{hash(description) % 10000}",
                    'source': 'ai_generated',
                    'description': description,
                    'scene_info': interpretation.scene_info,
                    'objects': interpretation.models,
                    'ai_info': {
                        'complexity': complexity,
                        'max_objects': max_objects,
                        'usage': ai_response.usage
                    },
                    'status': 'planned',
                    'message': f'Scene planned with {len(interpretation.models)} objects. Individual generation required.',
                    'created_at': '2024-01-01T12:00:00Z'
                }
                
                logger.info(f"AI scene interpreted successfully with {len(interpretation.models)} objects")
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"AI scene generation failed: {e}")
                return jsonify({
                    'error': 'AI scene generation failed',
                    'message': str(e)
                }), 500
                
        except Exception as e:
            logger.error(f"AI scene generation failed: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error during AI scene generation'}), 500
    
    # Scene Management API Routes
    @app.route('/api/scenes', methods=['GET'])
    def list_scenes():
        """List all available scenes."""
        if not SCENE_MANAGEMENT_AVAILABLE:
            return jsonify({'error': 'Scene management not available'}), 503
        
        try:
            scenes = app.scene_manager.list_scenes()
            return jsonify({
                'success': True,
                'scenes': scenes,
                'count': len(scenes)
            })
        except Exception as e:
            logger.error(f"Failed to list scenes: {e}")
            return jsonify({'error': 'Failed to list scenes'}), 500
    
    @app.route('/api/scenes', methods=['POST'])
    def create_scene():
        """Create a new scene."""
        if not SCENE_MANAGEMENT_AVAILABLE:
            return jsonify({'error': 'Scene management not available'}), 503
        
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('name'):
                return jsonify({'error': 'Scene name is required'}), 400
            
            scene = app.scene_manager.create_scene(
                name=data['name'],
                description=data.get('description', ''),
                scene_id=data.get('scene_id')
            )
            
            return jsonify({
                'success': True,
                'scene': {
                    'scene_id': scene.scene_id,
                    'name': scene.name,
                    'description': scene.description,
                    'object_count': scene.object_count,
                    'created_at': scene.created_at.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to create scene: {e}")
            return jsonify({'error': 'Failed to create scene'}), 500
    
    @app.route('/api/scenes/<scene_id>', methods=['GET'])
    def get_scene(scene_id):
        """Get details of a specific scene."""
        if not SCENE_MANAGEMENT_AVAILABLE:
            return jsonify({'error': 'Scene management not available'}), 503
        
        try:
            scene = app.scene_manager.get_scene(scene_id)
            if not scene:
                return jsonify({'error': 'Scene not found'}), 404
            
            # Get scene statistics
            stats = app.scene_manager.get_scene_statistics(scene_id)
            
            return jsonify({
                'success': True,
                'scene': {
                    'scene_id': scene.scene_id,
                    'name': scene.name,
                    'description': scene.description,
                    'object_count': scene.object_count,
                    'objects': [
                        {
                            'id': obj.id,
                            'name': obj.name,
                            'object_type': obj.object_type,
                            'position': obj.position,
                            'size': obj.size,
                            'rotation': obj.rotation,
                            'export_ready': obj.export_ready,
                            'ai_reasoning': obj.ai_reasoning
                        } for obj in scene.objects
                    ],
                    'relationships': [
                        {
                            'source_object_id': rel.source_object_id,
                            'target_object_id': rel.target_object_id,
                            'relationship_type': rel.relationship_type.value,
                            'description': rel.description
                        } for rel in scene.get_all_relationships()
                    ],
                    'created_at': scene.created_at.isoformat(),
                    'statistics': stats
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to get scene {scene_id}: {e}")
            return jsonify({'error': 'Failed to get scene'}), 500
    
    @app.route('/api/scenes/<scene_id>/preview', methods=['POST'])
    def generate_scene_preview(scene_id):
        """Generate a preview image for a scene."""
        if not SCENE_MANAGEMENT_AVAILABLE or not SCENE_PREVIEW_AVAILABLE:
            return jsonify({'error': 'Scene preview not available'}), 503
        
        try:
            scene = app.scene_manager.get_scene(scene_id)
            if not scene:
                return jsonify({'error': 'Scene not found'}), 404
            
            # Generate preview filename
            preview_filename = f"scene_{scene_id}_preview_{int(datetime.now().timestamp())}.png"
            preview_path = app.scene_preview_renderer.preview_dir / preview_filename
            
            # Generate preview
            success = app.scene_preview_renderer.render_scene_preview(
                scene, str(preview_path)
            )
            
            if success and preview_path.exists():
                return jsonify({
                    'success': True,
                    'preview_url': f'/api/preview/{preview_filename}',
                    'scene_id': scene_id
                })
            else:
                return jsonify({'error': 'Failed to generate scene preview'}), 500
                
        except Exception as e:
            logger.error(f"Failed to generate scene preview: {e}")
            return jsonify({'error': 'Failed to generate scene preview'}), 500
    
    @app.route('/api/scenes/<scene_id>/export', methods=['POST'])
    def export_scene(scene_id):
        """Export scene in various formats and modes."""
        if not SCENE_MANAGEMENT_AVAILABLE or not SCENE_EXPORT_AVAILABLE:
            return jsonify({'error': 'Scene export not available'}), 503
        
        try:
            data = request.get_json() or {}
            scene = app.scene_manager.get_scene(scene_id)
            if not scene:
                return jsonify({'error': 'Scene not found'}), 404
            
            export_type = data.get('export_type', 'complete')  # complete, individual, selective
            format = data.get('format', 'obj')
            custom_filename = data.get('filename')
            
            if export_type == 'complete':
                # Export complete scene
                result = app.scene_exporter.export_complete_scene(
                    scene, format=format, custom_filename=custom_filename
                )
                
            elif export_type == 'individual':
                # Export individual object
                object_id = data.get('object_id')
                if not object_id:
                    return jsonify({'error': 'object_id required for individual export'}), 400
                
                scene_object = scene.get_object_by_id(object_id)
                if not scene_object:
                    return jsonify({'error': 'Object not found in scene'}), 404
                
                result = app.scene_exporter.export_individual_object(
                    scene_object, scene_context=scene, format=format, custom_filename=custom_filename
                )
                
            elif export_type == 'selective':
                # Export selected objects
                object_ids = data.get('object_ids', [])
                if not object_ids:
                    return jsonify({'error': 'object_ids required for selective export'}), 400
                
                combined_file = data.get('combined_file', True)
                result = app.scene_exporter.export_selective_objects(
                    object_ids, scene, format=format, combined_file=combined_file, custom_filename=custom_filename
                )
                
            else:
                return jsonify({'error': 'Invalid export_type. Must be: complete, individual, or selective'}), 400
            
            if result and result.success:
                return jsonify({
                    'success': True,
                    'export_result': {
                        'scene_id': result.scene_id,
                        'export_type': result.export_type,
                        'format': result.format,
                        'exported_objects': result.exported_objects,
                        'output_files': result.output_files,
                        'total_file_size': result.total_file_size,
                        'export_timestamp': result.export_timestamp.isoformat()
                    }
                })
            else:
                error_msg = result.error_message if result else 'Export failed'
                return jsonify({'error': error_msg}), 500
                
        except Exception as e:
            logger.error(f"Failed to export scene {scene_id}: {e}")
            return jsonify({'error': 'Failed to export scene'}), 500
    
    @app.route('/api/scenes/<scene_id>/validate', methods=['POST'])
    def validate_scene(scene_id):
        """Validate a scene for issues and consistency."""
        if not SCENE_MANAGEMENT_AVAILABLE:
            return jsonify({'error': 'Scene management not available'}), 503
        
        try:
            scene = app.scene_manager.get_scene(scene_id)
            if not scene:
                return jsonify({'error': 'Scene not found'}), 404
            
            auto_fix = request.get_json().get('auto_fix', False) if request.get_json() else False
            validation_result = app.scene_validator.validate_scene(scene, auto_fix=auto_fix)
            
            return jsonify({
                'success': True,
                'validation': {
                    'is_valid': validation_result.is_valid,
                    'auto_fixes_applied': validation_result.auto_fixes_applied,
                    'issues': [
                        {
                            'severity': issue.severity.value,
                            'category': issue.category,
                            'message': issue.message,
                            'object_ids': issue.object_ids,
                            'suggestion': issue.suggestion,
                            'auto_fixable': issue.auto_fixable
                        } for issue in validation_result.issues
                    ],
                    'statistics': validation_result.scene_statistics
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to validate scene {scene_id}: {e}")
            return jsonify({'error': 'Failed to validate scene'}), 500


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
    port = int(os.environ.get('PORT', 5001))  # Changed default port to avoid macOS AirPlay conflict
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Flask development server on port {port}")
    logger.info(f"Access the application at: http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)