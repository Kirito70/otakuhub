"""
Main FastAPI application factory for OtakuHub.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from core.config import settings
from routers import auth, media, lists, social, watchparty, notifications, sync, admin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    """
    logger.info("Starting up OtakuHub application")
    # Initialization code can go here
    yield
    # Cleanup code can go here
    logger.info("Shutting down OtakuHub application")

# Create FastAPI app
app = FastAPI(
    title="OtakuHub",
    description="Private friend-group anime/manga tracking and social platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])
app.include_router(lists.router, prefix="/api/v1/lists", tags=["lists"])
app.include_router(social.router, prefix="/api/v1/social", tags=["social"])
app.include_router(watchparty.router, prefix="/api/v1/watchparty", tags=["watchparty"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["sync"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# Health check endpoint
@app.get("/health", response_model=dict)
async def health_check():
    """Check if the application is running."""
    return {"status": "healthy", "service": "otakuhub-backend"}

@app.get("/api/v1/status", response_model=dict)
async def status_check():
    """Check if the application and dependencies are running."""
    return {"status": "operational", "service": "otakuhub-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)