"""API routes package."""

from fastapi import APIRouter
from . import auth, media, lists

api_router = APIRouter()

# auth router already has prefix=/auth
api_router.include_router(auth.router)
# media router defines /media paths inline
api_router.include_router(media.router)
# lists router already has prefix=/lists
api_router.include_router(lists.router)
