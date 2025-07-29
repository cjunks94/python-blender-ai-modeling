# Python Blender AI Modeling

A modern web application for creating and manipulating 3D models using Blender programmatically with AI integration.

## Overview

This web application provides an intuitive interface for generating 3D models by translating user inputs into Blender Python (bpy) scripts. The app executes these scripts in Blender's background mode through a modern web interface, enabling programmatic 3D modeling without requiring direct Blender knowledge.

### Key Features

- **Modern Web UI**: Responsive interface built with HTML, Tailwind CSS, and vanilla JavaScript
- **AI-Powered Generation**: Natural language 3D model creation using Claude API integration
- **Multiple Object Types**: Generate cubes, spheres, cylinders, and planes with full parameter control
- **Real-time Interaction**: Interactive forms with live parameter feedback, rotation controls, and material settings
- **Blender Integration**: Seamless background execution of Blender scripts via subprocess with enhanced error handling
- **Model Previews**: Automatic thumbnail generation using Blender's Cycles render engine
- **Multi-Format Export**: Support for OBJ, GLTF/GLB, and STL formats with direct download
- **Enhanced Error Handling**: Retry mechanisms, categorized errors, and user-friendly messages
- **Security-First AI**: Comprehensive validation and safety checks for AI-generated content
- **Test-Driven Development**: Comprehensive test coverage ensuring reliability and maintainability
- **Modular Architecture**: Clean separation of web interface, API logic, Blender integration, AI, and export functionality

## Prerequisites

- Python 3.8 or higher
- Blender 3.0+ installed and accessible via command line (4.5+ recommended for latest features)
- Virtual environment support (recommended)
- **Optional**: Anthropic API key for AI-powered model generation

### Verifying Blender Installation

Ensure Blender is accessible from command line:

```bash
blender --version
# Should output Blender version information
```

## Quick Start Guide

**Get up and running in 5 minutes:**

```bash
# 1. Clone and navigate to project
git clone https://github.com/cjunker/python-blender-ai-modeling.git
cd python-blender-ai-modeling

# 2. Set up Python environment  
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure Blender path (IMPORTANT!)
python setup_blender.py
# This will find Blender and create a .env file

# 5. Optional: Configure AI (for natural language generation)
export ANTHROPIC_API_KEY="your-claude-api-key-here"
# Or add to .env file: ANTHROPIC_API_KEY=your-claude-api-key-here

# 6. Run the application
python start_server.py
# Or: python src/web/app.py

# 7. Open browser to http://127.0.0.1:5001
```

**Create your first model:**

**Manual Creation:**
1. Select object type (cube, sphere, cylinder, or plane)
2. Adjust size, position, rotation, and material settings
3. Click "Generate Model"
4. View the automatic preview thumbnail
5. Export in your preferred format (OBJ, GLTF, GLB, STL)

**AI-Powered Creation:**
1. Click "AI Generate" button
2. Describe your model: "A shiny metallic sphere for a sci-fi scene"
3. Choose style and complexity preferences
4. Let AI interpret and generate your model
5. View preview and export as desired

## Example Gallery

### What You Can Create

**Primitive Objects**:
- **Cubes**: Architectural blocks, building components, containers
- **Spheres**: Planets, balls, decorative orbs, sci-fi elements
- **Cylinders**: Columns, pipes, towers, mechanical parts
- **Planes**: Floors, walls, flat surfaces, terrain patches

**Model Parameters**:
- **Size Range**: 0.1 to 10.0 units for all object types
- **Position**: Full 3D positioning (X, Y, Z coordinates: -10 to 10 units)
- **Rotation**: Complete rotation control (X, Y, Z axes: -180° to 180°)
- **Materials**: Color selection, metallic/roughness properties, emission effects
- **Export Formats**: OBJ, GLTF/GLB, STL with proper normals and materials

**AI-Generated Examples**:
- "A glowing red sphere for a sci-fi scene" → Emissive red sphere with proper glow settings
- "An ancient stone pillar with weathered texture" → Cylinder with realistic stone materials
- "A futuristic metallic cube with sharp edges" → High-metallic, low-roughness cube
- "A wooden table surface" → Plane with wood-like material properties

**Generated Files**:
All models are exported in industry-standard formats compatible with:
- **3D Software**: Blender, Maya, 3ds Max, Cinema 4D
- **Game Engines**: Unity, Unreal Engine, Godot
- **3D Printing**: Cura, PrusaSlicer, Bambu Studio
- **CAD Applications**: Fusion 360, SolidWorks, SketchUp
- **Web/AR/VR**: Three.js, A-Frame, WebXR applications

## Installation

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/cjunker/python-blender-ai-modeling.git
cd python-blender-ai-modeling
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the application:
```bash
pip install -e .
```

4. Run the web application:
```bash
python main.py
```

5. Open your browser and visit: `http://127.0.0.1:5001`

### Development Installation

For development with all features and testing tools:

```bash
pip install -e ".[dev,ai,advanced-ui,export]"
```

## Usage

### Basic Object Creation

1. **Launch the application**:
   ```bash
   python main.py
   # Or alternatively:
   python src/web/app.py
   ```

2. **Access the web interface**:
   - Open your browser to `http://127.0.0.1:5001`

3. **Create a 3D model**:
   - **Object Types**: Cube, Sphere, Cylinder, Plane
   - **Manual Mode**: Adjust parameters via sliders and controls
     - **Size**: 0.1 to 10.0 units
     - **Position**: X, Y, Z coordinates (-10.0 to 10.0 units)
     - **Rotation**: X, Y, Z rotation (-180° to 180°)
     - **Materials**: Color picker, metallic/roughness sliders, emission effects
   - **AI Mode**: Describe your model in natural language
   - Click "Generate Model" or "AI Generate" to create your 3D object

4. **View and export your model**:
   - **Preview**: Automatic thumbnail generation with Cycles rendering
   - **Export Formats**: OBJ, GLTF/GLB, STL
   - Files are saved to `./exports/` directory
   - Download directly through the web interface

### API Usage

The application also provides REST API endpoints for programmatic access:

#### Health Check
```bash
curl http://localhost:5001/api/health
```

#### Generate Model
```bash
curl -X POST http://localhost:5001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "object_type": "cube",
    "size": 2.0,
    "pos_x": 1.0
  }'
```

#### Export Model
```bash
curl -X POST http://localhost:5001/api/export \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "my_cube_model",
    "format": "obj",
    "model_params": {
      "object_type": "cube",
      "size": 2.0,
      "pos_x": 1.0
    }
  }'
```

#### Download Exported File
```bash
curl http://localhost:5001/api/download/my_cube_model.obj -o model.obj
```

#### AI Model Generation
```bash
curl -X POST http://localhost:5001/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A glowing red sphere for a sci-fi scene",
    "preferred_style": "creative",
    "complexity": "medium",
    "user_level": "intermediate"
  }'
```

#### AI Scene Generation (Advanced)
```bash
curl -X POST http://localhost:5001/api/ai/scene \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A modern office desk setup",
    "max_objects": 5,
    "complexity": "medium"
  }'
```

### Troubleshooting

#### Common Issues

1. **Blender not found**: Ensure Blender is installed and accessible via `blender` command
2. **Permission errors**: Check that the application has write permissions for the `exports/` directory
3. **Timeout errors**: Large or complex models may take longer - the default timeout is 30 seconds

#### Error Messages

The application provides detailed error messages for common issues:
- **Blender execution timeout**: Operation took too long
- **Blender not found**: Blender executable not accessible
- **Permission denied**: File system permission issues
- **Invalid parameters**: Model parameter validation errors

## Development

### Project Structure

```
python-blender-ai-modeling/
├── src/
│   ├── web/                   # Web interface (Flask app, templates, static files)
│   │   ├── templates/         # HTML templates (base.html, index.html)
│   │   ├── static/
│   │   │   ├── js/           # JavaScript controllers
│   │   │   │   ├── model-form.js      # Manual model generation
│   │   │   │   ├── ai-integration.js  # AI-powered generation
│   │   │   │   └── ui-interactions.js # UI controls and interactions
│   │   │   └── css/          # Stylesheets (Tailwind CSS)
│   │   └── app.py            # Flask application with all endpoints
│   ├── blender_integration/   # Blender API integration and execution
│   │   ├── executor.py       # Blender subprocess execution
│   │   ├── script_generator.py # bpy script generation
│   │   └── preview_renderer.py # Model preview generation
│   ├── ai_integration/        # AI-powered model generation
│   │   ├── ai_client.py      # Claude API client
│   │   ├── model_interpreter.py # AI response interpretation
│   │   ├── prompt_engineer.py # Prompt optimization
│   │   └── script_validator.py # Security validation
│   └── export/               # Multi-format model export
│       ├── obj_exporter.py   # OBJ format support
│       ├── gltf_exporter.py  # GLTF/GLB format support
│       └── stl_exporter.py   # STL format support
├── tests/                    # Comprehensive test coverage
├── exports/                  # Generated model files
├── previews/                 # Model preview thumbnails
├── docs/                     # Documentation
├── CLAUDE.md                 # AI assistant guidance
└── requirements.txt          # Python dependencies
```

### Testing

The project has comprehensive test coverage with 64 tests across all modules:

```bash
# Run all tests (using unittest)
python -m unittest discover tests -v

# Run specific test modules
python -m unittest tests.test_blender_integration -v  # 26 tests
python -m unittest tests.test_script_generator -v    # 22 tests  
python -m unittest tests.test_export -v              # 16 tests

# Run with pytest (if installed)
python -m pytest

# With coverage (if pytest-cov installed)
python -m pytest --cov=src --cov-report=html
```

**Test Coverage by Module**:
- **Blender Integration**: 26 tests covering subprocess execution, error handling, retry mechanisms
- **Script Generation**: 22 tests covering bpy script generation and validation  
- **Export Functionality**: 16 tests covering OBJ export, file operations, error scenarios
- **Total**: 64 tests ensuring reliability and maintainability

### Code Quality

Format and lint code:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

### Security Audit

Check for security issues:

```bash
pip-audit
```

## Current Implementation Status

### ✅ **Fully Implemented Features**

- **Modern Web Interface**: Responsive UI built with HTML, Tailwind CSS, and vanilla JavaScript
- **Multiple Object Types**: Complete support for cubes, spheres, cylinders, and planes
- **Full Parameter Control**: Size, position (X,Y,Z), rotation (X,Y,Z), and material properties
- **Material System**: Color picker, metallic/roughness sliders, emission effects with strength control
- **AI-Powered Generation**: Natural language model creation using Claude API integration
  - Prompt optimization and style selection
  - Safety validation and script sanitization
  - AI reasoning display and user suggestions
- **Model Previews**: Automatic thumbnail generation using Blender's Cycles render engine
- **Multi-Format Export**: Support for OBJ, GLTF/GLB, and STL formats
- **Blender Integration**: Robust subprocess execution with comprehensive error handling
- **Complete API**: REST endpoints for manual generation, AI generation, and scene planning
- **Security-First Design**: Comprehensive validation for all AI-generated content
- **Error Handling**: Categorized errors, retry mechanisms, and user-friendly messages
- **Testing**: Comprehensive test coverage ensuring reliability across all modules

### 🚧 **Advanced Features Ready for Extension**

- **Complex Scene Generation**: Framework implemented, UI needs development
- **Batch Processing**: Backend architecture supports multiple model generation
- **Material Suggestions**: AI-powered material recommendations (API ready)
- **Performance Optimization**: Preview caching system ready for implementation

### 📋 **Future Enhancements**

The modular architecture easily supports:
- Real-time 3D preview using Three.js
- Advanced lighting and camera controls
- Custom material libraries and presets
- Model history and user accounts
- Plugin system for custom object types

## Configuration

### Environment Variables

The application works out-of-the-box with default settings. For customization, set these environment variables:

```bash
# Flask Configuration
FLASK_DEBUG=False                    # Set to True for development
PORT=5001                           # Web server port (default changed to avoid macOS AirPlay conflict)
SECRET_KEY=your-secret-key-here     # For session security

# Blender Configuration
BLENDER_EXECUTABLE_PATH=blender     # Path to Blender executable
BLENDER_TIMEOUT=30                  # Execution timeout in seconds

# AI Configuration (Optional)
ANTHROPIC_API_KEY=your-claude-api-key   # Required for AI-powered generation
# Get your API key from: https://console.anthropic.com/

# Export Configuration
EXPORT_DIR=./exports               # Directory for exported files

# Logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
```

### AI Setup (Optional)

To enable AI-powered model generation:

1. **Get an Anthropic API Key**:
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create an account and generate an API key
   - Note: Claude API usage has costs based on tokens processed

2. **Set up your API key**:
   ```bash
   # Option 1: Environment variable (recommended for production)
   export ANTHROPIC_API_KEY="your-api-key-here"
   
   # Option 2: Add to .env file (recommended for development)
   echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env
   ```

3. **Verify AI Integration**:
   - Start the application
   - Visit `/api/health` - should show `"ai_available": true`
   - The "AI Generate" button should be enabled in the UI

**Without API Key**: The application works fully in manual mode. The AI Generate button will show "AI Unavailable" if no API key is configured.

**For development**, create a `.env` file in the project root:
```bash
FLASK_DEBUG=True
BLENDER_TIMEOUT=60
LOG_LEVEL=DEBUG
ANTHROPIC_API_KEY=your-api-key-here
```

## Architecture

### Design Principles

- **Modular Design**: Clear separation of concerns across UI, Blender integration, AI, and export modules
- **Test-Driven Development**: Comprehensive test coverage with mocking for external dependencies
- **Error Handling**: Robust error handling for subprocess calls and API interactions
- **Security**: Safe input validation and secure API key management

### Technology Stack

- **Python 3.8+**: Core language
- **Flask**: Web framework for backend API
- **HTML/CSS/JavaScript**: Frontend with Tailwind CSS styling
- **Subprocess**: Blender background execution
- **Requests**: HTTP client for AI APIs
- **Pytest**: Testing framework

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Follow TDD principles: write tests first
4. Ensure code passes all quality checks
5. Submit a pull request

### Development Workflow

1. Write failing tests
2. Implement minimal code to pass tests
3. Refactor and improve
4. Commit frequently with descriptive messages
5. Push and create pull request

## Roadmap

### Phase 1: Core Foundation (MVP) ✅ **COMPLETED**
- [x] Project setup and structure
- [x] Modern web UI with responsive design
- [x] Blender integration with subprocess execution
- [x] Enhanced error handling and retry mechanisms
- [x] Parametric script generation for all primitive objects
- [x] Multi-format export functionality (OBJ, GLTF/GLB, STL)
- [x] Comprehensive test coverage

### Phase 2: Enhanced Features ✅ **COMPLETED**
- [x] Multiple object types (cube, sphere, cylinder, plane)
- [x] Advanced parameter controls (rotation, materials, emission)
- [x] Model preview thumbnails with Cycles rendering
- [x] Full material system with metallic/roughness controls
- [x] Complete UI with live parameter feedback

### Phase 3: AI Integration ✅ **COMPLETED**
- [x] Natural language processing for model descriptions
- [x] Claude API integration with security validation
- [x] Intelligent prompt engineering and optimization
- [x] AI response interpretation and parameter conversion
- [x] Safety validation and script sanitization
- [x] Complete AI generation pipeline

### Phase 4: Advanced Features (Next Priority)
- [ ] Complex scene generation with multiple objects
- [ ] Real-time 3D preview using Three.js
- [ ] Batch processing capabilities
- [ ] Preview caching for performance optimization
- [ ] AI-powered material suggestions

### Phase 5: Enterprise Features (Future)
- [ ] User authentication and model history
- [ ] Plugin system for custom object types
- [ ] Advanced export options and optimization
- [ ] Community model sharing platform
- [ ] Docker containerization and cloud deployment

## License

MIT License - see LICENSE file for details.

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub.