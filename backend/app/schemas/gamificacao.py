from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import OrigemCredito, Papel, ResultadoPeriodo, StatusCredito, StatusVale, TipoPeriodo


class ValeEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=80)
    descricao: str | None = Field(default=None, max_length=280)
    icone: str | None = Field(default=None, max_length=8)


class ValeSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    criador_id: str
    titulo: str
    descricao: str | None
    icone: str | None
    status: StatusVale
    resgatado_por_id: str | None
    criado_em: datetime
    resgatado_em: datetime | None
    utilizado_em: datetime | None


class CreditoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    origem: OrigemCredito
    referencia: str
    status: StatusCredito
    expira_em: datetime
    criado_em: datetime


class ParticipantePlacar(BaseModel):
    usuario_id: str
    nome: str
    papel: Papel
    pontos: int


class PlacarSaida(BaseModel):
    tipo: TipoPeriodo
    referencia: str
    data_inicio: date
    data_fim: date
    fechado: bool
    fecha_em: datetime | None
    participantes: list[ParticipantePlacar]
    resultado: ResultadoPeriodo | None   # só quando fechado
    lider_id: str | None                 # parcial, enquanto aberto


class RankingSaida(BaseModel):
    """Placar de um período já fechado (histórico)."""
    model_config = ConfigDict(from_attributes=True)
    tipo_periodo: TipoPeriodo
    referencia: str
    data_inicio: date
    data_fim: date
    pontos_a: int
    pontos_b: int
    resultado: ResultadoPeriodo
    fechado_em: datetime
