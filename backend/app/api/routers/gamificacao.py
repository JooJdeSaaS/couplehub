"""Vales (RF08, RF09) e ranking (RF07)."""
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.domain.enums import StatusVale, TipoPeriodo
from app.schemas.gamificacao import CreditoSaida, PlacarSaida, RankingSaida, ValeEntrada, ValeSaida
from app.services import ranking_service, vale_service

from ..deps import DB, Ctx, Notificar

vales = APIRouter(prefix="/vales", tags=["Vales"])
ranking = APIRouter(prefix="/ranking", tags=["Ranking"])


@vales.get("", response_model=list[ValeSaida])
def listar_vales(ctx: Ctx, db: DB, status_: Annotated[StatusVale | None, Query(alias="status")] = None):
    return vale_service.listar(db, ctx, status_)


@vales.get("/creditos", response_model=list[CreditoSaida], summary="Meus créditos para resgatar vales")
def meus_creditos(ctx: Ctx, db: DB, apenas_pendentes: bool = True):
    return vale_service.creditos(db, ctx, apenas_pendentes)


@vales.post("", response_model=ValeSaida, status_code=status.HTTP_201_CREATED,
            summary="Cria um vale que EU ofereço ao meu parceiro(a)")
def criar_vale(dados: ValeEntrada, ctx: Ctx, db: DB, notificar: Notificar):
    vale = vale_service.criar(db, ctx, dados)
    notificar(ctx, "vale.criado", vale_id=vale.id)
    return vale


@vales.post("/{vale_id}/resgatar", response_model=ValeSaida)
def resgatar(vale_id: str, ctx: Ctx, db: DB, notificar: Notificar):
    vale = vale_service.resgatar(db, ctx, vale_id)
    notificar(ctx, "vale.resgatado", vale_id=vale.id, titulo=vale.titulo)   # REQ-VAL-008
    return vale


@vales.post("/{vale_id}/confirmar-uso", response_model=ValeSaida)
def confirmar_uso(vale_id: str, ctx: Ctx, db: DB, notificar: Notificar):
    vale = vale_service.confirmar_uso(db, ctx, vale_id)
    notificar(ctx, "vale.utilizado", vale_id=vale.id)
    return vale


@vales.delete("/{vale_id}", response_model=ValeSaida, summary="Cancela um vale ainda disponível")
def cancelar(vale_id: str, ctx: Ctx, db: DB, notificar: Notificar):
    vale = vale_service.cancelar(db, ctx, vale_id)
    notificar(ctx, "vale.cancelado", vale_id=vale.id)
    return vale


@ranking.get("/semanal", response_model=PlacarSaida)
def semanal(ctx: Ctx, db: DB, referencia: Annotated[str | None, Query(examples=["2026-W43"])] = None):
    return ranking_service.placar(db, ctx, TipoPeriodo.SEMANAL, referencia)


@ranking.get("/mensal", response_model=PlacarSaida)
def mensal(ctx: Ctx, db: DB, referencia: Annotated[str | None, Query(examples=["2026-10"])] = None):
    return ranking_service.placar(db, ctx, TipoPeriodo.MENSAL, referencia)


@ranking.get("/historico", response_model=list[RankingSaida])
def historico(ctx: Ctx, db: DB, tipo: TipoPeriodo = TipoPeriodo.SEMANAL, limite: Annotated[int, Query(ge=1, le=52)] = 12):
    return ranking_service.historico(db, ctx, tipo, limite)
