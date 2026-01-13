#!/usr/bin/env python3
"""
Run Smart Recruiter API Server
==============================

Usage:
    python run.py

Or with uvicorn directly:
    uvicorn smart_recruiter.api:app --reload --port 8000
"""

import uvicorn
import asyncio
from smart_recruiter.config import get_settings
from smart_recruiter.database import init_db

settings = get_settings()


async def startup():
    """Initialize database on startup."""
    print("Initializing database...")
    await init_db()
    print("Database initialized!")


if __name__ == "__main__":
    # Initialize database
    asyncio.run(startup())

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           SMART RECRUITER - API Server                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Starting server...                                          ║
║                                                              ║
║  API Docs:    http://localhost:{settings.api_port}/docs                    ║
║  Health:      http://localhost:{settings.api_port}/health                  ║
║                                                              ║
║  Frontend:    {settings.frontend_url}                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "smart_recruiter.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
