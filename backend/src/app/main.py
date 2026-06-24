"""Main FastAPI application."""

import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import uvicorn

import sentry_sdk
from src.app.config import settings
from src.app.database import connect_db, disconnect_db
from src.app.routes import api_router

# ---------------------------------------------------------------------------
# Logging configuration — ensures all request logs appear on stderr
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
    force=True,  # override any previous config
)

# Ensure uvicorn access logger is configured
access_logger = logging.getLogger("uvicorn.access")
if not access_logger.handlers:
    access_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    access_logger.addHandler(handler)
    access_logger.propagate = False

# ---------------------------------------------------------------------------
# Sentry — error tracking and performance monitoring
# ---------------------------------------------------------------------------
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        enable_tracing=True,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
    )
    logging.getLogger("otakuhub").info(
        "Sentry enabled (traces_sample_rate=%.2f)", settings.sentry_traces_sample_rate
    )

# ---------------------------------------------------------------------------
# ASGI middleware that logs every request — guaranteed output even if uvicorn
# access logs are suppressed.
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger = logging.getLogger("otakuhub")
    logger.info("Starting %s ...", settings.app_name)
    logger.info("Environment: %s", settings.environment)
    logger.info("Debug mode: %s", settings.debug)

    await connect_db()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down %s ...", settings.app_name)
    await disconnect_db()


class RequestLogMiddleware:
    """Logs every HTTP request with method, path, status code, and duration."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        method = scope.get("method", "?")
        path = scope.get("path", "?")

        # Wrap send so we can capture the status code
        status_code = [None]

        async def _send(message):
            if message["type"] == "http.response.start":
                status_code[0] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, _send)
        except Exception as exc:
            elapsed = time.time() - start
            logging.getLogger("otakuhub.request").error(
                "%s %s -> exception=%s duration=%.3fs", method, path, exc, elapsed
            )
            raise

        elapsed = time.time() - start
        logging.getLogger("otakuhub.request").info(
            "%s %s -> %s duration=%.3fs", method, path, status_code[0], elapsed
        )


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

# Register request-logging middleware (after CORS so headers are set)
app.add_middleware(RequestLogMiddleware)

# ---------------------------------------------------------------------------
# Exception handlers — log details and return structured JSON
# ---------------------------------------------------------------------------


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Log DB errors with full traceback and return 500."""
    logger = logging.getLogger("otakuhub.error")
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    """Log Pydantic validation errors and return 422."""
    logger = logging.getLogger("otakuhub.error")
    logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all — log full traceback and return 500."""
    logger = logging.getLogger("otakuhub.error")
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
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
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
    )
