"""Fonte única de "agora". Os serviços chamam `relogio.agora()` (pelo módulo,
não por `from ... import agora`) para que os testes possam congelar o tempo
com monkeypatch."""
from datetime import datetime, timezone


def agora() -> datetime:
    return datetime.now(timezone.utc)
