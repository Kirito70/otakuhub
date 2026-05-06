"""Apprise notification delivery client."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any


def _load_apprise_module() -> Any | None:
    """Load apprise lazily; return None when dependency is missing."""
    try:
        return import_module("apprise")
    except ModuleNotFoundError:
        return None


@dataclass(slots=True)
class AppriseClient:
    """Thin wrapper around Apprise for multi-channel notifications."""

    apprise_urls: str
    _apprise: Any | None = field(init=False, default=None, repr=False)
    _configured_targets: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        apprise_module = _load_apprise_module()
        self._apprise = apprise_module.Apprise() if apprise_module else None

        if self._apprise is None:
            return

        for raw_url in self.apprise_urls.split(","):
            url = raw_url.strip()
            if not url:
                continue
            if self._apprise.add(url):
                self._configured_targets += 1

    @property
    def is_configured(self) -> bool:
        """Return whether at least one Apprise target is configured."""
        return self._configured_targets > 0

    @property
    def configured_targets(self) -> int:
        """Return count of valid configured Apprise targets."""
        return self._configured_targets

    def send_notification(self, *, title: str, body: str) -> bool:
        """Send a notification to all configured Apprise targets."""
        if self._apprise is None or not self.is_configured:
            return False

        return bool(
            self._apprise.notify(
                title=title,
                body=body,
            )
        )
