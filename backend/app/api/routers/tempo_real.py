"""Canal WebSocket do casal (RNF01). O app conecta em /ws?token=<JWT>."""
from typing import Annotated

import jwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.core.database import SessionLocal
from app.core.security import ler_token
from app.domain.enums import StatusCasal
from app.models import Usuario
from app.realtime.hub import hub

router = APIRouter(tags=["Tempo real"])


def _casal_do_token(token: str) -> str | None:
    try:
        usuario_id = ler_token(token)
    except jwt.PyJWTError:
        return None
    with SessionLocal() as db:
        usuario = db.get(Usuario, usuario_id)
        if usuario is None or usuario.casal is None or usuario.casal.status is not StatusCasal.ATIVO:
            return None
        return usuario.casal_id


@router.websocket("/ws")
async def canal_do_casal(websocket: WebSocket, token: Annotated[str, Query()]):
    casal_id = _casal_do_token(token)
    if casal_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await hub.conectar(casal_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # mantém a conexão; o cliente pode mandar "ping"
    except WebSocketDisconnect:
        hub.desconectar(casal_id, websocket)
