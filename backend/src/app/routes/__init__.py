"""API routes package."""

from fastapi import APIRouter
from . import auth, media, lists, social, watchparty, notifications, sync, admin

# Main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(lists.router, prefix="/lists", tags=["lists"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
api_router.include_router(watchparty.router, prefix="/watchparty", tags=["watchparty"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])