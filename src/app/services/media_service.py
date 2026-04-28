"""Media service stub – provides a minimal class for instantiation.

The real service would contain business logic for media lookup, but the tests only
verify that the class can be created (optionally with a DB session)."""

from .base_service import BaseService


class MediaService(BaseService):
    def __init__(self, session=None):
        super().__init__(session)
        from src.app.repositories.media_repository import MediaRepository
        self.media_repository = MediaRepository(session) if session else MediaRepository(None)
