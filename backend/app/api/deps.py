"""Dependências de autenticação e escopo do casal."""
from typing import Annotated

import jwt
from fastapi import BackgroundTasks, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ler_token
from app.domain.enums import StatusCasal
from app.domain.erros import AcessoNegado, NaoAutenticado
from app.models import Usuario
from app.realtime.hub import hub
from app.services.contexto import Contexto

_bearer = HTTPBearer(auto_error=False)

DB = Annotated[Session, Depends(get_db)]


def usuario_atual(
    db: DB, credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> Usuario:
    if credenciais is None:
        raise NaoAutenticado("Faça login para continuar.")
    try:
        usuario_id = ler_token(credenciais.credentials)
    except jwt.PyJWTError:
        raise NaoAutenticado("Sessão inválida ou expirada.") from None
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoAutenticado("Sessão inválida ou expirada.")
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(usuario_atual)]


def contexto_casal(usuario: UsuarioAtual) -> Contexto:
    """Funcionalidades do HUB exigem casal ATIVO (pareado) — REQ-PRV-001."""
    casal = usuario.casal
    if casal is None or casal.status is not StatusCasal.ATIVO:
        raise AcessoNegado("Conecte-se com seu parceiro(a) para usar esta função.", "CASAL_NAO_PAREADO")
    return Contexto(usuario=usuario, casal=casal)


Ctx = Annotated[Contexto, Depends(contexto_casal)]


class Notificador:
    """Agenda um evento WebSocket para DEPOIS que a resposta HTTP sair
    (ou seja, depois do commit)."""

    def __init__(self, tarefas: BackgroundTasks) -> None:
        self._tarefas = tarefas

    def __call__(self, ctx: Contexto, tipo: str, **dados) -> None:
        evento = {"tipo": tipo, "autor_id": ctx.usuario.id, **dados}
        self._tarefas.add_task(hub.publicar, ctx.casal.id, evento)


Notificar = Annotated[Notificador, Depends(Notificador)]
