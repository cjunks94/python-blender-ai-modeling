#!/usr/bin/env python3
"""
Test script for scene preview functionality.

This script creates a sample scene and tests the scene preview rendering.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scene_management import Scene, SceneObject, RelationshipType, ScenePreviewRenderer, SCENE_PREVIEW_AVAILABLE
from ai_integration.model_interpreter import ModelInterpreter


def create_test_scene():
    """Create a test scene with multiple objects."""
    scene = Scene(
        scene_id="test_scene",
        name="Test Multi-Object Scene",
        description="A test scene with a cube, sphere, and cylinder"
    )
    
    # Create a cube (base)
    cube_params = {
        'object_type': 'cube',
        'size': 3.0,
        'pos_x': 0.0,
        'pos_y': 0.0,
        'pos_z': 0.0,
        'rot_x': 0.0,
        'rot_y': 0.0,
        'rot_z': 0.0,
        'color': '#8B4513',  # Brown
        'metallic': 0.1,
        'roughness': 0.8
    }
    
    cube = SceneObject(
        id="base_cube",
        name="Base Platform",
        object_type="cube",
        parameters=cube_params,
        ai_reasoning="Acts as a base platform for other objects"
    )
    
    # Create a sphere (on top of cube)
    sphere_params = {
        'object_type': 'sphere',
        'size': 1.0,
        'pos_x': 0.0,
        'pos_y': 4.0,  # On top of the cube
        'pos_z': 0.0,
        'rot_x': 0.0,
        'rot_y': 0.0,
        'rot_z': 0.0,
        'color': '#FF0000',  # Red
        'metallic': 0.3,
        'roughness': 0.2
    }
    
    sphere = SceneObject(
        id="red_sphere",
        name="Red Ball",
        object_type="sphere",
        parameters=sphere_params,
        ai_reasoning="Decorative sphere placed on top of the base"
    )
    
    # Create a cylinder (next to cube)
    cylinder_params = {
        'object_type': 'cylinder',
        'size': 1.5,
        'pos_x': 5.0,  # Next to the cube
        'pos_y': 0.0,
        'pos_z': 0.0,
        'rot_x': 0.0,
        'rot_y': 0.0,
        'rot_z': 0.0,
        'color': '#0000FF',  # Blue
        'metallic': 0.8,
        'roughness': 0.1
    }
    
    cylinder = SceneObject(
        id="blue_cylinder",
        name="Blue Pillar",
        object_type="cylinder",
        parameters=cylinder_params,
        ai_reasoning="Vertical pillar element for visual balance"
    )
    
    # Add objects to scene
    scene.add_object(cube)
    scene.add_object(sphere)
    scene.add_object(cylinder)
    
    # Add relationships
    sphere.add_relationship(cube.id, RelationshipType.ON_TOP_OF)
    cylinder.add_relationship(cube.id, RelationshipType.NEXT_TO)
    
    return scene


def test_scene_preview():
    """Test scene preview rendering."""
    print("Testing Scene Preview Functionality")
    print("=" * 40)
    
    # Check if scene preview is available
    if not SCENE_PREVIEW_AVAILABLE:
        print("⚠️  Scene preview rendering not available - missing dependencies")
        return False
    
    try:
        # Create test scene
        print("Creating test scene...")
        scene = create_test_scene()
        print(f"✅ Created scene '{scene.name}' with {scene.object_count} objects")
        
        # Print scene info
        print(f"   - Objects: {[obj.name for obj in scene.objects]}")
        print(f"   - Relationships: {len(scene.get_all_relationships())}")
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Test scene preview rendering
        print("\nTesting scene preview rendering...")
        renderer = ScenePreviewRenderer()
        
        # Validate scene first
        is_valid, issues = renderer.validate_scene_for_preview(scene)
        if not is_valid:
            print(f"⚠️  Scene validation issues: {issues}")
        else:
            print("✅ Scene validation passed")
        
        # Render scene preview
        scene_preview_path = output_dir / "test_scene_preview.png"
        success = renderer.render_scene_preview(scene, str(scene_preview_path))
        
        if success:
            print(f"✅ Scene preview rendered: {scene_preview_path}")
        else:
            print("❌ Scene preview rendering failed")
            return False
        
        # Test individual object previews
        print("\nTesting individual object previews...")
        for obj in scene.objects:
            obj_preview_path = output_dir / f"{obj.id}_preview.png"
            success = renderer.render_individual_object_preview(
                obj, scene, str(obj_preview_path)
            )
            
            if success:
                print(f"✅ Object preview rendered: {obj.name}")
            else:
                print(f"❌ Failed to render preview for: {obj.name}")
        
        # Test thumbnail generation
        print("\nTesting thumbnail generation...")
        thumbnails = renderer.render_scene_thumbnails(scene, str(output_dir))
        
        if thumbnails:
            print(f"✅ Generated {len(thumbnails)} thumbnails")
            for obj_id, thumbnail_path in thumbnails.items():
                print(f"   - {obj_id}: {Path(thumbnail_path).name}")
        else:
            print("❌ Thumbnail generation failed")
        
        # Test selective object preview
        print("\nTesting selective object preview...")
        selected_objects = [scene.objects[0].id, scene.objects[1].id]  # Cube and sphere
        selective_preview_path = output_dir / "selective_preview.png"
        
        success = renderer.render_selective_objects_preview(
            selected_objects, scene, str(selective_preview_path)
        )
        
        if success:
            print(f"✅ Selective preview rendered: {selective_preview_path}")
        else:
            print("❌ Selective preview rendering failed")
        
        print(f"\n🎉 Scene preview testing completed!")
        print(f"📁 Output files saved to: {output_dir.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scene preview testing failed: {str(e)}")
        return False


def test_ai_integration():
    """Test AI integration with scene previews."""
    print("\nTesting AI Integration with Scene Previews")
    print("=" * 45)
    
    try:
        # Create model interpreter
        interpreter = ModelInterpreter()
        
        # Create test scene
        scene = create_test_scene()
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Test AI scene preview generation
        ai_preview_path = output_dir / "ai_scene_preview.png"
        success = interpreter.generate_scene_preview(scene, str(ai_preview_path))
        
        if success:
            print(f"✅ AI scene preview generated: {ai_preview_path}")
        else:
            print("❌ AI scene preview generation failed")
        
        # Test AI thumbnail generation
        thumbnails = interpreter.generate_object_thumbnails(scene, str(output_dir / "ai_thumbnails"))
        
        if thumbnails:
            print(f"✅ AI generated {len(thumbnails)} thumbnails")
        else:
            print("❌ AI thumbnail generation failed")
        
        return True
        
    except Exception as e:
        print(f"❌ AI integration testing failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Scene Preview System Test")
    print("=" * 25)
    
    # Test basic scene preview functionality
    success1 = test_scene_preview()
    
    # Test AI integration
    success2 = test_ai_integration()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)