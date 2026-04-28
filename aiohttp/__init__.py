"""Stub aiohttp package for testing – provides minimal symbols used in external clients.

Only the import needs to succeed; no functionality is required for the current test suite.
"""

# Define a minimal ClientSession class to satisfy type hints.
class ClientSession:
    def __init__(self, *args, **kwargs):
        pass
