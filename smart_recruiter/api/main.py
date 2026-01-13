"""
FastAPI Application
===================

Main entry point for the Smart Recruiter API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from ..config import get_settings
from ..database import init_db
from .routes import jobs, candidates, apply, screening

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting Smart Recruiter API...")

    # Create data directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.resume_dir, exist_ok=True)
    os.makedirs("./data", exist_ok=True)

    # Initialize database
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down Smart Recruiter API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Multi-Agent Recruitment System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(apply.router, prefix="/api/apply", tags=["Application"])
app.include_router(screening.router, prefix="/api/screening", tags=["Screening"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
