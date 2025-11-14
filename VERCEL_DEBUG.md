# How to Debug Vercel Deployment

## Accessing Detailed Logs

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Select your project**: `Aurora_Assessment`
3. **Click on the latest deployment** (the one that failed)
4. **Go to "Functions" tab** (top menu)
5. **Click on the function** (`api/index.py` or similar)
6. **Scroll down to see the logs** - you should see:
   - Build logs
   - Runtime logs
   - Error messages with full tracebacks

## What to Look For

The logs should show:
- Import errors (e.g., "No module named 'mangum'")
- Syntax errors in app.py
- Missing dependencies
- Environment variable issues

## Alternative: Check Build Logs

1. In the deployment page, click **"Build Logs"** tab
2. Look for Python installation and dependency installation errors
3. Check if all packages from `requirements.txt` installed successfully

## If Logs Are Empty

The error might be happening at import time. Check:
- The "Runtime Logs" section
- The "Function Logs" section
- Try accessing a specific endpoint to trigger the function

## Quick Test

Try accessing these URLs to trigger the function:
- https://aurora-assessment.vercel.app/health
- https://aurora-assessment.vercel.app/
- https://aurora-assessment.vercel.app/ask

This will generate runtime logs you can see in the Functions tab.

