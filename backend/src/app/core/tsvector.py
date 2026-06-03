"""Portable TSVECTOR type for SQLAlchemy.

Maps to PostgreSQL's TSVECTOR during Postgres operation, and falls back
to plain Text on SQLite (where TSVECTOR is not supported).

Usage:
    class MediaEntry(SQLModel, table=True):
        title_search: Optional[str] = Field(
            default=None,
            sa_column=Column(TSVector())
        )
"""

from sqlalchemy import TypeDecorator, Text
from sqlalchemy.dialects.postgresql import TSVECTOR


class TSVector(TypeDecorator):
    """Portable TSVECTOR type.

    On PostgreSQL: uses native TSVECTOR type with full-text search capabilities.
    On SQLite:     falls back to Text (SQLite cannot create tsvector columns).

    This allows the model to declare a TSVECTOR column while remaining
    compatible with SQLite-based test environments.
    """

    impl = TSVECTOR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(TSVECTOR())
        return dialect.type_descriptor(Text())
