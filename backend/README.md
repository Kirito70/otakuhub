# OtakuHub Backend

FastAPI backend application with SQLModel, repository pattern, and proper project structure.

## Features

- Clean FastAPI application structure
- SQLModel for database operations
- Repository pattern implementation
- Command-line interface using Typer
- Proper configuration management
- Database connection handling
- Test framework setup

## Project Structure

```
src/
├── app/                    # Main application package
│   ├── __init__.py         # Package init
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection management
│   ├── models/             # Database models
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic layer
│   ├── schemas/            # Pydantic models for request/response
│   ├── routes/             # API routes
│   └── commands/           # CLI commands
├── tests/                  # Test files
└── alembic/                # Database migrations
```

## Installation (uv - recommended)

1. Install `uv` (one time):
```bash
# Windows (PowerShell)
winget install astral-sh.uv

# or any platform:
# https://docs.astral.sh/uv/getting-started/installation/
```

2. Sync dependencies (including dev tools):
```bash
uv sync --extra dev
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

## Installation (pip alternative)

```bash
pip install -e .
pip install -e ".[dev]"
```

## Running

### Start backend with uv

Option A (new convenience command):
```bash
uv run otakuhub-dev
```

Option B (direct uvicorn):
```bash
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Run CLI commands:
```bash
uv run otakuhub db connect
uv run otakuhub db init

# Data seed (direct script)
uv run otakuhub seed run

# Enqueue seed on Celery
uv run otakuhub celery seed --batch-size 50

# Run Celery worker and scheduler
uv run otakuhub celery worker --loglevel info --queue sync
uv run otakuhub celery beat --loglevel info
```

3. Run tests:
```bash
uv run pytest tests/
```

## Configuration

Environment variables are loaded from `.env` file. Check `.env.example` for available settings.

### Frontend `.env`

Create `frontend/.env` from `frontend/.env.example`:

```bash
cp ../frontend/.env.example ../frontend/.env
```

Expected variable:

```env
API_BASE_URL=http://localhost:8000
```

## Development Setup

1. Set up pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

2. Run linting:
```bash
uv run ruff check src/
```

3. Run type checking:
```bash
uv run mypy src/ --strict
```

4. Run tests with coverage:
```bash
uv run pytest tests/ --cov=src/ --cov-report=html
```
