"""Common/shared Pydantic schemas."""

from pydantic import BaseModel


class DeleteResponse(BaseModel):
    """Generic response for soft-delete operations."""

    deleted: bool


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
