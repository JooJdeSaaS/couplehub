from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import (
    AmbienteDate,
    CategoriaDate,
    ContextoDecisao,
    CustoDate,
    StatusDecisao,
    TipoResultadoDecisao,
)


# --- Minigame de decisão -----------------------------------------------------
class SessaoEntrada(BaseModel):
    titulo: str = Field(min_length=2, max_length=80)
    contexto: ContextoDecisao = ContextoDecisao.RESTAURANTE


class PreferenciaEntrada(BaseModel):
    rotulo: str = Field(max_length=60)
    peso: int = 3


class EnvioDecisao(BaseModel):
    preferencias: list[PreferenciaEntrada]
    vetos: list[str] = []


class EntradaVisao(BaseModel):
    rotulo: str
    peso: int | None
    veto: bool


class ResultadoVisao(BaseModel):
    tipo: TipoResultadoDecisao
    rotulo: str | None
    favorecido_id: str | None
    escolhedor_id: str | None
    justificativa: str | None
    semente: int | None


class SessaoSaida(BaseModel):
    id: str
    titulo: str
    contexto: ContextoDecisao
    status: StatusDecisao
    criado_em: datetime
    eu_enviei: bool
    parceiro_enviou: bool
    minhas_entradas: list[EntradaVisao]
    entradas_do_parceiro: list[EntradaVisao] | None  # segredo até RESOLVIDA
    resultado: ResultadoVisao | None


# --- Ideias de dates ---------------------------------------------------------
class IdeiaEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    descricao: str | None = Field(default=None, max_length=500)
    ambiente: AmbienteDate
    categoria: CategoriaDate
    custo: CustoDate = CustoDate.BAIXO
    duracao_min: int | None = Field(default=None, ge=10, le=24 * 60)


class IdeiaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    titulo: str
    descricao: str | None
    ambiente: AmbienteDate
    categoria: CategoriaDate
    custo: CustoDate
    duracao_min: int | None
    personalizada: bool = False
    favorito: bool = False
    realizado_em: datetime | None = None
