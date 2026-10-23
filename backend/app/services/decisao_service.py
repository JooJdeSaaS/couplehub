"""Minigame "Onde vamos?" (RF03). Algoritmo em app/domain/decisao.py."""
import random
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import relogio
from app.domain import decisao as regras
from app.domain.enums import ContextoDecisao, Papel, StatusDecisao, TipoResultadoDecisao
from app.domain.erros import AcessoNegado, TransicaoInvalida
from app.models import EntradaDecisao, SessaoDecisao
from app.schemas.decisao_date import EnvioDecisao

from .contexto import Contexto, obter_do_casal


def criar(db: Session, ctx: Contexto, titulo: str, contexto: ContextoDecisao) -> SessaoDecisao:
    sessao = SessaoDecisao(casal_id=ctx.casal.id, criado_por_id=ctx.usuario.id, titulo=titulo.strip(), contexto=contexto)
    db.add(sessao)
    db.commit()
    return sessao


def listar(db: Session, ctx: Contexto, limite: int = 20) -> list[SessaoDecisao]:
    return list(db.scalars(
        select(SessaoDecisao).where(SessaoDecisao.casal_id == ctx.casal.id)
        .order_by(SessaoDecisao.criado_em.desc()).limit(limite)
    ))


def obter(db: Session, ctx: Contexto, sessao_id: str) -> SessaoDecisao:
    return obter_do_casal(db, SessaoDecisao, sessao_id, ctx.casal.id, "Rodada")


def enviar(db: Session, ctx: Contexto, sessao_id: str, envio: EnvioDecisao) -> SessaoDecisao:
    sessao = obter(db, ctx, sessao_id)
    if sessao.status is not StatusDecisao.COLETANDO:
        raise TransicaoInvalida("Esta rodada já foi encerrada.", "RODADA_ENCERRADA")
    if any(e.usuario_id == ctx.usuario.id for e in sessao.entradas):
        raise TransicaoInvalida("Você já enviou suas opções nesta rodada.", "ENVIO_DUPLICADO")

    submissao = _submissao(envio)
    regras.validar_submissao(submissao)
    for p in submissao.preferencias:
        sessao.entradas.append(EntradaDecisao(usuario_id=ctx.usuario.id, rotulo=p.rotulo.strip(), peso=p.peso, veto=False))
    for v in submissao.vetos:
        sessao.entradas.append(EntradaDecisao(usuario_id=ctx.usuario.id, rotulo=v.strip(), peso=None, veto=True))

    if {e.usuario_id for e in sessao.entradas} == {ctx.usuario.id, ctx.parceiro.id}:
        _resolver(db, ctx, sessao)
    db.commit()
    return sessao


def cancelar(db: Session, ctx: Contexto, sessao_id: str) -> SessaoDecisao:
    sessao = obter(db, ctx, sessao_id)
    if sessao.criado_por_id != ctx.usuario.id:
        raise AcessoNegado("Só quem abriu a rodada pode cancelá-la.", "NAO_CRIADOR")
    if sessao.status is not StatusDecisao.COLETANDO:
        raise TransicaoInvalida("Esta rodada já foi encerrada.", "RODADA_ENCERRADA")
    sessao.status = StatusDecisao.CANCELADA
    db.commit()
    return sessao


def _submissao(envio: EnvioDecisao) -> regras.Submissao:
    return regras.Submissao(
        preferencias=tuple(regras.Preferencia(p.rotulo, p.peso) for p in envio.preferencias),
        vetos=tuple(envio.vetos),
    )


def _submissao_de(sessao: SessaoDecisao, usuario_id: str) -> regras.Submissao:
    entradas = [e for e in sessao.entradas if e.usuario_id == usuario_id]
    return regras.Submissao(
        preferencias=tuple(regras.Preferencia(e.rotulo, e.peso) for e in entradas if not e.veto),
        vetos=tuple(e.rotulo for e in entradas if e.veto),
    )


def _ultimo_favorecido(db: Session, ctx: Contexto, exceto: str) -> Papel | None:
    favorecido_id = db.scalar(
        select(SessaoDecisao.favorecido_id)
        .where(SessaoDecisao.casal_id == ctx.casal.id, SessaoDecisao.id != exceto,
               SessaoDecisao.tipo_resultado == TipoResultadoDecisao.PONDERADO)
        .order_by(SessaoDecisao.resolvida_em.desc()).limit(1)
    )
    return ctx.papel_de(favorecido_id) if favorecido_id else None


def _resolver(db: Session, ctx: Contexto, sessao: SessaoDecisao) -> None:
    semente = secrets.randbits(31)
    resultado = regras.decidir(
        _submissao_de(sessao, ctx.id_do_papel(Papel.A)),
        _submissao_de(sessao, ctx.id_do_papel(Papel.B)),
        random.Random(semente),
        _ultimo_favorecido(db, ctx, exceto=sessao.id),
    )
    sessao.status = StatusDecisao.RESOLVIDA
    sessao.tipo_resultado = resultado.tipo
    sessao.resultado_rotulo = resultado.rotulo
    sessao.favorecido_id = ctx.id_do_papel(resultado.favorecido) if resultado.favorecido else None
    sessao.escolhedor_id = ctx.id_do_papel(resultado.escolhedor) if resultado.escolhedor else None
    sessao.justificativa = resultado.justificativa[:280]
    sessao.semente = semente
    sessao.resolvida_em = relogio.agora()


def montar_visao(ctx: Contexto, sessao: SessaoDecisao) -> dict:
    """Opções do parceiro ficam em segredo até a rodada ser resolvida (REQ-DEC-001)."""
    def visao(usuario_id: str) -> list[dict]:
        return [{"rotulo": e.rotulo, "peso": e.peso, "veto": e.veto} for e in sessao.entradas if e.usuario_id == usuario_id]

    resolvida = sessao.status is StatusDecisao.RESOLVIDA
    return {
        "id": sessao.id, "titulo": sessao.titulo, "contexto": sessao.contexto, "status": sessao.status,
        "criado_em": sessao.criado_em,
        "eu_enviei": any(e.usuario_id == ctx.usuario.id for e in sessao.entradas),
        "parceiro_enviou": any(e.usuario_id == ctx.parceiro.id for e in sessao.entradas),
        "minhas_entradas": visao(ctx.usuario.id),
        "entradas_do_parceiro": visao(ctx.parceiro.id) if resolvida else None,
        "resultado": {
            "tipo": sessao.tipo_resultado, "rotulo": sessao.resultado_rotulo,
            "favorecido_id": sessao.favorecido_id, "escolhedor_id": sessao.escolhedor_id,
            "justificativa": sessao.justificativa, "semente": sessao.semente,
        } if resolvida else None,
    }
