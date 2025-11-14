"""
Vercel serverless function for FastAPI app
Uses Mangum adapter to convert ASGI to AWS Lambda/API Gateway format
"""
import sys
import os
import traceback

# Print debug info to stderr (visible in Vercel logs)
print("=" * 50, file=sys.stderr)
print("Starting Vercel function initialization", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {os.getcwd()}", file=sys.stderr)
print(f"Python path: {sys.path}", file=sys.stderr)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Parent directory: {parent_dir}", file=sys.stderr)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    print(f"Added {parent_dir} to sys.path", file=sys.stderr)

# Import the app with better error handling
print("Attempting to import dependencies...", file=sys.stderr)
try:
    # Try importing dependencies first
    print("Importing mangum...", file=sys.stderr)
    try:
        from mangum import Mangum
        print("✓ Mangum imported successfully", file=sys.stderr)
    except ImportError as e:
        print(f"✗ Mangum import error: {e}", file=sys.stderr)
        print(f"Full error: {traceback.format_exc()}", file=sys.stderr)
        raise
    
    print("Importing app...", file=sys.stderr)
    try:
        from app import app
        print("✓ App imported successfully", file=sys.stderr)
    except Exception as e:
        print(f"✗ App import error: {e}", file=sys.stderr)
        print(f"Full traceback:\n{traceback.format_exc()}", file=sys.stderr)
        raise
    
    print("Creating Mangum handler...", file=sys.stderr)
    # Create Mangum adapter for AWS Lambda/API Gateway (Vercel uses this format)
    handler = Mangum(app, lifespan="off")
    print("=" * 50, file=sys.stderr)
    print("✓ Handler initialized successfully!", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
except Exception as e:
    # Better error handling for debugging
    error_msg = f"Error initializing app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Initialization failed", "details": "{str(e)}"}}'
        }
