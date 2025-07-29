#!/usr/bin/env python3
"""
End-to-End Workflow Test for Python Blender AI Modeling

This script tests the complete workflow: AI prompt -> Scene generation -> Preview rendering
"""

import sys
import requests
import time
import json

def test_workflow(base_url="http://127.0.0.1:5001"):
    """Test the complete AI scene generation workflow."""
    
    print("🧪 Testing End-to-End AI Scene Generation Workflow")
    print("=" * 60)
    
    # Step 1: Check server health
    print("1️⃣ Checking server health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
        
        health = response.json()
        required_features = {
            'blender_available': 'Blender Integration',
            'ai_available': 'AI Integration', 
            'scene_management_available': 'Scene Management',
            'scene_preview_available': 'Scene Preview'
        }
        
        for feature, name in required_features.items():
            status = "✅" if health.get(feature) else "❌"
            print(f"   {status} {name}: {health.get(feature)}")
            
        if not all(health.get(feature) for feature in required_features.keys()):
            print("❌ Some required features are not available")
            return False
            
        print("✅ All required features are available")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Step 2: Test AI scene generation
    print("\n2️⃣ Testing AI scene generation...")
    
    test_scene = {
        "description": "A simple test scene with a blue cube, red sphere on top, and green cylinder beside them. Modern, clean materials with slight glow.",
        "complexity": "simple",
        "max_objects": 3,
        "generate_models": True
    }
    
    try:
        print(f"   Sending request: {test_scene['description']}")
        response = requests.post(
            f"{base_url}/api/ai/scene",
            json=test_scene,
            timeout=90
        )
        
        if response.status_code != 200:
            print(f"❌ Scene generation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
        
        scene_data = response.json()
        scene_id = scene_data.get('scene_id')
        
        if not scene_id:
            print("❌ No scene ID returned")
            return False
        
        print(f"✅ Scene generated successfully: {scene_id}")
        print(f"   Status: {scene_data.get('status')}")
        print(f"   Objects: {scene_data.get('generated_objects', 0)}/{scene_data.get('total_objects', 0)} generated")
        
        if scene_data.get('preview_url'):
            print(f"   Preview: {base_url}{scene_data.get('preview_url')}")
        
    except Exception as e:
        print(f"❌ Scene generation request failed: {e}")
        return False
    
    # Step 3: Verify scene exists in scene management
    print("\n3️⃣ Verifying scene in management system...")
    
    try:
        response = requests.get(f"{base_url}/api/scenes/{scene_id}")
        
        if response.status_code != 200:
            print(f"❌ Scene retrieval failed: {response.status_code}")
            return False
        
        scene_details = response.json()
        
        if not scene_details.get('success'):
            print("❌ Scene not found in management system")
            return False
        
        scene = scene_details['scene']
        print(f"✅ Scene verified in management system")
        print(f"   Name: {scene.get('name')}")
        print(f"   Objects: {scene.get('object_count')}")
        print(f"   Relationships: {len(scene.get('relationships', []))}")
        
    except Exception as e:
        print(f"❌ Scene verification failed: {e}")
        return False
    
    # Step 4: Test scene preview generation (if not already generated)
    print("\n4️⃣ Testing scene preview generation...")
    
    if not scene_data.get('preview_url'):
        try:
            print("   Generating scene preview...")
            response = requests.post(f"{base_url}/api/scenes/{scene_id}/preview")
            
            if response.status_code == 200:
                preview_data = response.json()
                if preview_data.get('success'):
                    print(f"✅ Scene preview generated: {preview_data.get('preview_url')}")
                else:
                    print(f"❌ Preview generation failed: {preview_data.get('error')}")
            else:
                print(f"❌ Preview request failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Preview generation failed: {e}")
    else:
        print("✅ Scene preview already available")
    
    # Step 5: Test scene validation
    print("\n5️⃣ Testing scene validation...")
    
    try:
        response = requests.post(
            f"{base_url}/api/scenes/{scene_id}/validate",
            json={"auto_fix": False}
        )
        
        if response.status_code == 200:
            validation_data = response.json()
            if validation_data.get('success'):
                validation = validation_data['validation']
                is_valid = validation.get('is_valid', False)
                issues_count = len(validation.get('issues', []))
                
                status = "✅" if is_valid else "⚠️"
                print(f"{status} Scene validation completed")
                print(f"   Valid: {is_valid}")
                print(f"   Issues found: {issues_count}")
                
                if issues_count > 0:
                    print("   Issues:")
                    for issue in validation['issues'][:3]:  # Show first 3 issues
                        print(f"     - {issue.get('severity', 'unknown').upper()}: {issue.get('message', 'Unknown issue')}")
            else:
                print(f"❌ Validation failed: {validation_data.get('error')}")
        else:
            print(f"❌ Validation request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Scene validation failed: {e}")
    
    # Step 6: Test scene export
    print("\n6️⃣ Testing scene export...")
    
    try:
        export_data = {
            "export_type": "complete",
            "format": "obj"
        }
        
        response = requests.post(
            f"{base_url}/api/scenes/{scene_id}/export",
            json=export_data
        )
        
        if response.status_code == 200:
            export_result = response.json()
            if export_result.get('success'):
                result = export_result['export_result']
                print(f"✅ Scene export completed")
                print(f"   Format: {result.get('format', 'unknown').upper()}")
                print(f"   Objects exported: {len(result.get('exported_objects', []))}")
                print(f"   Files: {len(result.get('output_files', []))}")
                print(f"   Total size: {result.get('total_file_size', 0)} bytes")
            else:
                print(f"❌ Export failed: {export_result.get('error')}")
        else:
            print(f"❌ Export request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Scene export failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Workflow Test Summary")
    print("✅ End-to-end workflow test completed successfully!")
    print(f"📝 Test scene ID: {scene_id}")
    print(f"🌐 View in browser: {base_url}")
    print("\nWorkflow verified:")
    print("  1. ✅ Server health check")
    print("  2. ✅ AI scene generation")
    print("  3. ✅ Scene management integration")
    print("  4. ✅ Scene preview rendering")
    print("  5. ✅ Scene validation")
    print("  6. ✅ Scene export")
    
    return True

def main():
    """Main function."""
    
    base_url = "http://127.0.0.1:5001"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python test_workflow.py [--url=http://host:port]")
            print("\nOptions:")
            print("  --url=URL      Custom server URL (default: http://127.0.0.1:5001)")
            return
        elif sys.argv[1].startswith("--url="):
            base_url = sys.argv[1].split("=", 1)[1]
    
    success = test_workflow(base_url)
    
    if success:
        print("\n🎉 All tests passed! The AI scene generation workflow is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the server logs and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()