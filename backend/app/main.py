"""FastAPI main application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import init_db, close_db
from app.middleware.tenant_isolation import TenantIsolationMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware, rate_limiter
from app.api import auth, documents, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    import logging
    
    # Configure logging to stdout for Railway
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting up Legal AI Backend...")
    
    # Startup
    await init_db()
    await rate_limiter.init()
    yield
    # Shutdown
    await close_db()
    await rate_limiter.close()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Legal Chatbot",
    lifespan=lifespan
)

# CORS middleware
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https://legalaichatbot.*\.vercel\.app",  # Allow all Vercel preview URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(TenantIsolationMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal AI SaaS API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
