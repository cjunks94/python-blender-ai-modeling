# Python Blender AI Modeling

A desktop application for creating and manipulating 3D models using Blender programmatically with AI integration.

## Overview

This web application provides an intuitive interface for generating 3D models by translating user inputs into Blender Python (bpy) scripts. The app executes these scripts in Blender's background mode through a modern web interface, enabling programmatic 3D modeling without requiring direct Blender knowledge.

### Key Features

- **Modern Web UI**: Responsive interface built with HTML, Tailwind CSS, and vanilla JavaScript
- **Real-time Interaction**: Interactive forms with live parameter feedback and validation
- **Blender Integration**: Seamless background execution of Blender scripts via subprocess with enhanced error handling
- **Parametric Script Generation**: Automatic generation of bpy scripts for 3D objects with validation
- **OBJ Export Support**: Export generated models to OBJ format with direct download
- **Enhanced Error Handling**: Retry mechanisms, categorized errors, and user-friendly messages
- **Test-Driven Development**: 64 comprehensive tests ensuring reliability and maintainability
- **Modular Architecture**: Clean separation of web interface, API logic, Blender integration, and export functionality

## Prerequisites

- Python 3.8 or higher
- Blender 3.0+ installed and accessible via command line
- Virtual environment support (recommended)

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

# 4. Run the application
python src/web/app.py

# 5. Open browser to http://127.0.0.1:5000
```

**Create your first model:**
1. Select "Cube" as object type
2. Set size to 2.0 and position X to 1.0
3. Click "Generate Model"
4. Export as OBJ and download

## Example Gallery

### What You Can Create

**Basic Cube Models**:
- Small cube (size: 0.5) at origin → `small_cube.obj`
- Large cube (size: 3.0) offset to the right → `large_offset_cube.obj` 
- Precise positioning for architectural layouts

**Model Parameters**:
- **Size Range**: 0.1 to 10.0 units
- **Position X**: -10.0 to 10.0 units (Y and Z at origin currently)
- **Export Format**: OBJ with proper vertex normals and face definitions

**Generated Files**:
All models are exported as standard OBJ files that can be imported into:
- Blender (for further editing)
- Unity/Unreal Engine (for game development)
- 3D printing software (Cura, PrusaSlicer)
- CAD applications (Fusion 360, SolidWorks)

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

5. Open your browser and visit: `http://127.0.0.1:5000`

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
   - Open your browser to `http://127.0.0.1:5000`

3. **Create a 3D model**:
   - Currently supports: **Cube objects**
   - Adjust parameters:
     - **Size**: 0.1 to 10.0 units
     - **Position X**: -10.0 to 10.0 units
   - Click "Generate Model" to create your 3D object

4. **Export your model**:
   - After successful generation, use the export functionality
   - Supported format: **OBJ**
   - Files are saved to `./exports/` directory
   - Download directly through the web interface

### API Usage

The application also provides REST API endpoints for programmatic access:

#### Health Check
```bash
curl http://localhost:5000/api/health
```

#### Generate Model
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "object_type": "cube",
    "size": 2.0,
    "pos_x": 1.0
  }'
```

#### Export Model
```bash
curl -X POST http://localhost:5000/api/export \
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
curl http://localhost:5000/api/download/my_cube_model.obj -o model.obj
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
│   │   ├── templates/         # HTML templates
│   │   ├── static/js/         # JavaScript controllers
│   │   └── app.py            # Flask application
│   ├── api/                   # API business logic
│   ├── blender_integration/   # Blender API integration
│   ├── ai_integration/        # AI API integration
│   └── export/               # Model export functionality
├── tests/                    # Test modules
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
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

- **Web Interface**: Modern, responsive UI built with HTML, Tailwind CSS, and vanilla JavaScript
- **Cube Generation**: Create parametric cube objects with size and position controls
- **Blender Integration**: Robust subprocess execution with comprehensive error handling
- **OBJ Export**: Export generated models to OBJ format with automatic file serving
- **API Endpoints**: Complete REST API for programmatic access
- **Error Handling**: Categorized errors, retry mechanisms, and user-friendly messages
- **Testing**: 64 comprehensive tests ensuring reliability across all modules

### 🚧 **Partially Implemented Features**

- **Additional Object Types**: Architecture in place, currently supports cubes only
- **Web UI Forms**: Interface ready for additional object types and parameters

### 📋 **Ready for Implementation**

The codebase is architected to easily support:
- Additional object types (sphere, cylinder, plane) - just need new script generators
- Additional export formats (GLTF, STL) - export framework is modular
- Enhanced parameter controls - UI and validation framework is extensible

## Configuration

### Environment Variables

The application works out-of-the-box with default settings. For customization, set these environment variables:

```bash
# Flask Configuration
FLASK_DEBUG=False                    # Set to True for development
PORT=5000                           # Web server port
SECRET_KEY=your-secret-key-here     # For session security

# Blender Configuration
BLENDER_EXECUTABLE_PATH=blender     # Path to Blender executable
BLENDER_TIMEOUT=30                  # Execution timeout in seconds

# Export Configuration
EXPORT_DIR=./exports               # Directory for exported files

# Logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
```

**For development**, create a `.env` file in the project root:
```bash
FLASK_DEBUG=True
BLENDER_TIMEOUT=60
LOG_LEVEL=DEBUG
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
- [x] Parametric script generation for cube objects
- [x] OBJ export functionality with file download
- [x] Comprehensive test coverage (64 tests)

### Phase 2: Enhanced Features (In Progress)
- [ ] Additional object types (sphere, cylinder, plane)
- [ ] Advanced parameter controls (rotation, materials)
- [ ] Real-time model preview
- [ ] Additional export formats (GLTF, STL)
- [ ] Batch processing capabilities

### Phase 3: AI Integration (Future)
- [ ] Natural language processing for model descriptions
- [ ] AI API integration (Claude/OpenAI)
- [ ] Intelligent bpy code generation and validation
- [ ] Smart parameter recommendations
- [ ] Model suggestion system

### Phase 4: Advanced Features (Future)
- [ ] Plugin system for custom object types
- [ ] Advanced export options and optimization
- [ ] Community model sharing platform
- [ ] Performance optimization and caching
- [ ] Docker containerization

## License

MIT License - see LICENSE file for details.

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub.