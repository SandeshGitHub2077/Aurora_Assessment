# Vercel Deployment Guide

## Setup for Vercel

Vercel uses serverless functions, so we need to adapt FastAPI for Vercel's architecture.

## Steps to Deploy:

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Link your project**:
   ```bash
   vercel link
   ```

4. **Set Environment Variable** (if not already set):
   ```bash
   vercel env add HF_API_KEY
   # Enter your HuggingFace API key when prompted
   ```

5. **Deploy**:
   ```bash
   vercel --prod
   ```

## Or Deploy via GitHub:

1. **Go to Vercel Dashboard**: https://vercel.com
2. **Import Project** → Connect GitHub → Select `Aurora_Assessment`
3. **Configure**:
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
4. **Environment Variables**:
   - Add `HF_API_KEY` = (your HuggingFace API key - you've already set this)
5. **Deploy**

## Important Notes:

- Vercel uses serverless functions, so each request may have a cold start
- The `api/index.py` file wraps FastAPI for Vercel's serverless architecture
- Make sure `vercel.json` is in the root directory
- Environment variables must be set in Vercel dashboard

## Troubleshooting:

If you get errors:
1. Check Vercel logs in the dashboard
2. Ensure `HF_API_KEY` environment variable is set
3. Verify `api/index.py` exists and imports correctly
4. Check that all dependencies are in `requirements.txt`

