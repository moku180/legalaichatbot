"""Rate limiting middleware using Redis"""
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from app.core.config import settings


class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def init(self):
        """Initialize Redis connection"""
        redis_url = settings.REDIS_CONNECTION_URL
        if not redis_url:
            # Redis not configured, rate limiting will be disabled
            self.redis = None
            return
            
        try:
            self.redis = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            # If Redis connection fails, disable rate limiting gracefully
            print(f"Warning: Redis connection failed: {e}. Rate limiting disabled.")
            self.redis = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def is_rate_limited(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> bool:
        """Check if rate limit is exceeded"""
        if not self.redis or not settings.RATE_LIMIT_ENABLED:
            return False
        
        current_time = int(time.time())
        window_key = f"rate_limit:{key}:{current_time // window_seconds}"
        
        try:
            # Increment counter
            count = await self.redis.incr(window_key)
            
            # Set expiry on first increment
            if count == 1:
                await self.redis.expire(window_key, window_seconds)
            
            return count > limit
        except Exception:
            # If Redis fails, allow the request
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Get user/org from request state (set by tenant isolation middleware)
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "organization_id", None)
        
        if user_id and org_id:
            # Check per-minute rate limit
            user_key = f"user:{user_id}"
            if await rate_limiter.is_rate_limited(
                user_key,
                settings.RATE_LIMIT_PER_MINUTE,
                60
            ):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Check per-hour rate limit
            if await rate_limiter.is_rate_limited(
                user_key,
                settings.RATE_LIMIT_PER_HOUR,
                3600
            ):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Hourly rate limit exceeded. Please try again later."
                )
        
        response = await call_next(request)
        return response
