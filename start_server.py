#!/usr/bin/env python3
"""
Startup script for the Blender AI Modeling web application.

This script starts the Flask development server with proper configuration
and provides helpful startup information.
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
# Also add project root for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Start the Flask development server."""
    print("🚀 Starting Blender AI Modeling Web Application...")
    print("=" * 50)
    
    # Check if Blender is available
    import subprocess
    try:
        result = subprocess.run(['blender', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Blender found and accessible")
        else:
            print("⚠️  Blender may not be properly installed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Blender not found - model generation will not work")
        print("   Please install Blender and ensure it's in your PATH")
    
    # Set up environment
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Server will start on: http://127.0.0.1:{port}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print("=" * 50)
    
    # Import and start the Flask app
    try:
        from web.app import create_app
        app = create_app()
        
        print("✅ Flask application initialized successfully")
        print("\n📖 Usage:")
        print("   1. Click 'Generate Model' to create a cube")
        print("   2. Adjust size and position parameters")
        print("   3. Export as OBJ file when generation completes")
        print("   4. Press Ctrl+C to stop the server")
        print("\n🌟 Starting server...")
        
        # Start the server
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except ImportError as e:
        print(f"❌ Failed to import Flask application: {e}")
        print("   Make sure you're in the project directory and dependencies are installed")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user. Goodbye!")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()