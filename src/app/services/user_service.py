"""User service stub – minimal implementation for tests.

Only required to be instantiable; no methods are needed for the current test
suite.
"""

from .base_service import BaseService


class UserService(BaseService):
    def __init__(self, session=None):
        super().__init__(session)
        from src.app.repositories.user_repository import UserRepository
        self.user_repository = UserRepository(session) if session else UserRepository(None)
