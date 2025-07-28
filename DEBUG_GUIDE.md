# Debug Guide - Blender AI Modeling Web Interface

This guide helps troubleshoot the "Generate" button issue and other JavaScript errors.

## Quick Diagnosis Steps

### Step 1: Check if Flask Server is Running

```bash
# From project root directory
cd /Users/cjunker/Documents/python-blender-ai-modeling

# Start the Flask server
python src/web/app.py
```

**Expected output:**
```
INFO:src.web.app:Flask application created successfully
* Running on http://127.0.0.1:5000
```

### Step 2: Test Server Health

Open a new terminal and test the API:

```bash
# Test health endpoint
curl http://127.0.0.1:5000/api/health

# Expected response:
{
  "status": "healthy",
  "version": "0.1.0",
  "blender_path": "blender",
  "blender_available": true,
  "export_available": true,
  "blender_timeout": 30
}
```

### Step 3: Check Browser Console

1. Open the web interface: http://127.0.0.1:5000
2. Open browser developer tools (F12)
3. Go to Console tab
4. Look for errors when clicking "Generate"

**Common error patterns:**
- `TypeError: Cannot read property 'post' of undefined` → JavaScript loading issue
- `Network error: Unable to connect to server` → Flask server not running
- `404 Not Found` → API endpoint issue
- `500 Internal Server Error` → Server-side error

## Detailed Troubleshooting

### Issue 1: JavaScript Loading Problems

**Symptoms:** Console shows `BlenderAI is not defined` or similar

**Solution:**
1. Check that all JavaScript files are loading:
   - `src/web/static/js/utils.js`
   - `src/web/static/js/notifications.js`
   - `src/web/static/js/model-form.js`

**Test using debug page:**
```bash
# Open debug.html in browser
open debug.html
# Or serve it locally
python -m http.server 8000
# Then visit: http://localhost:8000/debug.html
```

### Issue 2: Flask Server Connection Problems

**Symptoms:** "Network error: Unable to connect to server" in console

**Solutions:**
1. **Check if server is running:**
   ```bash
   # Start server if not running
   python src/web/app.py
   ```

2. **Check for port conflicts:**
   ```bash
   # Check if port 5000 is in use
   lsof -i :5000
   
   # Use different port if needed
   PORT=5001 python src/web/app.py
   ```

3. **Check firewall/network:**
   ```bash
   # Test local connectivity
   curl http://127.0.0.1:5000/api/health
   ```

### Issue 3: Blender Integration Errors

**Symptoms:** Server responds but generation fails

**Check Blender installation:**
```bash
# Verify Blender is accessible
blender --version

# If not found, install or set path
export BLENDER_EXECUTABLE_PATH=/path/to/blender
```

**Test Blender integration directly:**
```bash
# Run a simple test
python -c "
from src.blender_integration.executor import BlenderExecutor
executor = BlenderExecutor()
result = executor.execute_script('import bpy; print(\"Blender working\")')
print(f'Success: {result.success}')
print(f'Output: {result.stdout}')
"
```

### Issue 4: API Response Format Problems

**Symptoms:** Strange formatted error blocks in UI

**Debug API responses:**
1. Check browser Network tab in developer tools
2. Look for failed requests to `/api/generate`
3. Check response format and status codes

**Test API manually:**
```bash
# Test generate endpoint
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "object_type": "cube",
    "size": 2.0,
    "pos_x": 1.0
  }'
```

## Common Solutions

### Fix 1: Restart Everything
```bash
# Kill any existing processes
pkill -f "python.*app.py"

# Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)

# Restart Flask server
python src/web/app.py
```

### Fix 2: Check File Permissions
```bash
# Ensure JavaScript files are readable
chmod 644 src/web/static/js/*.js

# Ensure Flask app has write permissions for exports
mkdir -p exports
chmod 755 exports
```

### Fix 3: Verify Dependencies
```bash
# Check if all required modules are installed
python -c "
try:
    from flask import Flask
    from pathlib import Path
    import subprocess
    print('✅ All basic dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
"
```

## Debug Mode Activation

To get more detailed error information:

1. **Enable Flask debug mode:**
   ```bash
   FLASK_DEBUG=True python src/web/app.py
   ```

2. **Enable JavaScript debug logging:**
   - Open browser console
   - All API requests/responses will be logged
   - Error details will be more verbose

3. **Check Flask logs:**
   - All server errors are logged to console
   - Look for stack traces and error details

## Testing the Fixed Version

After applying fixes, test in this order:

1. **Server health:** `curl http://127.0.0.1:5000/api/health`
2. **JavaScript loading:** Check console for no errors on page load
3. **Form validation:** Try submitting with invalid data
4. **Model generation:** Click "Generate" with valid cube parameters
5. **Export functionality:** Try exporting after successful generation

## Getting Help

If issues persist, provide this debug information:

1. **Browser console output** (copy/paste all errors)
2. **Flask server console output** (any error messages)
3. **Operating system and Python version**
4. **Blender version and installation path**
5. **Network/curl test results for API endpoints**

## Quick Test Commands

Run these to verify everything is working:

```bash
# 1. Test server startup
python src/web/app.py &
sleep 2

# 2. Test health endpoint
curl -s http://127.0.0.1:5000/api/health | jq .

# 3. Test generate endpoint
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"object_type": "cube", "size": 2.0, "pos_x": 1.0}' | jq .

# 4. Test JavaScript files load correctly
curl -s http://127.0.0.1:5000/static/js/utils.js | head -n 5

# 5. Stop server
pkill -f "python.*app.py"
```

All commands should succeed without errors for the application to work properly.