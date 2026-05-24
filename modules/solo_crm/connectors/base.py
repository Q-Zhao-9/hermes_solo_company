"""CRM connector interfaces and safe no-op implementation."""
from __future__ import annotations

from typing import Any


class CRMConnector:
    """Small common interface for outbound CRM adapters."""

    provider = "base"

    def upsert_contact(self, contact: dict[str, Any], company: dict[str, Any] | None = None,
                       website: dict[str, Any] | None = None, visitor: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def upsert_company(self, company: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def upsert_deal(self, deal: dict[str, Any], contact: dict[str, Any] | None = None,
                    company: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def add_activity(self, activity: dict[str, Any], contact: dict[str, Any] | None = None,
                     deal: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def test_connection(self) -> dict[str, Any]:
        raise NotImplementedError


class NoopConnector(CRMConnector):
    """Safe connector used when provider sync is disabled."""

    def __init__(self, provider: str = "noop") -> None:
        self.provider = provider

    def _skipped(self) -> dict[str, Any]:
        return {"provider": self.provider, "ok": True, "skipped": True}

    def upsert_contact(self, contact: dict[str, Any], company: dict[str, Any] | None = None,
                       website: dict[str, Any] | None = None, visitor: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._skipped()

    def upsert_company(self, company: dict[str, Any]) -> dict[str, Any]:
        return self._skipped()

    def upsert_deal(self, deal: dict[str, Any], contact: dict[str, Any] | None = None,
                    company: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._skipped()

    def add_activity(self, activity: dict[str, Any], contact: dict[str, Any] | None = None,
                     deal: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._skipped()

    def test_connection(self) -> dict[str, Any]:
        return {"provider": self.provider, "ok": True, "disabled": True}
