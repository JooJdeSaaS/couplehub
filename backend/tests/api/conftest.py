from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.core import relogio
from app.core.database import engine
from app.main import app
from app.models import Base


class RelogioFixo:
    def __init__(self, inicio: datetime):
        self.agora = inicio

    def ir_para(self, instante: datetime) -> None:
        self.agora = instante

    def avancar(self, **delta) -> None:
        self.agora += timedelta(**delta)


@pytest.fixture
def tempo(monkeypatch) -> RelogioFixo:
    # terça-feira, 20/10/2026, 12:00 em São Paulo (semana 2026-W43)
    r = RelogioFixo(datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc))
    monkeypatch.setattr(relogio, "agora", lambda: r.agora)
    return r


@pytest.fixture
def cliente(tempo):
    Base.metadata.drop_all(engine)
    with TestClient(app) as c:  # executa o lifespan: cria tabelas catálogo
        yield c


def cadastrar(cliente: TestClient, nome: str) -> tuple[dict, str]:
    r = cliente.post("/auth/cadastro", json={"nome": nome, "email": f"{nome.lower()}@couplehub.app", "senha": "segredo123"})
    assert r.status_code == 201, r.text
    corpo = r.json()
    return {"Authorization": f"Bearer {corpo['access_token']}"}, corpo["usuario"]["id"]


@dataclass
class Casal:
    a: dict   # headers do Parceiro A (Lucas)
    b: dict   # headers do Parceiro B (Beatris)
    id_a: str
    id_b: str


def parear(cliente: TestClient, nome_a: str, nome_b: str) -> Casal:
    ha, ida = cadastrar(cliente, nome_a)
    hb, idb = cadastrar(cliente, nome_b)
    codigo = cliente.post("/casais", headers=ha).json()["codigo_convite"]
    r = cliente.post("/casais/entrar", json={"codigo": codigo}, headers=hb)
    assert r.status_code == 200 and r.json()["status"] == "ATIVO", r.text
    return Casal(ha, hb, ida, idb)


@pytest.fixture
def casal(cliente) -> Casal:
    return parear(cliente, "Lucas", "Beatris")
