"""
Flask application factory for Python Blender AI Modeling.

This module provides a clean application factory pattern for creating
and configuring the Flask application with proper service initialization.
"""

import logging
from flask import Flask, render_template
from pathlib import Path

from .config import config
from .services.dependency_manager import dependency_manager
from .routes.api_routes import register_api_routes
from .routes.ai_routes import register_ai_routes
from .routes.scene_routes import register_scene_routes

logger = logging.getLogger(__name__)


def create_app(config_override: dict = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_override: Optional configuration overrides
        
    Returns:
        Configured Flask application instance
    """
    # Create Flask app with proper template and static paths
    template_dir = Path(__file__).parent / 'templates'
    static_dir = Path(__file__).parent / 'static'
    
    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir)
    )
    
    # Apply configuration
    app.config.update(config.flask_config)
    if config_override:
        app.config.update(config_override)
    
    # Initialize services and attach to app context
    _initialize_services(app)
    
    # Register routes
    _register_routes(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    logger.info("Flask application created successfully")
    return app


def _initialize_services(app: Flask) -> None:
    """Initialize and attach services to the Flask application."""
    try:
        # Attach service availability info to app context
        app.blender_available = dependency_manager.is_available('blender')
        app.export_available = dependency_manager.is_available('export')
        app.ai_available = dependency_manager.is_available('ai')
        app.scene_management_available = dependency_manager.is_available('scene_management')
        
        # Initialize Blender tools if available
        if app.blender_available:
            blender_services = dependency_manager.get_service('blender')
            app.blender_executor = blender_services['executor_class'](
                blender_path=app.config['BLENDER_PATH'],
                timeout=app.config['BLENDER_TIMEOUT']
            )
            app.script_generator = blender_services['generator_class'](clear_scene=True)
            
            # Initialize preview renderer
            app.preview_renderer = blender_services['renderer_class'](
                blender_path=app.config['BLENDER_PATH'],
                timeout=app.config['BLENDER_TIMEOUT']
            )
            # Set absolute path for preview directory
            app.preview_renderer.preview_dir = config.preview_dir
            app.preview_renderer.preview_dir.mkdir(exist_ok=True)
            
            logger.info("Blender services initialized successfully")
        
        # Initialize export tools if available
        if app.export_available:
            export_services = dependency_manager.get_service('export')
            app.obj_exporter = export_services['obj_exporter'](
                config.export_dir,
                blender_path=app.config['BLENDER_PATH'],
                timeout=app.config['BLENDER_TIMEOUT']
            )
            app.gltf_exporter = export_services['gltf_exporter'](
                config.export_dir,
                blender_path=app.config['BLENDER_PATH'],
                timeout=app.config['BLENDER_TIMEOUT']
            )
            app.stl_exporter = export_services['stl_exporter'](
                config.export_dir,
                blender_path=app.config['BLENDER_PATH'],
                timeout=app.config['BLENDER_TIMEOUT']
            )
            
            logger.info("Export services initialized successfully")
        
        # Initialize AI tools if available
        if app.ai_available:
            ai_services = dependency_manager.get_service('ai')
            app.ai_client = ai_services['client_class']()
            app.model_interpreter = ai_services['interpreter_class']()
            app.prompt_engineer = ai_services['engineer_class']()
            app.script_validator = ai_services['validator_class']()
            
            logger.info("AI integration initialized successfully")
        
        # Initialize scene management if available
        if app.scene_management_available:
            scene_services = dependency_manager.get_service('scene_management')
            app.scene_manager = scene_services['manager_class'](
                scenes_directory=config.scenes_dir
            )
            app.scene_validator = scene_services['validator_class']()
            
            # Optional scene services
            if 'preview_renderer' in scene_services:
                app.scene_preview_renderer = scene_services['preview_renderer'](
                    blender_executable=app.config['BLENDER_PATH']
                )
                logger.info("Scene preview renderer initialized")
            
            if 'scene_exporter' in scene_services:
                app.scene_exporter = scene_services['scene_exporter'](
                    output_dir=config.export_dir / "scene_exports",
                    blender_path=app.config['BLENDER_PATH'],
                    timeout=app.config['BLENDER_TIMEOUT']
                )
                logger.info("Scene exporter initialized")
            
            logger.info("Scene management initialized successfully")
        
    except Exception as e:
        logger.error(f"Service initialization failed: {str(e)}")
        # Continue without failing services - app will handle gracefully


def _register_routes(app: Flask) -> None:
    """Register all application routes."""
    # Register main page route
    @app.route('/')
    def index():
        """Main application page."""
        return render_template('index.html')
    
    # Register API routes
    register_api_routes(app)
    
    # Register AI routes if AI is available
    if dependency_manager.is_available('ai'):
        register_ai_routes(app)
    
    # Register scene routes if scene management is available
    if dependency_manager.is_available('scene_management'):
        register_scene_routes(app)
    
    logger.info("All routes registered successfully")


def _register_error_handlers(app: Flask) -> None:
    """Register application error handlers."""
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {str(error)}")
        return render_template('500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle uncaught exceptions."""
        logger.error(f"Uncaught exception: {str(e)}", exc_info=True)
        return {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }, 500
    
    logger.info("Error handlers registered successfully")