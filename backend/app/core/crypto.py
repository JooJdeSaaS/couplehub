"""Criptografia em repouso de campos sensíveis (RNF02 / ADR-0005).

Usa Fernet (AES-128-CBC + HMAC-SHA256). A chave vem de COUPLEHUB_CHAVE_DADOS;
em dev, se ausente, é gerada uma vez em backend/data/.chave_dev.
Gerar chave: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from .config import DATA_DIR, get_settings


@lru_cache
def _fernet() -> Fernet:
    cfg = get_settings()
    if cfg.chave_dados:
        return Fernet(cfg.chave_dados.encode())
    arquivo = DATA_DIR / ".chave_dev"
    if not arquivo.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        arquivo.write_bytes(Fernet.generate_key())
        arquivo.chmod(0o600)
    return Fernet(arquivo.read_bytes().strip())


def cifrar(texto: str) -> str:
    return _fernet().encrypt(texto.encode("utf-8")).decode("ascii")


def decifrar(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except InvalidToken as erro:
        raise ValueError("Dado cifrado com outra chave ou corrompido.") from erro
