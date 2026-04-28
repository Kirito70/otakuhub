"""Auth service stub – provides a minimal class for tests.

Only needed for import; no functionality required.
"""

from .base_service import BaseService


class AuthService(BaseService):
    async def login(self, username: str, password: str):
        # Placeholder implementation – returns dummy tokens
        from src.app.schemas.auth import TokenResponse
        return TokenResponse(access_token="dummy", refresh_token="dummy")

    async def refresh(self, refresh_token: str):
        from src.app.schemas.auth import TokenResponse
        return TokenResponse(access_token="new_dummy", refresh_token="new_dummy")
