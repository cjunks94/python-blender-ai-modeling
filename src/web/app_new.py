"""
Main Flask application entry point.

This module creates and runs the Flask application using the application factory pattern.
The original monolithic app.py has been refactored into proper service layers.
"""

import logging
from .app_factory import create_app
from .config import config

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    # Create application using factory pattern
    app = create_app()
    
    # Run the application
    try:
        logger.info(f"Starting web server on {config.host}:{config.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        app.run(
            host=config.host,
            port=config.port,
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == '__main__':
    main()