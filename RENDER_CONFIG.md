# Render.com Deployment Configuration

## Important: Update these settings in your Render dashboard

### Build Settings
- **Build Command**: `./build.sh`
- **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Python Version**: Will be read from runtime.txt (Python 3.11.9)

### Environment Variables (Add these in Render dashboard)

```env
# Database (Use Render PostgreSQL internal URL)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
POSTGRES_USER=legalai
POSTGRES_PASSWORD=<your-password>
POSTGRES_HOST=<your-render-postgres-host>
POSTGRES_PORT=5432
POSTGRES_DB=legalai_db

# Redis (Use Render Redis internal URL)
REDIS_HOST=<your-render-redis-host>
REDIS_PORT=6379

# Security
SECRET_KEY=<generate-random-32-char-string>
ALGORITHM=HS256

# API Keys
GEMINI_API_KEY=AIzaSyALOoINe1zu7wk9kaLHsL7IO-LK3V31Ts4

# CORS (Update with your Vercel frontend URL)
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]

# App
APP_NAME=Legal AI SaaS
APP_VERSION=1.0.0
ENVIRONMENT=production
```

### After Deployment
1. Go to Render Shell
2. Run: `cd backend && python -c "import asyncio; from app.db.base import engine, Base; from app.models.user import User; from app.models.organization import Organization; from app.models.document import Document; from app.models.query_history import QueryHistory; asyncio.run((lambda: engine.begin()).__self__.run_sync(Base.metadata.create_all))"`

Or create a simpler init script.
