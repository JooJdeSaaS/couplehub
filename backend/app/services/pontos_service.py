"""Livro-razão de pontos e emissão de créditos de vale (ADR-0004).

Ambas as operações são idempotentes: repetir a mesma chamada não duplica
pontos nem créditos (garantido também por UNIQUE no banco).
"""
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.domain.enums import OrigemCredito, OrigemPontos, StatusCredito
from app.domain.periodos import mes_da_semana
from app.domain.ranking import validade_credito
from app.models import CreditoVale, LancamentoPontos


def lancar(
    db: Session, casal_id: str, usuario_id: str, pontos: int, origem: OrigemPontos,
    referencia_id: str, semana_ref: str, descricao: str,
) -> LancamentoPontos | None:
    if pontos <= 0:
        return None
    existente = db.scalar(select(LancamentoPontos).where(
        LancamentoPontos.usuario_id == usuario_id,
        LancamentoPontos.origem == origem,
        LancamentoPontos.referencia_id == referencia_id,
    ))
    if existente:
        return existente
    lancamento = LancamentoPontos(
        casal_id=casal_id, usuario_id=usuario_id, pontos=pontos, origem=origem,
        referencia_id=referencia_id, semana_ref=semana_ref, mes_ref=mes_da_semana(semana_ref),
        descricao=descricao[:120],
    )
    db.add(lancamento)
    return lancamento


def somar(db: Session, casal_id: str, *, semana_ref: str | None = None, mes_ref: str | None = None) -> dict[str, int]:
    """{usuario_id: pontos} da semana OU do mês."""
    filtro = LancamentoPontos.semana_ref == semana_ref if semana_ref else LancamentoPontos.mes_ref == mes_ref
    linhas = db.execute(
        select(LancamentoPontos.usuario_id, func.sum(LancamentoPontos.pontos))
        .where(LancamentoPontos.casal_id == casal_id, filtro)
        .group_by(LancamentoPontos.usuario_id)
    ).all()
    return {usuario_id: int(total) for usuario_id, total in linhas}


def emitir_credito(
    db: Session, casal_id: str, usuario_id: str, origem: OrigemCredito, referencia: str, agora: datetime,
) -> CreditoVale:
    existente = db.scalar(select(CreditoVale).where(
        CreditoVale.usuario_id == usuario_id, CreditoVale.origem == origem, CreditoVale.referencia == referencia,
    ))
    if existente:
        return existente
    credito = CreditoVale(
        casal_id=casal_id, usuario_id=usuario_id, origem=origem, referencia=referencia,
        status=StatusCredito.PENDENTE, expira_em=validade_credito(agora),
    )
    db.add(credito)
    return credito


def expirar_creditos(db: Session, casal_id: str, agora: datetime) -> None:
    db.execute(
        update(CreditoVale)
        .where(CreditoVale.casal_id == casal_id, CreditoVale.status == StatusCredito.PENDENTE,
               CreditoVale.expira_em <= agora)
        .values(status=StatusCredito.EXPIRADO)
    )
