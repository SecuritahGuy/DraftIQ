"""
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await create_tables()
    yield
    # Shutdown
    pass


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import all models to ensure they're registered with SQLAlchemy
from app.models import user, fantasy, nfl_data

# Include API routers
from app.api.v1 import auth, yahoo, data_sync, nfl_data, scoring, projections, csv_import
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(yahoo.router, prefix=settings.api_v1_prefix)
app.include_router(data_sync.router, prefix=settings.api_v1_prefix)
app.include_router(nfl_data.router, prefix=settings.api_v1_prefix + "/nfl")
app.include_router(scoring.router, prefix=settings.api_v1_prefix + "/scoring")
app.include_router(projections.router, prefix=settings.api_v1_prefix + "/projections")
app.include_router(csv_import.router, prefix=settings.api_v1_prefix + "/csv")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
