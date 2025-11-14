# Quick Deployment Guide

## 🚀 Fastest Option: Railway (5 minutes)

### Steps:

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** (use GitHub for easy connection)
3. **New Project** → **Deploy from GitHub repo**
4. **Select your repo**: `SandeshGitHub2077/Aurora_Assessment`
5. **Add Environment Variable**:
   - Variable: `HF_API_KEY`
   - Value: `your_huggingface_token_here` (get from https://huggingface.co/settings/tokens)
6. **Deploy** - Railway auto-detects Dockerfile and deploys
7. **Get your public URL** from Railway dashboard

**Done!** Your API will be live at: `https://your-app-name.up.railway.app`

---

## Alternative: Render (Also Easy)

1. **Go to Render**: https://render.com
2. **New** → **Web Service**
3. **Connect GitHub** → Select your repo
4. **Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Environment Variable: `HF_API_KEY=your_huggingface_token_here`
5. **Deploy**

**Your API will be at**: `https://your-app-name.onrender.com`

---

## Test Your Deployment

Once deployed, test with:

```bash
# Health check
curl https://your-app-url.com/health

# Ask a question
curl -X POST https://your-app-url.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'
```

---

## Which Platform?

- **Railway**: Easiest, auto-detects everything, free tier
- **Render**: Also easy, free tier, slightly slower cold starts
- **Heroku**: Well-known but requires credit card for free tier
- **Fly.io**: Fast global deployment

**Recommendation**: Start with **Railway** - it's the fastest to deploy!

