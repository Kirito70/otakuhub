"""Schemas for first-run setup/bootstrap endpoints (Phase 12)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr
from uuid import UUID


class SetupStatusResponse(BaseModel):
    """Public setup status payload used by frontend routing."""

    model_config = ConfigDict(from_attributes=True)

    setup_required: bool | None = None


class BootstrapAdminRequest(BaseModel):
    """Payload for one-time super-admin bootstrap."""

    model_config = ConfigDict(from_attributes=True)

    username: constr(min_length=3, max_length=50)
    email: constr(min_length=5, max_length=255)
    password: constr(min_length=8)


class BootstrapLoggedInUser(BaseModel):
    """Slim logged-in user payload for frontend boot routing."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: str | None = None
    is_admin: bool


class AppBootstrapResponse(BaseModel):
    """Unified frontend bootstrap payload."""

    model_config = ConfigDict(from_attributes=True)

    site_status: str
    logged_in_user: BootstrapLoggedInUser | None = None
    setup_required: bool | None = None
