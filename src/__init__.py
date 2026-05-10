"""Deprecated root-level package namespace.

Canonical backend source lives under `backend/src/` and should be executed via
`otakuhub ...` commands from the backend project.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from repository-root `src/` is deprecated. "
    "Use backend package entrypoints (`otakuhub ...`) and `backend/src/` instead.",
    DeprecationWarning,
    stacklevel=2,
)
