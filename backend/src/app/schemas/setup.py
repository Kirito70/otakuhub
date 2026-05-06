"""Schemas for first-run setup/bootstrap endpoints (Phase 12)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr


class SetupStatusResponse(BaseModel):
    """Public setup status payload used by frontend routing."""

    model_config = ConfigDict(from_attributes=True)

    setup_required: bool


class BootstrapAdminRequest(BaseModel):
    """Payload for one-time super-admin bootstrap."""

    model_config = ConfigDict(from_attributes=True)

    username: constr(min_length=3, max_length=50)
    email: constr(min_length=5, max_length=255)
    password: constr(min_length=8)
