"""
Main FastAPI application entry point.
This is the core of the AI Learning Platform backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.config import settings


# Create uploads directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Runs on startup and shutdown.
    """
    # Startup
    print("\n" + "="*70)
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print("="*70)
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"🗄️  Database: {settings.mongodb_db_name}")
    print(f"\n🤖 AI Configuration:")
    print(f"   Provider: {settings.default_ai_provider}")
    print(f"   Chapter Gen: {settings.model_chapter_generation}")
    print(f"   Question Gen: {settings.model_question_generation}")
    print(f"   Answer Check: {settings.model_answer_checking}")
    print("="*70 + "\n")
    
    # Here we'll add database connection later
    
    yield
    
    # Shutdown
    print(f"👋 Shutting down {settings.app_name}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered learning platform with adaptive mentoring",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


# Import routers
from app.routers import courses

# Include routers
app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )