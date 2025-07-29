#!/usr/bin/env python3
"""
Test script for scene export functionality.

This script creates test scenes and validates all export modes:
- Individual object export
- Selective objects export  
- Complete scene export
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scene_management import Scene, SceneObject, RelationshipType
from export import SceneExporter, SCENE_EXPORT_AVAILABLE


def create_test_scene():
    """Create a comprehensive test scene."""
    scene = Scene(
        scene_id="export_test_scene",
        name="Export Test Scene",
        description="A test scene for validating export functionality"
    )
    
    # Create a wooden table (cube base)
    table_params = {
        'object_type': 'cube',
        'size': 4.0,
        'pos_x': 0.0,
        'pos_y': 0.0,
        'pos_z': 0.0,
        'rot_x': 0.0,
        'rot_y': 0.0,
        'rot_z': 0.0,
        'color': '#8B4513',  # Saddle brown (wood)
        'metallic': 0.0,
        'roughness': 0.8
    }
    
    table = SceneObject(
        id="table_01",
        name="Wooden_Table",
        object_type="cube",
        parameters=table_params,
        ai_reasoning="Serves as the main table surface"
    )
    
    # Create a red ceramic mug (cylinder)
    mug_params = {
        'object_type': 'cylinder',
        'size': 0.8,
        'pos_x': -1.5,
        'pos_y': 2.5,  # On top of table
        'pos_z': 1.0,
        'rot_x': 0.0,
        'rot_y': 0.0,
        'rot_z': 0.0,
        'color': '#DC143C',  # Crimson red
        'metallic': 0.1,
        'roughness': 0.3
    }
    
    mug = SceneObject(
        id="mug_01", 
        name="Red_Ceramic_Mug",
        object_type="cylinder",
        parameters=mug_params,
        ai_reasoning="Coffee mug placed on the table"
    )
    
    # Create a decorative sphere (glass ball)
    sphere_params = {
        'object_type': 'sphere',
        'size': 0.6,
        'pos_x': 1.2,
        'pos_y': 2.8,  # On top of table
        'pos_z': -0.8,
        'rot_x': 0.0,
        'rot_y': 0.0,
        'rot_z': 0.0,
        'color': '#87CEEB',  # Sky blue (glass-like)
        'metallic': 0.9,
        'roughness': 0.1
    }
    
    sphere = SceneObject(
        id="sphere_01",
        name="Glass_Ball",
        object_type="sphere", 
        parameters=sphere_params,
        ai_reasoning="Decorative glass sphere on the table"
    )
    
    # Create a book (plane, representing a flat book)
    book_params = {
        'object_type': 'plane',
        'size': 1.5,
        'pos_x': 0.5,
        'pos_y': 2.1,  # On table surface
        'pos_z': 0.5,
        'rot_x': 90.0,  # Rotated to lay flat
        'rot_y': 0.0,
        'rot_z': 15.0,  # Slightly angled
        'color': '#228B22',  # Forest green
        'metallic': 0.0,
        'roughness': 0.9
    }
    
    book = SceneObject(
        id="book_01",
        name="Green_Book",
        object_type="plane",
        parameters=book_params,
        ai_reasoning="Book lying on the table surface"
    )
    
    # Add objects to scene
    scene.add_object(table)
    scene.add_object(mug)
    scene.add_object(sphere)
    scene.add_object(book)
    
    # Add spatial relationships
    mug.add_relationship(table.id, RelationshipType.ON_TOP_OF)
    sphere.add_relationship(table.id, RelationshipType.ON_TOP_OF)
    book.add_relationship(table.id, RelationshipType.ON_TOP_OF)
    sphere.add_relationship(mug.id, RelationshipType.NEXT_TO)
    
    return scene


def test_individual_object_export():
    """Test individual object export functionality."""
    print("\n" + "="*50)
    print("Testing Individual Object Export")
    print("="*50)
    
    try:
        # Create test scene and exporter
        scene = create_test_scene()
        exporter = SceneExporter()
        
        print(f"Created test scene: {scene.name} with {scene.object_count} objects")
        
        # Test exporting each object individually in different formats
        formats = ['obj', 'stl', 'gltf']
        results = []
        
        for obj in scene.objects:
            print(f"\nExporting '{obj.name}' ({obj.object_type})...")
            
            for format in formats:
                result = exporter.export_individual_object(
                    obj, scene_context=scene, format=format
                )
                
                results.append(result)
                
                if result.success:
                    print(f"  ✅ {format.upper()}: {Path(result.output_files[0]).name} "
                          f"({result.total_file_size} bytes)")
                else:
                    print(f"  ❌ {format.upper()}: {result.error_message}")
        
        # Summary
        successful = sum(1 for r in results if r.success)
        total = len(results)
        print(f"\n📊 Individual Export Summary: {successful}/{total} successful")
        
        return successful == total
        
    except Exception as e:
        print(f"❌ Individual object export test failed: {str(e)}")
        return False


def test_selective_objects_export():
    """Test selective objects export functionality."""
    print("\n" + "="*50)
    print("Testing Selective Objects Export")
    print("="*50)
    
    try:
        # Create test scene and exporter
        scene = create_test_scene()
        exporter = SceneExporter()
        
        # Test Case 1: Export table items (mug + sphere + book) as combined file
        print("\nTest Case 1: Export table items as combined file")
        table_items = ['mug_01', 'sphere_01', 'book_01']
        
        result = exporter.export_selective_objects(
            table_items, scene, format='obj', combined_file=True,
            custom_filename="table_items_combined"
        )
        
        if result.success:
            print(f"✅ Combined export: {Path(result.output_files[0]).name} "
                  f"({result.total_file_size} bytes)")
            print(f"   Objects: {result.exported_objects}")
        else:
            print(f"❌ Combined export failed: {result.error_message}")
        
        # Test Case 2: Export same objects as separate files
        print("\nTest Case 2: Export table items as separate files")
        result2 = exporter.export_selective_objects(
            table_items, scene, format='stl', combined_file=False
        )
        
        if result2.success:
            print(f"✅ Separate exports: {len(result2.output_files)} files created")
            for file_path in result2.output_files:
                print(f"   - {Path(file_path).name}")
        else:
            print(f"❌ Separate exports failed: {result2.error_message}")
        
        # Test Case 3: Export just decorative items (sphere only)
        print("\nTest Case 3: Export single decorative item")
        result3 = exporter.export_selective_objects(
            ['sphere_01'], scene, format='gltf', combined_file=True,
            custom_filename="decorative_sphere"
        )
        
        if result3.success:
            print(f"✅ Single selective export: {Path(result3.output_files[0]).name}")
        else:
            print(f"❌ Single selective export failed: {result3.error_message}")
        
        # Summary
        all_success = all([result.success, result2.success, result3.success])
        print(f"\n📊 Selective Export Summary: {'All tests passed' if all_success else 'Some tests failed'}")
        
        return all_success
        
    except Exception as e:
        print(f"❌ Selective objects export test failed: {str(e)}")
        return False


def test_complete_scene_export():
    """Test complete scene export functionality."""
    print("\n" + "="*50)
    print("Testing Complete Scene Export")
    print("="*50)
    
    try:
        # Create test scene and exporter
        scene = create_test_scene()
        exporter = SceneExporter()
        
        print(f"Exporting complete scene: {scene.name}")
        print(f"Objects: {[obj.name for obj in scene.objects]}")
        
        # Test exporting complete scene in all formats
        formats = ['obj', 'stl', 'gltf']
        results = []
        
        for format in formats:
            print(f"\nExporting complete scene as {format.upper()}...")
            
            result = exporter.export_complete_scene(
                scene, format=format, 
                custom_filename=f"complete_table_scene"
            )
            
            results.append(result)
            
            if result.success:
                print(f"✅ {format.upper()}: {Path(result.output_files[0]).name} "
                      f"({result.total_file_size} bytes)")
                print(f"   Exported {len(result.exported_objects)} objects")
            else:
                print(f"❌ {format.upper()}: {result.error_message}")
        
        # Summary
        successful = sum(1 for r in results if r.success)
        total = len(results)
        print(f"\n📊 Complete Scene Export Summary: {successful}/{total} successful")
        
        return successful == total
        
    except Exception as e:
        print(f"❌ Complete scene export test failed: {str(e)}")
        return False


def test_multi_format_export():
    """Test multi-format export functionality."""
    print("\n" + "="*50)
    print("Testing Multi-Format Export")
    print("="*50)
    
    try:
        # Create test scene and exporter
        scene = create_test_scene()
        exporter = SceneExporter()
        
        # Test exporting scene in all formats at once
        print("Exporting scene in all formats simultaneously...")
        
        results = exporter.export_scene_formats(
            scene, formats=['obj', 'stl', 'gltf'], export_type='complete'
        )
        
        print(f"\nMulti-format export results:")
        for result in results:
            if result.success:
                print(f"✅ {result.format.upper()}: {Path(result.output_files[0]).name}")
            else:
                print(f"❌ {result.format.upper()}: {result.error_message}")
        
        # Test individual exports for all objects
        print(f"\nExporting all objects individually in OBJ format...")
        individual_results = exporter.export_scene_formats(
            scene, formats=['obj'], export_type='individual_all'
        )
        
        successful_individual = sum(1 for r in individual_results if r.success)
        print(f"Individual exports: {successful_individual}/{len(individual_results)} successful")
        
        # Summary
        successful_multi = sum(1 for r in results if r.success)
        all_success = (successful_multi == len(results) and 
                      successful_individual == len(individual_results))
        
        print(f"\n📊 Multi-Format Export Summary: {'All tests passed' if all_success else 'Some tests failed'}")
        
        return all_success
        
    except Exception as e:
        print(f"❌ Multi-format export test failed: {str(e)}")
        return False


def test_export_listing():
    """Test export file listing functionality."""
    print("\n" + "="*50)
    print("Testing Export Listing")
    print("="*50)
    
    try:
        exporter = SceneExporter()
        
        # List all exports
        all_exports = exporter.list_exports()
        print(f"Found {len(all_exports)} total export files")
        
        if all_exports:
            print("\nRecent exports:")
            for export_info in all_exports[:5]:  # Show first 5
                print(f"  📄 {export_info['filename']} ({export_info['format']}) - "
                      f"{export_info['size']} bytes - {export_info['export_type']}")
        
        # List exports for specific scene
        scene_exports = exporter.list_exports(scene_id="export_test_scene")
        print(f"\nFound {len(scene_exports)} exports for test scene")
        
        return True
        
    except Exception as e:
        print(f"❌ Export listing test failed: {str(e)}")
        return False


def main():
    """Run all scene export tests."""
    print("Scene Export System Test Suite")
    print("=" * 35)
    
    # Check if scene export is available
    if not SCENE_EXPORT_AVAILABLE:
        print("⚠️  Scene export functionality not available - missing dependencies")
        return False
    
    # Run all tests
    tests = [
        ("Individual Object Export", test_individual_object_export),
        ("Selective Objects Export", test_selective_objects_export), 
        ("Complete Scene Export", test_complete_scene_export),
        ("Multi-Format Export", test_multi_format_export),
        ("Export Listing", test_export_listing)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All scene export tests successful!")
        print("📁 Check the 'scene_exports' directory for exported files")
        return True
    else:
        print("⚠️  Some tests failed - check logs above")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)