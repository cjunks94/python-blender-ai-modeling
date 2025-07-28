# Python Blender AI Modeling

A desktop application for creating and manipulating 3D models using Blender programmatically with AI integration.

## Overview

This application provides a user-friendly interface for generating 3D models by translating user inputs into Blender Python (bpy) scripts. The app executes these scripts in Blender's background mode, enabling programmatic 3D modeling without requiring direct Blender knowledge.

### Key Features

- **Intuitive UI**: Simple interface for creating basic 3D objects (cubes, spheres, cylinders)
- **Blender Integration**: Seamless background execution of Blender scripts via subprocess
- **AI-Powered Modeling** (Stretch Goal): Natural language to 3D model translation using Claude/OpenAI APIs
- **Export Support**: Multiple format support (OBJ, GLTF, STL) with preview capabilities
- **Modular Architecture**: Clean separation of UI, Blender integration, AI features, and export functionality

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

4. Run the application:
```bash
python main.py
```

### Development Installation

For development with all features and testing tools:

```bash
pip install -e ".[dev,ai,advanced-ui,export]"
```

## Usage

### Basic Object Creation

1. Launch the application: `python main.py`
2. Select object type (cube, sphere, cylinder)
3. Adjust parameters (size, position, rotation)
4. Click "Generate" to create the model
5. Export to desired format

### AI-Powered Modeling (Future Feature)

1. Enter natural language description: "Create a red house with a blue roof"
2. The AI translates this into appropriate bpy code
3. Review and modify generated script if needed
4. Execute to create the model

## Development

### Project Structure

```
python-blender-ai-modeling/
├── src/
│   ├── ui/                    # User interface modules
│   ├── blender_integration/   # Blender API integration
│   ├── ai_integration/        # AI API integration
│   └── export/               # Model export functionality
├── tests/                    # Test modules
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

### Testing

Run the test suite:

```bash
# All tests
python -m pytest

# With coverage
python -m pytest --cov=src --cov-report=html

# Specific module
python -m pytest tests/test_ui.py -v
```

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

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```bash
# AI API Keys (optional)
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Blender Configuration
BLENDER_EXECUTABLE_PATH=/path/to/blender  # If not in PATH

# Application Settings
DEFAULT_EXPORT_FORMAT=obj
PREVIEW_RESOLUTION=512
```

## Architecture

### Design Principles

- **Modular Design**: Clear separation of concerns across UI, Blender integration, AI, and export modules
- **Test-Driven Development**: Comprehensive test coverage with mocking for external dependencies
- **Error Handling**: Robust error handling for subprocess calls and API interactions
- **Security**: Safe input validation and secure API key management

### Technology Stack

- **Python 3.8+**: Core language
- **Tkinter/PyQt**: User interface framework
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

### Phase 1: Core Foundation (MVP)
- [x] Project setup and structure
- [ ] Basic UI with object creation forms
- [ ] Blender integration with subprocess execution
- [ ] Simple object generation (cube, sphere, cylinder)

### Phase 2: Enhanced Features
- [ ] Advanced parameter controls
- [ ] Real-time preview
- [ ] Multiple object types and materials
- [ ] Export functionality

### Phase 3: AI Integration
- [ ] Natural language processing
- [ ] AI API integration (Claude/OpenAI)
- [ ] Code generation and validation
- [ ] Smart parameter recommendations

### Phase 4: Advanced Features
- [ ] Batch processing
- [ ] Plugin system
- [ ] Advanced export options
- [ ] Community model sharing

## License

MIT License - see LICENSE file for details.

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub.