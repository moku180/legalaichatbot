# Railway Deployment Guide - MUCH EASIER!

Railway is significantly easier than Render for this project because it automatically detects Python versions and handles dependencies better.

## Step 1: Sign Up for Railway
1. Go to https://railway.app
2. Sign up with GitHub (it will connect to your repository automatically)

## Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `moku180/legalaichatbot`
4. Railway will auto-detect it's a Python project

## Step 3: Add PostgreSQL Database
1. In your project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will create and connect it automatically
4. Copy the `DATABASE_URL` from the database service

## Step 4: Add Redis
1. Click "New" → "Database" → "Redis"
2. Railway will create and connect it automatically
3. Copy the Redis connection details

## Step 5: Configure Backend Service
1. Click on your backend service
2. Go to "Settings" → "Environment Variables"
3. Add these variables:

```env
# Database (Railway provides this automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway provides this automatically)  
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}

# Security
SECRET_KEY=your-secret-key-here-32-chars
ALGORITHM=HS256

# API
GEMINI_API_KEY=AIzaSyALOoINe1zu7wk9kaLHsL7IO-LK3V31Ts4

# CORS (update after frontend deployment)
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]

# App
APP_NAME=Legal AI SaaS
APP_VERSION=1.0.0
ENVIRONMENT=production
```

## Step 6: Configure Build Settings
1. Go to "Settings" → "Build"
2. **Root Directory**: Leave empty (or set to `/`)
3. **Build Command**: `cd backend && pip install -r requirements.txt`
4. **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Python Version**: Railway auto-detects from runtime.txt

## Step 7: Deploy
1. Click "Deploy"
2. Railway will build and deploy automatically
3. You'll get a URL like: `https://your-app.up.railway.app`

## Step 8: Initialize Database
1. Go to your backend service
2. Click "Shell" or "Terminal"
3. Run:
```bash
cd backend
python -c "
import asyncio
from app.db.base import engine, Base
from app.models.user import User
from app.models.organization import Organization
from app.models.document import Document
from app.models.query_history import QueryHistory

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Database initialized!')

asyncio.run(init())
"
```

## Why Railway is Better:
- ✅ Auto-detects Python version from runtime.txt
- ✅ Better handling of binary wheels
- ✅ Integrated database and Redis
- ✅ Simpler configuration
- ✅ Better error messages
- ✅ Free tier: $5 credit/month (enough for testing)

## Cost:
- Free $5 credit/month
- After that: ~$5-10/month for small apps

## Total Time: ~15 minutes vs 2+ hours on Render!
