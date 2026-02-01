"""Tenant isolation middleware for multi-tenancy"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_token


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and inject tenant context from JWT"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip tenant isolation for public endpoints
        public_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                # Inject organization_id into request state
                request.state.organization_id = payload.get("organization_id")
                request.state.user_id = payload.get("sub")
            except Exception:
                # Token validation will be handled by dependencies
                pass
        
        response = await call_next(request)
        return response
