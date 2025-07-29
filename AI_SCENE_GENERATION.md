# AI Scene Generation Guide

This guide covers the new AI-powered scene generation features in Python Blender AI Modeling.

## Overview

The AI Scene Generation system allows you to create complex 3D scenes from natural language descriptions. The system integrates Claude AI with Blender to generate, render, and manage multi-object scenes with spatial relationships.

## Features

- **Natural Language Scene Creation**: Describe scenes in plain English
- **Multi-Object Generation**: Create scenes with up to 8 objects
- **Spatial Relationships**: Objects are positioned with realistic spatial awareness
- **Real-time Preview**: Generate preview images of complete scenes
- **Scene Management**: Save, load, and organize generated scenes
- **Export Options**: Export complete scenes or individual objects in multiple formats
- **Validation System**: Automatic scene validation with issue detection

## Quick Start

### 1. Prerequisites

Ensure you have:
- Blender installed and accessible from command line
- Anthropic API key set as `ANTHROPIC_API_KEY` environment variable
- Python dependencies installed (`pip install -r requirements.txt`)

### 2. Start the Server

```bash
python main.py
```

The server will start at `http://127.0.0.1:5001`

### 3. Access the Web Interface

Open your browser and navigate to the server URL. You'll see:
- **Single Object Generation**: Create individual 3D objects
- **AI Scene Generation**: Create complex multi-object scenes
- **Scene Management**: Manage and export your scenes

## Using AI Scene Generation

### Via Web Interface

1. **Navigate to Scene Management**: Scroll down to the Scene Management section
2. **Click "🤖 AI Generate Scene"**: Opens the AI scene generation modal
3. **Describe your scene**: Enter a detailed description of what you want to create
4. **Configure settings**:
   - **Complexity**: Simple (2-3 objects), Medium (4-5 objects), Complex (6-8 objects)
   - **Max Objects**: Limit the number of objects (3-8)
   - **Generation Mode**: "Generate & Render" for full scene creation, "Plan Only" for concept validation
5. **Generate**: Click "Generate Scene with AI"

### Via API

```bash
curl -X POST http://127.0.0.1:5001/api/ai/scene \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A modern office desk with laptop, coffee mug, and plant",
    "complexity": "medium",
    "max_objects": 4,
    "generate_models": true
  }'
```

## Scene Description Best Practices

### Effective Descriptions

**Good Examples:**

```
"A modern office desk with a laptop centered on it, a coffee mug to the right, and a small plant to the left. Use clean white and gray materials."

"A kitchen counter with a red apple sitting in a white ceramic bowl, placed on a wooden cutting board. Simple, clean arrangement."

"A sci-fi space station module with glowing blue cylindrical power cores, a central metallic command sphere, and rectangular support structures."
```

**Tips for Better Results:**

1. **Be Specific**: Include materials, colors, and spatial relationships
2. **Mention Positioning**: Use terms like "on top of", "next to", "behind", "centered"
3. **Describe Style**: Modern, vintage, sci-fi, natural, minimalist, etc.
4. **Include Materials**: Metallic, wooden, glass, ceramic, glowing, matte
5. **Set Scale**: Small plant, large table, tiny details, massive structures

### Avoid These Patterns

- Vague descriptions: "Some objects on a table"
- Too many objects: Descriptions with more than 8 distinct items
- Impossible arrangements: Objects floating without support
- Non-primitive shapes: Complex organic forms (current system uses cubes, spheres, cylinders, planes)

## Scene Management Features

### Scene Organization

- **List Scenes**: View all created scenes with object counts
- **Load Scenes**: Select and inspect individual scenes
- **Scene Statistics**: Object counts, relationships, export status

### Preview Generation

- **Scene Previews**: Generate complete scene preview images
- **Object Thumbnails**: Individual object preview images
- **Multiple Angles**: Different camera perspectives (future feature)

### Export Options

1. **Complete Scene**: Export entire scene as single file
2. **Individual Objects**: Export each object separately
3. **Selective Export**: Choose specific objects to export
4. **Multiple Formats**: OBJ, GLTF, STL support

### Scene Validation

- **Collision Detection**: Identify overlapping objects
- **Relationship Validation**: Check spatial consistency
- **Auto-Fix**: Automatic correction of common issues
- **Issue Reporting**: Detailed problem descriptions with solutions

## Testing and Demo Scripts

### Create Demo Scenes

```bash
# Generate 5 demo scenes with full Blender rendering
python create_demo_scene.py

# Generate demo scenes in plan-only mode (faster, no Blender execution)
python create_demo_scene.py --plan-only

# Use custom server URL
python create_demo_scene.py --url=http://localhost:8000
```

### Test Complete Workflow

```bash
# Test end-to-end AI scene generation workflow
python test_workflow.py

# Test with custom server URL
python test_workflow.py --url=http://localhost:8000
```

## API Reference

### Scene Generation Endpoint

**POST** `/api/ai/scene`

```json
{
  "description": "Scene description in natural language",
  "complexity": "simple|medium|complex",
  "max_objects": 3-8,
  "generate_models": true|false
}
```

**Response:**
```json
{
  "scene_id": "ai_scene_1234",
  "source": "ai_generated",
  "description": "Original description",
  "scene_info": {
    "scene_name": "Generated Scene Name",
    "model_count": 4
  },
  "objects": [
    {
      "id": "obj_1",
      "name": "Object 1",
      "object_type": "cube",
      "status": "generated"
    }
  ],
  "total_objects": 4,
  "generated_objects": 3,
  "failed_objects": 1,
  "preview_url": "/api/preview/scene_1234_preview.png",
  "status": "generated",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Scene Management Endpoints

- **GET** `/api/scenes` - List all scenes
- **GET** `/api/scenes/{scene_id}` - Get scene details
- **POST** `/api/scenes/{scene_id}/preview` - Generate scene preview
- **POST** `/api/scenes/{scene_id}/export` - Export scene
- **POST** `/api/scenes/{scene_id}/validate` - Validate scene

## Troubleshooting

### Common Issues

**"AI integration not available"**
- Set the `ANTHROPIC_API_KEY` environment variable
- Verify your API key is valid and has sufficient credits

**"Blender integration not available"**
- Install Blender and ensure it's in your system PATH
- Run `python setup_blender.py` to configure Blender path

**"Scene preview not available"**
- Ensure Blender is properly configured
- Check that the `previews/` directory is writable

**"Objects are overlapping"**
- Use more specific spatial descriptions
- Run scene validation to detect and fix issues
- Try the auto-fix feature in scene validation

### Performance Tips

1. **Start Simple**: Begin with 2-3 objects before creating complex scenes
2. **Use Plan-Only Mode**: Test scene concepts quickly without Blender execution
3. **Batch Generation**: Use demo scripts to create multiple scenes efficiently
4. **Monitor Resources**: Blender execution can be memory-intensive

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export FLASK_DEBUG=true
python main.py
```

## Advanced Usage

### Custom Scene Templates

Create reusable scene templates by saving successful scene descriptions:

```python
# Example: Office scenes template
OFFICE_TEMPLATES = [
    "A executive desk with {laptop_color} laptop, {mug_style} coffee mug, and {plant_type} plant",
    "A meeting room with rectangular table, {chair_count} chairs around it, and presentation screen",
    "A cubicle workspace with computer monitor, keyboard, and personal items"
]

# Use with string formatting
scene_description = OFFICE_TEMPLATES[0].format(
    laptop_color="silver", 
    mug_style="ceramic white",
    plant_type="small succulent"
)
```

### Scene Composition Rules

The AI follows these spatial relationship rules:

1. **Support**: Objects need physical support (table, floor, other objects)
2. **Proximity**: Related objects are placed near each other
3. **Scale**: Object sizes are realistic relative to each other
4. **Balance**: Scenes maintain visual balance and stability

### Material System

Available material properties:
- **Colors**: Hex codes (#FF0000) or color names (red, blue, metallic silver)
- **Metallic**: 0.0 (non-metallic) to 1.0 (fully metallic)
- **Roughness**: 0.0 (mirror smooth) to 1.0 (completely rough)
- **Emission**: Optional glowing effect with intensity 0.0-10.0

## Integration Examples

### Python Script Integration

```python
import requests

def generate_scene(description, complexity="medium"):
    response = requests.post('http://127.0.0.1:5001/api/ai/scene', json={
        'description': description,
        'complexity': complexity,
        'generate_models': True
    })
    
    if response.ok:
        scene_data = response.json()
        print(f"Scene created: {scene_data['scene_id']}")
        return scene_data['scene_id']
    else:
        print(f"Error: {response.json()['error']}")
        return None

# Usage
scene_id = generate_scene("A cozy reading nook with armchair, side table, and lamp")
```

### Blender Add-on Integration

The system can be extended with custom Blender add-ons for advanced scene manipulation.

## Future Enhancements

Planned features:
- **Advanced Camera Controls**: Multiple viewing angles, custom camera positions
- **Animation Support**: Keyframe animations for scene objects  
- **Lighting Design**: AI-powered lighting setup and optimization
- **Texture Generation**: AI-generated textures and materials
- **Scene Physics**: Realistic physics simulation and validation
- **Collaboration**: Multi-user scene editing and version control

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review server logs for detailed error messages
3. Test with the provided demo and test scripts
4. Ensure all dependencies are properly installed

## License

This project is part of the Python Blender AI Modeling system. See the main project LICENSE file for details.