"""Fonte única de "agora" para as regras de negócio.

Os serviços chamam `relogio.agora()` (pelo módulo, não por `from ... import
agora`) para que os testes possam congelar o tempo com monkeypatch.

Viagem no tempo para demonstração (só em COUPLEHUB_AMBIENTE=dev):
    COUPLEHUB_AVANCAR_DIAS=7 uvicorn app.main:app ...
faz a API "viver" 7 dias no futuro. Serve para ver a semana fechar, o vencedor
ganhar crédito e os prazos vencerem sem esperar até segunda-feira. O token de
login continua usando o relógio real (app/core/security.py).
"""
import os
from datetime import datetime, timedelta, timezone


def _avanco() -> timedelta:
    if os.getenv("COUPLEHUB_AMBIENTE", "dev") != "dev":
        return timedelta(0)
    try:
        return timedelta(days=float(os.getenv("COUPLEHUB_AVANCAR_DIAS") or 0))
    except ValueError:
        return timedelta(0)


def agora() -> datetime:
    return datetime.now(timezone.utc) + _avanco()
