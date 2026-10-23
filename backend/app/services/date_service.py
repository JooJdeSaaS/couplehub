"""Banco de ideias de dates (RF04)."""
import random

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core import relogio
from app.domain.enums import AmbienteDate, CategoriaDate, CustoDate
from app.domain.erros import NaoEncontrado
from app.models import DateFavorito, IdeiaDate
from app.schemas.decisao_date import IdeiaEntrada

from .contexto import Contexto


def _visiveis(ctx: Contexto):
    """Catálogo global + ideias do próprio casal. Nunca as de outro casal (RB04)."""
    return or_(IdeiaDate.casal_id.is_(None), IdeiaDate.casal_id == ctx.casal.id)


def _obter(db: Session, ctx: Contexto, ideia_id: str) -> IdeiaDate:
    ideia = db.get(IdeiaDate, ideia_id)
    if ideia is None or ideia.casal_id not in (None, ctx.casal.id):
        raise NaoEncontrado("Ideia não encontrada.")
    return ideia


def listar(
    db: Session, ctx: Contexto, ambiente: AmbienteDate | None = None, categoria: CategoriaDate | None = None,
    custo: CustoDate | None = None, apenas_favoritos: bool = False, busca: str | None = None,
) -> list[dict]:
    consulta = (
        select(IdeiaDate, DateFavorito)
        .outerjoin(DateFavorito, (DateFavorito.ideia_id == IdeiaDate.id) & (DateFavorito.casal_id == ctx.casal.id))
        .where(_visiveis(ctx))
        .order_by(IdeiaDate.casal_id.is_(None), IdeiaDate.titulo)   # do casal primeiro
    )
    if ambiente:
        consulta = consulta.where(IdeiaDate.ambiente == ambiente)
    if categoria:
        consulta = consulta.where(IdeiaDate.categoria == categoria)
    if custo:
        consulta = consulta.where(IdeiaDate.custo == custo)
    if apenas_favoritos:
        consulta = consulta.where(DateFavorito.ideia_id.is_not(None))
    if busca:
        consulta = consulta.where(IdeiaDate.titulo.ilike(f"%{busca.strip()}%"))
    return [_visao(ideia, fav) for ideia, fav in db.execute(consulta)]


def criar(db: Session, ctx: Contexto, dados: IdeiaEntrada) -> dict:
    ideia = IdeiaDate(casal_id=ctx.casal.id, criado_por_id=ctx.usuario.id, **dados.model_dump())
    db.add(ideia)
    db.commit()
    return _visao(ideia, None)


def favoritar(db: Session, ctx: Contexto, ideia_id: str, favorito: bool) -> dict:
    ideia = _obter(db, ctx, ideia_id)
    fav = db.get(DateFavorito, (ctx.casal.id, ideia.id))
    if favorito and fav is None:
        fav = DateFavorito(casal_id=ctx.casal.id, ideia_id=ideia.id)
        db.add(fav)
    elif not favorito and fav is not None:
        db.delete(fav)
        fav = None
    db.commit()
    return _visao(ideia, fav)


def marcar_realizado(db: Session, ctx: Contexto, ideia_id: str) -> dict:
    ideia = _obter(db, ctx, ideia_id)
    fav = db.get(DateFavorito, (ctx.casal.id, ideia.id)) or DateFavorito(casal_id=ctx.casal.id, ideia_id=ideia.id)
    fav.realizado_em = relogio.agora()
    db.add(fav)
    db.commit()
    return _visao(ideia, fav)


def sortear(db: Session, ctx: Contexto, ambiente: AmbienteDate | None = None) -> dict:
    candidatas = listar(db, ctx, ambiente=ambiente)
    if not candidatas:
        raise NaoEncontrado("Nenhuma ideia para sortear com esse filtro.")
    return random.choice(candidatas)


def _visao(ideia: IdeiaDate, fav: DateFavorito | None) -> dict:
    return {
        "id": ideia.id, "titulo": ideia.titulo, "descricao": ideia.descricao, "ambiente": ideia.ambiente,
        "categoria": ideia.categoria, "custo": ideia.custo, "duracao_min": ideia.duracao_min,
        "personalizada": ideia.casal_id is not None, "favorito": fav is not None,
        "realizado_em": fav.realizado_em if fav else None,
    }
