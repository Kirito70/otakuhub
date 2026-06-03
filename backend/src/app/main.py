"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.app.config import settings
from src.app.database import connect_db, disconnect_db
from src.app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name}...", flush=True)
    print(f"Environment: {settings.environment}", flush=True)
    print(f"Debug mode: {settings.debug}", flush=True)

    await connect_db()

    yield

    # Shutdown
    print(f"Shutting down {settings.app_name}...", flush=True)
    await disconnect_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="FastAPI backend for OtakuHub with SQLModel",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "0.1.0",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }


@app.get("/health")
async def health():
    """Health endpoint for legacy tests and load balancers."""
    return {"status": "healthy", "service": settings.app_name}


def main() -> None:
    """Console script entrypoint."""
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000)
