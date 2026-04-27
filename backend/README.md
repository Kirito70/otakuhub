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

## Installation

1. Install dependencies:
```bash
pip install -e .
pip install -e ".[dev]"
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

## Running

1. Start the development server:
```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Run CLI commands:
```bash
otakuhub db connect
otakuhub db init
```

3. Run tests:
```bash
pytest tests/
```

## Configuration

Environment variables are loaded from `.env` file. Check `.env.example` for available settings.

## Development Setup

1. Set up pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

2. Run linting:
```bash
ruff check src/
```

3. Run type checking:
```bash
mypy src/ --strict
```

4. Run tests with coverage:
```bash
pytest tests/ --cov=src/ --cov-report=html
```
