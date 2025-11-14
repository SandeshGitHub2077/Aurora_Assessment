"""
Vercel serverless function for FastAPI app
Uses Mangum adapter to convert ASGI to AWS Lambda/API Gateway format
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the app
try:
    from app import app
    from mangum import Mangum
    
    # Create Mangum adapter for AWS Lambda/API Gateway (Vercel uses this format)
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # Fallback error handler
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': f'Error initializing app: {str(e)}'
        }
