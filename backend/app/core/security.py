"""Hash de senha (scrypt, biblioteca padrão) e tokens JWT (PyJWT)."""
import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from .config import get_settings

_N, _R, _P, _DKLEN = 2**14, 8, 1, 32
ALGORITMO_JWT = "HS256"


def _b64(dados: bytes) -> str:
    return base64.b64encode(dados).decode("ascii")


def gerar_hash_senha(senha: str) -> str:
    sal = secrets.token_bytes(16)
    chave = hashlib.scrypt(senha.encode(), salt=sal, n=_N, r=_R, p=_P, dklen=_DKLEN)
    return f"scrypt${_N}${_R}${_P}${_b64(sal)}${_b64(chave)}"


def verificar_senha(senha: str, armazenado: str | None) -> bool:
    if not armazenado:
        return False
    try:
        _, n, r, p, sal, esperado = armazenado.split("$")
        chave = hashlib.scrypt(
            senha.encode(), salt=base64.b64decode(sal), n=int(n), r=int(r), p=int(p),
            dklen=len(base64.b64decode(esperado)),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(_b64(chave), esperado)


def criar_token(usuario_id: str) -> str:
    """Usa o relógio real (não app.core.relogio): validade de token é segurança,
    não regra de negócio, e o PyJWT valida `exp` contra o relógio real."""
    cfg = get_settings()
    agora = datetime.now(timezone.utc)
    payload = {"sub": usuario_id, "iat": agora, "exp": agora + timedelta(minutes=cfg.jwt_expiracao_min)}
    return jwt.encode(payload, cfg.jwt_segredo, algorithm=ALGORITMO_JWT)


def ler_token(token: str) -> str:
    """Devolve o id do usuário. Lança jwt.PyJWTError se inválido/expirado."""
    dados = jwt.decode(token, get_settings().jwt_segredo, algorithms=[ALGORITMO_JWT], options={"require": ["sub", "exp"]})
    return dados["sub"]
