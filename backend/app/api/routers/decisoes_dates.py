"""Minigame de decisão (RF03) e ideias de dates (RF04)."""
from fastapi import APIRouter, status

from app.domain.enums import AmbienteDate, CategoriaDate, CustoDate
from app.schemas.decisao_date import EnvioDecisao, IdeiaEntrada, IdeiaSaida, SessaoEntrada, SessaoSaida
from app.services import date_service, decisao_service

from ..deps import DB, Ctx, Notificar

decisoes = APIRouter(prefix="/decisoes", tags=["Minigame de decisão"])
dates = APIRouter(prefix="/dates", tags=["Ideias de dates"])


@decisoes.get("", response_model=list[SessaoSaida])
def listar_rodadas(ctx: Ctx, db: DB):
    return [decisao_service.montar_visao(ctx, s) for s in decisao_service.listar(db, ctx)]


@decisoes.post("", response_model=SessaoSaida, status_code=status.HTTP_201_CREATED)
def abrir_rodada(dados: SessaoEntrada, ctx: Ctx, db: DB, notificar: Notificar):
    sessao = decisao_service.criar(db, ctx, dados.titulo, dados.contexto)
    notificar(ctx, "decisao.aberta", sessao_id=sessao.id, titulo=sessao.titulo)
    return decisao_service.montar_visao(ctx, sessao)


@decisoes.get("/{sessao_id}", response_model=SessaoSaida)
def ver_rodada(sessao_id: str, ctx: Ctx, db: DB):
    return decisao_service.montar_visao(ctx, decisao_service.obter(db, ctx, sessao_id))


@decisoes.put("/{sessao_id}/opcoes", response_model=SessaoSaida, summary="Envia preferências e vetos em segredo")
def enviar_opcoes(sessao_id: str, envio: EnvioDecisao, ctx: Ctx, db: DB, notificar: Notificar):
    sessao = decisao_service.enviar(db, ctx, sessao_id, envio)
    notificar(ctx, "decisao.atualizada", sessao_id=sessao.id, status=sessao.status)
    return decisao_service.montar_visao(ctx, sessao)


@decisoes.post("/{sessao_id}/cancelar", response_model=SessaoSaida)
def cancelar_rodada(sessao_id: str, ctx: Ctx, db: DB, notificar: Notificar):
    sessao = decisao_service.cancelar(db, ctx, sessao_id)
    notificar(ctx, "decisao.atualizada", sessao_id=sessao.id, status=sessao.status)
    return decisao_service.montar_visao(ctx, sessao)


@dates.get("", response_model=list[IdeiaSaida])
def listar_ideias(
    ctx: Ctx, db: DB, ambiente: AmbienteDate | None = None, categoria: CategoriaDate | None = None,
    custo: CustoDate | None = None, favoritos: bool = False, busca: str | None = None,
):
    return date_service.listar(db, ctx, ambiente, categoria, custo, favoritos, busca)


@dates.get("/sortear", response_model=IdeiaSaida, summary="Sugestão aleatória (ex.: dia de cansaço, em casa)")
def sortear_ideia(ctx: Ctx, db: DB, ambiente: AmbienteDate | None = None):
    return date_service.sortear(db, ctx, ambiente)


@dates.post("", response_model=IdeiaSaida, status_code=status.HTTP_201_CREATED)
def criar_ideia(dados: IdeiaEntrada, ctx: Ctx, db: DB):
    return date_service.criar(db, ctx, dados)


@dates.put("/{ideia_id}/favorito", response_model=IdeiaSaida)
def favoritar(ideia_id: str, ctx: Ctx, db: DB):
    return date_service.favoritar(db, ctx, ideia_id, True)


@dates.delete("/{ideia_id}/favorito", response_model=IdeiaSaida)
def desfavoritar(ideia_id: str, ctx: Ctx, db: DB):
    return date_service.favoritar(db, ctx, ideia_id, False)


@dates.put("/{ideia_id}/realizado", response_model=IdeiaSaida, summary="Marca o date como feito")
def realizado(ideia_id: str, ctx: Ctx, db: DB):
    return date_service.marcar_realizado(db, ctx, ideia_id)
