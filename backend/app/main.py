"""CoupleHUB API — ponto de entrada.

Rodar:  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Docs:   http://localhost:8000/docs (Swagger) e /redoc
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.database import SessionLocal, criar_tabelas
from app.domain.erros import (
    AcessoNegado,
    ErroDominio,
    NaoAutenticado,
    NaoEncontrado,
    RegraViolada,
    TransicaoInvalida,
)
from app.seed.catalogo import popular_catalogo

from .api.routers import auth_casal, decisoes_dates, gamificacao, quizzes, tempo_real


@asynccontextmanager
async def lifespan(_app: FastAPI):
    criar_tabelas()  # MVP: create_all. Próximo passo: migrações Alembic (ADR-0002)
    with SessionLocal() as db:
        popular_catalogo(db)
    yield


app = FastAPI(
    title="CoupleHUB API",
    version="0.1.0",
    summary="HUB privado de interação e gamificação para casais.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_settings().cors_origens),
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth_casal.router, quizzes.router, gamificacao.vales, gamificacao.ranking,
    decisoes_dates.decisoes, decisoes_dates.dates, tempo_real.router,
):
    app.include_router(router)

_STATUS_POR_ERRO = {
    NaoAutenticado: 401,
    AcessoNegado: 403,
    NaoEncontrado: 404,
    TransicaoInvalida: 409,
    RegraViolada: 422,
}


@app.exception_handler(ErroDominio)
async def tratar_erro_de_dominio(_request: Request, erro: ErroDominio):
    status_http = next((s for tipo, s in _STATUS_POR_ERRO.items() if isinstance(erro, tipo)), 400)
    return JSONResponse(status_code=status_http, content={"erro": erro.codigo, "mensagem": erro.mensagem})


@app.exception_handler(IntegrityError)
async def tratar_conflito(_request: Request, _erro: IntegrityError):
    return JSONResponse(status_code=409, content={"erro": "CONFLITO", "mensagem": "Operação conflitou com outra simultânea. Tente de novo."})


@app.get("/saude", tags=["Infra"])
def saude():
    return {"status": "ok"}
