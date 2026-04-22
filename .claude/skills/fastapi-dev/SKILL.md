---
name: fastapi-dev
description: Build a complete FastAPI feature: model, schema, repository, service, router, and tests in the correct layered order.
---

# FastAPI Feature Development

## Execution Order
Always build in this sequence — each layer depends on the previous.

### Step 1 — SQLAlchemy Model (`backend/models/<name>.py`)
```python
from sqlalchemy import String, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMPTZ
from .base import Base
import uuid

class MediaEntry(Base):
    __tablename__ = "media_entries"
    __table_args__ = (
        Index("idx_media_entries_status", "status"),
        Index("idx_media_entries_type", "media_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True,
        server_default=text("uuid_generate_v7()")
    )
    title_romaji: Mapped[str] = mapped_column(String(500), nullable=False)
    # ... columns
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)

    # Relationships
    external_ids: Mapped["MediaExternalIds"] = relationship(back_populates="media", uselist=False)
    genres: Mapped[list["Genre"]] = relationship(secondary="media_genres", lazy="selectin")
```

### Step 2 — Pydantic Schemas (`backend/schemas/<name>.py`)
```python
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class MediaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class MediaDetailResponse(MediaBase):
    id: UUID
    title: TitleSchema
    media_type: str
    # ... all response fields

class MediaSearchResponse(MediaBase):
    id: UUID
    title: TitleSchema
    cover_image_medium: str | None
    average_score: float | None
```

### Step 3 — Repository (`backend/repositories/<name>_repository.py`)
```python
class MediaRepository:
    async def get_by_id(self, db: AsyncSession, media_id: UUID) -> MediaEntry | None:
        stmt = (
            select(MediaEntry)
            .where(MediaEntry.id == media_id)
            .where(MediaEntry.deleted_at.is_(None))
            .options(
                selectinload(MediaEntry.genres),
                selectinload(MediaEntry.external_ids),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
```

### Step 4 — Service (`backend/services/<name>_service.py`)
Business logic only. Calls repositories. Returns Pydantic schemas.

### Step 5 — Router (`backend/routers/<name>.py`)
```python
router = APIRouter(prefix="/api/v1/media", tags=["media"])

@router.get("/{media_id}", response_model=MediaDetailResponse)
async def get_media_detail(
    media_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MediaDetailResponse:
    result = await media_service.get_detail(db, media_id=media_id)
    if not result:
        raise HTTPException(status_code=404, detail="Media not found")
    return result
```

### Step 6 — Tests (`tests/routers/test_<name>.py`)
Write: success, 401 auth failure, 404 not found, 422 validation.

### Step 7 — Register Router
Add `app.include_router(media_router)` in `backend/main.py`.

## Verify
```bash
cd backend
ruff check .
mypy . --strict
pytest tests/ -v --asyncio-mode=auto -k "test_media"
```
