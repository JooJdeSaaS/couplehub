"""Ranking semanal/mensal com fechamento preguiçoso (RF07 / ADR-0004).

Não há agendador: toda leitura de ranking ou de créditos chama
`fechar_periodos_pendentes`, que fecha (uma única vez, de forma idempotente)
toda semana cujo prazo já passou e, se for a última semana do mês, o mês.
"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import relogio
from app.domain import periodos
from app.domain.enums import OrigemCredito, Papel, TipoPeriodo
from app.domain.ranking import Placar, vencedores
from app.models import Ranking

from . import pontos_service, quiz_service
from .contexto import Contexto


def fechar_periodos_pendentes(db: Session, ctx: Contexto) -> list[Ranking]:
    agora = relogio.agora()
    quiz_service.aplicar_prazos(db, ctx, agora)   # pontos atrasados entram antes da apuração
    db.flush()

    ultima = db.scalar(select(func.max(Ranking.referencia)).where(
        Ranking.casal_id == ctx.casal.id, Ranking.tipo_periodo == TipoPeriodo.SEMANAL,
    ))
    inicio = periodos.semana_seguinte(ultima) if ultima else periodos.semana_do_instante(
        ctx.casal.pareado_em or ctx.casal.criado_em
    )
    fechados: list[Ranking] = []
    for semana in periodos.semanas_fechaveis(inicio, agora):
        fechados.append(_fechar(db, ctx, TipoPeriodo.SEMANAL, semana, agora))
        if periodos.ultima_semana_do_mes(semana):
            fechados.append(_fechar(db, ctx, TipoPeriodo.MENSAL, periodos.mes_da_semana(semana), agora))
    pontos_service.expirar_creditos(db, ctx.casal.id, agora)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()          # outra requisição fechou o mesmo período ao mesmo tempo
        return []
    return fechados


def _fechar(db: Session, ctx: Contexto, tipo: TipoPeriodo, referencia: str, agora: datetime) -> Ranking:
    placar = _placar_vivo(db, ctx, tipo, referencia)
    inicio, fim = _intervalo(tipo, referencia)
    ranking = Ranking(
        casal_id=ctx.casal.id, tipo_periodo=tipo, referencia=referencia, data_inicio=inicio, data_fim=fim,
        pontos_a=placar.pontos_a, pontos_b=placar.pontos_b, resultado=placar.resultado, fechado_em=agora,
    )
    db.add(ranking)
    origem = OrigemCredito.VENCEDOR_SEMANA if tipo is TipoPeriodo.SEMANAL else OrigemCredito.VENCEDOR_MES
    for papel in vencedores(placar.resultado):
        pontos_service.emitir_credito(db, ctx.casal.id, ctx.id_do_papel(papel), origem, referencia, agora)
    return ranking


def _intervalo(tipo: TipoPeriodo, referencia: str):
    return periodos.intervalo_semana(referencia) if tipo is TipoPeriodo.SEMANAL else periodos.intervalo_mes(referencia)


def _placar_vivo(db: Session, ctx: Contexto, tipo: TipoPeriodo, referencia: str) -> Placar:
    if tipo is TipoPeriodo.SEMANAL:
        somas = pontos_service.somar(db, ctx.casal.id, semana_ref=referencia)
    else:
        somas = pontos_service.somar(db, ctx.casal.id, mes_ref=referencia)
    return Placar(somas.get(ctx.id_do_papel(Papel.A), 0), somas.get(ctx.id_do_papel(Papel.B), 0))


def placar(db: Session, ctx: Contexto, tipo: TipoPeriodo, referencia: str | None = None) -> dict:
    """Placar do período: snapshot se já fechado, parcial ao vivo se aberto."""
    fechar_periodos_pendentes(db, ctx)
    agora = relogio.agora()
    if referencia is None:
        semana_atual = periodos.semana_do_instante(agora)
        referencia = semana_atual if tipo is TipoPeriodo.SEMANAL else periodos.mes_da_semana(semana_atual)
    inicio, fim = _intervalo(tipo, referencia)

    fechado = db.scalar(select(Ranking).where(
        Ranking.casal_id == ctx.casal.id, Ranking.tipo_periodo == tipo, Ranking.referencia == referencia,
    ))
    p = Placar(fechado.pontos_a, fechado.pontos_b) if fechado else _placar_vivo(db, ctx, tipo, referencia)
    ultima_semana = referencia if tipo is TipoPeriodo.SEMANAL else periodos.semanas_do_mes(referencia)[-1]
    lider = p.lider()
    return {
        "tipo": tipo, "referencia": referencia, "data_inicio": inicio, "data_fim": fim,
        "fechado": fechado is not None,
        "fecha_em": None if fechado else periodos.fechamento_semana(ultima_semana),
        "participantes": [
            {"usuario_id": u.id, "nome": u.nome, "papel": u.papel,
             "pontos": p.pontos_a if u.papel == Papel.A else p.pontos_b}
            for u in ctx.casal.membros
        ],
        "resultado": fechado.resultado if fechado else None,
        "lider_id": None if fechado or lider is None else ctx.id_do_papel(lider),
    }


def historico(db: Session, ctx: Contexto, tipo: TipoPeriodo, limite: int = 12) -> list[Ranking]:
    fechar_periodos_pendentes(db, ctx)
    return list(db.scalars(
        select(Ranking)
        .where(Ranking.casal_id == ctx.casal.id, Ranking.tipo_periodo == tipo)
        .order_by(Ranking.referencia.desc())
        .limit(limite)
    ))
