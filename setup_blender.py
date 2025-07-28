#!/usr/bin/env python3
"""
Setup script to help configure Blender path for the application.
"""

import os
import subprocess
import platform
from pathlib import Path

def find_blender():
    """Try to find Blender installation."""
    print("🔍 Searching for Blender installation...")
    
    # Common Blender locations
    common_paths = []
    
    system = platform.system()
    if system == "Darwin":  # macOS
        common_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/Applications/Blender.app/Contents/MacOS/blender",
            str(Path.home() / "Applications/Blender.app/Contents/MacOS/Blender"),
            "/usr/local/bin/blender",
            "/opt/homebrew/bin/blender",
        ]
    elif system == "Windows":
        common_paths = [
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender\blender.exe",
        ]
    else:  # Linux
        common_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/snap/bin/blender",
            str(Path.home() / "blender/blender"),
        ]
    
    # Check common paths
    for path in common_paths:
        if Path(path).exists():
            print(f"✅ Found Blender at: {path}")
            return path
    
    # Try to find using 'which' or 'where'
    try:
        cmd = "where" if system == "Windows" else "which"
        result = subprocess.run([cmd, "blender"], capture_output=True, text=True)
        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"✅ Found Blender in PATH: {path}")
            return path
    except:
        pass
    
    return None

def test_blender(blender_path):
    """Test if Blender executable works."""
    print(f"\n🧪 Testing Blender at: {blender_path}")
    try:
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Blender is working correctly!")
            print(f"   Version info: {result.stdout.splitlines()[0]}")
            return True
    except Exception as e:
        print(f"❌ Failed to run Blender: {e}")
    return False

def create_env_file(blender_path):
    """Create or update .env file with Blender path."""
    env_file = Path(".env")
    
    # Read existing content
    existing_content = ""
    if env_file.exists():
        existing_content = env_file.read_text()
    
    # Update or add BLENDER_EXECUTABLE_PATH
    lines = existing_content.splitlines()
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("BLENDER_EXECUTABLE_PATH="):
            lines[i] = f'BLENDER_EXECUTABLE_PATH="{blender_path}"'
            updated = True
            break
    
    if not updated:
        lines.append(f'BLENDER_EXECUTABLE_PATH="{blender_path}"')
    
    # Write back
    env_file.write_text("\n".join(lines) + "\n")
    print(f"\n✅ Created/updated .env file with Blender path")

def main():
    print("🚀 Blender Setup Assistant")
    print("=" * 50)
    
    # Try to find Blender automatically
    blender_path = find_blender()
    
    if not blender_path:
        print("\n❌ Could not find Blender automatically.")
        print("\n📋 Please install Blender from: https://www.blender.org/download/")
        print("\nOr enter the path to your Blender executable:")
        
        while True:
            user_path = input("> ").strip()
            if not user_path:
                print("❌ No path entered. Exiting.")
                return 1
            
            if Path(user_path).exists():
                blender_path = user_path
                break
            else:
                print(f"❌ Path not found: {user_path}")
                print("Please enter a valid path or press Enter to exit:")
    
    # Test the Blender installation
    if test_blender(blender_path):
        # Ask if user wants to save configuration
        print("\n💾 Would you like to save this configuration? (y/n)")
        response = input("> ").strip().lower()
        
        if response == 'y':
            create_env_file(blender_path)
            print("\n✅ Setup complete! You can now run the application:")
            print("   python start_server.py")
        else:
            print("\n⚠️  Configuration not saved. You'll need to set:")
            print(f'   export BLENDER_EXECUTABLE_PATH="{blender_path}"')
            print("   Before running the application.")
    else:
        print("\n❌ Blender test failed. Please check your installation.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())