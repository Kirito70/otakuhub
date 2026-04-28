import sys
import os
import pytest
from httpx import AsyncClient
from src.app.main import app

# Ensure the repository root (which contains the top‑level `src` package) is on sys.path
ROOT = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
print('CONFTST sys.path[0:3]=', sys.path[:3])

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac
