"""Vales e créditos de resgate (RF08, RF09)."""
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core import relogio
from app.domain import vales as regras
from app.domain.enums import StatusCredito, StatusVale
from app.domain.erros import TransicaoInvalida
from app.models import CreditoVale, Vale
from app.schemas.gamificacao import ValeEntrada

from . import ranking_service
from .contexto import Contexto, obter_do_casal


def listar(db: Session, ctx: Contexto, status: StatusVale | None = None) -> list[Vale]:
    consulta = select(Vale).where(Vale.casal_id == ctx.casal.id).order_by(Vale.criado_em.desc())
    if status:
        consulta = consulta.where(Vale.status == status)
    return list(db.scalars(consulta))


def creditos(db: Session, ctx: Contexto, apenas_pendentes: bool = True) -> list[CreditoVale]:
    ranking_service.fechar_periodos_pendentes(db, ctx)  # garante créditos da semana que acabou de fechar
    consulta = select(CreditoVale).where(CreditoVale.usuario_id == ctx.usuario.id).order_by(CreditoVale.expira_em)
    if apenas_pendentes:
        consulta = consulta.where(CreditoVale.status == StatusCredito.PENDENTE)
    return list(db.scalars(consulta))


def criar(db: Session, ctx: Contexto, dados: ValeEntrada) -> Vale:
    disponiveis = db.scalar(select(func.count(Vale.id)).where(
        Vale.criador_id == ctx.usuario.id, Vale.status == StatusVale.DISPONIVEL,
    ))
    regras.validar_criacao(dados.titulo, disponiveis or 0)
    vale = Vale(
        casal_id=ctx.casal.id, criador_id=ctx.usuario.id, titulo=dados.titulo.strip(),
        descricao=dados.descricao, icone=dados.icone, status=StatusVale.DISPONIVEL,
    )
    db.add(vale)
    db.commit()
    return vale


def resgatar(db: Session, ctx: Contexto, vale_id: str) -> Vale:
    vale = obter_do_casal(db, Vale, vale_id, ctx.casal.id, "Vale")
    pendentes = creditos(db, ctx)          # já fecha períodos e expira créditos vencidos
    credito = pendentes[0] if pendentes else None   # o que vence primeiro é usado primeiro
    novo = regras.validar_resgate(vale.status, vale.criador_id, ctx.usuario.id, tem_credito=credito is not None)
    assert credito is not None  # garantido por validar_resgate
    agora = relogio.agora()

    # compare-and-set: se dois resgates chegarem juntos, só um encontra DISPONIVEL (REQ-VAL-008)
    alterados = db.execute(
        update(Vale)
        .where(Vale.id == vale.id, Vale.status == StatusVale.DISPONIVEL)
        .values(status=novo, resgatado_por_id=ctx.usuario.id, credito_id=credito.id, resgatado_em=agora)
        .execution_options(synchronize_session=False)
    ).rowcount
    if alterados != 1:
        db.rollback()
        raise TransicaoInvalida("Este vale acabou de ser resgatado.", "CONCORRENCIA")
    credito.status, credito.consumido_em = StatusCredito.CONSUMIDO, agora
    db.commit()
    db.refresh(vale)
    return vale


def confirmar_uso(db: Session, ctx: Contexto, vale_id: str) -> Vale:
    vale = obter_do_casal(db, Vale, vale_id, ctx.casal.id, "Vale")
    vale.status = regras.validar_confirmacao_uso(vale.status, vale.resgatado_por_id, ctx.usuario.id)
    vale.utilizado_em = relogio.agora()
    db.commit()
    return vale


def cancelar(db: Session, ctx: Contexto, vale_id: str) -> Vale:
    vale = obter_do_casal(db, Vale, vale_id, ctx.casal.id, "Vale")
    vale.status = regras.validar_cancelamento(vale.status, vale.criador_id, ctx.usuario.id)
    vale.cancelado_em = relogio.agora()
    db.commit()
    return vale
