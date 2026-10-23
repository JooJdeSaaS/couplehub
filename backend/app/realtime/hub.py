"""Eventos em tempo real por casal via WebSocket (RNF01 / ADR-0006).

Implementação em memória: serve para um único processo (uvicorn sem
--workers). Para escalar horizontalmente, troque por Redis Pub/Sub mantendo a
mesma interface `publicar(casal_id, evento)`.
"""
import logging
from collections import defaultdict

from fastapi import WebSocket

log = logging.getLogger(__name__)


class HubCasal:
    def __init__(self) -> None:
        # sem trava: o event loop é single-thread e não há await entre ler e alterar o set
        self._conexoes: dict[str, set[WebSocket]] = defaultdict(set)

    async def conectar(self, casal_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._conexoes[casal_id].add(ws)

    def desconectar(self, casal_id: str, ws: WebSocket) -> None:
        self._conexoes[casal_id].discard(ws)

    async def publicar(self, casal_id: str, evento: dict) -> None:
        """Envia `evento` a todos os aparelhos conectados do casal."""
        alvos = list(self._conexoes.get(casal_id, ()))
        for ws in alvos:
            try:
                await ws.send_json(evento)
            except Exception:  # conexão caiu sem avisar
                log.debug("descartando websocket morto do casal %s", casal_id)
                self.desconectar(casal_id, ws)


hub = HubCasal()
