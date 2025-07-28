#!/usr/bin/env python3
"""
Main entry point for Python Blender AI Modeling application.

This module serves as the application launcher, initializing the GUI
and coordinating between different components.
"""

import sys
import logging
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure to install the project in development mode: pip install -e .")
    sys.exit(1)


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("blender_ai_modeling.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Python Blender AI Modeling application")
    
    try:
        # Initialize and run the main application window
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()