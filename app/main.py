"""
AI Data Insight Engine - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

from app.config import settings
from app.database import init_db
from app.auth.routes import router as auth_router
from app.api.upload import router as upload_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="AI Data Insight Engine API",
    description="Transform raw business data into actionable insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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