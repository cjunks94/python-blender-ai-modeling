#!/usr/bin/env python3
"""
Main entry point for Python Blender AI Modeling application.

This module serves as the application launcher, starting the Flask web server.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from web.app_factory import create_app
    from web.config import config
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure to install the project in development mode: pip install -e .")
    print("Also ensure you have installed the requirements: pip install -r requirements.txt")
    sys.exit(1)


def setup_logging() -> None:
    """Configure application logging."""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = os.environ.get('LOG_FILE', 'blender_ai_modeling.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    """Main application entry point."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Python Blender AI Modeling web application")
    
    try:
        # Create Flask application
        app = create_app()
        
        # Use configuration from config module
        logger.info(f"Starting web server on http://{config.host}:{config.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Start the web server
        app.run(host=config.host, port=config.port, debug=app.config['DEBUG'])
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()