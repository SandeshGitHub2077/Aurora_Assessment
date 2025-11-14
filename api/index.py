"""
Vercel serverless function for FastAPI app
Uses Mangum adapter to convert ASGI to AWS Lambda/API Gateway format
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the app
from app import app
from mangum import Mangum

# Create Mangum adapter for AWS Lambda/API Gateway (Vercel uses this format)
handler = Mangum(app, lifespan="off")

# Export handler for Vercel
__all__ = ['handler']
