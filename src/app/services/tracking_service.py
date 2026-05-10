"""Tracking service stub – minimal class for tests.

The real implementation would manage user list entries, but the test suite only
checks that the class can be instantiated (optionally with a session).
"""

from .base_service import BaseService


class TrackingService(BaseService):
    pass
