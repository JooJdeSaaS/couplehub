"""Engine e sessão SQLAlchemy (SQLite por padrão — ADR-0002)."""
from collections.abc import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import DATA_DIR, get_settings


def criar_engine(url: str) -> Engine:
    if not url.startswith("sqlite"):
        return create_engine(url, pool_pre_ping=True)

    em_memoria = url in ("sqlite://", "sqlite:///:memory:")
    if not em_memoria:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    opcoes: dict = {"connect_args": {"check_same_thread": False}}
    if em_memoria:
        opcoes["poolclass"] = StaticPool  # uma única conexão compartilhada (testes)
    engine = create_engine(url, **opcoes)

    @event.listens_for(engine, "connect")
    def _pragmas(conexao_dbapi, _registro):
        cursor = conexao_dbapi.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")   # SQLite ignora FKs sem isto
        if not em_memoria:
            cursor.execute("PRAGMA journal_mode = WAL")  # leituras não bloqueiam escritas
        cursor.close()

    return engine


engine = criar_engine(get_settings().database_url)
# expire_on_commit=False: objetos continuam legíveis após o commit (respostas da API)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def criar_tabelas(alvo: Engine | None = None) -> None:
    from app.models import Base  # garante que todos os modelos foram importados

    Base.metadata.create_all(alvo or engine)
