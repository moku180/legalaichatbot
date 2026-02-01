# Legal AI Chatbot - Deployment Guide

## Quick Deployment Options

### Option 1: Vercel (Frontend) + Render (Backend) - Recommended for Beginners
**Cost**: Free tier available  
**Time**: ~30 minutes  
**Difficulty**: Easy

### Option 2: Railway (Full Stack)
**Cost**: $5/month (includes database)  
**Time**: ~20 minutes  
**Difficulty**: Very Easy

### Option 3: AWS (Production Grade)
**Cost**: ~$50-100/month  
**Time**: ~2 hours  
**Difficulty**: Advanced

---

## Option 1: Vercel + Render (Recommended)

### Step 1: Prepare Your Code

1. **Create a GitHub repository** (if not already done):
```bash
cd c:\Users\moksh\OneDrive\Desktop\legalchatbot
git init
git add .
git commit -m "Initial commit - Legal AI Chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/legalchatbot.git
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `legalai-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**:
```env
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_host
POSTGRES_PORT=5432
POSTGRES_DB=legalai_db
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

REDIS_HOST=your_redis_host
REDIS_PORT=6379

SECRET_KEY=<generate-random-32-char-string>
GEMINI_API_KEY=AIzaSyALOoINe1zu7wk9kaLHsL7IO-LK3V31Ts4

BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]

APP_NAME=Legal AI SaaS
APP_VERSION=1.0.0
ENVIRONMENT=production
```

6. Click "Create Web Service"
7. Wait for deployment (~5 minutes)
8. Note your backend URL: `https://legalai-backend.onrender.com`

### Step 3: Set Up Database on Render

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `legalai-db`
   - **Database**: `legalai_db`
   - **User**: `legalai`
   - **Region**: Same as backend
3. Click "Create Database"
4. Copy the **Internal Database URL**
5. Update backend environment variable `DATABASE_URL` with this URL

### Step 4: Set Up Redis on Render

1. Click "New +" → "Redis"
2. Configure:
   - **Name**: `legalai-redis`
   - **Region**: Same as backend
3. Click "Create Redis"
4. Copy the **Internal Redis URL**
5. Update backend environment variables:
   - `REDIS_HOST`: (from Redis URL)
   - `REDIS_PORT`: 6379

### Step 5: Initialize Database

1. In Render dashboard, go to your backend service
2. Click "Shell" tab
3. Run:
```bash
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

### Step 6: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. **Add Environment Variable**:
```env
VITE_API_URL=https://legalai-backend.onrender.com
```

6. Click "Deploy"
7. Wait for deployment (~3 minutes)
8. Your app is live at: `https://your-app.vercel.app`

### Step 7: Update CORS

1. Go back to Render backend settings
2. Update `BACKEND_CORS_ORIGINS` environment variable:
```env
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]
```
3. Redeploy backend

### Step 8: Test Your Deployment

1. Visit `https://your-app.vercel.app`
2. Register a new account
3. Login
4. Ask a legal question
5. Upload a document
6. Verify everything works

---

## Option 2: Railway (Easiest - All-in-One)

### Step 1: Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your repository

### Step 2: Add Services

Railway will auto-detect your services. Add:
- PostgreSQL database
- Redis
- Backend (Python)
- Frontend (Node.js)

### Step 3: Configure Environment Variables

**Backend**:
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
SECRET_KEY=<generate-random-string>
GEMINI_API_KEY=AIzaSyALOoINe1zu7wk9kaLHsL7IO-LK3V31Ts4
BACKEND_CORS_ORIGINS=["${{Frontend.RAILWAY_STATIC_URL}}"]
```

**Frontend**:
```env
VITE_API_URL=${{Backend.RAILWAY_STATIC_URL}}
```

### Step 4: Deploy

Railway will automatically deploy all services. Your app will be live in ~10 minutes!

---

## Option 3: AWS (Production Grade)

### Services Needed:
- **EC2**: Backend server
- **RDS**: PostgreSQL database
- **ElastiCache**: Redis
- **S3**: Document storage
- **CloudFront**: CDN for frontend
- **Route 53**: Domain management

### Estimated Monthly Cost:
- EC2 t3.small: $15
- RDS db.t3.micro: $15
- ElastiCache t3.micro: $12
- S3: $5
- CloudFront: $5
- **Total**: ~$52/month

### Deployment Steps:

1. **Set up RDS PostgreSQL**
2. **Set up ElastiCache Redis**
3. **Deploy backend to EC2**
4. **Build and upload frontend to S3**
5. **Configure CloudFront**
6. **Set up Route 53 for custom domain**

*(Detailed AWS guide available upon request)*

---

## Post-Deployment Checklist

- [ ] Backend health check: `https://your-backend.com/health`
- [ ] API docs accessible: `https://your-backend.com/docs`
- [ ] Frontend loads correctly
- [ ] Registration works
- [ ] Login works
- [ ] Chat functionality works
- [ ] Document upload works
- [ ] SSL/HTTPS enabled
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up (optional)

---

## Environment Variables Reference

### Required Backend Variables:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
POSTGRES_USER=legalai
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=<db-host>
POSTGRES_PORT=5432
POSTGRES_DB=legalai_db

# Redis
REDIS_HOST=<redis-host>
REDIS_PORT=6379
REDIS_PASSWORD=<if-required>

# Security
SECRET_KEY=<32-char-random-string>
ALGORITHM=HS256

# API Keys
GEMINI_API_KEY=<your-gemini-key>

# CORS
BACKEND_CORS_ORIGINS=["https://your-frontend.com"]

# App
APP_NAME=Legal AI SaaS
APP_VERSION=1.0.0
ENVIRONMENT=production
```

### Required Frontend Variables:
```env
VITE_API_URL=https://your-backend.com
```

---

## Troubleshooting

### Backend won't start
- Check database connection
- Verify all environment variables are set
- Check logs for errors

### Frontend can't connect to backend
- Verify CORS settings
- Check API URL in frontend env
- Ensure backend is running

### Database errors
- Run database initialization script
- Check database credentials
- Verify database is accessible

### Document upload fails
- Check file size limits
- Verify storage configuration
- Check file permissions

---

## Support

For deployment help:
1. Check platform documentation (Render, Vercel, Railway)
2. Review error logs
3. Verify environment variables
4. Test locally first

**Your application is ready for deployment! Choose your preferred platform and follow the guide above.**
