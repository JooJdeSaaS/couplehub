"""Configuração lida de variáveis de ambiente (ver .env.example)."""
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"

_SEGREDO_DEV = "dev-inseguro-troque-este-segredo-antes-de-publicar"


@dataclass(frozen=True)
class Settings:
    ambiente: str
    database_url: str
    jwt_segredo: str
    jwt_expiracao_min: int
    chave_dados: str | None
    cors_origens: tuple[str, ...]

    @property
    def dev(self) -> bool:
        return self.ambiente == "dev"


@lru_cache
def get_settings() -> Settings:
    cfg = Settings(
        ambiente=os.getenv("COUPLEHUB_AMBIENTE", "dev"),
        database_url=os.getenv("COUPLEHUB_DATABASE_URL", f"sqlite:///{DATA_DIR / 'couplehub.db'}"),
        jwt_segredo=os.getenv("COUPLEHUB_JWT_SEGREDO", _SEGREDO_DEV),
        jwt_expiracao_min=int(os.getenv("COUPLEHUB_JWT_EXPIRACAO_MIN", str(60 * 24 * 7))),
        chave_dados=os.getenv("COUPLEHUB_CHAVE_DADOS") or None,
        cors_origens=tuple(o.strip() for o in os.getenv("COUPLEHUB_CORS", "*").split(",")),
    )
    if not cfg.dev and (cfg.jwt_segredo == _SEGREDO_DEV or not cfg.chave_dados):
        raise RuntimeError("Fora do ambiente dev, defina COUPLEHUB_JWT_SEGREDO e COUPLEHUB_CHAVE_DADOS.")
    return cfg
