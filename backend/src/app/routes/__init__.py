"""API routes package."""

from fastapi import APIRouter
from . import auth, media, lists, users, groups, sync

api_router = APIRouter()

# auth router already has prefix=/auth
api_router.include_router(auth.router)
# media router defines /media paths inline
api_router.include_router(media.router)
# lists router already has prefix=/lists
api_router.include_router(lists.router)
# users/groups routers include their own prefixes
api_router.include_router(users.router)
api_router.include_router(groups.router)
# sync router uses prefix=/sync
api_router.include_router(sync.router)
