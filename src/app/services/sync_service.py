"""Sync service stub – minimal class for tests.

The real service would coordinate background sync jobs, but the test suite only
requires that the class can be instantiated.
"""

from .base_service import BaseService


class SyncService(BaseService):
    pass
