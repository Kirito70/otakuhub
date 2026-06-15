"""Alembic migrations environment configuration.

Uses async SQLAlchemy engine and SQLModel metadata for autogeneration support.
"""

import asyncio
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import create_async_engine

# Load local .env before reading settings so DATABASE_URL is available
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

from src.app.config import settings

# Alembic Config object
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so they register with SQLModel.metadata
from src.app.models import *  # noqa: F401, F403
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using an async engine."""
    # Use the URL from settings (respects DATABASE_URL env var)
    # Fall back to alembic.ini value if not set
    db_url = settings.database_url

    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool,
    )

    # Enable required PostgreSQL extensions before running migrations
    async with connectable.connect() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin"))
        await conn.commit()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
