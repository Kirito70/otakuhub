"""Tests for portable TSVector type."""

from sqlalchemy import create_engine, Column, Integer, Text, inspect
from sqlalchemy.orm import DeclarativeBase

from src.app.core.tsvector import TSVector


class _TSVectorTestBase(DeclarativeBase):
    pass


class _TSVectorTestModel(_TSVectorTestBase):
    __tablename__ = "test_tsvector_model"
    id = Column(Integer, primary_key=True)
    title_vector = Column("title_vector", TSVector())


def test_tsvector_on_sqlite_is_text():
    """On SQLite, TSVector should resolve to Text."""
    engine = create_engine("sqlite://", echo=False)
    _TSVectorTestBase.metadata.create_all(engine)

    # Inspect the column type
    inspector = inspect(engine)
    columns = inspector.get_columns("test_tsvector_model")
    title_col = next(c for c in columns if c["name"] == "title_vector")
    # On SQLite, it should be TEXT
    assert str(title_col["type"]) == "TEXT", (
        f"Expected TEXT on SQLite, got {title_col['type']}"
    )

    engine.dispose()


def test_tsvector_accepts_string_values_on_sqlite():
    """On SQLite, TSVector should accept string values like a Text column."""
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite://", echo=False)
    _TSVectorTestBase.metadata.create_all(engine)

    with Session(engine) as session:
        obj = _TSVectorTestModel(id=1, title_vector="hello world")
        session.add(obj)
        session.commit()

    with Session(engine) as session:
        retrieved = session.get(_TSVectorTestModel, 1)
        assert retrieved.title_vector == "hello world"

    engine.dispose()
