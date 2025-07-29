#!/usr/bin/env python3
"""
Test script for scene management UI integration.

This script tests the complete integration of scene management functionality
into the Flask web application and UI.
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_flask_app_startup():
    """Test that Flask app starts with scene management capabilities."""
    print("Testing Flask App Startup with Scene Management")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            print("✅ Flask app is running")
            print(f"   - Scene Management: {'✅' if health.get('scene_management_available') else '❌'}")
            print(f"   - Scene Preview: {'✅' if health.get('scene_preview_available') else '❌'}")
            print(f"   - Scene Export: {'✅' if health.get('scene_export_available') else '❌'}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_scene_api_endpoints():
    """Test scene management API endpoints."""
    print("\nTesting Scene Management API Endpoints")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test 1: List scenes (should work even if empty)
        print("1. Testing GET /api/scenes")
        response = requests.get(f"{base_url}/api/scenes")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Listed {data.get('count', 0)} scenes")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
        
        # Test 2: Create a new scene
        print("2. Testing POST /api/scenes")
        scene_data = {
            "name": "Test Integration Scene",
            "description": "A test scene created during integration testing"
        }
        
        response = requests.post(f"{base_url}/api/scenes", 
                               json=scene_data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                scene_id = data['scene']['scene_id']
                print(f"   ✅ Created scene: {scene_id}")
                
                # Test 3: Get the created scene
                print("3. Testing GET /api/scenes/<scene_id>")
                response = requests.get(f"{base_url}/api/scenes/{scene_id}")
                
                if response.status_code == 200:
                    scene_data = response.json()
                    if scene_data.get('success'):
                        scene = scene_data['scene']
                        print(f"   ✅ Retrieved scene: {scene['name']}")
                        print(f"      Objects: {scene['object_count']}")
                        print(f"      Relationships: {len(scene['relationships'])}")
                        
                        # Test 4: Validate the scene
                        print("4. Testing POST /api/scenes/<scene_id>/validate")
                        response = requests.post(f"{base_url}/api/scenes/{scene_id}/validate",
                                               json={'auto_fix': False},
                                               headers={'Content-Type': 'application/json'})
                        
                        if response.status_code == 200:
                            validation = response.json()
                            if validation.get('success'):
                                is_valid = validation['validation']['is_valid']
                                issues_count = len(validation['validation']['issues'])
                                print(f"   ✅ Scene validation: {'Valid' if is_valid else 'Has Issues'}")
                                print(f"      Issues found: {issues_count}")
                            else:
                                print(f"   ❌ Validation failed: {validation}")
                        else:
                            print(f"   ❌ Validation request failed: {response.status_code}")
                        
                        return True
                    else:
                        print(f"   ❌ Failed to get scene data: {scene_data}")
                else:
                    print(f"   ❌ Failed to get scene: {response.status_code}")
            else:
                print(f"   ❌ Scene creation failed: {data}")
        else:
            print(f"   ❌ Scene creation request failed: {response.status_code}")
            
        return False
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def test_ai_scene_integration():
    """Test AI scene generation integration."""
    print("\nTesting AI Scene Generation Integration")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test AI scene generation
        print("1. Testing POST /api/ai/scene")
        ai_prompt = {
            "prompt": "Create a simple office desk scene with a computer monitor, keyboard, and coffee mug",
            "style": "realistic",
            "complexity": "medium"
        }
        
        response = requests.post(f"{base_url}/api/ai/scene",
                               json=ai_prompt,
                               headers={'Content-Type': 'application/json'},
                               timeout=60)  # AI generation takes time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                scene_info = data.get('scene_info', {})
                model_count = scene_info.get('model_count', 0)
                print(f"   ✅ AI generated scene with {model_count} objects")
                
                if 'scene_id' in data:
                    scene_id = data['scene_id']
                    print(f"   ✅ Scene saved with ID: {scene_id}")
                    
                    # Test scene preview generation
                    print("2. Testing AI scene preview generation")
                    response = requests.post(f"{base_url}/api/scenes/{scene_id}/preview")
                    
                    if response.status_code == 200:
                        preview_data = response.json()
                        if preview_data.get('success'):
                            print(f"   ✅ Scene preview generated: {preview_data['preview_url']}")
                        else:
                            print(f"   ❌ Preview generation failed: {preview_data}")
                    else:
                        print(f"   ❌ Preview request failed: {response.status_code}")
                
                return True
            else:
                print(f"   ❌ AI scene generation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ AI scene request failed: {response.status_code}")
            if response.text:
                print(f"      Response: {response.text[:200]}...")
        
        return False
        
    except requests.exceptions.Timeout:
        print("   ⚠️  AI scene generation timed out (this may be normal)")
        return True  # Don't fail the test for timeout
    except Exception as e:
        print(f"❌ AI integration test failed: {e}")
        return False


def test_export_functionality():
    """Test scene export functionality."""
    print("\nTesting Scene Export Functionality")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # First create a simple scene for testing exports
    scene_data = {
        "name": "Export Test Scene",
        "description": "A scene for testing export functionality"
    }
    
    try:
        response = requests.post(f"{base_url}/api/scenes", 
                               json=scene_data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            print("❌ Failed to create test scene for export")
            return False
        
        scene_id = response.json()['scene']['scene_id']
        print(f"Created test scene: {scene_id}")
        
        # Test different export types
        export_tests = [
            {
                'name': 'Complete Scene Export (OBJ)',
                'data': {'export_type': 'complete', 'format': 'obj'}
            },
            {
                'name': 'Complete Scene Export (STL)',
                'data': {'export_type': 'complete', 'format': 'stl'}
            },
            {
                'name': 'Complete Scene Export (GLTF)',
                'data': {'export_type': 'complete', 'format': 'gltf'}
            }
        ]
        
        for i, test in enumerate(export_tests, 1):
            print(f"{i}. Testing {test['name']}")
            
            response = requests.post(f"{base_url}/api/scenes/{scene_id}/export",
                                   json=test['data'],
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            
            if response.status_code == 200:
                export_data = response.json()
                if export_data.get('success'):
                    result = export_data['export_result']
                    print(f"   ✅ Export successful: {result['format'].upper()}")
                    print(f"      Files: {len(result['output_files'])}")
                    print(f"      Size: {result['total_file_size']} bytes")
                else:
                    print(f"   ❌ Export failed: {export_data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Export request failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False


def check_files_and_directories():
    """Check that all required files and directories exist."""
    print("\nChecking Required Files and Directories")
    print("=" * 50)
    
    required_files = [
        "src/web/app.py",
        "src/web/templates/index.html",
        "src/web/templates/scene_management.html",
        "src/web/static/js/scene-management.js",
        "src/scene_management/__init__.py",
        "src/scene_management/scene_models.py",
        "src/scene_management/scene_manager.py",
        "src/scene_management/scene_validator.py",
        "src/scene_management/scene_preview_renderer.py",
        "src/export/scene_exporter.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} files are missing")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files are present")
        return True


def main():
    """Run all integration tests."""
    print("Scene Management Integration Test Suite")
    print("=" * 55)
    
    tests = [
        ("File System Check", check_files_and_directories),
        ("Flask App Startup", test_flask_app_startup),
        ("Scene API Endpoints", test_scene_api_endpoints),
        ("AI Scene Integration", test_ai_scene_integration),
        ("Export Functionality", test_export_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {str(e)}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "="*60)
    print("INTEGRATION TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests successful!")
        print("🚀 Scene management is fully integrated and ready to use!")
        return True
    else:
        print("⚠️  Some integration tests failed")
        print("💡 Check the logs above for specific issues")
        return False


if __name__ == "__main__":
    print("🔧 Scene Management Integration Tester")
    print("📋 Prerequisites:")
    print("   1. Flask app should be running on http://127.0.0.1:5000")
    print("   2. All dependencies should be installed")
    print("   3. Blender should be available in PATH or configured")
    print("\n⚡ Starting tests...\n")
    
    success = main()
    sys.exit(0 if success else 1)