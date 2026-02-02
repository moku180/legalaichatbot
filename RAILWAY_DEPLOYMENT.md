# Complete Railway Deployment Guide (2026)

**Legal AI Chatbot - Step-by-Step Deployment on Railway**

> [!IMPORTANT]
> This guide uses Railway's current UI (as of 2026) and assumes you've already pushed your optimized code to GitHub.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ GitHub account with your code pushed to `moku180/legalaichatbot`
- ✅ Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- ✅ Railway account (free tier available)

**Estimated Time**: 15-20 minutes  
**Cost**: Free tier ($5 credit/month) - sufficient for testing

---

## 🚀 Part 1: Initial Setup

### Step 1: Create Railway Account

1. **Go to Railway**
   - Visit [https://railway.app](https://railway.app)
   - Click **"Start a New Project"** or **"Login"**

2. **Sign Up with GitHub**
   - Click **"Login with GitHub"**
   - Authorize Railway to access your GitHub account
   - This connection allows Railway to deploy directly from your repositories

> [!NOTE]
> Railway requires GitHub authentication for code deployments. This enables automatic deployments when you push code changes.

---

### Step 2: Create New Project from GitHub

1. **Start New Project**
   - On the Railway dashboard, click **"New Project"**
   - You'll see several deployment options

2. **Deploy from GitHub Repo**
   - Click **"Deploy from GitHub repo"**
   - If this is your first time, Railway will ask for GitHub permissions
   - Click **"Configure GitHub App"** if needed

3. **Select Your Repository**
   - Search for or select **`moku180/legalaichatbot`**
   - Click on the repository to select it

4. **Initial Detection**
   - Railway will automatically detect:
     - ✅ Python project (from `nixpacks.toml` or `requirements.txt`)
     - ✅ Start command (from `Procfile` or `nixpacks.toml`)
   - Click **"Deploy Now"** or **"Add variables"** (we'll add variables next)

> [!TIP]
> Railway uses **Nixpacks** to automatically detect and configure your project. Your `nixpacks.toml` file tells Railway exactly how to build and run your app.

---

## 🗄️ Part 2: Add Database Services

### Step 3: Add PostgreSQL Database

1. **Add New Service**
   - In your project dashboard, click **"New"** (top right)
   - Select **"Database"**
   - Choose **"Add PostgreSQL"**

2. **Database Auto-Configuration**
   - Railway will:
     - ✅ Create a PostgreSQL instance
     - ✅ Generate connection credentials
     - ✅ Make them available as environment variables
   - Wait for the database to finish provisioning (~30 seconds)

3. **Note the Database Variables**
   - Click on the **PostgreSQL service** card
   - Go to **"Variables"** tab
   - You'll see variables like:
     - `DATABASE_URL` (this is the main one you'll use)
     - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

> [!IMPORTANT]
> Railway automatically injects `DATABASE_URL` into your application. You don't need to copy/paste it manually between services.

---

### Step 4: Add Redis (Optional but Recommended)

1. **Add Redis Service**
   - Click **"New"** → **"Database"** → **"Add Redis"**
   - Railway will provision a Redis instance

2. **Redis Variables**
   - Click on the **Redis service** card
   - Go to **"Variables"** tab
   - Note these variables:
     - `REDIS_URL` (main connection string)
     - `REDIS_HOST`, `REDIS_PORT`

> [!NOTE]
> Redis is used for rate limiting in your app. If you skip this, the app will still work (graceful degradation), but rate limiting will be disabled.

---

## ⚙️ Part 3: Configure Your Application

### Step 5: Configure Environment Variables

1. **Open Your Application Service**
   - Click on your **application service** card (the one with your GitHub repo name)
   - This is different from the database services

2. **Go to Variables Tab**
   - Click on the **"Variables"** tab in the service panel
   - You'll see a list of environment variables (may be empty initially)

3. **Add Required Variables**
   
   Click **"New Variable"** and add each of these:

   **Database Configuration** (Railway auto-references)
   ```
   Variable Name: DATABASE_URL
   Value: ${{Postgres.DATABASE_URL}}
   ```
   
   **Redis Configuration** (if you added Redis)
   ```
   Variable Name: REDIS_URL
   Value: ${{Redis.REDIS_URL}}
   ```
   
   **Security Settings**
   ```
   Variable Name: SECRET_KEY
   Value: [Generate a random 32+ character string]
   ```
   
   ```
   Variable Name: ALGORITHM
   Value: HS256
   ```
   
   **API Keys**
   ```
   Variable Name: GEMINI_API_KEY
   Value: [Your Google Gemini API key]
   ```
   
   **Application Settings**
   ```
   Variable Name: APP_NAME
   Value: Legal AI Chatbot
   ```
   
   ```
   Variable Name: ENVIRONMENT
   Value: production
   ```
   
   ```
   Variable Name: BACKEND_CORS_ORIGINS
   Value: ["*"]
   ```
   
   **Optional: Rate Limiting** (if using Redis)
   ```
   Variable Name: RATE_LIMIT_ENABLED
   Value: true
   ```
   
   ```
   Variable Name: RATE_LIMIT_PER_MINUTE
   Value: 60
   ```
   
   ```
   Variable Name: RATE_LIMIT_PER_HOUR
   Value: 1000
   ```

4. **Save Variables**
   - Railway auto-saves as you add each variable
   - No need to click a "Save" button

> [!TIP]
> **Generate a secure SECRET_KEY:**
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```
> Or use an online generator: https://randomkeygen.com/

> [!WARNING]
> **Never commit your `.env` file to Git!** Railway manages environment variables securely through their dashboard.

---

### Step 6: Configure Build Settings (Verify Auto-Detection)

1. **Open Settings Tab**
   - In your application service, click **"Settings"**
   - Scroll to the **"Build"** section

2. **Verify Build Configuration**
   
   Railway should auto-detect from your `nixpacks.toml`:
   
   - **Builder**: Nixpacks
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `/` (or empty)

3. **If Not Auto-Detected** (Manual Configuration)
   
   If Railway didn't detect your configuration:
   
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt
     ```
   
   - **Start Command**:
     ```bash
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   
   - **Watch Paths**: Leave default (or set to `backend/**`)

> [!NOTE]
> Railway automatically sets the `PORT` environment variable. Your app must listen on `$PORT`, which is handled by the start command above.

---

### Step 7: Configure Networking (Generate Public URL)

1. **Open Settings Tab**
   - Still in your application service, stay in **"Settings"**
   - Scroll to the **"Networking"** section

2. **Generate Domain**
   - Click **"Generate Domain"**
   - Railway will create a public URL like:
     - `https://your-app-name.up.railway.app`
   - This URL is immediately accessible

3. **Custom Domain (Optional)**
   - If you have a custom domain:
     - Click **"Custom Domain"**
     - Enter your domain (e.g., `api.yourdomain.com`)
     - Follow Railway's DNS configuration instructions

> [!TIP]
> The generated Railway domain is free and includes HTTPS automatically. No SSL certificate setup needed!

---

## 🚢 Part 4: Deploy Your Application

### Step 8: Trigger Deployment

1. **Automatic Deployment**
   - Railway automatically deploys when you:
     - ✅ First create the project
     - ✅ Change environment variables
     - ✅ Push code to GitHub
   
2. **Manual Deployment** (if needed)
   - Go to your application service
   - Click **"Deployments"** tab
   - Click **"Deploy"** button (top right)

3. **Monitor Build Progress**
   - Click on the latest deployment in the **"Deployments"** tab
   - You'll see real-time build logs:
     ```
     ===== Nixpacks Build =====
     → Detecting Python version...
     → Installing dependencies...
     → Build complete!
     ===== Deploy =====
     → Starting application...
     → Listening on port 8080
     ```

4. **Wait for Success**
   - Build time: ~3-5 minutes
   - Look for: **"Build successful"** and **"Deployment live"**
   - Status indicator will turn green

> [!WARNING]
> **If build fails:**
> - Check the build logs for errors
> - Common issues:
>   - Missing environment variables
>   - Incorrect build/start commands
>   - Dependency installation failures

---

### Step 9: Initialize Database Tables

After successful deployment, you need to create database tables.

**Option A: Using Railway's Terminal** (Recommended)

1. **Open Service Shell**
   - Click on your application service
   - Click the **"..."** menu (top right)
   - Select **"Shell"** or **"Terminal"**

2. **Run Database Initialization**
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
       print('✅ Database initialized!')
   
   asyncio.run(init())
   "
   ```

3. **Verify Success**
   - You should see: `✅ Database initialized!`

**Option B: Using API Endpoint** (If you have one)

If you created a database initialization endpoint:
```bash
curl -X POST https://your-app.up.railway.app/api/v1/init-db
```

> [!NOTE]
> Database tables are created based on your SQLAlchemy models. This only needs to be done once after initial deployment.

---

## ✅ Part 5: Verify Deployment

### Step 10: Test Your Application

1. **Health Check**
   - Open your Railway URL: `https://your-app.up.railway.app/health`
   - Expected response:
     ```json
     {
       "status": "healthy",
       "timestamp": "2026-02-02T12:00:00Z"
     }
     ```

2. **API Documentation**
   - Visit: `https://your-app.up.railway.app/docs`
   - You should see the FastAPI Swagger UI
   - Test endpoints directly from the browser

3. **Test Chat Endpoint**
   ```bash
   curl -X POST https://your-app.up.railway.app/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is contract law?",
       "session_id": "test-session"
     }'
   ```

4. **Check Logs**
   - In Railway dashboard, click your application service
   - Click **"Logs"** tab
   - Look for:
     - ✅ Application startup messages
     - ✅ Database connection success
     - ✅ No error messages

> [!TIP]
> Railway's logs are real-time. Keep this tab open while testing to see live request/response logs.

---

## 🔧 Part 6: Ongoing Management

### Monitoring and Logs

**View Real-Time Logs**
- Dashboard → Your Service → **"Logs"** tab
- Filter by:
  - Build logs
  - Deploy logs
  - Application logs

**Metrics**
- Dashboard → Your Service → **"Metrics"** tab
- View:
  - CPU usage
  - Memory usage
  - Network traffic
  - Request count

### Automatic Deployments

**Configure Auto-Deploy**
1. Settings → **"Service"** section
2. **"Auto-Deploy"** toggle (should be ON by default)
3. Choose branch: `main` (or your preferred branch)

**How it works:**
- Push code to GitHub → Railway detects changes → Automatic build & deploy
- Zero-downtime deployments
- Rollback available if needed

### Rollback to Previous Deployment

1. Go to **"Deployments"** tab
2. Find a previous successful deployment
3. Click **"..."** menu → **"Redeploy"**
4. Confirm rollback

### Environment Variable Updates

1. Go to **"Variables"** tab
2. Edit any variable
3. Railway automatically redeploys with new values

> [!WARNING]
> Changing environment variables triggers a new deployment. Your app will restart.

---

## 💰 Cost Management

### Free Tier Limits

Railway's free tier includes:
- **$5 credit per month**
- **500 hours of usage** (enough for 1 always-on service)
- **100 GB bandwidth**
- **1 GB storage per database**

### Monitor Usage

1. Dashboard → **"Usage"** (top right)
2. View current month's:
   - Credit used
   - Hours consumed
   - Estimated cost

### Optimize Costs

**Enable Auto-Sleep** (for development)
1. Settings → **"Service"** section
2. Enable **"Auto-Sleep"**
3. App sleeps after 15 minutes of inactivity
4. Wakes up on first request (~10 seconds)

**Set Usage Limits**
1. Settings → **"Usage Limits"**
2. Set maximum monthly spend
3. Railway will pause services if limit is reached

> [!TIP]
> For production, consider upgrading to the **Hobby plan** ($5/month) for better performance and no sleep mode.

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Build Fails with "Module not found"

**Problem**: Missing Python dependencies

**Solution**:
- Check `backend/requirements.txt` is complete
- Verify build command: `pip install -r backend/requirements.txt`
- Check build logs for specific missing package

#### 2. Application Crashes on Startup

**Problem**: Missing environment variables or database connection

**Solution**:
- Verify all required environment variables are set
- Check `DATABASE_URL` is correctly referenced: `${{Postgres.DATABASE_URL}}`
- Review application logs for specific error

#### 3. "Port Already in Use" Error

**Problem**: App not listening on Railway's `$PORT`

**Solution**:
- Verify start command uses `$PORT`: `--port $PORT`
- Don't hardcode port 8000 in production

#### 4. Database Connection Timeout

**Problem**: Database not accessible or wrong credentials

**Solution**:
- Verify PostgreSQL service is running (green status)
- Check `DATABASE_URL` variable is set correctly
- Ensure database is in same Railway project

#### 5. CORS Errors from Frontend

**Problem**: Frontend can't access backend API

**Solution**:
- Update `BACKEND_CORS_ORIGINS` variable:
  ```
  ["https://your-frontend.vercel.app", "http://localhost:3000"]
  ```
- Restart deployment after changing

#### 6. 502 Bad Gateway

**Problem**: Application not responding

**Solution**:
- Check application logs for crash/error
- Verify app is listening on `0.0.0.0:$PORT`
- Check health endpoint: `/health`

### Getting Help

**Railway Community**
- Discord: [https://discord.gg/railway](https://discord.gg/railway)
- Documentation: [https://docs.railway.app](https://docs.railway.app)
- Status Page: [https://status.railway.app](https://status.railway.app)

**Check Logs First**
- 90% of issues are visible in logs
- Look for stack traces and error messages
- Check both build logs and application logs

---

## 📚 Next Steps

### 1. Deploy Frontend (Optional)

If you have a React frontend:
- Deploy to **Vercel** or **Netlify** (recommended for frontend)
- Update `BACKEND_CORS_ORIGINS` with frontend URL
- Set frontend's `VITE_API_URL` to Railway backend URL

### 2. Set Up Custom Domain

1. Purchase domain (Namecheap, Google Domains, etc.)
2. In Railway: Settings → Networking → Custom Domain
3. Add DNS records as instructed by Railway
4. Wait for DNS propagation (~24 hours)

### 3. Enable Monitoring

Consider adding:
- **Sentry** for error tracking
- **LogRocket** for session replay
- **Datadog** for APM (Application Performance Monitoring)

### 4. Set Up CI/CD

Railway already provides automatic deployments from GitHub. For advanced workflows:
- Add GitHub Actions for testing before deploy
- Set up staging environment (separate Railway project)
- Configure deployment notifications (Slack, Discord)

### 5. Database Backups

**Automatic Backups** (Paid plans)
- Railway Pro plan includes automatic daily backups
- Retention: 7 days

**Manual Backups** (Free tier)
```bash
# Connect to Railway PostgreSQL
railway run pg_dump $DATABASE_URL > backup.sql

# Restore from backup
railway run psql $DATABASE_URL < backup.sql
```

---

## 📊 Deployment Checklist

Use this checklist to ensure everything is configured correctly:

- [ ] Railway account created and GitHub connected
- [ ] Project created from `moku180/legalaichatbot` repository
- [ ] PostgreSQL database added and provisioned
- [ ] Redis database added (optional)
- [ ] All environment variables configured:
  - [ ] `DATABASE_URL`
  - [ ] `REDIS_URL` (if using Redis)
  - [ ] `SECRET_KEY`
  - [ ] `GEMINI_API_KEY`
  - [ ] `BACKEND_CORS_ORIGINS`
  - [ ] `ENVIRONMENT=production`
- [ ] Build settings verified (Nixpacks auto-detection)
- [ ] Public domain generated
- [ ] Application deployed successfully (green status)
- [ ] Database tables initialized
- [ ] Health check endpoint responding: `/health`
- [ ] API documentation accessible: `/docs`
- [ ] Test API endpoints working
- [ ] Logs showing no errors
- [ ] Auto-deploy enabled for `main` branch

---

## 🎉 Success!

Your Legal AI Chatbot is now live on Railway!

**Your Application URLs:**
- **API**: `https://your-app.up.railway.app`
- **Health Check**: `https://your-app.up.railway.app/health`
- **API Docs**: `https://your-app.up.railway.app/docs`

**Estimated Deployment Size**: ~492 MB (12% of Railway's 4GB limit)

**What's Working:**
✅ FastAPI backend with Gemini AI integration  
✅ Document processing (PDF, DOCX)  
✅ Vector search with FAISS  
✅ User authentication  
✅ PostgreSQL database  
✅ Redis caching (if configured)  
✅ Automatic HTTPS  
✅ Auto-deployments from GitHub

---

## 📞 Support

If you encounter any issues:

1. **Check this guide** - Most common issues are covered
2. **Review Railway logs** - Errors are usually logged
3. **Railway Discord** - Active community support
4. **Railway Docs** - Comprehensive documentation

**Happy Deploying! 🚀**
