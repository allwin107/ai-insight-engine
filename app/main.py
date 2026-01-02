"""
AI Data Insight Engine - Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import time

from app.config import settings
from app.database import init_db
from app.auth.routes import router as auth_router
from app.api.upload import router as upload_router
from app.utils.logging import logger

# Initialize database
init_db()
logger.info("database_initialized")

# Create FastAPI app
app = FastAPI(
    title="AI Data Insight Engine API",
    description="Transform raw business data into actionable insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=f"{process_time:.3f}s"
    )
    
    return response

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(upload_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "AI Data Insight Engine API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT,
            "checks": {
                "api": "ok",
                "database": "ok",  # TODO: Add actual database check
            }
        }
    )

# API v1 router placeholder
@app.get("/api/v1")
async def api_v1_root():
    """API v1 information"""
    return {
        "version": "1.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "upload": "/api/v1/upload",
            "jobs": "/api/v1/jobs",
            "export": "/api/v1/export"
        }
    }

# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )