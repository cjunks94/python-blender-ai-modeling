#!/usr/bin/env python3
"""
Demo Scene Creator for Python Blender AI Modeling

This script creates a demo scene to test the AI scene generation and preview functionality.
"""

import sys
import json
import requests
import time
from pathlib import Path

# Demo scene descriptions for testing
DEMO_SCENES = [
    {
        "name": "Modern Desk Setup",
        "description": "A modern office desk with a laptop, coffee mug, and small plant. The laptop should be centered on the desk with the mug to the right and the plant to the left. Use clean, minimalist design with white and gray colors.",
        "complexity": "medium",
        "max_objects": 4
    },
    {
        "name": "Simple Kitchen Counter",
        "description": "A kitchen counter with a red apple, white bowl, and wooden cutting board. The apple sits in the bowl, which is placed on the cutting board. Simple, clean arrangement.",
        "complexity": "simple", 
        "max_objects": 3
    },
    {
        "name": "Geometric Art Display",
        "description": "An artistic arrangement of geometric shapes: a large blue cube as the base, a red sphere on top, and two smaller cylindrical pillars on either side. Modern art gallery style with clean colors and precise positioning.",
        "complexity": "medium",
        "max_objects": 4
    },
    {
        "name": "Space Station Module",
        "description": "A futuristic space station module with glowing cylindrical power cores, a central command sphere, and rectangular support structures. Use metallic materials with blue and green glowing accents for a sci-fi aesthetic.",
        "complexity": "complex",
        "max_objects": 6
    },
    {
        "name": "Garden Scene",
        "description": "A simple garden scene with a wooden planter box containing geometric representations of plants (green spheres and cylinders) and a small watering can nearby. Earthy, natural color palette.",
        "complexity": "simple",
        "max_objects": 4
    }
]

def check_server_health(base_url="http://127.0.0.1:5001"):
    """Check if the server is running and all features are available."""
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("Server Status:")
            print(f"  ✓ Server running at {base_url}")
            print(f"  ✓ Blender available: {health.get('blender_available', False)}")
            print(f"  ✓ AI available: {health.get('ai_available', False)}")
            print(f"  ✓ Scene management: {health.get('scene_management_available', False)}")
            print(f"  ✓ Scene preview: {health.get('scene_preview_available', False)}")
            print(f"  ✓ Scene export: {health.get('scene_export_available', False)}")
            return health
        else:
            print(f"❌ Server returned status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return None

def create_demo_scene(scene_config, base_url="http://127.0.0.1:5001", generate_models=True):
    """Create a demo scene using the AI scene generation API."""
    print(f"\n🎬 Creating demo scene: {scene_config['name']}")
    print(f"Description: {scene_config['description']}")
    
    payload = {
        "description": scene_config["description"],
        "complexity": scene_config["complexity"],
        "max_objects": scene_config["max_objects"],
        "generate_models": generate_models
    }
    
    try:
        print("⚡ Sending request to AI scene generation API...")
        response = requests.post(
            f"{base_url}/api/ai/scene",
            json=payload,
            timeout=120  # 2 minutes timeout for scene generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scene generated successfully!")
            print(f"   Scene ID: {data.get('scene_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Total objects: {data.get('total_objects', 0)}")
            
            if generate_models:
                print(f"   Generated objects: {data.get('generated_objects', 0)}")
                print(f"   Failed objects: {data.get('failed_objects', 0)}")
                
                if data.get('preview_url'):
                    print(f"   Preview URL: {base_url}{data.get('preview_url')}")
            
            # Show object details
            if data.get('objects'):
                print("   Objects in scene:")
                for obj in data['objects']:
                    if generate_models:
                        status = obj.get('status', 'unknown')
                        status_emoji = "✅" if status == "generated" else "❌"
                        print(f"     {status_emoji} {obj.get('name', 'Object')}: {obj.get('object_type', 'unknown')} ({status})")
                    else:
                        print(f"     📝 {obj.get('name', 'Object')}: {obj.get('object_type', 'unknown')} (planned)")
            
            return data
        else:
            print(f"❌ Scene generation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                if 'message' in error_data:
                    print(f"   Details: {error_data['message']}")
            except:
                print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_scene_management_api(base_url="http://127.0.0.1:5001"):
    """Test basic scene management API endpoints."""
    print("\n🔧 Testing Scene Management API...")
    
    try:
        # List existing scenes
        response = requests.get(f"{base_url}/api/scenes")
        if response.status_code == 200:
            scenes_data = response.json()
            if scenes_data.get('success'):
                scenes = scenes_data.get('scenes', [])
                print(f"✅ Found {len(scenes)} existing scenes")
                for scene in scenes:
                    print(f"   - {scene.get('name', 'Unnamed')} ({scene.get('object_count', 0)} objects)")
            else:
                print("❌ Failed to list scenes")
        else:
            print(f"❌ Scene listing failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Scene management API test failed: {e}")

def main():
    print("🚀 Python Blender AI Modeling - Demo Scene Creator")
    print("=" * 60)
    
    # Parse command line arguments
    base_url = "http://127.0.0.1:5001"
    generate_models = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--plan-only":
            generate_models = False
            print("📝 Running in plan-only mode (no Blender generation)")
        elif sys.argv[1] == "--help":
            print("Usage: python create_demo_scene.py [--plan-only] [--url=http://host:port]")
            print("\nOptions:")
            print("  --plan-only    Generate scene plans without executing Blender")
            print("  --url=URL      Custom server URL (default: http://127.0.0.1:5001)")
            return
        elif sys.argv[1].startswith("--url="):
            base_url = sys.argv[1].split("=", 1)[1]
    
    print(f"🌐 Using server: {base_url}")
    
    # Check server health
    health = check_server_health(base_url)
    if not health:
        print("\n❌ Cannot connect to server. Please ensure the Flask app is running.")
        print("   Run: python main.py")
        sys.exit(1)
    
    # Check required features
    if generate_models:
        if not health.get('blender_available'):
            print("\n⚠️  Blender not available. Switching to plan-only mode.")
            generate_models = False
        if not health.get('ai_available'):
            print("\n❌ AI integration not available. Cannot generate scenes.")
            print("   Please set ANTHROPIC_API_KEY environment variable.")
            sys.exit(1)
    
    # Test scene management API
    test_scene_management_api(base_url)
    
    # Create demo scenes
    print(f"\n🎨 Creating {len(DEMO_SCENES)} demo scenes...")
    successful_scenes = []
    
    for i, scene_config in enumerate(DEMO_SCENES):
        print(f"\n--- Demo Scene {i+1}/{len(DEMO_SCENES)} ---")
        result = create_demo_scene(scene_config, base_url, generate_models)
        
        if result:
            successful_scenes.append(result)
            # Add small delay between scenes to avoid overwhelming the server
            if i < len(DEMO_SCENES) - 1:
                print("⏳ Waiting 2 seconds before next scene...")
                time.sleep(2)
        else:
            print("❌ Skipping to next scene...")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Scene Creation Summary")
    print(f"✅ Successfully created: {len(successful_scenes)}/{len(DEMO_SCENES)} scenes")
    
    if successful_scenes:
        print("\n🎯 Generated Scenes:")
        for scene in successful_scenes:
            scene_id = scene.get('scene_id', 'unknown')
            scene_name = scene.get('scene_info', {}).get('scene_name', 'Unknown Scene')
            total_objects = scene.get('total_objects', 0)
            generated_objects = scene.get('generated_objects', 0)
            
            if generate_models:
                print(f"   - {scene_name} (ID: {scene_id}): {generated_objects}/{total_objects} objects generated")
                if scene.get('preview_url'):
                    print(f"     Preview: {base_url}{scene.get('preview_url')}")
            else:
                print(f"   - {scene_name} (ID: {scene_id}): {total_objects} objects planned")
        
        print(f"\n🌐 Open the web interface: {base_url}")
        print("   Navigate to the Scene Management section to view and interact with the generated scenes.")
    else:
        print("\n❌ No scenes were successfully created. Check the server logs for errors.")

if __name__ == "__main__":
    main()